

import time
from playwright.sync_api import sync_playwright

def extract_blinkit_visual(url):
    with sync_playwright() as p:
        # headless=False so you can see it
        # slow_mo helps you observe the click
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        try:
            print(f"Navigating to: {url}")
            # 'commit' means as soon as the server responds. 
            # We don't wait for the whole page to load here.
            page.goto(url, wait_until="commit", timeout=60000)

            # Wait for the specific button to be attached to the DOM
            # This is much safer than waiting for networkidle
            print("Waiting for 'view more details' button...")
            view_more_selector = "text=view more details"
            
            # Wait up to 10 seconds for the button to appear
            page.wait_for_selector(view_more_selector, state="visible", timeout=10000)
            
            time.sleep(3)
            # Click it
            page.get_by_text("view more details").click()
            print("Clicked successfully!")

            # Now find that sibling div you wanted
            sibling_locator = page.locator("div[class^='ProductCarousel__ImageSliderContainer'] + div + div")
            sibling_locator.wait_for(state="visible")
            
            print("\n--- THIS HTML CONTAINS ALL PRODUCT DATA ---")
            print(sibling_locator.inner_html())

            # Keep browser open for a few seconds so you can see the result
            time.sleep(5)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

url = "https://blinkit.com/prn/bombay-banta-cola-masala-soda/prid/679237"
extract_blinkit_visual(url)