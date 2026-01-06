# Zepto Headers - Extracted from cURL

All headers have been extracted from the cURL command and are now configured in the scraper.

## Headers Included

### ✅ Standard Browser Headers
- `accept`: application/json, text/plain, */*
- `accept-language`: en-US,en;q=0.9,en-IN;q=0.8
- `origin`: https://www.zepto.com
- `referer`: https://www.zepto.com/
- `user-agent`: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

### ✅ Zepto-Specific Headers
- `app_sub_platform`: WEB
- `app_version`: 14.4.4
- `appversion`: 14.4.4
- `auth_from_cookie`: true
- `auth_revamp_flow`: v2
- `device_id`: (generated UUID - consistent per session)
- `deviceid`: (same as device_id)
- `marketplace_type`: SUPER_SAVER
- `platform`: WEB
- `priority`: u=1, i
- `request_id`: (generated UUID - unique per request)
- `requestid`: (same as request_id)
- `session_id`: (generated UUID - consistent per session)
- `sessionid`: (same as session_id)
- `source`: DIRECT
- `tenant`: ZEPTO

### ✅ Security Headers
- `sec-fetch-dest`: empty
- `sec-fetch-mode`: cors
- `sec-fetch-site`: same-site

### ✅ Compatible Components
- `compatible_components`: (long static string with all enabled features)

## Optional Headers (Not Included by Default)

These headers may be needed in some cases but are not included by default:

### Cookies
- `Cookie`: Copy from browser DevTools if API requires authentication
  - Location: DevTools → Application → Cookies → zepto.com
  - Example: `_gcl_au=...; _ga=...; _fbp=...; session_id=...`

### CSRF Tokens
- `x-csrf-secret`: Extract from cookies
- `x-xsrf-token`: Extract from cookies

### Store Information
- `store_id`: From API response (store ID for location)
- `store_ids`: Comma-separated store IDs
- `storeid`: Same as store_id
- `store_etas`: JSON string with delivery times per store

### Request Signature
- `request-signature`: May need to be generated based on request content

### Timezone
- `x-timezone`: Can be generated or extracted

## How to Add Optional Headers

If you encounter 403/401 errors, you may need to add cookies:

1. **Get cookies from browser:**
   - Open Zepto in browser
   - DevTools → Application → Cookies
   - Copy all cookies for zepto.com

2. **Update the scraper:**
   ```javascript
   const headers = getZeptoHeaders({
     cookies: 'your_cookies_here',
     csrfSecret: 'extract_from_cookies',
     xsrfToken: 'extract_from_cookies',
   });
   ```

## Testing

The scraper should now work with the basic headers. If you get errors:

1. **403 Forbidden**: Add cookies
2. **401 Unauthorized**: Add CSRF tokens and cookies
3. **400 Bad Request**: Check if store_id is needed for your location

## Files Updated

- ✅ `server.js` - Updated to use header config
- ✅ `zepto-headers-config.js` - New file with all headers
- ✅ Headers extracted from cURL command

The scraper is ready to test!

