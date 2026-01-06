# How to Find Required Headers for API Scraping

## Quick Method: Copy from Browser DevTools

### Step-by-Step:

1. **Open Zepto website** in Chrome/Firefox
2. **Open DevTools** (F12)
3. **Go to Network tab**
4. **Search for a product** or navigate to home page
5. **Find the API request** (the one you found: `get_page`)
6. **Click on the request**
7. **Go to "Headers" tab**
8. **Scroll to "Request Headers" section**
9. **Copy all headers** (especially these important ones):

## Important Headers to Look For:

### Usually Required:
- `User-Agent` - Identifies your browser
- `Accept` - What content types you accept
- `Accept-Language` - Language preference
- `Content-Type` - If sending POST data
- `Referer` - Where the request came from

### Platform-Specific (Zepto):
- `x-platform` or `x-platform-type` - Platform identifier
- `x-app-version` - App version
- `x-device-id` - Device identifier
- `Authorization` - If authentication required
- `x-session-id` or `x-token` - Session/authentication tokens
- `Cookie` - Session cookies (very important!)

### Location Headers:
- `x-latitude` / `x-longitude` - Location coordinates
- `x-city-id` / `x-location-id` - City/location identifier
- `x-pincode` - Delivery pincode

## Example: What Zepto Might Need

Based on the endpoint you found, here's what you likely need:

```javascript
const headers = {
  // Standard browser headers
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'en-US,en;q=0.9',
  'Referer': 'https://www.zepto.com/',
  'Origin': 'https://www.zepto.com',
  
  // Zepto-specific (check in DevTools)
  'x-platform': 'DESKTOP', // or 'WEB', 'MOBILE'
  'x-app-version': 'v2', // or whatever version they use
  'x-device-id': '...', // May be required
  
  // Cookies (VERY IMPORTANT - copy from browser)
  'Cookie': 'session_id=...; user_token=...; ...',
  
  // If they use authentication
  'Authorization': 'Bearer ...', // Check if present
};
```

## How to Extract Headers from Browser

### Method 1: Manual Copy
1. In DevTools → Network tab
2. Right-click on the request
3. Select "Copy" → "Copy as cURL"
4. Paste in terminal/notepad
5. Extract headers from the cURL command

### Method 2: Use Browser Extension
- Install a browser extension that shows request details
- Or use Postman/Insomnia to import the request

### Method 3: JavaScript in Browser Console
```javascript
// Run this in browser console on Zepto page
fetch('https://bff-gateway.zepto.com/lms/api/v2/get_page?latitude=13.035819079405993&longitude=77.53113274824308&page_type=HOME&version=v2&show_new_eta_banner=true&page_size=1&enforce_platform_type=DESKTOP')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

## Testing Headers

### Minimal Headers (Try First):
```javascript
const minimalHeaders = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  'Accept': 'application/json',
};
```

### If That Fails, Add More:
```javascript
const moreHeaders = {
  ...minimalHeaders,
  'Referer': 'https://www.zepto.com/',
  'Origin': 'https://www.zepto.com',
  'Accept-Language': 'en-US,en;q=0.9',
};
```

### If Still Fails, Add Cookies:
```javascript
// Get cookies from browser DevTools → Application → Cookies
const withCookies = {
  ...moreHeaders,
  'Cookie': 'your_cookies_here',
};
```

## Common Issues & Solutions

### 403 Forbidden
- **Problem**: Missing authentication or wrong headers
- **Solution**: Add cookies, authorization token, or session ID

### 401 Unauthorized
- **Problem**: Need authentication
- **Solution**: Add `Authorization` header or login first

### CORS Error
- **Problem**: Browser blocking cross-origin request
- **Solution**: This is why we use backend server (not browser)

### Rate Limiting (429)
- **Problem**: Too many requests
- **Solution**: Add delays between requests, use proxies

## Quick Test Script

Create a test file to check what headers work:

```javascript
const axios = require('axios');

async function testZeptoHeaders() {
  const url = 'https://bff-gateway.zepto.com/lms/api/v2/get_page';
  const params = {
    latitude: 13.035819079405993,
    longitude: 77.53113274824308,
    page_type: 'HOME',
    version: 'v2',
    show_new_eta_banner: true,
    page_size: 1,
    enforce_platform_type: 'DESKTOP'
  };

  // Test 1: Minimal headers
  try {
    const response = await axios.get(url, {
      params,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
      }
    });
    console.log('✅ Minimal headers work!', response.data);
    return response.data;
  } catch (error) {
    console.log('❌ Minimal headers failed:', error.response?.status);
  }

  // Test 2: Add more headers (copy from browser)
  // ... continue testing
}

testZeptoHeaders();
```

