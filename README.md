# Fast E-commerce Product Compare

A modern product comparison website that helps users compare prices and delivery times across fast e-commerce platforms like Zepto, Swiggy Instamart, BigBasket, Blinkit, and more.

## Features

- ⚡ **Fast E-commerce Focus**: Compare products from quick delivery platforms (10-30 min delivery)
- 🔍 **Real-time Product Search**: Search for groceries, essentials, and daily needs
- 📍 **Location-Based Results**: Automatically detects your location and shows relevant prices
- 🏪 **Multi-Platform Comparison**: Compare prices from Zepto, Swiggy Instamart, BigBasket, Blinkit, Dunzo, Demart Ready, Flipkart Minutes, and Amazon Prime Now
- ⏱️ **Delivery Time Comparison**: See delivery times and fees for each platform
- 🎯 **Advanced Filtering**: Filter by platform, price range, delivery time, and ratings
- 📊 **Comparison Tables**: Side-by-side comparison of products with price differences
- 💰 **Best Price Highlighting**: Automatically highlights the best price option
- ⭐ **Ratings & Reviews**: View product ratings and review counts

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **shadcn/ui** components for UI
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install frontend dependencies:
```bash
npm install
```

2. (Optional) Set up backend API server for real product scraping:
```bash
cd backend-example
npm install
node server.js
```

3. Create a `.env` file in the root directory (optional, only if using backend):
```env
VITE_API_BASE_URL=http://localhost:3001
```

4. Start the development server:
```bash
npm run dev
```

5. Open your browser and navigate to `http://localhost:5173`

### Backend API Setup

The app is designed to work with a backend API that handles web scraping from various platforms to avoid CORS issues. See `backend-example/` directory for a sample implementation.

**Note**: Without a backend API, the app will attempt to fetch data directly, which may fail due to CORS restrictions. For production use, set up the backend API server.

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # shadcn/ui components
│   ├── SearchBar.tsx
│   ├── FilterPanel.tsx
│   ├── ProductCard.tsx
│   ├── ProductComparisonTable.tsx
│   └── LocationDisplay.tsx
├── services/           # Business logic services
│   ├── locationService.ts
│   ├── productService.ts
│   ├── fastEcommerceAPI.ts    # Main API service
│   └── platformScraper.ts     # Platform-specific scrapers
├── types/             # TypeScript type definitions
│   └── product.ts
├── data/              # Platform data and configurations
│   └── platformData.ts
├── lib/               # Utility functions
│   └── utils.ts
├── App.tsx            # Main app component
└── main.tsx           # Entry point

backend-example/       # Backend API server example
├── server.js          # Express server with scraping logic
├── package.json
└── README.md          # Backend setup instructions
```

## Features in Detail

### Location Detection
The app uses the browser's Geolocation API to detect your location. You can manually refresh your location if needed.

### Product Search
Search for any product and get results from all configured platforms. Results are filtered based on your location.

### Comparison View
Products are grouped by name and displayed in comparison tables showing:
- Platform badges with icons
- Product images
- Ratings and reviews
- Prices with delivery fees
- Delivery time information
- Original prices (if discounted)
- Best price highlighting
- Direct links to purchase

### Filtering Options
- **Platforms**: Select which fast e-commerce platforms to include
- **Price Range**: Set minimum and maximum price
- **Delivery Time**: Filter by maximum delivery time (in minutes)
- **Rating**: Filter by minimum rating
- **Sorting**: Sort by price (low/high), delivery time, rating, or review count

## Supported Platforms

- **Zepto** - 10-minute delivery
- **Swiggy Instamart** - Quick grocery delivery
- **BigBasket** - Online grocery shopping
- **Blinkit** - 10-minute delivery
- **Dunzo** - Hyperlocal delivery
- **Demart Ready** - Quick delivery
- **Flipkart Minutes** - Fast delivery
- **Amazon Prime Now** - Same-day delivery

## Implementation Notes

### Web Scraping

The app uses a backend API server to scrape product data from various platforms. This is necessary because:
- Browser CORS restrictions prevent direct API calls
- Some platforms require authentication
- Rate limiting and IP blocking concerns

See `backend-example/` for a sample implementation using Express, Axios, and Cheerio/Puppeteer.

### Legal Considerations

⚠️ **Important**: 
- Always check robots.txt and Terms of Service before scraping
- Respect rate limits and implement proper delays
- Consider using official APIs if available
- Some platforms may block automated access

## Future Enhancements

- Real-time price updates
- Price history tracking and alerts
- User accounts and saved comparisons
- Product availability notifications
- More fast e-commerce platforms
- Product specifications comparison
- Image search functionality
- Mobile app version

## License

MIT



