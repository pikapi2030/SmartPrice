import re
from rapidfuzz import fuzz
from backend.config import settings

def clean_title(title: str) -> str:
    """Helper to lowercase, strip parentheses contents, truncate marketing fluff, and strip punctuation."""
    t = title.lower()
    
    # 1. Ignore contents inside parentheses and brackets completely
    t = re.sub(r'\(.*?\)', ' ', t)
    t = re.sub(r'\[.*?\]', ' ', t)
    
    # 2. Truncate marketing fluff after common separators: `:`, `;`, `|`
    for sep in [':', ';', '|']:
        if sep in t:
            t = t.split(sep)[0]
            
    # 3. Also split by " - " (hyphen with spaces)
    if " - " in t:
        t = t.split(" - ")[0]
        
    # 4. Strip common color descriptors (fallback for non-parenthesis text)
    colors = [
        'titanium black', 'titanium whitesilver', 'titanium white', 'titanium gray',
        'titanium yellow', 'titanium violet', 'titanium orange', 'desert titanium',
        'natural titanium', 'black titanium', 'white titanium', 'charcoal black',
        'sky blue', 'silver shadow', 'siren blue', 'starshine green', 'starry black',
        'mint green', 'forest green', 'black velvet', 'green silk', 'cobalt violet',
        'onyx black', 'glacier white', 'fresh blue', 'hyper black', 'mint breeze',
        'dark knight', 'sand storm', 'pitch black', 'quick silver', 'deep purple',
        'sierra blue', 'pacific blue',
        'black', 'white', 'blue', 'teal', 'pink', 'ultramarine', 'yellow', 'violet', 'gray', 'grey',
        'green', 'red', 'gold', 'silver', 'charcoal', 'bronze', 'sand', 'titanium', 'desert', 'natural',
        'space', 'midnight', 'starlight', 'rose', 'mint', 'emerald', 'sapphire', 'obsidian', 'porcelain',
        'hazel', 'bay', 'coral', 'graphite', 'sky', 'shadow', 'silverbirch', 'whitesilver', 'cream', 'peach',
        'lavender', 'phantom', 'aura', 'cloud', 'prism', 'marine', 'sage', 'chalk', 'aloe', 'orange',
        'cobalt', 'onyx', 'glacier', 'breeze', 'dark', 'knight', 'storm', 'pitch', 'quick', 'silk',
        'starry', 'fresh', 'hyper', 'frost', 'mystic', 'cosmic', 'nebula', 'iris', 'amber', 'copper',
        'ruby', 'pearl', 'lemon'
    ]
    for c in colors:
        t = re.sub(rf'\b{c}\b', ' ', t)
        
    t = re.sub(r'[^\w\s\+]', ' ', t)  # keep words, spaces, plus sign
    return " ".join(t.split())

def extract_ram_and_storage(title: str):
    """
    Extracts RAM and Storage specs from a title.
    Returns a tuple of (ram, storage) e.g. ("12gb", "256gb") or (None, None).
    """
    title_clean = title.lower()
    
    ram = None
    storage = None
    
    # 1. Match explicit RAM declarations: e.g. "12gb ram", "12 gb ram", "12 gb lpddr"
    ram_match = re.search(r'\b(\d+)\s*(?:gb|g)\s*(?:ram|lpddr)\b', title_clean)
    if ram_match:
        ram = f"{ram_match.group(1)}gb"
        
    # 2. Match explicit storage: "256gb storage" or "256 gb rom" or "256 gb internal"
    storage_match = re.search(r'\b(\d+)\s*(gb|tb|g|t)\s*(?:storage|rom|internal|ssd|hdd|space|memory)\b', title_clean)
    if storage_match:
        size = storage_match.group(1)
        unit = storage_match.group(2)
        if unit in ('tb', 't'):
            storage = f"{size}tb"
        else:
            storage = f"{size}gb"
            
    # 3. If not found explicitly, parse all GB/TB occurrences
    if not ram or not storage:
        matches = re.findall(r'\b(\d+)\s*(gb|tb|g|t)\b', title_clean)
        sizes = []
        for val, unit in matches:
            v = int(val)
            if unit in ('tb', 't'):
                sizes.append((v * 1024, f"{v}tb"))
            else:
                sizes.append((v, f"{v}gb"))
                
        if len(sizes) >= 2:
            sorted_sizes = sorted(sizes, key=lambda x: x[0])
            if not ram:
                if sorted_sizes[0][0] in (2, 3, 4, 6, 8, 12, 16, 24, 32):
                    ram = sorted_sizes[0][1]
            if not storage:
                storage = sorted_sizes[-1][1]
        elif len(sizes) == 1:
            size_val, size_str = sizes[0]
            if size_val >= 32 or 'tb' in size_str:
                if not storage:
                    storage = size_str
            else:
                if not storage:
                    storage = size_str
                    
    return ram, storage

def is_accessory_item(title: str, query: str, price: float = 0.0) -> bool:
    """
    Determines if a product title is an accessory when the user query is not.
    """
    title_lower = title.lower()
    query_lower = query.lower()
    
    # Check if the query itself is searching for an accessory
    accessory_keywords = [
        'case', 'cover', 'glass', 'protector', 'guard', 'charger', 'cable', 
        'strap', 'adapter', 'pouch', 'skin', 'holder', 'stand', 'mount',
        'buds', 'earbuds', 'headphone', 'headset', 'film', 'shield'
    ]
    
    is_acc_query = any(kw in query_lower for kw in accessory_keywords)
    if is_acc_query:
        return False
        
    # Clean title for accessory check (remove "without charger", etc.)
    clean_title = re.sub(r'\b(without|no|not included|not inbox|not in the box)\s+(charger|adapter|cable|earphones|buds|headphones)\b', '', title_lower)
    clean_title = re.sub(r'\b(charger|adapter|cable|earphones|buds|headphones)\s+(not included|not in the box|not inbox)\b', '', clean_title)
    
    # Match patterns
    accessory_patterns = [
        r'\bcase\b', r'\bcover\b', r'\bprotector\b', r'\bguard\b', r'\bcharger\b',
        r'\bcable\b', r'\bstrap\b', r'\badapter\b', r'\bpouch\b', r'\bskin\b',
        r'\bholder\b', r'\bstand\b', r'\bmount\b', r'\btempered\s+glass\b',
        r'\bglass\s+protector\b', r'\bscreen\s+shield\b', r'\bfilm\b',
        r'\bbuds\b', r'\bearbuds\b', r'\bheadphone\b', r'\bheadset\b'
    ]
    
    for pattern in accessory_patterns:
        if re.search(pattern, clean_title):
            # Safeguard: if price is very high, it is probably a bundled/main device, not just an accessory
            if price > 8000:
                return False
            return True
            
    return False

def extract_color(title: str) -> str:
    title_lower = title.lower()
    found_colors = []
    
    # 1. Check for multi-word colors first
    multi_word_colors = [
        'deep purple', 'sierra blue', 'pacific blue', 'titanium gray', 'titanium black',
        'titanium yellow', 'titanium violet', 'titanium white', 'titanium whitesilver',
        'titanium orange', 'desert titanium', 'natural titanium', 'black titanium',
        'white titanium', 'charcoal black', 'sky blue', 'silver shadow', 'siren blue',
        'starshine green', 'starry black', 'mint green', 'forest green', 'black velvet',
        'green silk', 'cobalt violet', 'onyx black', 'glacier white', 'fresh blue',
        'hyper black', 'mint breeze', 'dark knight', 'sand storm', 'pitch black', 'quick silver'
    ]
    for c in multi_word_colors:
        if c in title_lower:
            found_colors.append(c)
            title_lower = title_lower.replace(c, ' ') # remove to avoid duplicate single word match
            
    # 2. Check for single-word colors
    colors = [
        'black', 'white', 'blue', 'teal', 'pink', 'ultramarine', 'yellow', 'violet', 'gray', 'grey',
        'green', 'red', 'gold', 'silver', 'charcoal', 'bronze', 'sand', 'titanium', 'desert', 'natural',
        'space', 'midnight', 'starlight', 'rose', 'mint', 'emerald', 'sapphire', 'obsidian', 'porcelain',
        'hazel', 'bay', 'coral', 'graphite', 'sky', 'shadow', 'whitesilver', 'cream', 'peach',
        'lavender', 'phantom', 'aura', 'cloud', 'prism', 'aloe', 'bronze', 'orange', 'cobalt', 'onyx', 'glacier',
        'breeze', 'dark', 'knight', 'storm', 'pitch', 'quick', 'silk', 'fresh', 'hyper', 'frost',
        'mystic', 'cosmic', 'nebula', 'iris', 'amber', 'copper', 'ruby', 'pearl', 'lemon'
    ]
    for c in colors:
        if re.search(rf'\b{c}\b', title_lower):
            found_colors.append(c)
            
    if found_colors:
        # Titlecase them for neat display
        return ", ".join([c.title() for c in found_colors])
    return "Standard"

def group_variants(product_list: list) -> list:
    """
    Groups products of different colors on the same platform into a single product entry with a variants list.
    """
    if not product_list:
        return []
        
    grouped = {}
    for item in product_list:
        title = item["title"]
        brand = extract_brand(title)
        ram, storage = extract_ram_and_storage(title)
        
        # Base key: brand + clean_title + ram + storage
        base_key = f"{brand or ''}_{clean_title(title)}_{ram or ''}_{storage or ''}"
        
        color = extract_color(title)
        
        variant_info = {
            "color": color,
            "price": item["price"],
            "rating": item["rating"],
            "url": item["url"],
            "image": item["image"],
            "title": title
        }
        
        if base_key not in grouped:
            base_item = item.copy()
            base_item["variants"] = [variant_info]
            grouped[base_key] = base_item
        else:
            # Check if we already have this color in variants
            existing_variant_idx = -1
            for idx, v in enumerate(grouped[base_key]["variants"]):
                if v["color"].lower() == color.lower():
                    existing_variant_idx = idx
                    break
                    
            if existing_variant_idx != -1:
                # If the new variant is cheaper, replace the existing one
                if variant_info["price"] < grouped[base_key]["variants"][existing_variant_idx]["price"]:
                    grouped[base_key]["variants"][existing_variant_idx] = variant_info
            else:
                grouped[base_key]["variants"].append(variant_info)
                
            # Update the base item's price/url/image/title to the cheapest overall variant
            cheapest_variant = min(grouped[base_key]["variants"], key=lambda x: x["price"])
            grouped[base_key]["price"] = cheapest_variant["price"]
            grouped[base_key]["url"] = cheapest_variant["url"]
            grouped[base_key]["image"] = cheapest_variant["image"]
            grouped[base_key]["title"] = cheapest_variant["title"]
            
    return list(grouped.values())

def validate_model_match(title1: str, title2: str) -> bool:
    """
    Checks if there's an explicit model mismatch (e.g. S24 vs S25, iPhone 15 vs 16).
    Returns False if there is a mismatch, True otherwise.
    """
    t1_lower = title1.lower()
    t2_lower = title2.lower()
    
    # 1. Samsung Galaxy S series mismatch
    s1 = re.search(r'\bs(\d{2})\b', t1_lower)
    s2 = re.search(r'\bs(\d{2})\b', t2_lower)
    if s1 and s2 and s1.group(1) != s2.group(1):
        return False
        
    # 2. iPhone series mismatch
    ip1 = re.search(r'\biphone\s*(\d{2})\b', t1_lower)
    ip2 = re.search(r'\biphone\s*(\d{2})\b', t2_lower)
    if ip1 and ip2 and ip1.group(1) != ip2.group(1):
        return False
        
    # 3. OnePlus / other series mismatch
    # If one title explicitly mentions a model number and the other mentions a different model number, reject.
    for pattern in [r'\b(?:oneplus|nord)\s*(\d+[a-z]?)\b', r'\bpixel\s*(\d+[a-z]?)\b']:
        m1 = re.search(pattern, t1_lower)
        m2 = re.search(pattern, t2_lower)
        if m1 and m2 and m1.group(1) != m2.group(1):
            return False
            
    return True

def extract_brand(title: str) -> str:
    """Extracts known brand name from title to prevent cross-brand matching."""
    title_clean = title.lower()
    brands = ["apple", "samsung", "oneplus", "xiaomi", "redmi", "realme", "motorola", "moto", "google", "pixel", "asus", "lenovo", "hp", "dell", "sony", "boat", "noise"]
    for b in brands:
        if b in title_clean:
            return b
    return None

def match_products(amazon_list: list, flipkart_list: list) -> list:
    """
    Fuzzy matches products from Amazon and Flipkart using RapidFuzz.
    """
    # Group color variants on each platform
    amazon_list = group_variants(amazon_list)
    flipkart_list = group_variants(flipkart_list)
    
    matched_results = []
    used_flipkart_indices = set()
    
    threshold = settings.MATCHING_THRESHOLD
    
    for am_idx, am_item in enumerate(amazon_list):
        am_title = am_item["title"]
        am_clean = clean_title(am_title)
        am_brand = extract_brand(am_title)
        am_ram, am_storage = extract_ram_and_storage(am_title)
        
        best_match_idx = -1
        best_score = 0.0
        
        for fk_idx, fk_item in enumerate(flipkart_list):
            if fk_idx in used_flipkart_indices:
                continue
                
            fk_title = fk_item["title"]
            fk_clean = clean_title(fk_title)
            
            # 1. Brand validation: If both have brands and they differ, do not match.
            fk_brand = extract_brand(fk_title)
            if am_brand and fk_brand and am_brand != fk_brand:
                continue
                
            # 2. Storage/Spec validation: If both have specs and they differ, do not match.
            fk_ram, fk_storage = extract_ram_and_storage(fk_title)
            if am_storage and fk_storage and am_storage != fk_storage:
                continue
            if am_ram and fk_ram and am_ram != fk_ram:
                continue
                
            # 3. Model validation: Prevent cross-generation/cross-model mismatch
            if not validate_model_match(am_title, fk_title):
                continue
            
            # Token Sort Ratio (requires word alignment, very strict)
            sort_score = fuzz.token_sort_ratio(am_clean, fk_clean)
            
            # Token Set Ratio (handles permutations, slightly looser)
            set_score = fuzz.token_set_ratio(am_clean, fk_clean)
            
            # Combined score: 65% weight on strict sort, 35% on set ratio
            combined_score = (sort_score * 0.65) + (set_score * 0.35)
            
            if combined_score > threshold and combined_score > best_score:
                best_score = combined_score
                best_match_idx = fk_idx
                
        if best_match_idx != -1:
            # Found a match!
            used_flipkart_indices.add(best_match_idx)
            fk_item = flipkart_list[best_match_idx]
            
            # Compute comparisons
            am_price = am_item["price"]
            fk_price = fk_item["price"]
            
            best_platform = "Amazon"
            if fk_price < am_price:
                best_platform = "Flipkart"
            elif fk_price == am_price:
                best_platform = "Equal"
                
            diff = abs(am_price - fk_price)
            max_price = max(am_price, fk_price)
            pct_diff = round((diff / max_price) * 100, 2) if max_price > 0 else 0.0
            
            # Choose the longer title so we display full product details (e.g. brand, color, specs) instead of brand-only strings
            product_name = am_title if len(am_title) > len(fk_title) else fk_title
            
            matched_results.append({
                "product_name": product_name,
                "amazon_price": am_price,
                "flipkart_price": fk_price,
                "best_platform": best_platform,
                "difference": diff,
                "percentage_difference": pct_diff,
                "amazon_product": am_item,
                "flipkart_product": fk_item,
                "similarity_score": round(best_score, 2)
            })
        else:
            # No match found for this Amazon item - add it as unmatched Amazon item
            matched_results.append({
                "product_name": am_item["title"],
                "amazon_price": am_item["price"],
                "flipkart_price": None,
                "best_platform": "Amazon",
                "difference": 0.0,
                "percentage_difference": 0.0,
                "amazon_product": am_item,
                "flipkart_product": None,
                "similarity_score": 0.0
            })
            
    # Add all remaining unmatched Flipkart items
    for fk_idx, fk_item in enumerate(flipkart_list):
        if fk_idx not in used_flipkart_indices:
            matched_results.append({
                "product_name": fk_item["title"],
                "amazon_price": None,
                "flipkart_price": fk_item["price"],
                "best_platform": "Flipkart",
                "difference": 0.0,
                "percentage_difference": 0.0,
                "amazon_product": None,
                "flipkart_product": fk_item,
                "similarity_score": 0.0
            })
            
    return matched_results
