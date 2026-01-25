import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

STORAGE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "product_data")
os.makedirs(STORAGE_FOLDER, exist_ok=True)


def remove_duplicate_products(product_list):
    """Removes exact duplicate dictionaries from a list while preserving order."""
    seen = set()
    unique_products = []
    
    for product in product_list:
        product_tuple = tuple(sorted(product.items()))
        if product_tuple not in seen:
            unique_products.append(product)
            seen.add(product_tuple)
            
    return unique_products


def check_access_denied(page, screenshot_name="access_denied_bigbasket.png"):
    """Check if BigBasket is blocking access."""
    page_title = page.title()
    page_url = page.url
    
    if "access denied" in page_title.lower() or "blocked" in page_title.lower():
        print("ERROR: Access denied detected!")
        print(f"Page title: {page_title}")
        print(f"Page URL: {page_url}")
        page.screenshot(path=f"product_data/{screenshot_name}")
        raise Exception("BigBasket is blocking access. This may be due to bot detection.")


def set_location(page, location):
    """Set location on BigBasket."""
    print(f"Setting location to: {location}")
    
    # Find and click the location selection button
    location_button = page.locator('xpath=//button[contains(., "Delivery in 10 min") and contains(., "Select Location")]').first
    location_button.wait_for(state="visible", timeout=10000)
    location_button.scroll_into_view_if_needed()
    location_button.evaluate("element => element.click()")
    
    # Wait for the location modal to appear
    modal_title = page.get_by_text("Select a location for delivery", exact=False).first
    modal_title.wait_for(state="visible", timeout=5000)
    print("Successfully clicked location button and modal appeared!")
    
    # Find and interact with location input field
    location_input = page.locator('input[placeholder="Search for area or street name"]').first
    location_input.wait_for(state="visible", timeout=5000)
    location_input.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    location_input.click(force=True)
    print("Clicked on input field to focus it")

    page.wait_for_timeout(1000)
    
    # Type location
    keyboard = page.keyboard
    print(f"Typing location: {location}")
    keyboard.type(location, delay=100)
    
    print("Waiting 1 second for location suggestions to appear...")
    page.wait_for_timeout(1000)
    
    # Select first location suggestion
    first_location_item = page.locator('ul li.sc-jdkBTo.cnPYAb').first
    print("Found first location suggestion with class 'sc-jdkBTo cnPYAb'")
    
    try:
        location_name = first_location_item.evaluate("el => el.textContent || el.innerText || ''")
        print(f"Selecting first location suggestion: {location_name}")
    except:
        print("Selecting first location suggestion (text unavailable)")
    
    # Click on location suggestion
    box = first_location_item.bounding_box()
    if box:
        center_x = box['x'] + box['width'] / 2
        center_y = box['y'] + box['height'] / 2
        print(f"Clicking location suggestion at ({center_x}, {center_y})")
        page.mouse.click(center_x, center_y)
        print("Clicked on first location suggestion using mouse.click()")
    else:
        print("Bounding box not available, using fallback click")
        first_location_item.click(force=True)
        print("Clicked on first location suggestion")
    
    # Wait for location selection to complete
    print("Waiting for location selection to complete...")
    page.wait_for_timeout(1000)
    
    # Check immediately if access denied appeared
    try:
        page_title = page.title()
        if "access denied" in page_title.lower() or "blocked" in page_title.lower():
            print("ERROR: Access denied detected immediately after location click!")
            print(f"Page title: {page_title}")
            page.screenshot(path="product_data/access_denied_immediate.png")
            raise Exception("BigBasket blocked access immediately after location selection.")
    except Exception as e:
        if "blocked" in str(e).lower() or "access denied" in str(e).lower():
            raise
        pass
    
    # Wait for navigation or modal close
    try:
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        print("Page loaded after location selection.")
    except:
        print("No page navigation detected, waiting for modal to close...")
    
    try:
        modal_title.wait_for(state="hidden", timeout=5000)
        print("Location modal closed.")
    except:
        print("Modal may have already closed or page reloaded.")
    
    page.wait_for_timeout(3000)
    
    # Final check for access denied after location selection
    check_access_denied(page, "access_denied_after_location.png")
    print("Location selection completed!")
    
    try:
        page.wait_for_load_state("domcontentloaded", timeout=10000)
    except:
        print("Page may have already loaded.")


def search_and_scroll(page, product_name):
    """Search for a product on BigBasket and scroll to load more results."""
    print("Looking for search input field...")
    
    search_input = page.locator('input[placeholder="Search for Products..."]').first
    search_input.wait_for(state="visible", timeout=10000)
    search_input.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    search_input.click(force=True)
    print("Successfully clicked on search input field!")
    
    page.wait_for_timeout(1000)
    
    keyboard = page.keyboard
    print(f"Typing product name: {product_name}")
    keyboard.type(product_name, delay=100)
    page.wait_for_timeout(500)
    
    keyboard.press("Enter")
    print(f"Pressed Enter to search for: {product_name}")
    
    page.wait_for_timeout(3000)
    check_access_denied(page, "access_denied_after_search.png")
    print("Search completed successfully!")
    
    # Scroll to load more products
    page.evaluate("document.body.style.zoom = '20%'")
    time.sleep(3)
    page.wait_for_load_state("domcontentloaded")
    
    for i in range(2):
        print(f"Scroll iteration {i+1}/2")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)


def extract_product_list(page):
    """Extract product data from BigBasket search results."""
    print("Extracting all items in one go...")
    
    extraction_script = """
    () => {
        const items = document.querySelectorAll('.SKUDeck___StyledDiv-sc-1e5d9gk-0.bFjDCO');

        const products = Array.from(items).map(item => {
            const brandEl = item.querySelector('span.BrandName___StyledLabel2-sc-hssfrl-0');
            const brand = brandEl ? brandEl.innerText.trim() : "";

            const nameEl = item.querySelector('h3.line-clamp-2');
            const productNameOnly = nameEl ? nameEl.innerText.trim() : "N/A";

            const fullProductName = brand ? `${brand} ${productNameOnly}` : productNameOnly;

            const priceBlock = item.querySelector('div.flex.flex-col.gap-0\\\\.5');
            let price = "N/A";
            let mrp = "N/A";

            if (priceBlock) {
                const spans = priceBlock.querySelectorAll('span');
                if (spans[0]) price = spans[0].innerText.trim(); 
            }

            const deliveryEl = item.querySelector('div.text-sunglow-800');
            const deliveryTime = deliveryEl ? deliveryEl.innerText.trim() : "N/A";

            const linkEl = item.querySelector('div.relative.border-solid a');
            let productLink = "N/A";
            let imageUrl = "N/A";

            if (linkEl) {
                const href = linkEl.getAttribute('href');
                productLink = href ? `https://www.bigbasket.com${href}` : "N/A";
                
                const imgEl = linkEl.querySelector('img');
                imageUrl = imgEl ? imgEl.getAttribute('src') : "N/A";
            }

            const qtyEl = item.querySelector('h3 span.truncate');
            const description = qtyEl ? qtyEl.innerText.trim() : "N/A";

            return {
                "product_name": fullProductName,
                "price": price,
                "description": description,
                "delivery_time": deliveryTime,
                "product_link": productLink,
                "image_url": imageUrl,
            };
        });

        return products.filter(p => p.product_name !== "N/A");
    }
    """
    
    products = page.evaluate(extraction_script)
    return [p for p in products if p['product_name'] != "N/A"]


def save_to_timestamped_folder(data, platform_name, run_parent_folder=None):
    """Save scraped data to JSON file."""
    if run_parent_folder:
        run_folder = os.path.join(STORAGE_FOLDER, run_parent_folder)
        os.makedirs(run_folder, exist_ok=True)
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_folder = os.path.join(STORAGE_FOLDER, f"run-{timestamp}-{platform_name.lower()}")
        os.makedirs(run_folder, exist_ok=True)
    
    json_filename = f"{platform_name.lower()}.json"
    json_path = os.path.join(run_folder, json_filename)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"--- Data Saved Successfully ---")
    print(f"Folder: {run_folder}")
    print(f"File: {json_filename}")
    return json_path


def setup_browser_context(p, headless):
    """Setup browser with stealth settings."""
    browser = p.firefox.launch(
        headless=headless,
        firefox_user_prefs={
            'dom.webdriver.enabled': False,
            'useAutomationExtension': False,
            'general.useragent.override': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        }
    )
    
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        locale='en-US',
        timezone_id='Asia/Kolkata',
        permissions=['geolocation'],
        extra_http_headers={
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    )
    
    page = context.new_page()
    return browser, context, page


def run_bigbasket_flow(product_name, location, headless, max_products, run_parent_folder=None, platform_name='bigbasket'):
    """Main function to run BigBasket scraping flow."""
    start_time = time.time()
    
    with sync_playwright() as p:
        browser, context, page = setup_browser_context(p, headless)
        
        try:
            print("Navigating to BigBasket...")
            page.goto("https://www.bigbasket.com/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            
            check_access_denied(page)
            set_location(page, location)
            search_and_scroll(page, product_name)
            
            # Extract products
            final_data_list = extract_product_list(page)
            final_data_list = remove_duplicate_products(final_data_list)
            
            # Save to file
            _ = save_to_timestamped_folder(final_data_list, platform_name, run_parent_folder=run_parent_folder)
            
            time_end = time.time()
            print(f"--- BigBasket Total Time Taken: {time_end - start_time:.2f} seconds ---")
            return final_data_list
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            context.close()
            browser.close()
            print("Browser closed.")

if __name__ == "__main__":
    run_bigbasket_flow(product_name="peanut butter", location="Mumbai", headless=False, max_products=50)

