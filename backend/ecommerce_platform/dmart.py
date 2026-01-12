import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# Get the absolute path to product_data folder (backend/product_data/)
# ecommerce_platform folder -> parent -> product_data
STORAGE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "product_data")
os.makedirs(STORAGE_FOLDER, exist_ok=True)

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

def set_dmart_location(page, location_name):
    handle_popups(page)

    print("Waiting for DMart location input...")

    # 1. Type location
    search_input = page.locator('#pincodeInput')
    search_input.wait_for(state="visible", timeout=15000)
    search_input.click()
    search_input.fill("")
    search_input.press_sequentially(location_name, delay=120)

    # 2. Select first suggestion
    print("Selecting first location result...")
    suggestions_container = page.locator('.pinCodeScrollBar')
    suggestions_container.wait_for(state="visible", timeout=15000)

    first_result = suggestions_container.locator('li button').first
    first_result.wait_for(state="visible", timeout=15000)
    first_result.click()

    # 3. Wait for Confirm Location popup and click confirm
    print("Waiting for Confirm Location popup...")
    confirm_btn = page.locator('button:has-text("CONFIRM LOCATION")')
    confirm_btn.wait_for(state="visible", timeout=15000)
    confirm_btn.click()

    print("DMart location fully set.")
    time.sleep(3)

def search_dmart_products(page, query):
    handle_popups(page)

    print(f"Searching DMart for: {query}")

    # 1. Focus and type in search input
    search_input = page.locator('#scrInput')
    search_input.wait_for(state="visible", timeout=15000)
    search_input.click()
    search_input.fill("")
    search_input.press_sequentially(query, delay=100)

    # Small wait so UI registers text
    page.wait_for_timeout(500)

    # 2. Click SEARCH button
    print("Clicking SEARCH button...")
    search_button = page.locator('button:has-text("SEARCH")')
    search_button.wait_for(state="visible", timeout=15000)
    search_button.click()

    # 3. Wait for search results to load
    page.wait_for_load_state("domcontentloaded")
    time.sleep(3)

    # 4. Scroll to load more products
    for i in range(1):
        print(f"Scrolling DMart... ({i+1}/1)")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)

def extract_dmart_data(page):
    extraction_script = """
    () => {
        const items = document.querySelectorAll(
            'div.w-\\\\[265px\\\\].h-\\\\[390px\\\\].bg-appWhite'
        );

        return Array.from(items).map(item => {

            // PRODUCT NAME (correct element)
            const nameEl = item.querySelector("div.text-primaryColor.min-h-10")
            const productName = nameEl ? nameEl.innerText.trim() : "N/A";

            // PRODUCT LINK
            let productLink = "N/A";
            const linkEl = item.querySelector('a');
            if (linkEl && linkEl.href) {
                productLink = null
            }

            // PRICES
            let mrp = "N/A";
            let dmartPrice = "N/A";

            const priceTexts = Array.from(item.querySelectorAll('p'))
                .map(p => p.innerText.trim())
                .filter(t => t.startsWith("₹"));

            if (priceTexts.length >= 2) {
                mrp = priceTexts[0];
                dmartPrice = priceTexts[1];
            } else if (priceTexts.length === 1) {
                dmartPrice = priceTexts[0];
            }

            // WEIGHT / PACK SIZE
            const weightEl = item.querySelector('select, button, input, div[role="button"]');
            const weight = weightEl ? weightEl.innerText.trim() : "N/A";

            // IMAGE
            const imgEl = item.querySelector('img');
            const image = imgEl ? imgEl.src : "N/A";

            return {
                product_name: productName,
                product_link: productLink,
                mrp: mrp,
                dmart_price: dmartPrice,
                weight: weight,
                image: image
            };
        });
    }
    """
    return page.evaluate(extraction_script)




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
    
    # Define file path: run_folder/blinkit.json (directly in parent folder)
    json_filename = f"{platform_name.lower()}.json"
    json_path = os.path.join(run_folder, json_filename)
    
    # Save the data
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"--- Data Saved Successfully ---")
    print(f"Folder: {run_folder}")
    print(f"File: {json_filename}")
    return json_path


# --- MAIN EXECUTION ---
def run_dmart_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # Use a standard Chrome User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        context = browser.new_context(user_agent=user_agent)
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        
        try:
            page.goto("https://www.dmart.in/", wait_until="domcontentloaded")
            
            set_dmart_location(page, 'Mumbai')
            search_dmart_products(page, 'Ghee')
            
            final_list = extract_dmart_data(page)
            print("Final List: ", final_list)
            # save_to_timestamped_folder(final_list, platform_name, run_parent_folder=run_parent_folder)
            
            # Return the products list so server.py can use them
            return final_list
            
        except Exception as e:
            print(f"[Blinkit] Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            return []  # Return empty list on error
        finally:
            browser.close()

if __name__ == "__main__":
    run_dmart_flow()