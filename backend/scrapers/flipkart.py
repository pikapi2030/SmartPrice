import time
import logging
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.config import settings
from backend.scrapers.amazon import get_chrome_options
from backend.scrapers.mock_data import generate_mock_results
from backend.services.matcher import is_accessory_item

logger = logging.getLogger(__name__)

def scrape_flipkart(query: str) -> list:
    """
    Scrapes Flipkart for the given query and returns top 15 results.
    """
    logger.info(f"Starting Flipkart scrape for query: {query}")
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.flipkart.com/search?q={encoded_query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
    
    driver = None
    results = []
    
    try:
        chrome_options = get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(settings.SELENIUM_TIMEOUT)
        
        driver.get(url)
        
        # Wait for either list-style elements, grid-style elements, or any product link
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="_2kHMtA"], div[class*="tUxRFH"], div[class*="_4dduaL"], a[href*="/p/"]'))
        )
        # Dynamic render sleep: wait 2 seconds for React listings to settle
        time.sleep(2)
        
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # 1. Primary: Containers with data-id (Universal Flipkart product identifier attribute)
        items = soup.select('div[data-id]')
        
        # 2. Fallback to list-view containers
        if not items:
            items = soup.select('div[class*="tUxRFH"], div._2kHMtA')
        
        # 3. Fallback to grid-view containers
        if not items:
            items = soup.select('div[class*="_4dduaL"], div._1AtVb7, div._1xHGtK')
            
        # If still not found, let's extract all anchors containing "/p/itm" and get their containers
        if not items:
            p_anchors = []
            for a in soup.select('a[href*="/p/itm"]'):
                # Skip brand name anchors (which typically have class containing '_2WkVRV' or 'brand')
                classes = a.get("class", [])
                class_str = " ".join(classes) if isinstance(classes, list) else str(classes)
                if '_2WkVRV' in class_str or 'brand' in class_str:
                    continue
                
                # Skip if the anchor text is just a known brand name
                text_clean = a.text.strip().lower()
                if text_clean in ['boat', 'noise', 'apple', 'samsung', 'oneplus', 'sony', 'realme', 'mi', 'redmi']:
                    continue
                
                p_anchors.append(a)

            seen_hrefs = set()
            items = []
            for a in p_anchors:
                href = a.get("href")
                if href and href not in seen_hrefs:
                    seen_hrefs.add(href)
                    # Use the anchor itself or its immediate parent as container
                    items.append(a.parent if a.parent else a)
        
        logger.info(f"Found {len(items)} raw result containers on Flipkart")
        
        for item in items:
            if len(results) >= 15:
                break
                
            try:
                # Title - Try multiple selectors since Flipkart class names change frequently
                title = ""
                title_selectors = [
                    'div.RG5Slk', 'a.k7wcnx', 'div[class*="RG5Slk"]', 'a[class*="k7wcnx"]',
                    'div[class*="KzDlHZ"]', 'a[class*="IRpwTa"]', 'a[class*="wjcE5T"]', 
                    'div._4rR01T', 'a.IRpwTa', 'a._2WkVRV', '.product-title', 'a[title]'
                ]
                for selector in title_selectors:
                    title_el = item.select_one(selector)
                    if title_el:
                        title = title_el.text.strip() or title_el.get("title", "").strip()
                        if title:
                            # If we matched the brand name tag e.g. '_2WkVRV', we need to append the product name tag
                            if selector == 'a._2WkVRV' or 'brand' in selector:
                                prod_name_el = item.select_one('a[class*="IRpwTa"]')
                                if prod_name_el:
                                    title = f"{title} {prod_name_el.text.strip()}"
                            break
                
                # Bulletproof fallback: use the alt text of the first product image, which always contains the full title
                if not title:
                    img_el = item.select_one('img[alt]')
                    if img_el:
                        title = img_el.get("alt", "").strip()
                            
                if not title:
                    # Try text content of anchor
                    if item.name == 'a' or item.select_one('a'):
                        anchor = item if item.name == 'a' else item.select_one('a')
                        if "/p/itm" in anchor.get("href", ""):
                            title = anchor.text.strip()
                            
                if not title:
                    continue
                
                # Price - Try multiple price selectors
                price = None
                price_selectors = [
                    'div.hZ3P6w', 'div.DeU9vF', 'div[class*="hZ3P6w"]', 'div[class*="DeU9vF"]',
                    'div[class*="Nx9saj"]', 'div._30jeq3', 'div._1vC4OI', 'div[class*="_1vC4OI"]', 'div[class*="Nx9saj"] span'
                ]
                for selector in price_selectors:
                    price_el = item.select_one(selector)
                    if price_el:
                        price_str = price_el.text.replace(",", "").replace("₹", "").strip()
                        # Extract numbers only in case of combined text (e.g. "₹50,00010% off")
                        price_digits = "".join(c for c in price_str if c.isdigit() or c == '.')
                        if price_digits:
                            try:
                                price = float(price_digits)
                                break
                            except ValueError:
                                pass
                                
                if price is None:
                    continue
                
                # Filter accessories
                if is_accessory_item(title, query, price):
                    continue
                
                # Rating
                rating = 0.0
                rating_selectors = [
                    'div.MKiFS6', 'div[class*="MKiFS6"]',
                    'div[class*="X1Z1Jn"]', 'div._3LWZlK', 'span[class*="Y1Z1Jn"]', 'div[class*="Y1Z1Jn"]'
                ]
                for selector in rating_selectors:
                    rating_el = item.select_one(selector)
                    if rating_el:
                        rating_text = rating_el.text.strip()
                        # Clean rating string (sometimes contains stars/extra details)
                        rating_digits = "".join(c for c in rating_text if c.isdigit() or c == '.')
                        if rating_digits:
                            try:
                                rating = float(rating_digits)
                                # Ensure it's a valid out-of-5 rating (Flipkart rating is e.g. 4.5)
                                if 0.0 <= rating <= 5.0:
                                    break
                            except ValueError:
                                pass
                
                # Product URL
                product_url = ""
                if item.name == 'a' and "/p/itm" in item.get("href", ""):
                    product_url = item.get("href")
                else:
                    url_el = item.select_one('a[href*="/p/"]')
                    if url_el:
                        product_url = url_el.get("href")
                
                if not product_url:
                    continue
                    
                if product_url.startswith("/"):
                    product_url = f"https://www.flipkart.com{product_url}"
                # Keep full URL (parameters like 'pid' are required by Flipkart to route to the correct product page)
                pass
                
                # Image URL
                image_url = ""
                img_selectors = ['img[class*="DByoEF"]', 'img._396cs4', 'img._2r_l1q', 'img[src]']
                for selector in img_selectors:
                    img_el = item.select_one(selector)
                    if img_el:
                        src = img_el.get("src")
                        if src and "data:image" not in src:
                            image_url = src
                            break
                            
                results.append({
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "url": product_url,
                    "image": image_url,
                    "platform": "Flipkart"
                })
                
            except Exception as item_err:
                logger.debug(f"Error parsing Flipkart item: {item_err}")
                continue
                
    except Exception as e:
        logger.error(f"Flipkart scraper failed or was blocked: {e}")
        
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
                
    # Fallback to mock data if empty results
    if not results and settings.MOCK_FALLBACK:
        logger.warning(f"No results scraped from Flipkart. Falling back to mock data.")
        return generate_mock_results(query, "flipkart")
        
    return results
