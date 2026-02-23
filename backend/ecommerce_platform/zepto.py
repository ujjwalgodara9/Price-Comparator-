import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# Storage folder for product data
STORAGE_FOLDER = "/var/lib/product-compare/product_data"
os.makedirs(STORAGE_FOLDER, exist_ok=True)

def remove_duplicate_products(product_list):
    """
    Removes exact duplicate dictionaries from a list while preserving order.
    """
    seen = set()
    unique_products = []
    
    for product in product_list:
        # Convert dict to a sorted tuple of items so it can be hashed/tracked
        # sorting keys ensures {'a':1, 'b':2} and {'b':2, 'a':1} are seen as same
        product_tuple = tuple(sorted(product.items()))
        
        if product_tuple not in seen:
            unique_products.append(product)
            seen.add(product_tuple)
            
    return unique_products

def set_location_by_geolocation(page):
    """Set location using Zepto's 'Use My Current Location' button (requires geolocation on context)."""
    print("Setting location using browser geolocation...")
    address_header = page.get_by_test_id("user-address")
    address_header.wait_for(state="visible")
    address_header.click()

    saved_container = page.get_by_test_id("saved-address-container")
    saved_container.wait_for(state="visible", timeout=10000)

    enable_btn = saved_container.get_by_role("button", name="Enable")
    enable_btn.click()

    page.wait_for_load_state("networkidle")
    time.sleep(3)


def set_location(page, location_name):
    print(f"Setting location to: {location_name}")
    address_header = page.get_by_test_id("user-address")
    address_header.wait_for(state="visible")
    address_header.click()

    search_container = page.get_by_test_id("address-search-input")
    search_container.wait_for(state="visible")

    search_input = search_container.locator("input")
    search_input.fill(location_name)

    results_container = page.get_by_test_id("address-search-container")
    first_result = results_container.get_by_test_id("address-search-item").first
    first_result.wait_for(state="visible", timeout=10000)
    first_result.click()

    page.wait_for_load_state("networkidle")
    time.sleep(3)

def search_and_scroll(page, product_query):
    print(f"Searching for: {product_query}")
    # 1. Click search icon to open the search overlay
    search_icon = page.get_by_test_id("search-bar-icon")
    search_icon.click()

    # Wait for the search input to appear (overlay is client-side rendered).
    # Don't rely on placeholder text — Zepto changes it; match any visible input instead.
    try:
        page.wait_for_selector('input:not([type="hidden"])', state="visible", timeout=10000)
        search_input = page.locator('input:not([type="hidden"])').first
        search_input.click()
        search_input.fill(product_query)
    except Exception:
        # Fallback: if the click auto-focused the input, type directly
        time.sleep(1)
        page.keyboard.type(product_query)
    page.keyboard.press("Enter")
    
    page.evaluate("document.body.style.zoom = '20%'")
    time.sleep(3)
    page.wait_for_load_state("networkidle")
    
    # 2. Scroll Loop (5 times with 4s wait)
    for i in range(1):
        print(f"Scroll iteration {i+1}/2")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)

def extract_product_list(page):
    print("Extracting all items in one go...")
    
    # We run this JavaScript inside the browser context
    # It finds all cards and extracts their data into a list of dictionaries
    extraction_script = """
    () => {
        const items = document.querySelectorAll('.B4vNQ');
        return Array.from(items).map(item => {
            const relativeLink = item.getAttribute('href');
            const fullLink = relativeLink ? `https://www.zepto.com${relativeLink}` : "N/A";

            const priceEl = item.querySelector('span.cptQT7');
            const nameEl = item.querySelector('div.cQAjo6.ch5GgP');
            const descEl = item.querySelector('div.cyNbxx.c0ZFba span');
            const timeEl = item.querySelector('div.cTDqth.cTDqth');
            const imgEl = item.querySelector('img.c2ahfT');

            return {
                "product_name": nameEl ? nameEl.innerText.trim() : "N/A",
                "price": priceEl ? priceEl.innerText.trim() : "N/A",
                "description": descEl ? descEl.innerText.trim() : "N/A",
                "delivery_time": timeEl ? timeEl.innerText.trim() : "N/A",
                "product_link": fullLink,
                "image_url": imgEl ? imgEl.getAttribute('src') : "N/A"
            };
        });
    }
    """
    
    # This happens almost instantly regardless of how many items there are
    products = page.evaluate(extraction_script)
    
    # Filter out empty entries if any
    return [p for p in products if p['product_name'] != "N/A"]

def save_to_timestamped_folder(data, platform_name, run_parent_folder=None):
    # If parent folder is provided, use it; otherwise create a new one
    if run_parent_folder:
        # Use the shared parent folder: product_data/run-2026-01-10_20-10-15/
        run_folder = os.path.join(STORAGE_FOLDER, run_parent_folder)
        os.makedirs(run_folder, exist_ok=True)
    else:
        # Fallback: Create a unique timestamp (e.g., 2026-01-10_01-30-45)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_folder = os.path.join(STORAGE_FOLDER, f"run-{timestamp}-{platform_name.lower()}")
        os.makedirs(run_folder, exist_ok=True)
    
    # Define file path: run_folder/zepto.json (directly in parent folder)
    json_filename = f"{platform_name.lower()}.json"
    json_path = os.path.join(run_folder, json_filename)
    
    # Save the data
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"--- Data Saved Successfully ---")
    print(f"Folder: {run_folder}")
    print(f"File: {json_filename}")
    return json_path

def run_zepto_flow(product_name, location, headless=True, max_products=50, run_parent_folder=None, platform_name='zepto'):
    start_time = time.time()

    # Accept location as a dict (with city + coordinates) or a plain string
    if isinstance(location, dict):
        location_name = location.get("city") or location.get("address") or "Mumbai"
        coords = location.get("coordinates", {})
        lat = coords.get("lat")
        lng = coords.get("lng")
    else:
        location_name = str(location)
        lat = None
        lng = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)

        context_kwargs = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if lat and lng:
            context_kwargs["geolocation"] = {"latitude": lat, "longitude": lng}
            context_kwargs["permissions"] = ["geolocation"]

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        try:
            page.goto("https://www.zepto.com", wait_until="networkidle")

            # Location: prefer geolocation (uses actual coordinates) over text search
            # Text search for "New Delhi" picks Rajpath/Rashtrapati Bhavan — a government zone
            # that shows "Coming Soon", so coordinates-based detection is more reliable.
            if lat and lng:
                try:
                    set_location_by_geolocation(page)
                except Exception as e:
                    print(f"Geolocation failed ({e}), falling back to text search")
                    set_location(page, location_name)
            else:
                set_location(page, location_name)

            # Detect "coming soon" page — means Zepto doesn't serve this area
            if page.locator("text=We're Coming Soon").count() > 0:
                print("[Zepto] Location not serviceable, returning empty list")
                return []

            # Search and Scroll
            search_and_scroll(page, product_name)

            # Wait for React to render product cards before extracting
            try:
                page.wait_for_selector('.B4vNQ', timeout=20000)
            except Exception:
                print("No .B4vNQ product cards appeared — returning empty list")
                return []

            # Scrape
            final_data_list = extract_product_list(page)

            # Remove Duplicates
            final_data_list = remove_duplicate_products(final_data_list)

            # Save to File with shared parent folder
            final_saved_path = save_to_timestamped_folder(final_data_list, platform_name, run_parent_folder=run_parent_folder)

            time_end = time.time()
            print(f"--- Zepto Total Time Taken: {time_end - start_time:.2f}) seconds ---")
            return final_data_list

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
    

# For standalone script execution
if __name__ == "__main__":
    run_zepto_flow(product_name="atta", location="Mumbai", headless=False, max_products=50)