def get_cheapest_price(item: dict) -> float:
    """Returns the lowest available price for an item, ignoring None values."""
    am_price = item.get("amazon_price")
    fk_price = item.get("flipkart_price")
    
    if am_price is not None and fk_price is not None:
        return min(am_price, fk_price)
    if am_price is not None:
        return am_price
    if fk_price is not None:
        return fk_price
    return float('inf')

def get_highest_rating(item: dict) -> float:
    """Gets the best rating between platforms."""
    am_rate = 0.0
    fk_rate = 0.0
    if item.get("amazon_product"):
        am_rate = item["amazon_product"].get("rating", 0.0) or 0.0
    if item.get("flipkart_product"):
        fk_rate = item["flipkart_product"].get("rating", 0.0) or 0.0
    return max(am_rate, fk_rate)

def sort_comparison_results(results: list, sort_by: str) -> list:
    """
    Sorts comparison results based on:
    - 'price_asc': Lowest price first
    - 'price_desc': Highest price first
    - 'discount_desc': Highest percentage difference first
    - 'rating_desc': Best rating first
    """
    if sort_by == "price_asc":
        return sorted(results, key=get_cheapest_price)
    elif sort_by == "price_desc":
        return sorted(results, key=lambda x: get_cheapest_price(x), reverse=True)
    elif sort_by == "discount_desc":
        return sorted(results, key=lambda x: x.get("percentage_difference", 0.0), reverse=True)
    elif sort_by == "rating_desc":
        return sorted(results, key=get_highest_rating, reverse=True)
    return results

def calculate_comparison_stats(results: list) -> dict:
    """
    Calculates summary statistics comparing platforms:
    - Total compared items
    - Number of items cheaper on Amazon
    - Number of items cheaper on Flipkart
    - Average difference percentage
    """
    matched = [r for r in results if r["amazon_price"] is not None and r["flipkart_price"] is not None]
    
    amazon_cheaper_count = sum(1 for r in matched if r["best_platform"] == "Amazon")
    flipkart_cheaper_count = sum(1 for r in matched if r["best_platform"] == "Flipkart")
    equal_count = sum(1 for r in matched if r["best_platform"] == "Equal")
    
    avg_diff_pct = 0.0
    if matched:
        avg_diff_pct = sum(r["percentage_difference"] for r in matched) / len(matched)
        
    return {
        "total_items": len(results),
        "matched_items": len(matched),
        "amazon_cheaper_count": amazon_cheaper_count,
        "flipkart_cheaper_count": flipkart_cheaper_count,
        "equal_count": equal_count,
        "avg_difference_percentage": round(avg_diff_pct, 2)
    }
