import logging
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.config import settings
from backend.scrapers.mock_data import generate_mock_results
from backend.services.matcher import is_accessory_item

logger = logging.getLogger(__name__)

def get_chrome_options():
    chrome_options = Options()
    if settings.SELENIUM_HEADLESS:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Speed optimization: disable image loading
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    
    # Prevent bot detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    return chrome_options

def scrape_amazon(query: str) -> list:
    """
    Scrapes Amazon India for the given query and returns top 15 results.
    """
    logger.info(f"Starting Amazon scrape for query: {query}")
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.amazon.in/s?k={encoded_query}"
    
    driver = None
    results = []
    
    try:
        chrome_options = get_chrome_options()
        # Initialize Chrome webdriver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(settings.SELENIUM_TIMEOUT)
        
        driver.get(url)
        
        # Wait until products are loaded (wait for result items)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-component-type="s-search-result"], .s-result-item'))
        )
        
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # Find search result items
        items = soup.select('div[data-component-type="s-search-result"]')
        if not items:
            items = soup.select('.s-result-item[data-asin]')
            
        logger.info(f"Found {len(items)} raw result containers on Amazon")
        
        for item in items:
            if len(results) >= 15:
                break
                
            try:
                # Title - Target link-bounded headings only to avoid brand labels
                title_el = item.select_one('a[class*="a-link-normal"] h2 span, h2 a span, a[class*="a-link-normal"] h2')
                title = ""
                if title_el:
                    title = title_el.text.strip()
                else:
                    # Fallback using product image alt text
                    img_el = item.select_one('img[alt]')
                    if img_el:
                        title = img_el.get("alt", "").strip()
                
                # Clean sponsored indicators if present
                if title.startswith("Sponsored Ad -"):
                    title = title.replace("Sponsored Ad -", "").strip()
                if title.startswith("Sponsored"):
                    title = title.replace("Sponsored", "").strip()
                title = title.strip()
                
                if not title:
                    continue
                
                # Price
                price_el = item.select_one('.a-price-whole')
                if not price_el:
                    continue  # We need price for comparison
                price_str = price_el.text.replace(",", "").replace("₹", "").strip()
                price = float(price_str)
                
                # Filter accessories
                if is_accessory_item(title, query, price):
                    continue
                
                # Rating
                rating = 0.0
                rating_el = item.select_one('span.a-icon-alt, .a-icon-star-small')
                if rating_el:
                    rating_text = rating_el.text or rating_el.get("aria-label", "")
                    # Extract decimal rating (e.g. "4.3 out of 5 stars" -> 4.3)
                    parts = rating_text.split()
                    if parts:
                        try:
                            rating = float(parts[0])
                        except ValueError:
                            pass
                
                # Product URL
                url_el = item.select_one('h2 a.a-link-normal, .a-link-normal.s-no-outline')
                if not url_el:
                    continue
                href = url_el.get("href")
                if href.startswith("/"):
                    href = f"https://www.amazon.in{href}"
                # Clean URL (remove trailing tracking parameters)
                product_url = href.split("/ref=")[0] if "/ref=" in href else href
                
                # Image URL
                img_el = item.select_one('img.s-image')
                image_url = img_el.get("src") if img_el else ""
                
                results.append({
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "url": product_url,
                    "image": image_url,
                    "platform": "Amazon"
                })
                
            except Exception as item_err:
                logger.debug(f"Error parsing Amazon item: {item_err}")
                continue
                
    except Exception as e:
        logger.error(f"Amazon scraper failed or was blocked: {e}")
        
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
                
    # Fallback to mock data if empty results (usually because of CAPTCHA/bot-blocking)
    if not results and settings.MOCK_FALLBACK:
        logger.warning(f"No results scraped from Amazon. Falling back to mock data.")
        return generate_mock_results(query, "amazon")
        
    return results
