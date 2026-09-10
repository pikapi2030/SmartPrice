import sys
import os

# Ensure the root directory is in the Python search path to resolve relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import engine, Base
from backend.services.matcher import match_products
from backend.services.comparator import calculate_comparison_stats
from backend.scrapers.mock_data import generate_mock_results

def test_integration():
    print("==================================================")
    print("       INTEGRATION VERIFICATION STARTING         ")
    print("==================================================")
    
    # 1. Test database schema creation
    print("[1/4] Initializing SQLite database cache schema...")
    Base.metadata.create_all(bind=engine)
    print("      Database cache schema created successfully.")
    
    # 2. Test mock data fallback generation
    print("\n[2/4] Simulating fallback scraper data for 'iPhone 16'...")
    amazon_mock = generate_mock_results("iPhone 16", "amazon", count=5)
    flipkart_mock = generate_mock_results("iPhone 16", "flipkart", count=5)
    print(f"      Scraped mock details (Amazon: {len(amazon_mock)} items, Flipkart: {len(flipkart_mock)} items)")
    
    # 3. Test matcher
    print("\n[3/4] Running fuzzy match comparison engine using RapidFuzz...")
    matched_results = match_products(amazon_mock, flipkart_mock)
    print(f"      Matched list: {len(matched_results)} comparisons generated.")
    for idx, item in enumerate(matched_results[:3]):
        print(f"      - Match #{idx+1}: {item['product_name']}")
        print(f"        Amazon: Rs.{item['amazon_price']} | Flipkart: Rs.{item['flipkart_price']} | Winner: {item['best_platform']}")
        
    # 4. Test comparator statistics
    print("\n[4/4] Calculating comparative savings metrics...")
    stats = calculate_comparison_stats(matched_results)
    print("      Savings analysis details:")
    print(f"      - Total Items Compared: {stats['total_items']}")
    print(f"      - Matched Items count: {stats['matched_items']}")
    print(f"      - Amazon is Cheaper: {stats['amazon_cheaper_count']} times")
    print(f"      - Flipkart is Cheaper: {stats['flipkart_cheaper_count']} times")
    print(f"      - Avg. Discount Difference: {stats['avg_difference_percentage']}%")
    
    print("\n==================================================")
    print("       VERIFICATION COMPLETED SUCCESSFULLY        ")
    print("==================================================")

if __name__ == "__main__":
    test_integration()
