import { useState, useEffect } from 'react';
import { SearchBar } from './components/SearchBar';
import { FilterPanel } from './components/FilterPanel';
import { ProductComparisonTable } from './components/ProductComparisonTable';
import { LocationDisplay } from './components/LocationDisplay';
import { LocationService } from './services/locationService';
import { ProductService } from './services/productService';
import { Product, LocationData, ComparisonFilters, MatchedProduct, Platform } from './types/product';
import { Loader2 } from 'lucide-react';

function App() {
  const [location, setLocation] = useState<LocationData | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState<MatchedProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<ComparisonFilters>({
    platforms: ['zepto', 'blinkit', 'swiggy-instamart'],
    sortBy: 'price-low',
  });

  useEffect(() => {
    // Get user location on mount
    LocationService.getCurrentLocation().then((loc) => {
      setLocation(loc);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (location) {
      // Search products whenever location, query, or filters change
      const searchProducts = async () => {
        console.log('[App] useEffect triggered - searching:', {
          searchQuery,
          location,
          platforms: filters.platforms,
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
          const results = await ProductService.searchProducts(searchQuery, location, filters);
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
  }, [location, searchQuery, filters]);

  const handleSearch = (query: string) => {
    console.log('[App] handleSearch called with query:', query);
    setSearchQuery(query);
  };

  const handleRefreshLocation = async () => {
    setLoading(true);
    const newLocation = await LocationService.getCurrentLocation();
    setLocation(newLocation);
    setLoading(false);
  };

  // Products are already matched products with all platforms in one object
  // Filter to only show products where quantities match across all platforms
  const filteredProducts = products.filter(matchedProduct => {
    const platformData = Object.values(matchedProduct.platforms || {});
    if (platformData.length <= 1) return true; // Single platform, no comparison needed
    
    // Extract quantities
    const quantities = platformData.map(p => p.quantity).filter(q => q);
    if (quantities.length === 0) return true; // No quantities to compare
    
    // Check if all quantities match (using ProductService logic)
    const mockProducts: Product[] = platformData.map((p, idx) => ({
      id: `temp-${idx}`,
      name: matchedProduct.name,
      description: '',
      image: matchedProduct.image,
      price: p.price,
      currency: 'INR',
      platform: Object.keys(matchedProduct.platforms)[idx] as Platform,
      availability: true,
      rating: 0,
      reviewCount: 0,
      features: [],
      link: p.link,
      location: '',
      deliveryTime: p.deliveryTime,
      quantity: p.quantity
    }));
    
    return ProductService.hasMatchingQuantities(mockProducts);
  });

  if (loading && !location) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading your search sit up tight...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold">Product Compare</h1>
            {location && <LocationDisplay location={location} onRefresh={handleRefreshLocation} />}
          </div>
          <SearchBar onSearch={handleSearch} />
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <aside className="lg:col-span-1">
            <FilterPanel filters={filters} onFiltersChange={setFilters} />
          </aside>

          {/* Products Area */}
          <div className="lg:col-span-3">
            {loading && searchQuery && location && (
              <div className="mb-6 flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                <p className="text-muted-foreground">Searching for products...</p>
              </div>
            )}
            
            {!loading && searchQuery && (
              <div className="mb-6">
                <p className="text-muted-foreground">
                  Found {products.length} product{products.length !== 1 ? 's' : ''} for "{searchQuery}"
                </p>
              </div>
            )}

            {!loading && filteredProducts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground text-lg">
                  {searchQuery
                    ? 'No products found with matching quantities across platforms. Try a different search term.'
                    : 'Search for products to compare prices and delivery times across fast e-commerce platforms'}
                </p>
              </div>
            ) : !loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
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
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

