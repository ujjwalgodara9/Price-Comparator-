# Architecture: Sub-20s Price Comparison App

## Research Findings

### Why the Current Approach is Slow (60-90s+)

- Each Playwright scraper launches a full browser, navigates, sets location, searches, scrolls, extracts — takes **15-30s per platform**
- Even with `ThreadPoolExecutor` parallelism, the slowest scraper bottlenecks everything
- CSS selectors are fragile — platforms change class names frequently, breaking scrapers
- DMart's direct REST API returned 0 results (storeId likely stale)

### How Comparify Does It Fast (~5-10s)

- They do **NOT** scrape in real-time on every request
- They use **pre-indexed product catalogs** + **periodic background scraping**
- Their API returns structured data instantly from their own database
- Real-time scraping only happens for price/availability refresh, not product discovery

### Platform API Availability

| Platform | Direct API? | Auth Required? | Notes |
|----------|------------|----------------|-------|
| Zepto | Yes (GraphQL) | Session token | Needs valid location cookie |
| Blinkit | Yes (REST) | Minimal | Location via lat/lng params |
| DMart | Yes (REST) | StoreId header | API exists but storeId mapping is tricky |
| BigBasket | Yes (REST) | Heavy bot detection | Firefox fingerprint needed |
| Instamart | Yes (Swiggy API) | Auth token | Swiggy's internal API, heavily guarded |

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND (React)                  │
│  Search → API Call → Display Results                 │
│  Target: Instant display from cache, live refresh    │
└──────────────────────┬──────────────────────────────┘
                       │ POST /api/search
                       ▼
┌─────────────────────────────────────────────────────┐
│              API GATEWAY (FastAPI/Flask)              │
│                                                      │
│  1. Check Redis cache (city+query key)               │
│  2. If HIT → return cached results (<1s)             │
│  3. If MISS → trigger parallel platform fetchers     │
│  4. Stream results as they arrive (SSE/WebSocket)    │
└──────┬──────┬──────┬──────┬──────┬──────────────────┘
       │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────────┐
│Zepto ││Blink-││DMart ││Big   ││Instamart │
│Fetch ││it    ││Fetch ││Basket││Fetcher   │
│er    ││Fetch ││er    ││Fetch ││          │
│      ││er    ││      ││er    ││          │
└──┬───┘└──┬───┘└──┬───┘└──┬───┘└────┬─────┘
   │       │       │       │         │
   ▼       ▼       ▼       ▼         ▼
┌─────────────────────────────────────────────────────┐
│           PLATFORM ADAPTER LAYER                     │
│                                                      │
│  Strategy per platform (ordered by speed):           │
│  1. Direct REST/GraphQL API call (fastest, <3s)      │
│  2. Mobile API reverse-engineered (fast, <5s)        │
│  3. Lightweight HTTP scrape (medium, <10s)           │
│  4. Playwright headless (last resort, 15-30s)        │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│              COMPARISON ENGINE                        │
│                                                      │
│  - Fuzzy name matching (SequenceMatcher + TF-IDF)    │
│  - Quantity normalization (500g = 0.5kg)             │
│  - Brand extraction & matching                       │
│  - Confidence scoring per match                      │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│              CACHE + STORAGE                         │
│                                                      │
│  Redis: query+city → results (TTL: 10-30 min)       │
│  PostgreSQL: product catalog, price history          │
│  Background jobs: refresh popular queries hourly     │
└─────────────────────────────────────────────────────┘
```

---

## Three-Tier Speed Strategy

### Tier 1: Direct API Calls (2-5s per platform)

The **game-changer**. Instead of Playwright, reverse-engineer each platform's internal API:

```python
# Example: What Blinkit's mobile app actually calls
async def fetch_blinkit(query: str, lat: float, lng: float):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://blinkit.com/v6/search/products",
            params={"q": query, "lat": lat, "lng": lng},
            headers={"User-Agent": "Blinkit/4.x", "app_version": "4.x.x"}
        )
        return normalize_blinkit(resp.json())
```

### Tier 2: Cached Results (<1s)

```python
# Redis cache with city+query granularity
cache_key = f"compare:{city}:{normalize(query)}"
cached = redis.get(cache_key)
if cached:
    return json.loads(cached)  # <1s response

# After fresh fetch, cache for 15 min
redis.setex(cache_key, 900, json.dumps(results))
```

### Tier 3: Playwright Fallback (15-30s, only when APIs break)

Keep existing scrapers as fallback, but never as primary.

---

## Progressive Loading (UX for Perceived Speed)

```
Timeline:
0s     → Show skeleton/loading UI
2-3s   → First platform results arrive → show immediately
4-5s   → Second platform → merge & show
5-8s   → All platforms done → final comparison
```

Use **Server-Sent Events (SSE)** to stream results as each platform responds:

```python
@app.route('/api/search/stream')
def search_stream():
    def generate():
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch, p): p for p in platforms}
            for future in as_completed(futures):
                platform = futures[future]
                result = future.result()
                yield f"data: {json.dumps({'platform': platform, 'products': result})}\n\n"
    return Response(generate(), mimetype='text/event-stream')
```

---

## Speed Comparison

| Component | Current | Proposed | Speed Gain |
|---|---|---|---|
| Data fetching | Playwright (15-30s) | Direct API (2-5s) | **6-10x** |
| Parallelism | ThreadPool | `asyncio` + `httpx` | **2x** |
| Caching | None | Redis (15min TTL) | **Instant repeat** |
| Result delivery | Wait for all | SSE streaming | **Perceived 3s** |
| Comparison | Post-fetch sync | Async as results arrive | **Overlapped** |
| Fallback | None | Playwright if API fails | **Reliability** |

**Realistic timeline: 3-8s for fresh queries, <1s for cached.**

---

## How to Find Platform APIs

### Step 1: Mobile App Traffic Interception

```
Tools: mitmproxy + Android emulator (or rooted device)

1. Install mitmproxy on your machine
2. Set up Android emulator (Android Studio) or use physical phone
3. Install platform apps (Zepto, Blinkit, BigBasket, Instamart)
4. Configure proxy → mitmproxy
5. Search for products → capture ALL API calls
6. Document: URL, method, headers, request body, response format
```

This is how Comparify figured out the APIs. Every request the app makes goes through your proxy.

### Step 2: Browser DevTools Network Tab

```
1. Open each platform website in Chrome
2. Open DevTools → Network tab → XHR/Fetch filter
3. Search for a product
4. Look for JSON API responses (not HTML)
5. Right-click → Copy as cURL → test in terminal
```

### Step 3: What to Capture Per Platform

| Capture This | Why |
|---|---|
| Search endpoint URL | Core API call |
| Required headers | Auth tokens, device IDs |
| Location mechanism | How lat/lng maps to store/warehouse |
| Response schema | Product name, price, image, quantity format |
| Rate limits | How aggressive you can be |
| Token refresh flow | How to maintain valid session |

---

## Async Adapter Pattern

For each platform, create a lightweight `httpx`-based fetcher:

```python
# backend/adapters/zepto_api.py
import httpx

class ZeptoAdapter:
    BASE = "https://api.zeptonow.com"  # discover via interception

    async def search(self, query: str, lat: float, lng: float) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.BASE}/search", json={
                "query": query,
                "lat": lat, "lng": lng
            }, headers=self._get_headers())
            return self._normalize(resp.json())

    def _normalize(self, raw: dict) -> list[dict]:
        return [{"name": p["name"], "price": p["mrp"], ...} for p in raw["products"]]
```

---

## Immediate Action Items

1. **Set up mitmproxy** — intercept Zepto and Blinkit mobile app traffic (easiest targets)
2. **Use Chrome DevTools** — capture XHR calls on each platform's website during search
3. **Document every API endpoint** in a structured format
4. **Build async adapters** with `httpx` for each discovered API
5. **Add Redis caching** layer
6. **Implement SSE streaming** for progressive result loading
7. **Keep Playwright scrapers** as fallback only
