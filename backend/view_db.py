import sys
import os
import json

# Ensure parent directory is in python search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import SearchHistory, CachedResult

def inspect_database():
    db = SessionLocal()
    try:
        print("=====================================================================")
        print("                   SMARTPRICE DATABASE VIEWER")
        print("=====================================================================")
        
        # 1. Inspect Search History
        print("\n[1] RECENT SEARCH HISTORY:")
        print("---------------------------------------------------------------------")
        history = db.query(SearchHistory).order_by(SearchHistory.timestamp.desc()).all()
        if not history:
            print("    No search history logged yet.")
        else:
            for idx, entry in enumerate(history):
                print(f"    {idx+1:02d}. Timestamp: {entry.timestamp} | Query: '{entry.query}'")
                
        # 2. Inspect Cache Database
        print("\n[2] CACHED SCRAPED RESULTS:")
        print("---------------------------------------------------------------------")
        caches = db.query(CachedResult).all()
        if not caches:
            print("    No cached items stored yet.")
        else:
            for idx, cache in enumerate(caches):
                try:
                    amazon_count = len(json.loads(cache.amazon_data))
                    flipkart_count = len(json.loads(cache.flipkart_data))
                except Exception:
                    amazon_count = "Error"
                    flipkart_count = "Error"
                
                print(f"    {idx+1:02d}. Query: '{cache.query}'")
                print(f"        Created At:   {cache.created_at}")
                print(f"        Amazon Cache: {amazon_count} items")
                print(f"        Flipkart Cache: {flipkart_count} items")
                print("        ---------------------------------------------")
                
        print("=====================================================================")
    
    except Exception as e:
        print(f"Error reading database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_database()
