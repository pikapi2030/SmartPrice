import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database.connection import engine, Base, get_db
from backend.database.models import SearchHistory, CachedResult
from backend.scrapers.amazon import scrape_amazon
from backend.scrapers.flipkart import scrape_flipkart
from backend.services.matcher import match_products
from backend.services.comparator import calculate_comparison_stats, sort_comparison_results

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Successfully initialized SQLite database.")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time price comparison API between Amazon India and Flipkart.",
    version="1.0.0"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class SearchRequest(BaseModel):
    query: str

class ProductVariant(BaseModel):
    color: str
    price: float
    rating: float
    url: str
    image: str
    title: str

class ProductDetail(BaseModel):
    title: str
    price: float
    rating: float
    url: str
    image: str
    platform: str
    variants: Optional[List[ProductVariant]] = None

class ComparisonResult(BaseModel):
    product_name: str
    amazon_price: Optional[float] = None
    flipkart_price: Optional[float] = None
    best_platform: str
    difference: float
    percentage_difference: float
    amazon_product: Optional[ProductDetail] = None
    flipkart_product: Optional[ProductDetail] = None
    similarity_score: float

class Stats(BaseModel):
    total_items: int
    matched_items: int
    amazon_cheaper_count: int
    flipkart_cheaper_count: int
    equal_count: int
    avg_difference_percentage: float

class SearchResponse(BaseModel):
    results: List[ComparisonResult]
    stats: Stats
    source: str  # "cache" or "live"

class HistoryResponse(BaseModel):
    query: str
    timestamp: str

def filter_price_outliers(raw_list: list, query: str) -> list:
    if not raw_list:
        return raw_list
        
    query_lower = query.lower()
    accessory_keywords = [
        'case', 'cover', 'glass', 'protector', 'guard', 'charger', 'cable', 
        'strap', 'adapter', 'pouch', 'skin', 'holder', 'stand', 'mount',
        'buds', 'earbuds', 'headphone', 'headset', 'film', 'shield'
    ]
    is_acc_query = any(kw in query_lower for kw in accessory_keywords)
    if is_acc_query:
        return raw_list
        
    valid_prices = [item['price'] for item in raw_list if item.get('price') is not None]
    if not valid_prices:
        return raw_list
        
    max_price = max(valid_prices)
    if max_price <= 15000:
        return raw_list
        
    filtered = []
    for item in raw_list:
        price = item.get('price', 0.0)
        # If the item is less than 12% of the max price, and it's under Rs 8000, filter it
        if price < (max_price * 0.12) and price < 8000:
            logger.info(f"Filtering out price outlier: {item['title']} (Price: {price})")
            continue
        filtered.append(item)
        
    return filtered

# Endpoints
@app.post("/api/search", response_model=SearchResponse)
async def search_and_compare(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Search for a product. Looks up cache first. If cache is missing/expired,
    concurrently scrapes Amazon & Flipkart using Selenium, caches the results,
    and returns matched & compared items.
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
    logger.info(f"Received search query: '{query}'")
    
    # Save search history
    try:
        history_entry = SearchHistory(query=query)
        db.add(history_entry)
        db.commit()
    except Exception as he:
        logger.error(f"Failed to record history entry: {he}")
        db.rollback()

    # Check database cache
    cache_record = db.query(CachedResult).filter(CachedResult.query == query.lower()).first()
    now = datetime.utcnow()
    
    use_cache = False
    amazon_raw = []
    flipkart_raw = []
    
    if cache_record:
        expiry_time = cache_record.created_at + timedelta(seconds=settings.CACHE_EXPIRY_SECONDS)
        if now < expiry_time:
            use_cache = True
            logger.info("Cache hit! Serving from database cache.")
            try:
                amazon_raw = json.loads(cache_record.amazon_data)
                flipkart_raw = json.loads(cache_record.flipkart_data)
            except Exception as e:
                logger.error(f"Error parsing cached JSON: {e}")
                use_cache = False  # Recalculate if cache load fails
        else:
            logger.info("Cache expired. Initiating live scrape.")
            
    source = "cache"
    
    if not use_cache:
        source = "live"
        logger.info("Cache miss or expired. Scraping platforms concurrently...")
        
        # Run Selenium scrapers concurrently in separate threads to not block asyncio event loop
        try:
            amazon_task = asyncio.to_thread(scrape_amazon, query)
            flipkart_task = asyncio.to_thread(scrape_flipkart, query)
            
            amazon_raw, flipkart_raw = await asyncio.gather(amazon_task, flipkart_task)
            
            logger.info(f"Live scrape complete. Amazon: {len(amazon_raw)} items, Flipkart: {len(flipkart_raw)} items.")
            
            # Update cache
            if cache_record:
                cache_record.amazon_data = json.dumps(amazon_raw)
                cache_record.flipkart_data = json.dumps(flipkart_raw)
                cache_record.created_at = now
            else:
                new_cache = CachedResult(
                    query=query.lower(),
                    amazon_data=json.dumps(amazon_raw),
                    flipkart_data=json.dumps(flipkart_raw),
                    created_at=now
                )
                db.add(new_cache)
                
            db.commit()
            logger.info("Successfully updated database cache.")
            
        except Exception as scrap_err:
            logger.error(f"Error during live scraping / caching: {scrap_err}")
            db.rollback()
            # If live scraping throws an error, return empty results or fall back
            if not amazon_raw and not flipkart_raw:
                raise HTTPException(
                    status_code=500, 
                    detail=f"An error occurred while fetching product results: {str(scrap_err)}"
                )

    # Filter price outliers
    amazon_filtered = filter_price_outliers(amazon_raw, query)
    flipkart_filtered = filter_price_outliers(flipkart_raw, query)
    
    # Perform matching
    matched_results = match_products(amazon_filtered, flipkart_filtered)
    
    # Calculate stats
    stats = calculate_comparison_stats(matched_results)
    
    # Default sort: cheapest price first
    sorted_results = sort_comparison_results(matched_results, "price_asc")
    
    return SearchResponse(
        results=sorted_results,
        stats=stats,
        source=source
    )

@app.get("/api/history", response_model=List[HistoryResponse])
def get_search_history(db: Session = Depends(get_db)):
    """
    Returns the top 10 unique recent search queries.
    """
    try:
        # Get unique recent search queries
        results = (
            db.query(SearchHistory.query, SearchHistory.timestamp)
            .order_by(SearchHistory.timestamp.desc())
            .limit(50)
            .all()
        )
        
        # Filter for unique queries while preserving order
        seen = set()
        unique_history = []
        for query, timestamp in results:
            clean = query.strip()
            if clean.lower() not in seen:
                seen.add(clean.lower())
                unique_history.append(
                    HistoryResponse(
                        query=clean,
                        timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    )
                )
            if len(unique_history) >= 10:
                break
                
        return unique_history
    except Exception as e:
        logger.error(f"Error fetching search history: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve search history")

@app.post("/api/cache/clear")
def clear_cache(db: Session = Depends(get_db)):
    """
    Clears all cached scraping results from the database.
    """
    try:
        num_rows = db.query(CachedResult).delete()
        db.commit()
        logger.info(f"Database cache cleared. Removed {num_rows} records.")
        return {"status": "success", "message": f"Successfully cleared {num_rows} cached results."}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to clear database cache.")

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
