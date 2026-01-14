import { useState, useEffect } from 'react';
import { SearchBar } from './components/SearchBar';
import { ProductComparisonTable } from './components/ProductComparisonTable';
import { LocationDisplay } from './components/LocationDisplay';
import { LocationPopup } from './components/LocationPopup';
import { LocationService } from './services/locationService';
import { ProductService } from './services/productService';
import { LocationData, ComparisonFilters, MatchedProduct, Platform } from './types/product';
import { Loader2, Sparkles, TrendingDown, Zap } from 'lucide-react';
import groeaseLogo from './images/groease.jpg';

function App() {
  const [location, setLocation] = useState<LocationData | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState<MatchedProduct[]>([]);
  const [loading, setLoading] = useState(false);
  const [showLocationPopup, setShowLocationPopup] = useState(true); // Show popup by default
  
  // Default platforms to search (no filters panel, so hardcoded)
  const defaultPlatforms: Platform[] = ['zepto', 'blinkit', 'swiggy-instamart', 'bigbasket', 'dmart'];

  useEffect(() => {
    if (location) {
      // Search products whenever location, query, or filters change
      const searchProducts = async () => {
        console.log('[App] useEffect triggered - searching:', {
          searchQuery,
          location,
          platforms: defaultPlatforms,
        });
        
        // Don't search if query is empty
        if (!searchQuery.trim()) {
          console.log('[App] Empty query, skipping search');
          setProducts([]);
          setLoading(false);
          return;
        }
        
        setLoading(true);
        try {
          // Use default filters with hardcoded platforms
          const defaultFilters: ComparisonFilters = {
            platforms: defaultPlatforms,
            sortBy: 'price-low',
          };
          const results = await ProductService.searchProducts(searchQuery, location, defaultFilters);
          console.log('[App] Search results:', results.length, 'products');
          setProducts(results);
        } catch (error) {
          console.error('[App] Error searching products:', error);
          setProducts([]);
        } finally {
          setLoading(false);
        }
      };
      searchProducts();
    }
  }, [location, searchQuery]);

  const handleSearch = (query: string) => {
    console.log('[App] handleSearch called with query:', query);
    setSearchQuery(query);
  };

  const handleRefreshLocation = () => {
    setShowLocationPopup(true);
  };

  const handleLocationSet = async (locationData: { address: string; lat: number; lng: number }) => {
    // Location is mandatory - don't allow closing without setting location
    if (!locationData.address || locationData.lat === 0 || locationData.lng === 0) {
      return; // Don't close popup if location is not set
    }

    setLoading(true);
    try {
      // Convert Google Places location to LocationData format
      const locationDataFormatted = await LocationService.convertGooglePlacesToLocationData(
        locationData.address,
        locationData.lat,
        locationData.lng
      );
      
      setLocation(locationDataFormatted);
      localStorage.setItem('userLocation', JSON.stringify(locationDataFormatted));
      setShowLocationPopup(false);
    } catch (error) {
      console.error('Error setting location:', error);
    } finally {
      setLoading(false);
    }
  };

  // Show all matched products - don't filter by quantity matching
  // Users can see all products even if quantities differ (useful for comparison)
  const filteredProducts = products;

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-blue-50/30 to-white">
      {/* Location Popup */}
      {showLocationPopup && (
        <LocationPopup onClose={handleLocationSet} />
      )}

      {/* GROEASE Header with Logo */}
      <header className="bg-gradient-to-r from-white via-blue-50/40 to-white border-b border-blue-100 shadow-sm sticky top-0 z-50 backdrop-blur-sm">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-4">
              <img 
                src={groeaseLogo} 
                alt="GROEASE Logo" 
                className="h-12 w-12 object-contain"
              />
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent tracking-tight">
                  GROEASE
                </h1>
                <p className="text-sm text-blue-600 font-medium mt-0.5">ONE APP. ENDLESS EASE</p>
              </div>
            </div>
            {location && <LocationDisplay location={location} onRefresh={handleRefreshLocation} />}
          </div>
          <SearchBar onSearch={handleSearch} />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && searchQuery && location && (
          <div className="mb-8 flex items-center justify-center gap-3 py-12">
            <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
            <p className="text-blue-700 font-medium">Searching for products...</p>
          </div>
        )}
        
        {!loading && searchQuery && (
          <div className="mb-6">
            <p className="text-blue-700 text-sm">
              Found <span className="font-semibold text-blue-900">{products.length}</span> product{products.length !== 1 ? 's' : ''} for <span className="font-medium">"{searchQuery}"</span>
            </p>
          </div>
        )}

        {!loading && filteredProducts.length === 0 && !searchQuery ? (
          /* Initial State with Creative Quote */
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="max-w-2xl mx-auto text-center px-4">
              {/* Decorative Elements */}
              <div className="relative mb-8">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-32 h-32 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full blur-3xl opacity-50"></div>
                </div>
                <div className="relative flex justify-center mb-6">
                  <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl shadow-lg border border-blue-200">
                    <img 
                      src={groeaseLogo} 
                      alt="GROEASE Logo" 
                      className="h-16 w-16 object-contain mx-auto"
                    />
                  </div>
                </div>
              </div>

              {/* Creative Quote */}
              <div className="space-y-6">
                <blockquote className="text-3xl md:text-4xl font-bold text-gray-900 leading-tight">
                  <span className="text-blue-600">"</span>
                  <span className="bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent">
                    ONE PRODUCT. MULTIPLE APPS. ONE BEST DEAL.
                  </span>
                  <span className="text-blue-600">"</span>
                </blockquote>
                
                <p className="text-lg text-blue-700 font-medium">
                  Compare prices across quick-commerce apps and choose the smartest option, every time
                </p>

                {/* Feature Icons */}
                <div className="flex flex-wrap items-center justify-center gap-8 mt-10 pt-8 border-t border-blue-200">
                  <div className="flex flex-col items-center gap-2">
                    <div className="p-3 bg-blue-50 rounded-xl border border-blue-100">
                      <TrendingDown className="h-6 w-6 text-blue-600" />
                    </div>
                    <span className="text-sm font-medium text-blue-700">Best Prices</span>
                  </div>
                  <div className="flex flex-col items-center gap-2">
                    <div className="p-3 bg-blue-50 rounded-xl border border-blue-100">
                      <Zap className="h-6 w-6 text-blue-600" />
                    </div>
                    <span className="text-sm font-medium text-blue-700">Quick Delivery</span>
                  </div>
                  <div className="flex flex-col items-center gap-2">
                    <div className="p-3 bg-blue-50 rounded-xl border border-blue-100">
                      <Sparkles className="h-6 w-6 text-blue-600" />
                    </div>
                    <span className="text-sm font-medium text-blue-700">Transparent Shopping</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : !loading && filteredProducts.length === 0 && searchQuery ? (
          <div className="text-center py-16">
            <div className="max-w-md mx-auto">
              <div className="mb-4 p-4 bg-blue-50 rounded-full w-16 h-16 mx-auto flex items-center justify-center border border-blue-100">
                <Sparkles className="h-8 w-8 text-blue-400" />
              </div>
              <p className="text-blue-700 text-lg mb-2 font-medium">
                No products found with matching quantities across platforms.
              </p>
              <p className="text-blue-600 text-sm mt-2">Try a different search term</p>
            </div>
          </div>
        ) : !loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
            {filteredProducts
              .sort((a, b) => {
                // First sort by number of platform matches (descending)
                const matchCountA = Object.keys(a.platforms || {}).length;
                const matchCountB = Object.keys(b.platforms || {}).length;
                
                if (matchCountA !== matchCountB) {
                  return matchCountB - matchCountA; // Descending order (3 matches before 2 matches)
                }
                
                // If same number of matches, sort alphabetically
                // Custom sort: letters before numbers
                const nameA = a.name;
                const nameB = b.name;
                const startsWithLetterA = /^[a-zA-Z]/.test(nameA);
                const startsWithLetterB = /^[a-zA-Z]/.test(nameB);
                
                // If one starts with letter and other with number, letter comes first
                if (startsWithLetterA && !startsWithLetterB) return -1;
                if (!startsWithLetterA && startsWithLetterB) return 1;
                
                // Both start with same type (letter or number), sort normally
                return nameA.localeCompare(nameB, undefined, { sensitivity: 'base', numeric: true });
              })
              .map((matchedProduct) => (
                <ProductComparisonTable
                  key={matchedProduct.name}
                  matchedProduct={matchedProduct}
                />
              ))}
          </div>
        ) : null}
      </main>
    </div>
  );
}

export default App;

