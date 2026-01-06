# Quick Start: Finding Headers for Zepto API

## You Found the API! 🎉

You found: `https://bff-gateway.zepto.com/lms/api/v2/get_page`

## Step 1: Get Headers from Browser

1. **Open Zepto website** in Chrome
2. **Open DevTools** (F12)
3. **Go to Network tab**
4. **Reload the page** or search for a product
5. **Find the request** named `get_page`
6. **Click on it**
7. **Go to "Headers" tab**
8. **Scroll to "Request Headers"**

## Step 2: Copy These Headers

Look for and copy these headers (if present):

### Essential Headers:
- ✅ `User-Agent` - Always needed
- ✅ `Accept` - Content type you accept
- ✅ `Referer` - Where request came from
- ✅ `Origin` - Request origin

### Zepto-Specific (Check if present):
- `x-platform` or `x-platform-type`
- `x-app-version`
- `x-device-id`
- `x-session-id`
- `Cookie` - **Very important!** Copy all cookies

### Authentication (If present):
- `Authorization` - Bearer token or API key

## Step 3: Test Headers

I've created a test script for you:

```bash
cd backend-example
node test-zepto-headers.js
```

This will test different header combinations to see what works.

## Step 4: Update Scraper

Once you know which headers work:

1. Open `server.js`
2. Find the `scrapeZepto` function
3. Update the headers object with the working headers
4. Test again

## Common Scenarios

### ✅ If it works with minimal headers:
```javascript
headers: {
  'User-Agent': 'Mozilla/5.0 ...',
  'Accept': 'application/json',
}
```

### ⚠️ If you get 403 Forbidden:
Add cookies:
```javascript
headers: {
  'User-Agent': 'Mozilla/5.0 ...',
  'Accept': 'application/json',
  'Cookie': 'session_id=...; user_token=...', // Copy from browser
}
```

### ⚠️ If you get 401 Unauthorized:
Add authorization:
```javascript
headers: {
  'User-Agent': 'Mozilla/5.0 ...',
  'Accept': 'application/json',
  'Authorization': 'Bearer ...', // Copy from browser
}
```

## Quick Copy Method

**Easiest way:**

1. In DevTools → Network tab
2. Right-click on `get_page` request
3. Select **"Copy" → "Copy as cURL"**
4. Paste in terminal/notepad
5. Extract headers from the `-H` flags

Example cURL output:
```bash
curl 'https://bff-gateway.zepto.com/lms/api/v2/get_page?...' \
  -H 'User-Agent: Mozilla/5.0 ...' \
  -H 'Accept: application/json' \
  -H 'Cookie: session_id=abc123'
```

Convert to JavaScript:
```javascript
headers: {
  'User-Agent': 'Mozilla/5.0 ...',
  'Accept': 'application/json',
  'Cookie': 'session_id=abc123',
}
```

## What I've Updated

✅ Updated `server.js` with your API endpoint
✅ Created `test-zepto-headers.js` to test headers
✅ Created `HOW_TO_FIND_HEADERS.md` with detailed guide

## Next Steps

1. **Run the test script** to see what headers work
2. **Copy working headers** to `server.js`
3. **Test the API** with a real query
4. **Adjust response parsing** based on actual response structure

The scraper is ready - you just need to add the correct headers!

