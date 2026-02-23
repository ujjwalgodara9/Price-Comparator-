# Groease Mobile — React Native + Expo

This folder is a **fully self-contained** React Native + Expo app.
It uses the same Flask backend as the web app — the mobile app is just a client.

---

## React Native + Expo: Pros vs Cons (with Solutions)

### ✅ Pros

| Benefit | Detail |
|---|---|
| Code reuse | ~65% of your web logic reused: all TypeScript types, services, API layer, product sorting |
| Single codebase | One project → both iOS & Android |
| Expo Go | Test instantly on your real phone without Xcode/Android Studio |
| OTA Updates | Push bug fixes without App Store re-submission (via expo-updates) |
| Same React skills | Hooks, state, useEffect — identical mental model |
| Native GPS | `expo-location` gives better GPS than browser geolocation |
| Linking | Deep links, open platform URLs natively |

### ❌ Cons (and their Solutions)

| Con | Why it happens | Solution used in this project |
|---|---|---|
| Tailwind CSS doesn't work | Tailwind targets the DOM; RN has no DOM | `StyleSheet.create({})` — all styles rewritten in RN syntax |
| shadcn/ui doesn't work | Built on HTML/Radix which requires the DOM | Components rebuilt from scratch using RN primitives |
| `localStorage` doesn't exist | RN has no browser storage | `@react-native-async-storage/async-storage` (drop-in replacement) |
| `navigator.geolocation` is web-only | RN doesn't expose browser APIs | `expo-location` — same logic, different import |
| `<a href>` links don't exist | No HTML anchor tags | `Linking.openURL()` from `expo-linking` |
| `import.meta.env` doesn't work | Vite-specific; not available in Metro bundler | `src/config.ts` — change `API_BASE_URL` manually |
| Playwright runs on your backend — NOT the phone | Mobile can't run headless browsers | Not changed — the Flask backend handles all scraping, mobile is just a client |
| App Store review takes time | Apple reviews take 1–7 days | Plan ahead; submit early. Expo EAS Submit automates the process |
| Images need different import syntax | RN uses `require()` or network URIs | Product images are network URIs (from scraped data), logos add to `/assets/` |

---

## Project Structure

```
groease-mobile/
├── app/                        # Expo Router screens (file-based routing)
│   ├── _layout.tsx             # Navigation stack setup
│   ├── index.tsx               # Home screen (landing page)
│   └── results.tsx             # Search results screen
├── src/
│   ├── components/
│   │   ├── SearchBar.tsx       # RN version of web SearchBar
│   │   ├── LocationModal.tsx   # RN version of web LocationPopup
│   │   ├── ProductCard.tsx     # RN version of web ProductComparisonTable
│   │   ├── ProgressBar.tsx     # Animated progress bar
│   │   └── PlatformBadge.tsx   # Platform color badge
│   ├── services/
│   │   ├── api.ts              # Adapted from fastEcommerceAPI.ts
│   │   ├── productService.ts   # Adapted from productService.ts
│   │   ├── geoapifyService.ts  # Adapted from geoapifyService.ts
│   │   └── locationService.ts  # Adapted (uses expo-location instead of navigator)
│   ├── types/
│   │   └── product.ts          # COPIED directly from web (no changes)
│   ├── data/
│   │   └── platformData.ts     # Adapted (hex colors instead of Tailwind classes)
│   └── config.ts               # API_BASE_URL — edit this before running
├── app.json
├── babel.config.js
├── package.json
└── tsconfig.json
```

---

## Setup & Run

### Step 1: Install dependencies

```bash
cd groease-mobile
npm install
```

### Step 2: Set your backend URL

Open `src/config.ts` and change the IP to your machine's local network IP:

```bash
# Find your IP on Windows:
ipconfig
# Look for "IPv4 Address" under your WiFi adapter, e.g. 192.168.1.105

# Find your IP on Mac/Linux:
ifconfig | grep "inet "
```

Then update `src/config.ts`:
```ts
export const API_BASE_URL = 'http://192.168.1.105:8080'; // your actual IP
```

> **Important:** Your phone and PC must be on the **same WiFi network**.
> `localhost` will NOT work from a physical device.

### Step 3: Start your Flask backend

```bash
# In the main project folder (outside groease-mobile)
cd backend
python app.py
```

Make sure Flask is listening on `0.0.0.0:8080` (not just `127.0.0.1`):
```python
# In backend/app.py, the run call should be:
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Step 4: Install Expo Go on your phone

- iOS: Search "Expo Go" on the App Store
- Android: Search "Expo Go" on Play Store

### Step 5: Start the app

```bash
npm start
```

Scan the QR code with:
- **iOS**: Use the Camera app (it detects QR codes automatically)
- **Android**: Use the Expo Go app → "Scan QR Code"

---

## Building for App Store / Play Store

Use **EAS Build** (Expo Application Services):

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure build
eas build:configure

# Build for Android (.aab)
eas build --platform android

# Build for iOS (.ipa) — requires Apple Developer account ($99/year)
eas build --platform ios

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

---

## What's Reused from the Web Codebase

| Web File | Mobile File | Status |
|---|---|---|
| `src/types/product.ts` | `src/types/product.ts` | ✅ Copied directly |
| `src/data/platformData.ts` | `src/data/platformData.ts` | ✅ Adapted (colors only) |
| `src/services/fastEcommerceAPI.ts` | `src/services/api.ts` | ✅ Adapted (env var → config) |
| `src/services/productService.ts` | `src/services/productService.ts` | ✅ Adapted (import swap) |
| `src/services/geoapifyService.ts` | `src/services/geoapifyService.ts` | ✅ Adapted (env var → config) |
| `src/services/locationService.ts` | `src/services/locationService.ts` | ✅ Adapted (expo-location) |
| `src/components/SearchBar.tsx` | `src/components/SearchBar.tsx` | 🔄 Rewritten in RN |
| `src/components/LocationPopup.tsx` | `src/components/LocationModal.tsx` | 🔄 Rewritten in RN |
| `src/components/ProductComparisonTable.tsx` | `src/components/ProductCard.tsx` | 🔄 Rewritten in RN |
| `src/App.tsx` (landing + search state) | `app/index.tsx` | 🔄 Rewritten in RN |
| `src/App.tsx` (results state) | `app/results.tsx` | 🔄 Rewritten in RN |

Backend (`backend/` folder) — **unchanged, not included here, run separately.**
