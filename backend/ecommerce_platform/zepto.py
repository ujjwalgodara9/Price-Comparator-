import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

STORAGE_FOLDER = "product_data"
os.makedirs(STORAGE_FOLDER, exist_ok=True)

def set_location(page, city_name):
    print(f"Setting location to: {city_name}")
    address_header = page.get_by_test_id("user-address")
    address_header.wait_for(state="visible")
    address_header.click()

    search_container = page.get_by_test_id("address-search-input")
    search_container.wait_for(state="visible")

    search_input = search_container.locator("input")
    search_input.fill(city_name)

    results_container = page.get_by_test_id("address-search-container")
    first_result = results_container.get_by_test_id("address-search-item").first
    first_result.wait_for(state="visible", timeout=10000)
    first_result.click()

    page.wait_for_load_state("networkidle")
    time.sleep(5)

def search_and_scroll(page, product_query):
    print(f"Searching for: {product_query}")
    # 1. Click search icon and type
    search_icon = page.get_by_test_id("search-bar-icon")
    search_icon.click()
    
    # Zepto search input usually appears after clicking icon
    search_input = page.get_by_placeholder("Search for", exact=False)
    search_input.fill(product_query)
    page.keyboard.press("Enter")
    
    page.wait_for_load_state("networkidle")
    
    # 2. Scroll Loop (5 times with 4s wait)
    for i in range(15):
        print(f"Scroll iteration {i+1}/15")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(4)

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

            return {
                "product_name": nameEl ? nameEl.innerText.trim() : "N/A",
                "price": priceEl ? priceEl.innerText.trim() : "N/A",
                "description": descEl ? descEl.innerText.trim() : "N/A",
                "delivery_time": timeEl ? timeEl.innerText.trim() : "N/A",
                "product_link": fullLink
            };
        });
    }
    """
    
    # This happens almost instantly regardless of how many items there are
    products = page.evaluate(extraction_script)
    
    # Filter out empty entries if any
    return [p for p in products if p['product_name'] != "N/A"]

def save_to_timestamped_folder(data, platform_name):
    # 1. Create a unique timestamp (e.g., 2026-01-10_01-30-45)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # 2. Define the folder path: scraped_results/run-2026-01-10_01-30-45
    run_folder = os.path.join(STORAGE_FOLDER, f"run-{timestamp}-zepto")
    
    # 3. Create the folder if it doesn't exist
    os.makedirs(run_folder, exist_ok=True)
    
    # 4. Define file path: scraped_results/run-.../zepto.json
    json_filename = f"{platform_name.lower()}.json"
    json_path = os.path.join(run_folder, json_filename)
    
    # 5. Save the data
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"--- Data Saved Successfully ---")
    print(f"Folder: {run_folder}")
    print(f"File: {json_filename}")
    return json_path

def run_zepto_flow(city, product_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto("https://www.zepto.com", wait_until="networkidle")
            
            # Location
            set_location(page, city)
            
            # Search and Scroll
            search_and_scroll(page, product_name)
            
            # Scrape
            final_data_list = extract_product_list(page)

            # Save to File
            final_saved_path = save_to_timestamped_folder(final_data_list, "zepto")

            return final_data_list

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

# Example Usage
run_zepto_flow("Bandra", "Ghee")