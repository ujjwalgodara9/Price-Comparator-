import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

STORAGE_FOLDER = "product_data"

def handle_popups(page):
    """Closes the Download App modal if it appears."""
    try:
        # Looking for the partial class of the Download App Modal
        modal_close_btn = page.locator('[class*="DownloadAppModal__Image"], [class*="modal-close"]')
        if modal_close_btn.is_visible():
            print("Closing Download App Modal...")
            modal_close_btn.click()
    except:
        pass

def set_blinkit_location(page, city_name):
    handle_popups(page)
    
    # 1. Click on Location Bar auto appear hence commented
    # print("Opening location bar...")
    # page.locator('[class^="LocationBar__Title"]').click()
    
    # 2. Focus and Click the input specifically
    # Waiting for the container and then locating the 'input' within it
    search_input_container = page.locator('.modal-right__input-wrapper')
    search_input_container.wait_for(state="visible")
    
    search_input = search_input_container.locator('input')
    
    # EXPLICIT CLICK before filling
    search_input.click() 
    
    # Use press_sequentially to ensure React triggers its search results correctly
    search_input.press_sequentially(city_name, delay=100) 
    
    # 3. Click first result
    print("Selecting location result...")
    # Use a more specific locator for the result items
    first_result = page.locator('.address-container-v1 [class*="LocationSearchList__LocationListContainer"]').first
    
    # Ensure it's ready for interaction
    first_result.wait_for(state="visible", timeout=15000)
    first_result.click()
    
    # 4. Final stabilizing wait
    print("Location set. Refreshing catalog...")
    # page.wait_for_load_state("domcontentloaded")
    time.sleep(5)

def search_blinkit_products(page, query):
    handle_popups(page)
    
    # 1. Search Bar Interaction
    search_container = page.locator('[class^="SearchBar__PlaceholderContainer"]')
    search_container.click()
    
    # Fill the input that appears
    time.sleep(2)
    page.keyboard.type(query)
    page.keyboard.press("Enter")
    # page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # 2. Scroll Loop (5 times, 4s wait)
    for i in range(5):
        handle_popups(page)
        print(f"Scrolling Blinkit... ({i+1}/5)")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(4)

def extract_blinkit_data(page):
    """Fast extraction using JS evaluate for React structure."""
    extraction_script = """
        () => {
        // Find all parent containers
        const items = document.querySelectorAll('.tw-relative.tw-flex');
        
        return Array.from(items).map(item => {
            // 1. Identify the info box
            const infoBox = item.querySelector('.tw-mb-2.tw-flex.tw-flex-col.tw-text-400');
            
            // 2. Extract Name (Higher emphasis class)
            const nameEl = infoBox ? infoBox.querySelector('.tw-text-300.tw-font-semibold.tw-line-clamp-2') : null;
            
            // 3. Extract Description (The medium font class you specified)
            // FIX: Added .innerText here
            const descEl = infoBox ? infoBox.querySelector('.tw-text-200.tw-font-medium.tw-line-clamp-1') : null;
            
            // 4. Time extraction (Looking for the bold uppercase div)
            const timeEl = item.querySelector('.tw-text-050.tw-font-bold.tw-uppercase');
            
            // 5. Price extraction
            const priceEl = item.querySelector('.tw-text-200.tw-font-semibold');

            return {
                "product_name": nameEl ? nameEl.innerText.trim() : "N/A",
                "description": descEl ? descEl.innerText.trim() : "N/A",
                "price": priceEl ? priceEl.innerText.trim() : "N/A",
                "delivery_time": timeEl ? timeEl.innerText.trim() : "N/A"
            };
        }).filter(p => p.product_name !== "N/A");
    }
    """
    return page.evaluate(extraction_script)




def save_to_timestamped_folder(data, platform_name):
    # 1. Create a unique timestamp (e.g., 2026-01-10_01-30-45)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # 2. Define the folder path: scraped_results/run-2026-01-10_01-30-45
    run_folder = os.path.join(STORAGE_FOLDER, f"run-{timestamp}-blinkit")
    
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


# --- MAIN EXECUTION ---
def run_blinkit_flow(city, product):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto("https://blinkit.com/", wait_until="domcontentloaded")
            
            set_blinkit_location(page, city)
            search_blinkit_products(page, product)
            
            final_list = extract_blinkit_data(page)
            save_to_timestamped_folder(final_list, "blinkit")
            
        finally:
            browser.close()

if __name__ == "__main__":
    run_blinkit_flow("Mumbai", "Atta")