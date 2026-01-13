import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

# Storage folder for product data
STORAGE_FOLDER = "/var/lib/product-compare/product_data"
os.makedirs(STORAGE_FOLDER, exist_ok=True)

def set_location(page, location_name):
    print(f"[Bigbasket] Setting location to: {location_name}")
    
    # 1. Click the location menu button
    # Using ID with escaping because of the colons
    page.wait_for_timeout(10000)
    loc_button = page.locator('span.Label-sc-15v1nk5-0.jnBJRV.w-full.inline.text-sm.text-darkOnyx-600.leading-md.truncate').first

    # It is highly recommended to keep the wait_for to ensure the element is loaded 
    # and clickable before the script attempts to interact with it.
    loc_button.wait_for(state="visible")
    loc_button.click()

    # 2. Type location in the input field
    search_input = page.locator('div.sc-fatcLD.fxbjsi input.Input-sc-tvw4mq-0.sc-cgjDci.gtCggY.fRZjfW')
    search_input.wait_for(state="visible")
    search_input.fill(location_name)
    
    # Wait for suggestions to stabilize
    page.wait_for_timeout(2000)

    # 3. Click the first suggestion
    first_result = page.locator('li.sc-djTQaJ.khoJMT').first
    first_result.wait_for(state="visible")
    first_result.click()

    # Allow content to stabilize
    page.wait_for_timeout(3000)

def search_and_scroll(page, product_query):
    print(f"[Bigbasket] Searching for: {product_query}")
    
    # 1. Locate search input inside the specified div and type
    search_input = page.locator('div.sc-fAGzit.bfbicI input')
    search_input.wait_for(state="visible")
    search_input.fill(product_query)
    page.keyboard.press("Enter")
    
    # Wait for content to load
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # 2. UI Cleanup: Delete footer to prevent scroll interference
    page.evaluate("document.querySelector('footer')?.remove()")

    # 3. Zoom out and Scroll Loop
    page.evaluate("document.body.style.zoom = '20%'")
    page.wait_for_timeout(2000)

    for i in range(2):
        print(f"Scroll iteration {i+1}/2")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)

def extract_product_list(page):
    print("[Bigbasket] Extracting items...")
    
    extraction_script = """
    () => {
        const items = document.querySelectorAll('.SKUDeck___StyledDiv-sc-1e5d9gk-0.bFjDCO');
        
        return Array.from(items).map(item => {
            // Name fusion: Brand + Title
            const brandEl = item.querySelector('span.BrandName___StyledLabel2-sc-hssfrl-0');
            const titleEl = item.querySelector('div.break-words.h-10.w-full h3');
            const fullName = (brandEl ? brandEl.innerText.trim() : "") + " " + (titleEl ? titleEl.innerText.trim() : "");

            // Price
            const priceEl = item.querySelector('div.sc-jMakVo.iKejGM span.Label-sc-15v1nk5-0.sc-iMTnTL.jnBJRV.knDrlZ');
            
            // Description/Pack Size
            const descEl = item.querySelector('div.Label-sc-15v1nk5-0.PackSelector___StyledLabel-sc-1lmu4hv-0.jnBJRV.hZcweF span');
            
            // Time
            const timeEl = item.querySelector('span.Eta___StyledLabel-sc-wkn76j-0 div.text-sunglow-800');
            
            // Product Link
            const linkEl = item.querySelector('a');
            const relativeLink = linkEl ? linkEl.getAttribute('href') : null;
            // Note: Prepending bigbasket.com instead of blinkit.com for accuracy
            const fullLink = relativeLink ? `https://www.bigbasket.com${relativeLink}` : "N/A";

            return {
                "product_name": fullName.trim() || "N/A",
                "price": priceEl ? priceEl.innerText.trim() : "N/A",
                "description": descEl ? descEl.innerText.trim() : "N/A",
                "delivery_time": timeEl ? timeEl.innerText.trim() : "N/A",
                "product_link": fullLink
            };
        });
    }
    """
    products = page.evaluate(extraction_script)
    return [p for p in products if p['product_name'] != "N/A"]

def save_to_timestamped_folder(data, platform_name, run_parent_folder=None):
    if run_parent_folder:
        run_folder = os.path.join(STORAGE_FOLDER, run_parent_folder)
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_folder = os.path.join(STORAGE_FOLDER, f"run-{timestamp}-{platform_name}")
    
    os.makedirs(run_folder, exist_ok=True)
    json_path = os.path.join(run_folder, f"{platform_name}.json")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"--- Data Saved to: {json_path} ---")
    return json_path

def run_bigbasket_flow(product_name="milk", location="Mumbai", headless=False, run_parent_folder=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, channel="chrome")
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto("https://www.bigbasket.com", wait_until="domcontentloaded")
            
            set_location(page, location)
            search_and_scroll(page, product_name)
            
            final_data_list = extract_product_list(page)
            save_to_timestamped_folder(final_data_list, "bigbasket", run_parent_folder)

            return final_data_list

        except Exception as e:
            print(f"Bigbasket Scrape Error: {e}")
            page.screenshot(path="bigbasket_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run_bigbasket_flow(product_name="atta", location="Mumbai", headless=False)