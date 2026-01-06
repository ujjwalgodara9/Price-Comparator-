/**
 * Example Zepto Scraper Implementation
 * 
 * This is a working example showing how to implement real scraping for Zepto.
 * You'll need to:
 * 1. Inspect Zepto's website to find actual API endpoints or HTML structure
 * 2. Update the selectors/API endpoints based on what you find
 * 3. Handle authentication if required
 */

const axios = require('axios');
const cheerio = require('cheerio');

/**
 * Scrape Zepto products
 * 
 * @param {string} query - Search query
 * @param {Object} location - Location data with city, state, coordinates
 * @returns {Promise<Array>} Array of product objects
 */
async function scrapeZepto(query, location) {
  try {
    // METHOD 1: Try to use API endpoint (if available)
    // First, check browser DevTools Network tab to find the actual API
    const products = await scrapeZeptoAPI(query, location);
    if (products.length > 0) {
      return products;
    }
    
    // METHOD 2: Fallback to HTML scraping
    return await scrapeZeptoHTML(query, location);
  } catch (error) {
    console.error('Zepto scraping error:', error);
    return [];
  }
}

/**
 * Attempt to scrape via API endpoint
 * 
 * Based on actual Zepto API endpoint found:
 * https://bff-gateway.zepto.com/lms/api/v2/get_page
 */
async function scrapeZeptoAPI(query, location) {
  try {
    const lat = location.coordinates?.lat || 13.035819079405993;
    const lng = location.coordinates?.lng || 77.53113274824308;
    
    // Zepto's actual API endpoint
    const apiUrl = `https://bff-gateway.zepto.com/lms/api/v2/get_page`;
    
    const response = await axios.get(apiUrl, {
      params: {
        latitude: lat,
        longitude: lng,
        page_type: 'HOME', // or 'SEARCH' for search results
        version: 'v2',
        show_new_eta_banner: true,
        page_size: 50, // Increase for more products
        enforce_platform_type: 'DESKTOP',
        // For search, you might need:
        // query: query,
        // search_type: 'PRODUCT',
      },
      headers: {
        // Standard browser headers
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.zepto.com/',
        'Origin': 'https://www.zepto.com',
        
        // Zepto-specific headers (check in DevTools and add if present)
        // 'x-platform': 'DESKTOP',
        // 'x-app-version': 'v2',
        // 'x-device-id': '...',
        // 'x-session-id': '...',
        
        // IMPORTANT: Copy cookies from browser DevTools if needed
        // 'Cookie': 'session_id=...; user_token=...',
        
        // If authentication required:
        // 'Authorization': 'Bearer ...',
      },
      timeout: 15000,
    });

    // Parse the response based on actual API structure
    // Inspect response.data in browser DevTools to see actual structure
    const data = response.data;
    
    // Zepto API response structure (adjust based on actual response):
    // The response likely has a structure like:
    // { data: { products: [...] } } or { results: [...] } or { items: [...] }
    
    // Extract products from response (adjust path based on actual structure)
    let items = [];
    if (data.data?.products) items = data.data.products;
    else if (data.data?.items) items = data.data.items;
    else if (data.results) items = data.results;
    else if (data.items) items = data.items;
    else if (data.products) items = data.products;
    else if (Array.isArray(data)) items = data;
    
    // Map to our product format
    const products = items.map((item, index) => ({
      id: item.id || item.product_id || item.productId || `zepto-${index}`,
      name: item.name || item.title || item.product_name || item.productName || '',
      description: item.description || item.short_description || item.desc || '',
      image: item.image || item.image_url || item.imageUrl || item.thumbnail || item.img || 'https://via.placeholder.com/400',
      price: parseFloat(item.price || item.final_price || item.finalPrice || item.selling_price || item.sellingPrice || item.amount || 0),
      currency: 'INR',
      platform: 'zepto',
      availability: item.in_stock !== false && item.available !== false && item.is_available !== false,
      rating: parseFloat(item.rating || item.avg_rating || item.averageRating || item.avgRating || 0),
      reviewCount: parseInt(item.review_count || item.reviews || item.reviewCount || 0),
      features: item.features || item.highlights || item.tags || [],
      link: item.url || item.link || item.product_url || `https://www.zepto.com/product/${item.slug || item.id || item.product_id}`,
      location: `${location.city}, ${location.state}`,
      deliveryTime: item.delivery_time || item.deliveryTime || item.estimated_delivery || item.eta || '10-15 mins',
      deliveryFee: parseFloat(item.delivery_fee || item.deliveryFee || item.shipping_charge || item.shippingCharge || 0),
      originalPrice: item.original_price || item.originalPrice || item.mrp || item.list_price || item.listPrice || null,
    })).filter(p => p.name && p.price > 0); // Filter out invalid products

    return products;
  } catch (error) {
    // If API fails, return empty array to try HTML scraping
    console.warn('Zepto API failed, trying HTML scraping:', error.message);
    return [];
  }
}

/**
 * Scrape Zepto by parsing HTML
 */
async function scrapeZeptoHTML(query, location) {
  try {
    const url = `https://www.zepto.com/search?q=${encodeURIComponent(query)}`;
    
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
      },
      timeout: 15000,
    });

    const $ = cheerio.load(response.data);
    const products = [];

    // TODO: Inspect Zepto's HTML structure and update these selectors
    // Open Zepto search page → Right-click on product → Inspect Element
    // Find the container class/id and update selectors below
    
    // Example selectors (you need to verify these):
    $('.product-item, .product-card, [data-product-id], .search-result-item').each((index, element) => {
      const $elem = $(element);
      
      // Extract product name
      const name = $elem.find('.product-name, h3, .title, [data-product-name]').first().text().trim();
      if (!name) return; // Skip if no name found
      
      // Extract price
      const priceText = $elem.find('.price, .product-price, [data-price]').first().text();
      const price = parseFloat(priceText.replace(/[^0-9.]/g, '')) || 0;
      
      // Extract image
      const image = $elem.find('img').first().attr('src') || 
                   $elem.find('img').first().attr('data-src') ||
                   $elem.find('img').first().attr('data-lazy-src') ||
                   'https://via.placeholder.com/400';
      
      // Extract link
      const linkElem = $elem.find('a').first();
      const relativeLink = linkElem.attr('href') || '';
      const link = relativeLink.startsWith('http') ? relativeLink : `https://www.zepto.com${relativeLink}`;
      
      // Extract product ID
      const productId = $elem.attr('data-product-id') || 
                       link.match(/product\/([^\/]+)/)?.[1] ||
                       `zepto-${index}`;

      products.push({
        id: productId,
        name: name,
        description: $elem.find('.description, .product-desc').text().trim() || '',
        image: image,
        price: price,
        currency: 'INR',
        platform: 'zepto',
        availability: !$elem.find('.out-of-stock, .unavailable').length,
        rating: parseFloat($elem.find('.rating, [data-rating]').attr('data-rating') || 
                         $elem.find('.rating').text().replace(/[^0-9.]/g, '') || 0),
        reviewCount: parseInt($elem.find('.reviews, .review-count').text().replace(/[^0-9]/g, '') || 0),
        features: [],
        link: link,
        location: `${location.city}, ${location.state}`,
        deliveryTime: $elem.find('.delivery-time, [data-delivery-time]').text().trim() || '10-15 mins',
        deliveryFee: parseFloat($elem.find('.delivery-fee').text().replace(/[^0-9.]/g, '') || 0),
        originalPrice: (() => {
          const originalPriceText = $elem.find('.original-price, .mrp, .strikethrough').text();
          return originalPriceText ? parseFloat(originalPriceText.replace(/[^0-9.]/g, '')) : null;
        })(),
      });
    });

    return products;
  } catch (error) {
    console.error('Zepto HTML scraping error:', error);
    return [];
  }
}

/**
 * Alternative: Use Puppeteer for JavaScript-rendered content
 */
async function scrapeZeptoWithPuppeteer(query, location) {
  const puppeteer = require('puppeteer');
  const browser = await puppeteer.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  try {
    // Set user agent
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
    
    // Navigate to search page
    const url = `https://www.zepto.com/search?q=${encodeURIComponent(query)}`;
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    
    // Wait for products to load
    await page.waitForSelector('.product-item, .product-card', { timeout: 10000 });
    
    // Extract product data
    const products = await page.evaluate(() => {
      const items = Array.from(document.querySelectorAll('.product-item, .product-card'));
      return items.map((item, index) => {
        const nameElem = item.querySelector('.product-name, h3, .title');
        const priceElem = item.querySelector('.price, .product-price');
        const imgElem = item.querySelector('img');
        const linkElem = item.querySelector('a');
        
        return {
          id: item.getAttribute('data-product-id') || `zepto-${index}`,
          name: nameElem?.textContent?.trim() || '',
          price: parseFloat(priceElem?.textContent?.replace(/[^0-9.]/g, '') || 0),
          image: imgElem?.src || imgElem?.getAttribute('data-src') || '',
          link: linkElem?.href || '',
        };
      }).filter(p => p.name && p.price > 0);
    });
    
    return products;
  } finally {
    await browser.close();
  }
}

module.exports = { scrapeZepto, scrapeZeptoWithPuppeteer };

