# Real-Time Data Fetching Guide

## Current Status

⚠️ **The current implementation is a framework/skeleton**. The actual scraping logic needs to be implemented for each platform.

## How Real-Time Data Works

There are **three main approaches** to get real-time data from fast e-commerce platforms:

### 1. **Official APIs** (Best Option - If Available)
Some platforms provide public or partner APIs:
- ✅ Most reliable
- ✅ Legal and supported
- ✅ Structured data
- ❌ May require authentication/API keys
- ❌ May have rate limits
- ❌ May be paid

### 2. **Web Scraping** (Most Common)
Scraping HTML/JSON from websites:
- ✅ Works for most platforms
- ✅ No API keys needed
- ❌ Can break if site structure changes
- ❌ May violate ToS
- ❌ Requires maintenance

### 3. **Browser Automation** (For JavaScript-Heavy Sites)
Using Puppeteer/Playwright to render pages:
- ✅ Handles dynamic content
- ✅ Can interact with pages
- ❌ Slower and resource-intensive
- ❌ More complex

## Platform-Specific Implementation

### Zepto

**Approach**: Check for API endpoints or scrape search results

```javascript
async function scrapeZepto(query, location) {
  try {
    // Option 1: Try to find API endpoint (check browser DevTools Network tab)
    const apiUrl = `https://api.zepto.com/v1/search?q=${encodeURIComponent(query)}&lat=${location.coordinates?.lat}&lng=${location.coordinates?.lng}`;
    
    const response = await axios.get(apiUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        // May need additional headers like authorization tokens
      }
    });

    // Parse API response
    const products = response.data.results?.map(item => ({
      id: item.id || item.product_id,
      name: item.name || item.title,
      description: item.description || '',
      image: item.image_url || item.image,
      price: item.price || item.final_price,
      currency: 'INR',
      platform: 'zepto',
      availability: item.in_stock !== false,
      rating: item.rating || 0,
      reviewCount: item.review_count || 0,
      features: item.features || [],
      link: `https://www.zepto.com/product/${item.slug || item.id}`,
      location: `${location.city}, ${location.state}`,
      deliveryTime: item.delivery_time || '10-15 mins',
      deliveryFee: item.delivery_fee || 0,
      originalPrice: item.original_price || item.mrp,
    })) || [];

    return products;
  } catch (error) {
    console.error('Zepto API error:', error);
    
    // Fallback: Web scraping
    return await scrapeZeptoHTML(query, location);
  }
}

async function scrapeZeptoHTML(query, location) {
  const url = `https://www.zepto.com/search?q=${encodeURIComponent(query)}`;
  const response = await axios.get(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
  });
  
  const $ = cheerio.load(response.data);
  const products = [];
  
  // Find product containers (inspect page to find correct selectors)
  $('.product-item, .product-card, [data-product-id]').each((i, elem) => {
    const $elem = $(elem);
    products.push({
      id: $elem.attr('data-product-id') || `zepto-${i}`,
      name: $elem.find('.product-name, h3, .title').text().trim(),
      price: parseFloat($elem.find('.price, .product-price').text().replace(/[^0-9.]/g, '')),
      image: $elem.find('img').attr('src') || $elem.find('img').attr('data-src'),
      link: $elem.find('a').attr('href'),
      // ... extract other fields
    });
  });
  
  return products;
}
```

### Swiggy Instamart

**Approach**: Swiggy uses internal APIs - check Network tab in DevTools

```javascript
async function scrapeSwiggyInstamart(query, location) {
  try {
    // Swiggy uses internal APIs - you need to:
    // 1. Open Swiggy Instamart in browser
    // 2. Open DevTools > Network tab
    // 3. Search for a product
    // 4. Find the API call (usually contains "search" or "instamart")
    // 5. Copy the request URL and headers
    
    // Example API endpoint (you need to find the actual one):
    const apiUrl = `https://www.swiggy.com/dapi/instamart/search?query=${encodeURIComponent(query)}`;
    
    const response = await axios.get(apiUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        // May need: 'x-swiggy-device-id', 'Authorization', etc.
        // Copy all headers from browser request
      }
    });

    // Parse response structure (varies by platform)
    const products = response.data.data?.cards?.flatMap(card => 
      card.data?.data?.items?.map(item => ({
        id: item.id,
        name: item.name,
        price: item.price || item.final_price,
        image: item.imageId ? `https://res.cloudinary.com/swiggy/image/upload/${item.imageId}` : '',
        deliveryTime: item.deliveryTime || '30-45 mins',
        // ... map other fields
      })) || []
    ) || [];

    return products;
  } catch (error) {
    console.error('Swiggy Instamart error:', error);
    return [];
  }
}
```

### Blinkit

**Approach**: Similar to Swiggy - uses internal APIs

```javascript
async function scrapeBlinkit(query, location) {
  try {
    // Find API endpoint from browser DevTools
    const apiUrl = `https://blinkit.com/api/search?q=${encodeURIComponent(query)}`;
    
    const response = await axios.get(apiUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        // May need location headers: 'x-location-id', 'x-city-id'
      }
    });

    return parseBlinkitResponse(response.data);
  } catch (error) {
    console.error('Blinkit error:', error);
    return [];
  }
}
```

### BigBasket

**Approach**: Can scrape HTML or find API endpoints

```javascript
async function scrapeBigBasket(query, location) {
  try {
    const url = `https://www.bigbasket.com/ps/?q=${encodeURIComponent(query)}`;
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });
    
    const $ = cheerio.load(response.data);
    const products = [];
    
    // BigBasket product selectors (inspect page to verify)
    $('.product-item, .sku-item').each((i, elem) => {
      const $elem = $(elem);
      products.push({
        id: $elem.attr('data-product-id') || `bb-${i}`,
        name: $elem.find('.prod-name, h3').text().trim(),
        price: parseFloat($elem.find('.price, .final-price').text().replace(/[^0-9.]/g, '')),
        originalPrice: parseFloat($elem.find('.mrp, .original-price').text().replace(/[^0-9.]/g, '')),
        image: $elem.find('img').attr('src') || $elem.find('img').attr('data-src'),
        link: `https://www.bigbasket.com${$elem.find('a').attr('href')}`,
        deliveryTime: '1-2 hours', // BigBasket typically takes longer
      });
    });
    
    return products;
  } catch (error) {
    console.error('BigBasket error:', error);
    return [];
  }
}
```

## Using Puppeteer for JavaScript-Heavy Sites

For sites that load content via JavaScript:

```javascript
const puppeteer = require('puppeteer');

async function scrapeWithPuppeteer(platform, query, location) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // Navigate to search page
    await page.goto(`https://${platform}.com/search?q=${query}`, {
      waitUntil: 'networkidle2'
    });
    
    // Wait for products to load
    await page.waitForSelector('.product-item, .product-card', { timeout: 10000 });
    
    // Extract product data
    const products = await page.evaluate(() => {
      const items = Array.from(document.querySelectorAll('.product-item'));
      return items.map(item => ({
        name: item.querySelector('.product-name')?.textContent?.trim(),
        price: item.querySelector('.price')?.textContent?.trim(),
        // ... extract other fields
      }));
    });
    
    return products;
  } finally {
    await browser.close();
  }
}
```

## Finding API Endpoints

**Step-by-step guide:**

1. Open the platform website in Chrome/Firefox
2. Open DevTools (F12)
3. Go to **Network** tab
4. Search for a product
5. Look for requests with:
   - Type: `xhr` or `fetch`
   - Name containing: `search`, `product`, `api`
   - Response type: `json`
6. Click on the request → **Headers** tab
   - Copy the **Request URL**
   - Copy all **Request Headers** (especially `Authorization`, `x-*` headers)
7. Click **Response** tab to see data structure
8. Use this information in your scraper

## Important Considerations

### Rate Limiting
```javascript
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Add delay between requests
await delay(1000); // Wait 1 second between requests
```

### Error Handling
```javascript
async function scrapeWithRetry(platform, query, location, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await scrapePlatform(platform, query, location);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await delay(2000 * (i + 1)); // Exponential backoff
    }
  }
}
```

### Caching
```javascript
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 300 }); // 5 minutes

async function scrapeWithCache(platform, query, location) {
  const cacheKey = `${platform}-${query}-${location.city}`;
  const cached = cache.get(cacheKey);
  if (cached) return cached;
  
  const products = await scrapePlatform(platform, query, location);
  cache.set(cacheKey, products);
  return products;
}
```

## Legal & Ethical Considerations

⚠️ **Important:**
- Check `robots.txt` (e.g., `https://zepto.com/robots.txt`)
- Read Terms of Service
- Respect rate limits
- Don't overload servers
- Consider using official APIs if available
- Some platforms may block automated access

## Next Steps

1. **For each platform:**
   - Open in browser and inspect network requests
   - Identify API endpoints or HTML structure
   - Implement scraper function
   - Test and handle errors

2. **Add to backend server:**
   - Replace placeholder functions in `server.js`
   - Add proper error handling
   - Implement caching
   - Add rate limiting

3. **Test thoroughly:**
   - Test with various queries
   - Test with different locations
   - Handle edge cases
   - Monitor for errors

