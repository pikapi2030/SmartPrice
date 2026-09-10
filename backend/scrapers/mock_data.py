import random
import re

def generate_mock_results(query: str, platform: str, count: int = 15) -> list:
    """
    Generates realistic mock product search results based on the search query
    to act as a robust fallback if Amazon/Flipkart block the scraper.
    """
    platform = platform.lower()
    results = []
    
    # Normalize query for detection
    clean_query = query.lower().strip()
    
    # Standardize brands & products
    brand = "Generic"
    if "iphone" in clean_query or "apple" in clean_query:
        brand = "Apple"
    elif "samsung" in clean_query or "galaxy" in clean_query:
        brand = "Samsung"
    elif "oneplus" in clean_query:
        brand = "OnePlus"
    elif "redmi" in clean_query or "xiaomi" in clean_query:
        brand = "Xiaomi"
    elif "hp" in clean_query or "hewlett" in clean_query:
        brand = "HP"
    elif "dell" in clean_query:
        brand = "Dell"
    elif "lenovo" in clean_query:
        brand = "Lenovo"
    elif "sony" in clean_query:
        brand = "Sony"
    
    # Extract numbers from query to keep specifications consistent (e.g. "16", "24", "128")
    numbers = re.findall(r'\d+', clean_query)
    model_num = numbers[0] if numbers else ""
    
    # Base titles, prices, ratings depending on query
    if brand == "Apple" and "iphone" in clean_query:
        model = f"iPhone {model_num}" if model_num else "iPhone 15"
        base_price = 79900
        if "pro" in clean_query:
            model += " Pro"
            base_price = 119900
        if "max" in clean_query:
            model += " Max"
            base_price = 139900
        if "plus" in clean_query:
            model += " Plus"
            base_price = 89900
            
        colors = ["Black", "White", "Blue", "Teal", "Pink", "Natural Titanium", "Desert Titanium"]
        storages = ["128 GB", "256 GB", "512 GB"]
        
        # Generate variations
        for i in range(count):
            col = colors[i % len(colors)]
            st = storages[(i // 2) % len(storages)]
            # Adjust price based on storage
            price_mult = 1.0 + (0.12 * ((i // 2) % len(storages)))
            price = int(base_price * price_mult)
            # Flipkart vs Amazon slight price variations
            price = price - 400 + random.randint(100, 800) if platform == "flipkart" else price + random.randint(100, 500)
            
            # Format title slightly differently for Amazon vs Flipkart
            if platform == "amazon":
                title = f"Apple {model} ({col}, {st})"
                url = f"https://www.amazon.in/Apple-{model.replace(' ', '-')}-{col}-{st.replace(' ', '')}/dp/B0D123456{i}"
                img = "https://images-eu.ssl-images-amazon.com/images/I/71v2jvh6nHL._AC_UL320_.jpg"
            else:
                title = f"APPLE {model.upper()} ({col.upper()}, {st})"
                url = f"https://www.flipkart.com/apple-{model.lower().replace(' ', '-')}-{col.lower()}-{st.lower().replace(' ', '')}-store/p/itm1234567890{i}"
                img = "https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/h/d/9/-original-imagtc2qznszgzwv.jpeg"
                
            results.append({
                "title": title,
                "price": float(price),
                "rating": round(random.uniform(4.4, 4.8), 1),
                "url": url,
                "image": img,
                "platform": "Amazon" if platform == "amazon" else "Flipkart"
            })
            
    elif brand == "Samsung" and ("galaxy" in clean_query or "s24" in clean_query or "s23" in clean_query):
        model = f"Galaxy S{model_num}" if model_num else "Galaxy S24"
        base_price = 74900
        if "ultra" in clean_query:
            model += " Ultra"
            base_price = 124900
        elif "plus" in clean_query or "+" in clean_query:
            model += " Plus"
            base_price = 99900
            
        colors = ["Titanium Black", "Titanium Gray", "Titanium Yellow", "Titanium Violet"]
        storages = ["256 GB", "512 GB"]
        
        for i in range(count):
            col = colors[i % len(colors)]
            st = storages[(i // 2) % len(storages)]
            price_mult = 1.0 + (0.10 * ((i // 2) % len(storages)))
            price = int(base_price * price_mult)
            price = price - 700 + random.randint(100, 1000) if platform == "flipkart" else price + random.randint(100, 600)
            
            if platform == "amazon":
                title = f"Samsung {model} ({col}, {st})"
                url = f"https://www.amazon.in/Samsung-{model.replace(' ', '-')}-{col.replace(' ', '-')}/dp/B0S123456{i}"
                img = "https://images-eu.ssl-images-amazon.com/images/I/71618r-D-WL._AC_UL320_.jpg"
            else:
                title = f"SAMSUNG {model.upper()} ({col.upper()}, {st})"
                url = f"https://www.flipkart.com/samsung-{model.lower().replace(' ', '-')}-{col.lower().replace(' ', '-')}-store/p/itm1234567890{i}"
                img = "https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/5/t/j/galaxy-s24-ultra-sm-s928bztqins-samsung-original-imagxwdptfs75ky3.jpeg"
                
            results.append({
                "title": title,
                "price": float(price),
                "rating": round(random.uniform(4.3, 4.7), 1),
                "url": url,
                "image": img,
                "platform": "Amazon" if platform == "amazon" else "Flipkart"
            })
            
    else:
        # Generic fallback using query terms
        words = query.split()
        product_name = " ".join([w.capitalize() for w in words[:3]])
        base_price = random.choice([999, 1499, 2999, 7999, 15999, 24999])
        
        colors = ["Black", "Blue", "Grey", "White"]
        specs = ["Standard", "Premium", "Pro"]
        
        for i in range(count):
            col = colors[i % len(colors)]
            spec = specs[i % len(specs)]
            price = int(base_price * (1.0 + (i * 0.05)))
            price = price - 50 + random.randint(5, 100) if platform == "flipkart" else price + random.randint(10, 80)
            
            title = f"{brand} {product_name} - {spec} Edition ({col})"
            
            if platform == "amazon":
                url = f"https://www.amazon.in/{product_name.lower().replace(' ', '-')}/dp/B0G123456{i}"
                img = "https://images-eu.ssl-images-amazon.com/images/I/61-r9Z4QYqL._AC_UL320_.jpg"
            else:
                title = title.upper()
                url = f"https://www.flipkart.com/{product_name.lower().replace(' ', '-')}/p/itm1234567890{i}"
                img = "https://rukminim2.flixcart.com/image/312/312/xif0q/computer/8/t/a/inspiron-3520-thin-and-light-laptop-dell-original-imagm9v64h3t2vhh.jpeg"
                
            results.append({
                "title": title,
                "price": float(price),
                "rating": round(random.uniform(3.5, 4.6), 1),
                "url": url,
                "image": img,
                "platform": "Amazon" if platform == "amazon" else "Flipkart"
            })
            
    return results
