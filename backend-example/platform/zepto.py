import os
import json
import uuid
import requests
import random
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
STORAGE_FOLDER = "product_data"
IMAGE_FOLDER = os.path.join(STORAGE_FOLDER, "images")

# Ensure directories exist
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# --- EXTRACTION FUNCTIONS ---

def get_product_price(page):
    """Extracts and cleans the price."""
    try:
        # Scoped to avoid strict mode violation
        price_locator = page.locator("#product-features-wrapper .u-flex.WwbTC.xs2VX")
        raw_price = price_locator.inner_text()
        return "".join(raw_price.split())
    except:
        return "N/A"

def get_product_highlights(page):
    """Extracts highlights and parses them into a dictionary."""
    try:
        highlights_locator = page.locator("#productHighlights .__9M1qu")
        if highlights_locator.count() == 0:
            return {}
        
        raw_html = highlights_locator.inner_html()
        soup = BeautifulSoup(raw_html, 'html.parser')
        product_info = {}

        rows = soup.find_all("div", class_="KjTQZ")
        for row in rows:
            key_el = row.find("h3")
            val_el = row.find("p")
            if key_el and val_el:
                key = key_el.get_text(strip=True).lower().replace(" ", "_")
                val = val_el.get_text(strip=True)
                product_info[key] = val
        return product_info
    except:
        return {}

def download_image(page, product_name):
    """Downloads the primary product image."""
    try:
        img_locator = page.locator("#left-carousel .rounded-2xl img").first
        img_url = img_locator.get_attribute("src")
        
        if not img_url:
            return "no_image.jpg"

        # Create a unique but recognizable filename
        clean_name = "".join(x for x in product_name if x.isalnum())[:20]
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{clean_name}_{unique_id}.jpg"
        filepath = os.path.join(IMAGE_FOLDER, filename)

        img_data = requests.get(img_url).content
        with open(filepath, 'wb') as f:
            f.write(img_data)
        
        return filename
    except Exception as e:
        print(f"Image download error: {e}")
        return "error.jpg"

# --- CORE LOGIC ---

def extract_zepto_data(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print(f"Fetching: {url}")
            page.goto(url, wait_until="networkidle")
            
            # Allow for some dynamic content to finish loading
            time.sleep(2)

            # 1. Basic Info
            product_name = page.locator("h1").inner_text().strip()
            price = get_product_price(page)

            # 2. Structured Data
            highlights = get_product_highlights(page)

            # 3. Assets
            image_filename = download_image(page, product_name)

            # 4. Compile Final JSON
            final_data = {
                "source": "Zepto",
                "product_name": product_name,
                "price": price,
                "image_name": image_filename,
                "highlights": highlights,
                "url": url,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            # 5. Save to File
            # Generate filename like: zepto-OrganicTattvaWheatFlour.json
            safe_name = "".join(x for x in product_name if x.isalnum())[:30]
            json_filename = f"zepto-{safe_name}.json"
            json_path = os.path.join(STORAGE_FOLDER, json_filename)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=4)

            print(f"Successfully saved data to: {json_path}")
            return final_data

        except Exception as e:
            print(f"Critical error during extraction: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    target_url = "https://www.zepto.com/pn/organic-tattva-wheat-flour-chakki-atta/pvid/3587eb86-cc71-4dda-aee1-786f8e1ae3dc"
    extract_zepto_data(target_url)

# demo urls
# url = "https://www.zepto.com/pn/fablue-rock-crawler-remote-control-car-for-kids-off-road-car-toy-for-kids/pvid/4295179b-6cbb-4488-b576-4923c6b7c8c1"
# url = "https://www.zepto.com/pn/organic-tattva-wheat-flour-chakki-atta/pvid/3587eb86-cc71-4dda-aee1-786f8e1ae3dc"
# url = "https://www.zepto.com/pn/nandini-fresh-toned-fresh-milk-pouch-blue/pvid/25eb526c-9c26-48cd-95a3-8e4058910f8a"
