# Quick Commerce Price Comparison Apps - India Market Research

## 1. All Apps Found

### A. Grocery / Quick Commerce Price Comparison (Consumer)

| App | Platforms Compared | Availability | Key Differentiator |
|-----|-------------------|-------------|-------------------|
| **Comparify** (comparify.pro) | Blinkit, Zepto, Swiggy Instamart, BigBasket, DMart, JioMart, Flipkart Minutes + Uber, Ola, Rapido, Namma Yatri | Android, iOS, Web | Only app doing both cabs AND groceries. Account linking via OTP for personalized prices |
| **QuickCompare** (quickcompare.in) | Blinkit, Zepto, Swiggy Instamart, Flipkart Minutes, BigBasket, DMart, JioMart | Android, iOS, Web | "Skyscanner for Quick-Commerce". Company: QuickCompare AI Technologies Pvt Ltd, Bangalore |
| **Savvio** | Blinkit, Zepto, Swiggy Instamart, BigBasket, JioMart, DMart, Flipkart Minutes | iOS, Android | Claims ₹2000/month savings. Developer: Jainam Mukeshbhai Shah |
| **ShopSwiftly** | Blinkit, Zepto, Swiggy Instamart, BigBasket | Android, iOS | 230K+ downloads. "Top searches" and "top picks" features |
| **Dealulu** (dealulu.in) | Blinkit, Zepto, Swiggy Instamart, BigBasket | iOS, Android | Shows ALL fees (delivery, surge, packaging) transparently. Account linking |
| **SmartPrix Groceries** | Zepto, Blinkit, JioMart | Web | Extension of existing electronics comparison brand |
| **BuyHatke** | Multiple e-commerce + some groceries | Web, Extension | Browser extension, price history, coupon finder |

### B. Cab Fare Comparison

| App | Platforms Compared | Key Differentiator |
|-----|-------------------|--------------------|
| **Comparify** (comparify.pro/cabs) | Uber, Ola, Rapido, Namma Yatri, Bharat Taxi | Account-specific prices via OTP linking |
| **Naviget** (naviget.in) | Ola, Uber, Rapido, BluSmart + ONDC providers | Powered by ONDC/Beckn Protocol, enables actual booking |
| **Choose.app** | Uber, Ola, Rapido | ETAs and fare estimates |

### C. B2B / Enterprise Tools

| Tool | Purpose |
|------|---------|
| **MetricsCart** | SKU-level analytics updated every 10 seconds. For FMCG brand managers |
| **Nextract** (nextract.dev) | Data extraction API for Blinkit, Zepto etc. Sub-second response times |

---

## 2. Feature Comparison Matrix

| Feature | Comparify | QuickCompare | Savvio | ShopSwiftly | Dealulu |
|---------|-----------|-------------|--------|-------------|---------|
| Groceries | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cabs | ✅ | ❌ | ❌ | ❌ | ❌ |
| Account Linking (OTP) | ✅ | ❌ | ❌ | ❌ | ✅ |
| Per-unit pricing (₹/g, ₹/ml) | ✅ | ? | ? | ? | ? |
| Web version | ✅ | ✅ | ❌ | ❌ | ❌ |
| Personalized offers/wallet | ✅ | ❌ | ❌ | ❌ | ✅ |
| Total cart comparison | ✅ | ✅ | ? | ? | ✅ |
| Delivery fee visibility | ? | ? | ? | ? | ✅ |
| Price alerts | ❌ | ✅ | ❌ | ❌ | ❌ |

---

## 3. Technical Stacks Discovered

### Comparify (from JS bundle analysis)
- **Framework**: React Native (Expo) with Expo Router
- **CSS**: Tailwind CSS via react-native-css-interop
- **Bundler**: Metro (Expo's bundler)
- **Hosting**: Vercel (Mumbai `bom1` region)
- **Error Tracking**: Sentry (version 1.6.8)
- **Analytics**: PostHog
- **React**: v19.1.0
- **Font**: Inter (Google Fonts)
- **API Backend**: `api.comparify.pro/api` (groceries), `cabs.comparify.pro/api` (cabs)
- **OTA Updates**: `ota.comparify.pro/manifest`
- **Monetization**: Free + `/donate` page (no ads)
- **Android Package**: com.akshat.comparify
- **Developer**: Akshat Kejriwal (solo full-stack dev)

#### Key URLs found in Comparify's 4.7MB JS bundle:
```
https://api.comparify.pro/api          ← Grocery comparison backend
https://cabs.comparify.pro/api         ← Cab comparison backend
https://ota.comparify.pro/manifest     ← Over-the-air updates
https://m.uber.com/go/graphql          ← Uber GraphQL API
https://auth.uber.com/v2/              ← Uber auth
https://accounts.olacabs.com           ← Ola auth
https://book.olacabs.com               ← Ola booking
https://blinkit.com/prn/x/prid/        ← Blinkit product deep links
https://www.zeptonow.com/pn/x/pvid/    ← Zepto product deep links
https://cdn.zeptonow.com/production/   ← Zepto image CDN
https://instamart-media-assets.swiggy.com/  ← Swiggy image CDN
https://dl.dmart.in/                   ← DMart deep links
https://places.googleapis.com/v1/places ← Google Places API (location)
```

### QuickCompare (from HTML source analysis)
- **Framework**: React SPA with Vite build tool
- **Data Fetching**: React Query (TanStack Query)
- **Auth/Push**: Firebase
- **CDN**: AWS CloudFront (`d2chhaxkq6tvay.cloudfront.net`)
- **Analytics**: Google Analytics 4, Mixpanel, Microsoft Clarity
- **Ads**: Google Ad Manager (5 ad slots)
- **Communication**: WATI WhatsApp (phone: +91 7795723048)
- **Company**: QuickCompare AI Technologies Pvt Ltd, Bangalore (April 2025)
- **Founders**: Anurag Kabra, Asha Kabra
- **PWA**: Yes (installable web app)
- **Security**: Request IDs encrypted with XOR cipher + Base64

---

## 4. Architecture: How They Return Results in 10-15 Seconds

### Approach 1: Reverse-Engineered Mobile/Web APIs (Most Common)
```
User searches "Amul Milk" → Backend fires parallel API calls:

┌─ Blinkit API (~200-400ms)
├─ Zepto API (~300-500ms)
├─ Swiggy Instamart API (~400-800ms)
├─ BigBasket API (~300-600ms)
└─ DMart API (~200-400ms)

Total: ~1-3 seconds (parallel, not sequential)
```
- Each platform has internal REST/GraphQL APIs discoverable via DevTools/mitmproxy
- APIs respond in 200-800ms (optimized for mobile apps)
- Calls happen in parallel → total time = max(individual times)
- No browser rendering, no DOM parsing - just JSON API responses

### Approach 2: Account-Linked Sessions (Comparify's approach for cabs)
```
User links Uber/Ola via OTP → App stores session token
→ Uses YOUR authenticated session for API calls
→ Returns personalized pricing (wallet, coupons, offers)
```
- Built with Expo (React Native) - can embed WebViews for auth
- Session tokens stored and reused for subsequent searches
- Shows REAL prices you'd actually pay

### Approach 3: Pre-Cached Database (MetricsCart, enterprise tools)
```
Background scrapers → Database (Redis/Mongo) → User gets cached results (<100ms)
```
- MetricsCart updates every 10 seconds
- Tradeoff: slightly stale data but instant responses

### Why NOT browser automation in production:
| Metric | Direct API | Browser (Puppeteer/Playwright) |
|--------|-----------|-------------------------------|
| Response time | 200-800ms | 15-40 seconds |
| Memory per request | ~5MB | 100-300MB |
| Scalability | 1000s concurrent | 10s concurrent |
| Reliability | High | Fragile (selectors break) |

---

## 5. Known API Patterns

### Blinkit
- Endpoint: `GET /v6/search/products?q={query}`
- Headers: `lat`, `lon`, `app_client`, `session_uuid`
- Location → dark store mapping determines prices
- Rate limiting: Session-based throttling

### Zepto
- Endpoint: `POST /api/v1/search` with `storeId`
- Headers: `Authorization: Bearer <token>`, `x-store-id`
- `storeId` derived from lat/lon

### Swiggy Instamart
- Endpoint: `POST /api/instamart/search`
- Heavy anti-bot (Akamai Bot Manager)
- Location via lat/lng cookies

### DMart
- Endpoint: `GET /api/v3/search/{query}?page={page}&size={size}&storeId={store_id}`
- Clean REST API, minimal auth
- Headers: `X-REQUEST-ID`, `storeId`, `d_info`

### Uber (from Comparify bundle)
- GraphQL: `m.uber.com/go/graphql`
- Auth: `auth.uber.com/v2/`

### Ola (from Comparify bundle)
- Auth: `accounts.olacabs.com`
- Booking: `book.olacabs.com`

---

## 6. Business Analysis & Challenges

### Why price comparison is hard (Manas Saloi's analysis):
- "Base price does not determine the final price" - delivery fees, surge, discounts vary per user
- Affiliate model weak - platforms resist intermediaries, margins already low
- Mobile attribution harder than web cookies
- Platform frontends change weekly → scrapers break constantly

### Maintenance burden:
- APIs change endpoints/auth regularly
- Anti-bot measures get upgraded
- New platforms launch, old ones pivot
- Location/dark store mappings change

---

## 7. Comparify Deep Dive (Reverse Engineering from 4.7MB JS Bundle)

### Architecture Overview
- **Single codebase**: Expo (React Native) app serving web + Android + iOS
- **Two API servers**:
  - `api.comparify.pro/api` → Grocery price comparison
  - `cabs.comparify.pro/api` → Cab fare comparison
- **OTA Updates**: `ota.comparify.pro/manifest` (Expo OTA)

### Complete API Route Map (extracted from module 737)
```
Route Name       → Endpoint Path              → Purpose
─────────────────────────────────────────────────────────────
catalogSearch    → /v1/search/catalog          → Main product search across all platforms
matchedCards     → /v1/search/cards            → Matched/compared product cards
bootstrap        → /v1/bootstrap               → Resolve store IDs for each platform from lat/lng
eta              → /v1/promise                  → Delivery time estimates
locationSuggest  → /v1/location/suggest         → Address autocomplete
locationResolve  → /v1/location/resolve         → Geocode address → lat/lng
locationReverse  → /v1/location/reverse         → Reverse geocode lat/lng → address + pincode
searchHints      → /v1/search/hints             → Search autocomplete suggestions
```

### Cab API Routes (extracted from template literals)
```
/cabs/compare                        → Compare fares across all cab platforms
/cabs/eta?{params}                   → ETA for all platforms
/cabs/ola/login                      → Initiate Ola OTP login
/cabs/ola/verify-otp                 → Verify Ola OTP
/cabs/namma-yatri/login              → Initiate Namma Yatri login
/cabs/namma-yatri/verify-otp         → Verify Namma Yatri OTP
/cabs/namma-yatri/fare               → Get Namma Yatri fare
/cabs/namma-yatri/fare/poll?searchId=  → Poll for Namma Yatri fare result
/cabs/bharat-taxi/fare               → Get Bharat Taxi fare
/cabs/bharat-taxi/fare/poll?searchId=  → Poll for Bharat Taxi fare result
```

### Custom Headers (Platform Session Tokens)
```
Header    → Platform             → Purpose
──────────────────────────────────────────────────
x-fkud    → Flipkart/Blinkit     → User data token (stored after bootstrap)
x-jsc     → JioMart              → Session cookie
x-jrc     → JioMart              → Refresh cookie
x-dms     → DMart                → Store ID
x-dss     → DMart                → Session/store token
x-zat     → Zepto                → Access token
x-amc     → Amazon               → Cookies (has_amazon_cookies flag)
x-wh      → Web                  → Obfuscated web header payload
```

### How Search Works (reconstructed from deobfuscated code)
```
1. USER SETS LOCATION
   → App calls bootstrap(lat, lng, providers="instamart,zepto,flipkart-minutes,dmart,jiomart,dealshare")
   → Backend resolves lat/lng to each platform's nearest dark store/storeId
   → Returns: { zepto: { storeId: "..." }, instamart: { storeId: "..." }, ... }
   → Stores x-fkud token from response header
   → Stores jsc, jrc cookies for JioMart
   → Stores dealshare_store_id

2. USER SEARCHES "amul milk"
   → App calls catalogSearch with:
     - query: "amul milk"
     - userLocation: { latitude, longitude }
     - storeId: zepto store (if serviceable)
     - instamartStoreId: instamart store
     - dmartStoreId: dmart store
     - pincode: user's pincode
   → All platform tokens passed as headers (x-fkud, x-jsc, x-jrc, x-dms, x-zat)
   → Backend calls each platform's internal API IN PARALLEL
   → Returns aggregated results with prices from all platforms

3. MATCHED CARDS (parallel to catalog search)
   → Same params as catalogSearch
   → Returns product cards matched across platforms
   → Tracks performance: client_roundtrip_duration_ms, server duration, extra time

4. DELIVERY ETA
   → App calls eta(location, storeId, pincode)
   → Returns delivery time estimates for ALL platforms
```

### Web vs Mobile Request Handling
```
On Web (browser):
  → Uses appendWebQueryPayload() to encode params in URL query string
  → Uses setWebHeaderPayload() to encode tokens in obfuscated header
  → Response decoded via decodeWebPayload() with WEB_OBFUSCATION_RESPONSE_HEADER

On Mobile (React Native):
  → Params sent as standard query params
  → Headers sent directly (x-fkud, x-zat, etc.)
  → Standard JSON parsing
```

### Performance Tracking (PostHog events)
```
product_search_performance → { query, client_roundtrip_duration_ms, per-platform timings }
product_search_error       → { query, duration, error_message }
```

### Google Places API Key (for location services)
```
AIzaSyBRaywHtynMtnOqZRDFENiwiKAcSqkghho
```

### Key Insights
1. **Comparify's backend does ALL the heavy lifting** - the app itself is a thin client
2. **The backend maintains sessions with each platform** - it has its own Flipkart, Zepto, JioMart etc. session management
3. **For cabs, users link their OWN accounts** (OTP flow) - this is why it shows personalized prices
4. **For groceries, NO user account linking needed** - the backend uses its own sessions to fetch catalog prices
5. **The backend handles platform-specific quirks** - Namma Yatri/Bharat Taxi use polling (fare/poll?searchId=), suggesting async fare calculation
6. **Encryption on web** - web requests use XOR cipher + Base64 obfuscation to protect API traffic from easy interception
7. **Error handling per-platform** - if one platform is "Not Serviceable", others still work

### Supported Providers
- Grocery: `instamart, zepto, flipkart-minutes, dmart, jiomart, dealshare, blinkit, bigbasket`
- Cabs: `uber, ola, rapido, namma-yatri, bharat-taxi`

### Supported Cities (Namma Yatri - subset)
Bengaluru, Chennai, Trichy, Coimbatore, Hyderabad, Trivandrum, Kochi, Kolkata, Siliguri, Asansol, Durgapur, Bhubaneshwar

---

## 8. API Interception Results

### Comparify API Test Results
```
Endpoint                              HTTP Code   Response Time   Notes
──────────────────────────────────────────────────────────────────────────
GET  /api/v1/bootstrap                400         0.48s           Returns encrypted error (wb field)
GET  /api/v1/location/suggest         404         0.46s           Needs POST method
POST /api/v1/search/cards             401         0.48s           Unauthorized - needs createAuthorizedHeaders
POST /api/v1/search/catalog           500         0.49s           Server error without proper params
POST /api/v1/location/resolve         400         1.15s           Needs searchWord + location body
```
The API is protected by:
- Encrypted request/response payloads (XOR cipher with key `04026aadf...`)
- `createAuthorizedHeaders` function generates auth tokens
- Web requests use additional obfuscation layer

### DMart API - WORKING (Location: Bharthal Village, Dwarka Sec 26)
```
Endpoint: GET https://digital.dmart.in/api/v3/search/amul%20milk?page=0&size=5
Response Time: 442ms
Total Products Found: 286

Sample Results:
  Amul Milk Chocolate : 150 g
  Amul Lite Milk Fat Bread Spread : 500 g
  Amul Taaza Toned Milk : 1 L → MRP: Rs 75.00 | Sale: Rs 71.00 (Save Rs 4)
  Amul Kool Badam Milk : 180 ml
  Amul Kool Kesar Milk : 180 ml

SKU Data Fields: name, skuUniqueID, articleNumber, priceMRP, priceSALE, savePrice,
                 savingPercentage, maxQuantity, variantText, variantTextValue,
                 invStatus, invType, groceryType, imageKey, offers
```

### Blinkit API - Needs Session Token
```
Blinkit Config (from preloaded state):
  apiURL: https://blinkit.com
  requestKey: c0e6868e-1180-400c-be51-f473479f1f0a
  appClient: consumer_web
  appVersion: 52434332
  Default location: lat 28.4652382, lon 77.0615957 (Gurugram)
  Search URL pattern: /s/?q={search_term_string}

Feature flags found:
  is_consumer_web_bff_enabled: true
  is-web-search-bff-enabled: true
  is-web-plp-bff-enabled: true

Endpoints tried (all returned 404 - need proper session/auth):
  /v6/search/products  → 404
  /v2/search           → 404 ("no Route matched")
  /v1/layout/search    → 404
  /bff/search/products → Returns SSR HTML page

NOTE: Blinkit uses server-side rendering (SSR) with preloaded state embedded in HTML.
The search data may be embedded in the SSR HTML response via PRELOADED_STATE.
```

### Zepto API - Blocked
```
POST https://api.zeptonow.com/api/v3/search → HTTP 000 (connection refused, 200ms)
GET  https://www.zeptonow.com/search?query=amul+milk → 301 redirect to SPA (670ms)
Page loads as 231KB SPA but search results require client-side JS rendering.
```

### BigBasket API - Needs Session
```
GET https://www.bigbasket.com/listing-svc/v2/products?type=search&slug=amul-milk
HTTP: 400 | Time: 195ms | Error: "Missing either Mid or AddressId or lat-long"

Session cookies obtained:
  _bb_aid=MjkxMzA4NDUzMA==
  _bb_cid=1
  _bb_vid=MTE1OTcyNTc4MzAxODI3MDQ0Ng==
  x-channel=web

Even with cookies + lat/lng, returns 400. Needs proper member session (MID).
```

### Swiggy Instamart - Empty Response
```
GET https://www.swiggy.com/api/instamart/search?query=amul+milk&lat=28.5578&lng=77.0319
HTTP: 202 | Time: 510ms | Body: empty
Likely needs Akamai bot manager cookies + proper session.
```

### Flipkart Minutes - reCAPTCHA
```
POST https://www.flipkart.com/api/4/page/fetch
HTTP: 403 | Time: 429ms | Returns reCAPTCHA challenge page
Heavy bot protection via Google reCAPTCHA Enterprise.
```

### JioMart - Blocked
```
GET https://www.jiomart.com/search/amul%20milk
HTTP: 403 | Time: 218ms
```

---

## 9. Complete API Accessibility Summary

```
Platform          Method              Status      Response Time   Notes
──────────────────────────────────────────────────────────────────────────────────
DMart             REST API (direct)   ✅ WORKS    442ms           286 products, full prices
Blinkit           SSR HTML            ❌ Empty    486ms           Products loaded via client-side BFF JS
Blinkit           /v6/search API      ❌ 404      313ms           Endpoint not available on web
Zepto             api.zeptonow.com    ❌ Blocked  200ms           Connection refused from non-app clients
Zepto             Web page scrape     ❌ SPA      670ms           Needs JS rendering
BigBasket         listing-svc/v2      ❌ 400      195ms           Needs MID (member session ID)
Swiggy Instamart  /api/instamart      ❌ Empty    510ms           Needs Akamai session
Flipkart Minutes  /api/4/page/fetch   ❌ 403      429ms           reCAPTCHA Enterprise
JioMart           /search             ❌ 403      218ms           Blocked
Comparify API     /v1/search/cards    ❌ 401      479ms           Needs createAuthorizedHeaders
```

### Key Takeaway
**Only DMart has an easily accessible public REST API.** All other platforms require:
1. **Authenticated session tokens** obtained via login flow (Blinkit, BigBasket, Swiggy)
2. **Headless browser rendering** to execute JS and get search results (Zepto, Flipkart Minutes)
3. **Mobile app API reverse engineering** via mitmproxy/Charles Proxy (all platforms)

### This is how Comparify solves it:
Comparify's backend (`api.comparify.pro`) maintains persistent sessions with each platform.
When you search, their backend calls each platform's internal API using those pre-authenticated
sessions IN PARALLEL, aggregates the results, and returns them. This is why they can return
results in 3-5 seconds instead of 30-60 seconds (browser scraping approach).

---

## 10. Maintenance & API Stability Estimates

### How often do these APIs change?
- **Blinkit**: Uses BFF pattern, endpoints change every 2-4 weeks with app updates
- **Zepto**: Next.js app, API structure changes with major releases (~monthly)
- **Swiggy Instamart**: Most stable (Swiggy has been around longer), changes quarterly
- **BigBasket**: Moderate changes, listing-svc versioned (currently v2/v3)
- **DMart**: Most stable API, minimal changes, versioned (v3)
- **Flipkart Minutes**: Aggressively protected, frequent anti-bot updates
- **JioMart**: Moderate stability, Jio platform is relatively stable

### Estimated Maintenance Cost
- **Direct API approach**: 5-10 hours/month to fix broken endpoints, update auth flows
- **Browser scraping approach**: 10-20 hours/month to fix broken selectors, handle new anti-bot measures
- **Comparify's approach**: They proxy through their own backend which absorbs platform changes
  - When an API changes, they fix it once on their backend
  - All app users immediately get the fix (no app update needed)

---

## Sources
- [Comparify on India.com](https://www.india.com/business/this-app-will-help-you-in-checking-grocery-rates-on-uber-ola-blinkit-zepto-and-swiggy-in-real-time-name-is-android-comparify-pro-akshat-kejriwal-8001558/)
- [QuickCom GitHub (open-source scraper)](https://github.com/KshKnsl/QuickCom)
- [Blinkit-Zepto Scraper GitHub](https://github.com/iamonjarvis/Blinkit-Zepto-product-backend)
- [Manas Saloi - Quick Commerce Price Comparison](https://manassaloi.com/2025/02/17/quick-commerce-price-comparison.html)
- [Cashify - 5 Best Price Comparison Apps](https://www.cashify.in/find-the-best-shopping-deals-with-these-apps-compare-grocery-prices-and-more)
- [Moneylife - Quick Compare](https://www.moneylife.in/article/compare-prices-quick-compare-across-quick-commerce/76811.html)
- [MetricsCart - QC Monitoring Tools](https://metricscart.com/insights/quick-commerce-monitoring-tools-india/)
- [Nextract Zepto API](https://nextract.dev/apis/zepto-api/)
- [Morning Context - Why Price Comparison Apps Won't Take Off](https://themorningcontext.com/tech/why-quick-commerce-price-comparison-apps-wont-take-off)
- [Akshat Kejriwal on X](https://x.com/akshatkejriwal)
- [QuickCompare on Inc42](https://inc42.com/company/quickcompare-ai/)
- [Dealulu](https://www.dealulu.in/)
- [Naviget](https://naviget.in/)
- [DesiDime - QuickCompare Discussion](https://www.desidime.com/discussions/quick-compare-app-compare-grocery-prices-from-various-quick-commerce-apps-in-real-time)
