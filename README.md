# Fast E-commerce Product Compare

A modern product comparison website for quick delivery platforms like Zepto, Swiggy Instamart, BigBasket, and Blinkit.

## Quick Start

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
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
├── app.py             # Flask API server
├── requirements.txt   # Python dependencies
└── zepto_headers_config.py
```

## Supported Platforms

Zepto • Swiggy Instamart • BigBasket • Blinkit • Dunzo • Demart Ready • Flipkart Minutes • Amazon Prime Now

Architecture
- Location finding for all the platform
- Pass the location page for searching and scraping
- Check the scraping results output platform based json
- Soritng name matching give output combine json
- compare display on window
- Architecture can be async as it gets the data algorithm should start searching and as it gets the pairs in platform start displaying it on website
- Have to give the merging for quantities too so the search should decrease accross the platforms 

Task - 

UI -
- Exposing location API key, have to hide it    
- Changes acc. to data remove the extra part
- Remove the detect my location in initial loading
- Make UI better
- Change in UI for same price

Compare 
- Price comparing
- Filter should only run the compare again not to scrape again 
- Internally it is counting twice
- Check the similarity score strict, Aashriwad organic atta 

Scraping
- Image scraping methodology
- Scraping Image for product all the platformm because of product might not be present in all the platform
- Remove the location hardcoded Mumbai
- scrolling in instamart and integrate instamart

GCP
- make the server.log active for GCP
- zepto on GCP not working

Testing - 
- Similarity matching for name 
- test the price matching in algorithm after name
- Test the dataset generation and flagging
- Test the compare 
- Every search saving and flaging not to save
- Cap on scrapping product
- Filtering panel testing
- Can give the automation for giving vivid product and auto assess the results from compare.json
- Common item list - 
        Milk
        Curds / Dahi
        Atta / Flour
        Cooking Oil
        Dosa Batter
        Vegetable & Fruits
        Potato Chips
        Soft Drinks / Cold Beverages
        Eggs
        Bread / Bakery
        Personal Care (soap, shampoo)
        Toiletries
        Condoms / Wellness Products
        Biscuits / Namkeen
        Pet Food
        Ice Cubes & Frozen Items
        Chocolates
        Household Essentials (detergent, cleaners)

- Change the UI.
- Filter should not be blocker it should be responsive 
- Change the theme and colour of the page
    - Should look professional and deployed website not a demo website 
    - Make it lively website
- Remove the rating from filter
- Remove review and highest rated from the order
- Frontend needs to sort the product according to relevance

- Change the print of other modules.
- Check for log saving make a run logs and save it.
- Merge the matching branch to UI and then change the UI, for filter to be secondary and not primary


- UI shows kg for water too
- While merging make sure app.py and scraping scripts are fine 
- Logging and SS feature
- Harsh setup 

- Compare is happening between different kg's only problem with blinkit platform quantity mismatch

- Reduce the search time for scraping