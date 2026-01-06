import { useState, useEffect } from 'react';
import { SearchBar } from './components/SearchBar';
import { FilterPanel } from './components/FilterPanel';
import { ProductComparisonTable } from './components/ProductComparisonTable';
import { LocationDisplay } from './components/LocationDisplay';
import { LocationService } from './services/locationService';
import { ProductService } from './services/productService';
import { Product, LocationData, ComparisonFilters, Platform } from './types/product';
import { Loader2 } from 'lucide-react';

function App() {
  const [location, setLocation] = useState<LocationData | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<ComparisonFilters>({
    platforms: ['amazon', 'flipkart', 'myntra', 'nykaa', 'meesho', 'ajio', 'snapdeal', 'tatacliq'],
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
      const results = ProductService.searchProducts(searchQuery, location, filters);
      setProducts(results);
    }
  }, [location, searchQuery, filters]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleRefreshLocation = async () => {
    setLoading(true);
    const newLocation = await LocationService.getCurrentLocation();
    setLocation(newLocation);
    setLoading(false);
  };

  const groupedProducts = ProductService.groupProductsByName(products);

  if (loading || !location) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Detecting your location...</p>
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
            <LocationDisplay location={location} onRefresh={handleRefreshLocation} />
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
            {searchQuery && (
              <div className="mb-6">
                <p className="text-muted-foreground">
                  Found {products.length} product{products.length !== 1 ? 's' : ''} for "{searchQuery}"
                </p>
              </div>
            )}

            {groupedProducts.size === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground text-lg">
                  {searchQuery
                    ? 'No products found. Try a different search term.'
                    : 'Search for products to compare prices across platforms'}
                </p>
              </div>
            ) : (
              Array.from(groupedProducts.entries()).map(([productName, productList]) => (
                <ProductComparisonTable
                  key={productName}
                  products={productList}
                  productName={productName}
                />
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

