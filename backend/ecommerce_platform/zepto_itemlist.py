from playwright.sync_api import sync_playwright
import re
import time
import json
import os
import uuid
from datetime import datetime

def parse_product_from_card(raw_text):
    """
    Parse a single product from a card's text.
    Returns one product per card (the main product).
    """
    if not raw_text or not raw_text.strip():
        return None
    
    lines = raw_text.strip().split('\n')
    
    # Find the price (first ₹ amount)
    price_match = re.search(r"₹\s*(\d+)", raw_text)
    if not price_match:
        return None
    
    price = price_match.group(1)
    
    # Find the product name (longest line that doesn't contain ₹, OFF, or is just numbers)
    name = ""
    name_candidates = []
    
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Skip lines that are clearly not product names
        if (
            len(line) > 15 and
            "₹" not in line and
            "OFF" not in line and
            not re.match(r'^[\d\s\.\(\)]+$', line) and
            not re.match(r'^\d+\s*pc$', line, re.IGNORECASE) and
            not re.match(r'^\d+\.\d+$', line) and  # Skip rating numbers
            not re.match(r'^\(\d+\)$', line) and  # Skip review counts like "(635)"
            not line.lower().startswith('delivery') and
            not line.lower().startswith('free')
        ):
            name_candidates.append(line)
            # Prefer longer lines as they're more likely to be product names
            if len(line) > len(name):
                name = line
    
    # If no name found with strict criteria, try more lenient approach
    if not name and name_candidates:
        # Use the first candidate
        name = name_candidates[0]
    elif not name:
        # Last resort: find any line that's not a price or number
        for line in lines:
            line = line.strip()
            if line and "₹" not in line and not re.match(r'^[\d\s\.\(\)]+$', line) and len(line) > 10:
                name = line
                break
    
    if not name or not price:
        return None
    
    return {
        "name": name,
        "price": price,
        "other_details": raw_text.strip()
    }


def scrape_zepto_products(search_query, location=None, headless=True, max_products=50, search_debug=False, search_timestamp=None):
    """
    Scrape Zepto products using Playwright
    
    Args:
        search_query (str): The search query from frontend
        location (dict): Optional location data
        headless (bool): Whether to run browser in headless mode
        max_products (int): Maximum number of products to scrape
    
    Returns:
        list: List of products formatted for frontend display
    """
    results = []
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)

            context = browser.new_context(
                viewport={"width": 390, "height": 844},
                user_agent=(
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Version/16.0 Mobile/15E148 Safari/604.1"
                )
            )

            page = context.new_page()

            page.goto(
                "https://www.zepto.com/search?query=" + search_query,
                wait_until="domcontentloaded"
            )

            page.wait_for_selector("img", timeout=20000)

            # Trigger lazy loading
            for _ in range(5):
                page.mouse.wheel(0, 2000)
                time.sleep(1)

            cards = page.locator("div").filter(has_text="₹")
            card_count = cards.count()
            print(f"Found cards: {card_count}")
            
            # Use a set to track seen products and avoid duplicates
            seen_products = set()

            for i in range(min(card_count, max_products)):
                try:
                    card = cards.nth(i)
                    text = card.inner_text()

                    # ✅ IMAGE SCRAPING with timeout protection
                    img_url = None
                    try:
                        img = card.locator("img").first
                        # Use shorter timeout to avoid getting stuck
                        img_url = (
                            img.get_attribute("src", timeout=2000) or
                            img.get_attribute("data-src", timeout=2000) or
                            img.get_attribute("data-original", timeout=2000)
                        )
                    except Exception as img_error:
                        # If image scraping fails, continue without image
                        img_url = None

                    # ✅ PRODUCT LINK EXTRACTION
                    product_link = f"https://www.zepto.com/search?query={search_query}"
                    try:
                        # Look for anchor tag with class B4vNQ that contains the product link
                        # Try multiple approaches to find the link
                        link_element = None
                        href = None
                        
                        # First try: direct anchor with class B4vNQ
                        try:
                            link_element = card.locator('a.B4vNQ').first
                            href = link_element.get_attribute("href", timeout=2000)
                        except:
                            # Second try: any anchor tag within the card
                            try:
                                link_element = card.locator('a[href*="/pn/"]').first
                                href = link_element.get_attribute("href", timeout=2000)
                            except:
                                pass
                        
                        if href:
                            # If href is relative, make it absolute
                            if href.startswith('/'):
                                product_link = f"https://www.zepto.com{href}"
                            elif href.startswith('http'):
                                product_link = href
                            else:
                                # If it doesn't start with / or http, prepend the base URL
                                product_link = f"https://www.zepto.com/{href.lstrip('/')}"
                    except Exception as link_error:
                        # If link extraction fails, use default search link
                        product_link = f"https://www.zepto.com/search?query={search_query}"

                    # ✅ RATING AND REVIEW COUNT EXTRACTION
                    rating = 0.0
                    review_count = 0
                    try:
                        # Look for rating information div
                        rating_div = card.locator('[data-slot-id="RatingInformation"]').first
                        # Check if element exists by trying to get count
                        try:
                            if rating_div.count() > 0:
                                # Extract rating from span with class cPdMhy (contains SVG + rating number)
                                rating_span = rating_div.locator('span.cPdMhy').first
                                if rating_span.count() > 0:
                                    rating_text = rating_span.inner_text(timeout=2000)
                                    # Extract number from text (e.g., "4.2" from "4.2" or "⭐4.2")
                                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                                    if rating_match:
                                        rating = float(rating_match.group(1))
                                
                                # Extract review count from span with class cuNaP7 (contains "(678)")
                                review_span = rating_div.locator('span.cuNaP7').first
                                if review_span.count() > 0:
                                    review_text = review_span.inner_text(timeout=2000)
                                    # Extract number from parentheses (e.g., "678" from "(678)")
                                    review_match = re.search(r'\((\d+)\)', review_text)
                                    if review_match:
                                        review_count = int(review_match.group(1))
                        except:
                            # If count() fails, try direct access
                            try:
                                rating_text = rating_div.locator('span.cPdMhy').first.inner_text(timeout=2000)
                                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                                if rating_match:
                                    rating = float(rating_match.group(1))
                                
                                review_text = rating_div.locator('span.cuNaP7').first.inner_text(timeout=2000)
                                review_match = re.search(r'\((\d+)\)', review_text)
                                if review_match:
                                    review_count = int(review_match.group(1))
                            except:
                                pass
                    except Exception as rating_error:
                        # If rating extraction fails, continue with default values (0)
                        rating = 0.0
                        review_count = 0

                    # Parse ONE product per card
                    p = parse_product_from_card(text)
                    
                    if not p:
                        continue
                    
                    # Create a unique key for deduplication (name + price)
                    product_key = (p.get("name", "").strip().lower(), p.get("price", ""))
                    
                    # Skip if we've seen this product before
                    if product_key in seen_products:
                        continue
                    
                    seen_products.add(product_key)
                    
                    # Format product to match frontend expectations
                    price_value = float(p.get("price", 0))
                    product = {
                        "id": f"zepto-{uuid.uuid4().hex[:8]}",
                        "name": p.get("name", "").strip(),
                        "description": p.get("other_details", "").strip(),
                        "image": img_url or "https://via.placeholder.com/400",
                        "price": price_value,
                        "currency": "INR",
                        "platform": "zepto",
                        "availability": True,
                        "rating": rating,
                        "reviewCount": review_count,
                        "features": [],
                        "link": product_link,
                        "location": f"{location.get('city', '')}, {location.get('state', '')}" if location else "",
                        "deliveryTime": "10-15 mins",
                        "deliveryFee": 0,
                        "originalPrice": None,
                    }
                    
                    # Only add valid products
                    if product["name"] and product["price"] > 0:
                        print(f"  [Card {i}] Product: {product['name'][:50]}... | Price: ₹{product['price']} | Rating: {rating} ({review_count} reviews) | Link: {product_link[:60]}...")
                        results.append(product)
                    else:
                        print(f"  [Card {i}] Skipped - name: '{product['name']}', price: {product['price']}")
                            
                except Exception as card_error:
                    # If one card fails, continue with next card
                    print(f"  [Card {i}] Error processing card: {card_error}")
                    continue

            browser.close()
            print(f"[Zepto] Found {len(results)} products for query '{search_query}'")
            
            # ✅ SAVE JSON FOR DEBUGGING
            try:
                base_dir = os.path.join(os.path.dirname(__file__), "product_data")
                
                if search_debug and search_timestamp:
                    # Create timestamped folder for this search
                    output_dir = os.path.join(base_dir, search_timestamp)
                    os.makedirs(output_dir, exist_ok=True)
                    # Sanitize query for filename
                    safe_query = re.sub(r'[^\w\s-]', '', search_query).strip().replace(' ', '_')[:50]
                    filename = f"zepto_search_{safe_query}.json"
                else:
                    # Use current behavior - overwrite in product_data folder
                    output_dir = base_dir
                    os.makedirs(output_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_query = re.sub(r'[^\w\s-]', '', search_query).strip().replace(' ', '_')[:50]
                    filename = f"zepto_search_{safe_query}_{timestamp}.json"
                
                filepath = os.path.join(output_dir, filename)
                
                output_data = {
                    "search_query": search_query,
                    "timestamp": datetime.now().isoformat(),
                    "total_products": len(results),
                    "location": location,
                    "products": results
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                
                print(f"[Zepto] Debug JSON saved to: {filepath}")
            except Exception as json_error:
                print(f"[Zepto] Error saving JSON: {json_error}")
            
            return results
            
    except Exception as error:
        print(f"[Zepto] Scraping error: {error}")
        import traceback
        traceback.print_exc()
        return []


# For standalone script execution
if __name__ == "__main__":
    search_query = "atta"
    results = scrape_zepto_products(search_query, headless=True)
    
    # Save results to JSON file
    output_dir = os.path.join(os.path.dirname(__file__), "product_data")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"zepto_search_{search_query}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    output_data = {
        "search_query": search_query,
        "timestamp": datetime.now().isoformat(),
        "total_products": len(results),
        "products": results
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n Results saved to: {filepath}")
    print(f"Total products found: {len(results)}")
