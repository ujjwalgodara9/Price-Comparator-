# Groease — Product Proposal & Technical Architecture
**Confidential | Version 1.0 | February 2026**

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Problem & Solution](#2-problem--solution)
3. [What's Already Built (Prototype)](#3-whats-already-built-prototype)
4. [Technical Architecture — Three Approaches](#4-technical-architecture--three-approaches)
5. [Pricing Breakdown](#5-pricing-breakdown)
6. [Timeline](#6-timeline)
7. [Business Impact](#7-business-impact)
8. [Recommendation](#8-recommendation)

---

## 1. Executive Summary

Groease is a cross-platform quick-commerce aggregator that lets users compare product prices, stock availability, and delivery timelines across Zepto, Blinkit, Swiggy Instamart, BigBasket Now, D-Mart, and Amazon Fresh — all within a single interface.

A working prototype has already been built and demonstrated. It covers the mobile app (iOS + Android via Expo), web frontend, Flask backend, and live product scraping from 4 platforms. This document outlines the path from prototype to production across three technical approaches, with pricing and timelines for each.

**Deliverables across all versions:**
- Mobile app (iOS `.ipa` + Android `.apk`)
- Web frontend (responsive)
- Backend API
- Location-aware product comparison
- Redirect to platform via deep link

---

## 2. Problem & Solution

### Problem
Quick-commerce users today:
- Switch between 4–6 apps manually to compare prices
- Cannot verify real-time stock before clicking
- Miss better deals and offers on other platforms
- Have no single place to track their savings

### Solution
Groease centralises this into one search — show the user what each platform charges for the same product, which has it in stock, and how fast it can be delivered. User taps, gets redirected to the right platform. Done.

---

## 3. What's Already Built (Prototype)

The following has been built and is functional:

| Component | Status | Details |
|-----------|--------|---------|
| React Native Mobile App (Expo) | ✅ Working | iOS + Android, gradient UI, location-aware |
| Web Frontend | ✅ Working | Product comparison, filter/sort |
| Flask Backend API | ✅ Working | Parallel platform scraping, REST API |
| Zepto Scraper | ✅ Working | GPS-aware, 40–60 products per search |
| Blinkit Scraper | ✅ Working | Location-aware, consistent results |
| BigBasket Scraper | ⚠️ Partial | Loads but CSS selectors need refresh |
| D-Mart Scraper | ⚠️ Partial | Location serviceability check working |
| Geoapify Location | ✅ Working | Autocomplete + reverse geocode |
| Product Matching | ✅ Working | Cross-platform name matching algorithm |
| Deep Link Redirect | ✅ Working | Tap → opens platform app/web |

**Current Latency:** 30–60 seconds per search (live Playwright scraping)
**Platforms Demonstrated:** Zepto + Blinkit (cross-platform comparison working end-to-end)

---

## 4. Technical Architecture — Three Approaches

---

### Approach A — Scraping (Current Prototype, Productionised)

**What it is:** Live browser automation (Playwright/headless Chromium) that opens each platform in the background, searches for the product, extracts results, and returns them. This is what is currently built.

**How it works:**
```
User searches "Amul Milk"
        ↓
Backend launches 4 parallel Playwright browsers
        ↓
Each browser: open platform → set location → search → extract products
        ↓
Results merged, matched, ranked
        ↓
Response returned to app (30–60 seconds)
```

**Platforms supported:** Zepto, Blinkit, BigBasket, D-Mart, Swiggy Instamart
**Data freshness:** Real-time (live at time of search)
**Latency:** 30–60 seconds

**Pros:**
- Already built and working
- True real-time prices
- No platform agreements needed
- Covers all platforms

**Cons:**
- High latency (30–60s) — poor UX
- Fragile: platforms change HTML periodically → scrapers break
- Requires ongoing maintenance when selectors change
- Legal grey area (violates ToS of most platforms)
- High server costs (need powerful VMs to run headless browsers)

**Infrastructure needed:**
- 2× vCPU, 4GB RAM minimum server (AWS EC2 `t3.medium` ~$35/month)
- Can serve ~30–50 concurrent searches

---

### Approach B — Scheduled Cache + Scraping (Recommended for MVP)

**What it is:** A backend scheduler pre-scrapes popular products for every major city every 30 minutes. User searches hit a cache instead of triggering live scraping. Latency drops from 60 seconds to under 2 seconds.

**How it works:**
```
Scheduler (runs every 30 min)
        ↓
Scrapes top 500 search terms × 10 cities
        ↓
Stores results in database (PostgreSQL/Redis)
        ↓
─────────────────────────────────
User searches "Amul Milk" in Delhi
        ↓
Cache hit → returns results in < 2 seconds
        ↓
If cache miss → trigger live scrape in background
        → Show "Fetching live prices..." (5–10s max)
```

**Data freshness:** 30 minutes (shown to user as "Updated 12 min ago")
**Latency:** < 2 seconds (cached) / 5–10 seconds (cache miss)

**Additional components to build vs Approach A:**
- APScheduler / Celery scheduler running scrapes every 30 minutes
- PostgreSQL or Redis for product cache
- Top search term dictionary (curated list of popular grocery searches)
- "Last updated" timestamp shown in UI
- Cache miss fallback (triggers background live scrape)
- Price history table (enables price drop alerts later)

**Pros:**
- Fast UX (2 second responses)
- Covers all platforms
- No API agreements needed
- Enables price history, drop alerts, trend graphs
- Foundation for all features in the requirement document

**Cons:**
- Prices may be 30 minutes old (acceptable for grocery)
- Scrapers still need maintenance when platforms update HTML
- Higher infrastructure cost (scheduler + DB)
- Legal grey area still applies

**Infrastructure needed:**
- 4× vCPU, 8GB RAM server (AWS EC2 `t3.xlarge` ~$120/month)
- PostgreSQL database (~$20/month managed RDS)
- Redis for hot cache (~$15/month)
- Total: ~$155/month

---

### Approach C — Platform API Partnerships (Full Product Vision)

**What it is:** Direct API integrations with platforms via their affiliate or partner programs. Platforms provide official APIs that return product data in milliseconds.

**How it works:**
```
User searches "Amul Milk"
        ↓
Backend calls 4 platform APIs in parallel (< 500ms each)
        ↓
Results merged and returned in < 1 second
```

**Data freshness:** Real-time (live inventory)
**Latency:** < 1 second

**API availability (as of 2026):**
| Platform | API Status | Path |
|----------|-----------|------|
| Blinkit | Partner API (via Zomato Ads) | Partnership required |
| Zepto | No public API | Internal API (grey area) or partnership |
| BigBasket | BB Affiliate API (limited) | Apply at affiliate.bigbasket.com |
| Swiggy Instamart | No public API | Partnership or Swiggy partner program |
| D-Mart | No API | Scraping only option currently |
| Amazon Fresh | Product Advertising API (PA-API) | AWS account + approval |

**What needs to be built vs Approach B:**
- API client integrations per platform (replace scrapers)
- OAuth / API key management
- Rate limiting and quota management
- Fallback to scraping for platforms without APIs

**Reality check:** Getting API access from Blinkit, Zepto, Swiggy Instamart requires a formal partnership/business agreement. This takes 1–3 months of business development, not just engineering. Platforms are protective of their data.

**Pros:**
- Sub-second latency
- Legal, ToS-compliant
- Reliable (no scraper breakage)
- Real-time stock, pricing, offers via official data

**Cons:**
- Requires business agreements (time-consuming)
- Some platforms have no API
- May require revenue sharing or minimum transaction volume
- D-Mart will still need scraping

---

## 5. Pricing Breakdown

> All prices are for end-to-end delivery: mobile app (iOS + Android), web frontend, backend, deployment setup, and documentation. Quoted for a 2-year experienced engineer.

---

### Version A — Prototype to Production (Scraping)
*What you have now, production-hardened*

| Item | Details |
|------|---------|
| Scope | Fix all scrapers, production deploy, app store submission |
| Platforms | Zepto, Blinkit, BigBasket, D-Mart |
| Latency | 30–60 seconds |
| Includes | Mobile app (iOS + Android), Web, Backend, 1 month post-launch support |

| Client Type | Price |
|-------------|-------|
| Indian startup/SME | ₹1,50,000 – ₹2,50,000 |
| International | $2,500 – $4,500 |

**Monthly maintenance** (scraper upkeep when platforms change): ₹10,000–15,000/month

---

### Version B — Cached Scraping (Recommended)
*Production-ready, fast UX, full feature set*

| Item | Details |
|------|---------|
| Scope | Scheduler, cache layer, all scrapers, improved UI, alerts system |
| Platforms | Zepto, Blinkit, BigBasket, D-Mart, Swiggy Instamart |
| Latency | < 2 seconds (cached) |
| Includes | Mobile app, Web, Backend, Scheduler, DB, 2 months post-launch support |
| Features | Savings dashboard, price drop alerts, offer aggregation |

| Client Type | Price |
|-------------|-------|
| Indian startup/SME | ₹3,50,000 – ₹6,00,000 |
| International | $6,000 – $10,000 |

**Monthly infrastructure + maintenance**: ₹20,000–35,000/month
(Server: ₹12,000 + DB: ₹2,000 + Scraper maintenance: ₹10,000–20,000)

---

### Version C — Full API Partnerships
*Enterprise-grade, legal, sub-second*

| Item | Details |
|------|---------|
| Scope | API integrations, partnership contracts (client-side BD), full feature set |
| Platforms | Blinkit, BigBasket, Amazon Fresh (API) + Zepto/D-Mart (scraping fallback) |
| Latency | < 1 second |
| Includes | Everything in Version B + API clients + auth management |

| Client Type | Price |
|-------------|-------|
| Indian startup/SME | ₹8,00,000 – ₹15,00,000 |
| International | $12,000 – $20,000 |

**Note:** Partnership BD time (getting API access approved) is on the client. Engineering starts in parallel.

**Monthly infrastructure**: ₹15,000–25,000/month (lower infra than B, no scheduler costs)

---

## 6. Timeline

### Version A — Scraping (Production)

| Week | Deliverable |
|------|-------------|
| Week 1 | Fix all scrapers (BigBasket, D-Mart), harden Zepto + Blinkit |
| Week 2 | Production deploy, error handling, logging, monitoring |
| Week 3 | App Store submission (iOS + Google Play), web deployment |
| Week 4 | Bug fixes, UAT, handover |

**Total: 4 weeks**

---

### Version B — Cached Scraping (Recommended)

| Week | Deliverable |
|------|-------------|
| Week 1–2 | All scrapers fixed and stable |
| Week 3 | Scheduler + cache layer (Redis/PostgreSQL) |
| Week 4 | UI: Savings dashboard, "Updated X mins ago" timestamps |
| Week 5 | Price drop + restock alerts (push notifications) |
| Week 6 | Offer aggregation, deal highlighting |
| Week 7 | Testing, performance tuning, staging environment |
| Week 8 | App store submission, production deployment, handover |

**Total: 8 weeks**

---

### Version C — API Partnerships

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | 3 weeks | Version B completed (base layer) |
| Phase 2 | 4–6 weeks | API client integrations (dependent on partner approval timeline) |
| Phase 3 | 2 weeks | Migration from scraping to API, testing |
| Phase 4 | 1 week | Production launch |

**Total: 10–12 weeks** (assuming API approvals are in parallel)

> **Note:** API partnership approvals from Blinkit/Zepto/Swiggy typically take 4–8 weeks independently. Engineering and BD should run in parallel.

---

## 7. Business Impact

### Market Opportunity
- India quick-commerce market: **$5.5 billion (2024)**, growing at 40% YoY
- Average Indian household places 8–12 quick-commerce orders per month
- Price difference for the same product across platforms: **15–35%** (verified in our prototype)
- No existing app offers cross-platform quick-commerce comparison in India

### User Value
| Metric | Estimate |
|--------|----------|
| Average savings per search | ₹15–40 per order |
| Average orders per user per month | 10 |
| Monthly savings per user | ₹150–400 |
| Annual savings per user | ₹1,800–4,800 |

### Monetisation Paths

**1. Affiliate Commission (Primary)**
Platforms pay 1–3% commission for orders referred via affiliate links. At 10,000 monthly orders of average ₹400 each: **₹40,000–1,20,000/month**.

**2. Featured Placement / Sponsored Results**
Platforms pay for highlighted placement in comparison results (similar to how Google Shopping works). Scalable with user base.

**3. Subscription — "Groease Pro"**
Premium users get price drop alerts, spending analytics, and saved lists. ₹49–99/month subscription.

**4. Data Insights (B2B)**
Anonymised pricing trend data sold to FMCG brands, market research firms, and retail analysts.

### Competitive Moat
- **First mover:** No direct competitor exists in India for quick-commerce price comparison
- **Data flywheel:** More searches → better cache coverage → faster responses → more users
- **Switching cost:** Savings dashboard and search history create retention

---

## 8. Recommendation

### For a Demo / Investor Pitch
**Version A** is sufficient. The prototype already works. Invest ₹50,000–75,000 in stabilising scrapers and deploying it properly. Use it to validate demand and raise funding.

### For a Paying Client / MVP Launch
**Version B** is the right choice. It solves the latency problem (the #1 UX blocker), enables the full feature set from the requirement document, and is deliverable in 8 weeks. This is the version to quote and build.

### For a Funded Product Company
**Version B → Version C migration path.** Launch with Version B, prove traction, then negotiate platform partnerships from a position of existing user data. Platforms are more likely to provide API access to an app with 10,000 active users than to a cold approach.

---

## Appendix: Technology Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Mobile | React Native (Expo) | Single codebase → iOS + Android |
| Web | React / Next.js | SEO-friendly, same components as mobile |
| Backend | Python / Flask | Playwright integration, fast iteration |
| Scraping | Playwright (Chromium) | Handles JS-heavy SPAs like Zepto |
| Scheduler | APScheduler / Celery | Background scraping for cache approach |
| Cache / DB | Redis + PostgreSQL | Fast reads, persistent storage |
| Location | Geoapify API | Autocomplete + reverse geocode |
| Hosting | AWS EC2 / Render | Scalable, cost-effective |
| App Store | Expo EAS Build | Automated iOS + Android build pipeline |
| Push Alerts | Expo Push Notifications | Cross-platform, free tier available |

---

*Document prepared by: [Your Name]*
*Contact: [Your Email / LinkedIn]*
*Prototype available for live demo on request*
