# Product Compare

A modern product comparison website that helps users compare prices across multiple e-commerce platforms based on their location.

## Features

- 🔍 **Product Search**: Search for products across all platforms
- 📍 **Location-Based Results**: Automatically detects your location and shows relevant prices
- 🏪 **Multi-Platform Comparison**: Compare prices from Amazon, Flipkart, Myntra, Nykaa, Meesho, Ajio, Snapdeal, and Tata CLiQ
- 🎯 **Advanced Filtering**: Filter by platform, price range, and ratings
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

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

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
│   └── ProductComparisonTable.tsx
├── services/           # Business logic services
│   ├── locationService.ts
│   └── productService.ts
├── types/             # TypeScript type definitions
│   └── product.ts
├── data/              # Mock data
│   └── mockProducts.ts
├── lib/               # Utility functions
│   └── utils.ts
├── App.tsx            # Main app component
└── main.tsx           # Entry point
```

## Features in Detail

### Location Detection
The app uses the browser's Geolocation API to detect your location. You can manually refresh your location if needed.

### Product Search
Search for any product and get results from all configured platforms. Results are filtered based on your location.

### Comparison View
Products are grouped by name and displayed in comparison tables showing:
- Platform badges
- Product images
- Ratings and reviews
- Prices with difference indicators
- Best price highlighting
- Direct links to purchase

### Filtering Options
- **Platforms**: Select which platforms to include
- **Price Range**: Set minimum and maximum price
- **Rating**: Filter by minimum rating
- **Sorting**: Sort by price (low/high), rating, or review count

## Future Enhancements

- Integration with real product APIs
- User accounts and saved comparisons
- Price history tracking
- Price drop alerts
- More platforms
- Product specifications comparison
- Image search functionality

## License

MIT

