from playwright.sync_api import sync_playwright
import re
import time
import json
import os
import uuid
from datetime import datetime

def parse_products(raw_text):
    products = re.split(r'\n?ADD\n?', raw_text)
    parsed = []

    for product_text in products:
        if not product_text.strip():
            continue

        lines = product_text.strip().split('\n')

        price_match = re.search(r"₹\s*(\d+)", product_text)
        if not price_match:
            continue

        name = ""
        for line in lines:
            if (
                len(line) > 20 and
                "₹" not in line and
                not re.match(r'^[\d\s\.\(\)]+$', line) and
                "OFF" not in line
            ):
                name = line
                break

        parsed.append({
            "name": name,
            "price": price_match.group(1),
            "other_details": product_text.strip()
        })

    return parsed


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        viewport={"width": 390, "height": 844},
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/16.0 Mobile/15E148 Safari/604.1"
        )
    )

    page = context.new_page()

    search_query = "atta"

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
    print("Found cards:", cards.count())

    results = []

    for i in range(min(cards.count(), 10)):
        card = cards.nth(i)

        text = card.inner_text()

        # ✅ IMAGE SCRAPING
        img_url = None
        img = card.locator("img").first
        img_url = (
            img.get_attribute("src") or
            img.get_attribute("data-src") or
            img.get_attribute("data-original")
        )

        products = parse_products(text)

        for p in products:
            p["image_url"] = img_url
            results.append(p)

    for r in results:
        print("----")
        print(r)

    browser.close()

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
    
    print(f"\n✅ Results saved to: {filepath}")
    print(f"Total products found: {len(results)}")
