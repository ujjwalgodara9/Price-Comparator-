import { chromium } from "playwright";

async function getSwiggyCookies() {
  const browser = await chromium.launch({
    headless: false,
    slowMo: 50   // slow things a bit to look human
  });

  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    viewport: { width: 1280, height: 800 }
  });

  const page = await context.newPage();

  console.log("Opening Swiggy…");
  await page.goto(
    "https://www.swiggy.com/instamart/search?custom_back=true&query=coffee",
    { waitUntil: "domcontentloaded" }
  );

  // Give Swiggy time to run JS challenges
  console.log("Waiting for WAF challenge to finish…");
  await page.waitForTimeout(15000);

  // Sometimes Swiggy needs a reload to finalize cookies
  console.log("Reloading page…");
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForTimeout(8000);

  const cookies = await context.cookies();
  await browser.close();

  const cookieHeader = cookies.map(c => `${c.name}=${c.value}`).join("; ");

  console.log("\nCOOKIE HEADER:\n");
  console.log(cookieHeader);

  return cookieHeader;
}

// Run it
getSwiggyCookies()
  .then(() => console.log("\nCookies extracted successfully"))
  .catch(console.error);
