from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    )
    page = context.new_page()

    # 1️⃣ Homepage
    page.goto("https://www.bigbasket.com", timeout=60000)
    page.wait_for_timeout(5000)

    # 2️⃣ Set location
    page.click("text=Select Location", timeout=10000)
    page.fill("input[placeholder*='Search']", "Bangalore")
    page.wait_for_timeout(1000)
    page.click("text=Bangalore", timeout=10000)
    page.wait_for_timeout(5000)

    # 3️⃣ Search page
    page.goto("https://www.bigbasket.com/ps/?q=peanut+butter", timeout=60000)
    page.wait_for_timeout(6000)

    # 4️⃣ App popup
    try:
        page.click("text=Continue with web", timeout=3000)
    except:
        pass

    # 5️⃣ Scroll
    for _ in range(5):
        page.mouse.wheel(0, 4000)
        page.wait_for_timeout(2000)

    # 6️⃣ Extract
    cards = page.locator("article")
    print("Products found:", cards.count())

    for i in range(cards.count()):
        card = cards.nth(i)
        try:
            name = card.locator("h3").inner_text()
            price = card.locator("span:has-text('₹')").first.inner_text()
            print(name, price)
        except:
            pass

    browser.close()
