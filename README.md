# Fast E-commerce Product Compare

A modern product comparison website for quick delivery platforms like Zepto, Swiggy Instamart, BigBasket, and Blinkit.

## Quick Start

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python server.py
```

**Terminal 2 - Frontend:**
```bash
npm install
npm run dev
```

Open: `http://localhost:5173/`

## Features

- ⚡ Compare products from 8+ quick delivery platforms
- 📍 Location-based pricing and availability  
- ⏱️ Delivery time comparison (10-30 min focus)
- 💰 Price comparison with best deal highlighting
- 🎯 Advanced filtering by platform, price, delivery time, ratings

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: Python Flask + Web Scraping
- **UI**: shadcn/ui components + Lucide icons

## Project Structure

```
src/
├── components/          # React components
├── services/           # API and business logic
├── types/             # TypeScript definitions
└── data/              # Platform configurations

backend/
├── server.py          # Flask API server
├── requirements.txt   # Python dependencies
└── zepto_headers_config.py
```

## Supported Platforms

Zepto • Swiggy Instamart • BigBasket • Blinkit • Dunzo • Demart Ready • Flipkart Minutes • Amazon Prime Now


- Location finding for all the platform
- Pass the location page for searching and scraping
- Check the scraping results output platform based json
- Soritng name matching give output combine json
- compare display on window
- Architecture can be async as it gets the data algorithm should start searching and as it gets the pairs in platform start displaying it on website
- Have to give the merging for quantities too so the search should decrease accross the platforms 

Task - 

UI -
- Changes acc. to data remove the extra part
Compare 
- Price comparing
Frontend
- Change in UI for same price
Scraping
- Every search saving and flaging not to save
- Cap on scrapping product


Testing - 
- Similarity matching for name 
- test the price matching in algorithm after name
- Test the dataset generation and flagging
- Test the compare 