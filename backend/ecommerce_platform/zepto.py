import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# Storage folder for product data
STORAGE_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'product_data')
os.makedirs(STORAGE_FOLDER, exist_ok=True)

def remove_duplicate_products(product_list):
    seen = set()
    unique_products = []
    for product in product_list:
        product_tuple = tuple(sorted(product.items()))
        if product_tuple not in seen:
            unique_products.append(product)
            seen.add(product_tuple)
    return unique_products


def set_location_by_geolocation(page):
    """Set location by clicking Zepto's GPS 'Enable' button (browser context must have geolocation set)."""
    print("Setting location using browser geolocation...")
    address_header = page.get_by_test_id("user-address")
    address_header.wait_for(state="visible", timeout=10000)
    address_header.click()
    time.sleep(2)

    saved_container = page.get_by_test_id("saved-address-container")
    saved_container.wait_for(state="visible", timeout=12000)

    enable_btn = saved_container.get_by_role("button", name="Enable")
    enable_btn.click()
    time.sleep(4)


def set_location(page, location_name):
    print(f"Setting location to: {location_name}")
    address_header = page.get_by_test_id("user-address")
    address_header.wait_for(state="visible", timeout=10000)
    address_header.click()
    time.sleep(1)

    # Use .first to avoid strict mode error when two address-search-input elements exist
    search_container = page.get_by_test_id("address-search-input").first
    search_container.wait_for(state="visible", timeout=10000)

    search_input = search_container.locator("input")
    search_input.fill(location_name)

    results_container = page.get_by_test_id("address-search-container")
    first_result = results_container.get_by_test_id("address-search-item").first
    first_result.wait_for(state="visible", timeout=10000)
    first_result.click()
    time.sleep(3)


def search_and_scroll(page, product_query):
    print(f"Searching for: {product_query}")
    search_icon = page.get_by_test_id("search-bar-icon")
    search_icon.click()

    try:
        page.wait_for_selector('input:not([type="hidden"])', state="visible", timeout=10000)
        search_input = page.locator('input:not([type="hidden"])').first
        search_input.click()
        search_input.fill(product_query)
    except Exception:
        time.sleep(1)
        page.keyboard.type(product_query)

    page.keyboard.press("Enter")
    page.evaluate("document.body.style.zoom = '20%'")
    time.sleep(3)

    for i in range(1):
        print(f"Scroll iteration {i+1}/2")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)


def extract_product_list(page):
    print("Extracting all items in one go...")

    # Resilient extractor — uses content patterns, not hashed CSS class names.
    # Price: span containing ₹
    # Name: longest non-price span (>3 chars)
    # Quantity: span with unit keywords (ml, kg, g, pack, pcs, litre)
    # Delivery time: div.cTDqth (stable, data-attribute-backed class)
    extraction_script = r"""
    () => {
        const items = document.querySelectorAll('.B4vNQ');
        return Array.from(items).map(item => {
            const relativeLink = item.getAttribute('href');
            const fullLink = relativeLink ? `https://www.zepto.com${relativeLink}` : "N/A";

            const allSpans = [...item.querySelectorAll('span')];

            const priceSpan = allSpans.find(s => s.innerText && s.innerText.includes('\u20b9'));
            const priceText = priceSpan ? priceSpan.innerText.trim() : "N/A";

            const nameSpan = allSpans
                .filter(s => s !== priceSpan && s.innerText && s.innerText.trim().length > 3 && !s.innerText.includes('\u20b9'))
                .sort((a, b) => b.innerText.length - a.innerText.length)[0];
            const productName = nameSpan ? nameSpan.innerText.trim() : "N/A";

            const qtySpan = allSpans.find(s => {
                const t = s.innerText.trim().toLowerCase();
                return s !== nameSpan && !t.includes('\u20b9') &&
                    (t.includes('ml') || t.includes('kg') || /\d+\s*g\b/.test(t) ||
                     t.includes('litre') || t.includes('pack') || t.includes('pcs'));
            });
            const quantity = qtySpan ? qtySpan.innerText.trim() : "N/A";

            const timeEl = item.querySelector('div.cTDqth');
            const deliveryTime = timeEl ? timeEl.innerText.trim() : "N/A";

            const imgEl = item.querySelector('img');
            const imageUrl = imgEl ? (imgEl.getAttribute('src') || "N/A") : "N/A";

            return {
                "product_name": productName,
                "price": priceText,
                "description": quantity,
                "delivery_time": deliveryTime,
                "product_link": fullLink,
                "image_url": imageUrl
            };
        });
    }
    """

    products = page.evaluate(extraction_script)
    return [p for p in products if p['product_name'] != "N/A"]


def save_to_timestamped_folder(data, platform_name, run_parent_folder=None):
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


def run_zepto_flow(product_name, location, headless=True, max_products=50, run_parent_folder=None, platform_name='zepto'):
    start_time = time.time()

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
            page.goto("https://www.zepto.com", wait_until="domcontentloaded", timeout=60000)
            time.sleep(4)  # Let React hydrate before interacting

            if lat and lng:
                try:
                    set_location_by_geolocation(page)
                except Exception as e:
                    print(f"Geolocation failed ({e}), falling back to text search")
                    set_location(page, location_name)
            else:
                set_location(page, location_name)

            if page.locator("text=We're Coming Soon").count() > 0:
                print("[Zepto] Location not serviceable, returning empty list")
                return []

            search_and_scroll(page, product_name)

            try:
                page.wait_for_selector('.B4vNQ', timeout=20000)
            except Exception:
                print("No .B4vNQ product cards appeared — returning empty list")
                return []

            final_data_list = extract_product_list(page)
            final_data_list = remove_duplicate_products(final_data_list)
            save_to_timestamped_folder(final_data_list, platform_name, run_parent_folder=run_parent_folder)

            time_end = time.time()
            print(f"--- Zepto Total Time Taken: {time_end - start_time:.2f} seconds ---")
            return final_data_list

        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            browser.close()


if __name__ == "__main__":
    run_zepto_flow(product_name="milk", location="Mumbai", headless=False, max_products=50)
