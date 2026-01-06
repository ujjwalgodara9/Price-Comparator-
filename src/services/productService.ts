import { Product, ComparisonFilters, LocationData } from '../types/product';
import { mockProducts } from '../data/mockProducts';

export class ProductService {
  static searchProducts(query: string, location: LocationData, filters: ComparisonFilters): Product[] {
    let results = mockProducts.filter(product => {
      // Filter by location
      if (product.location !== LocationService.getLocationString(location)) {
        return false;
      }

      // Filter by search query
      if (query && !product.name.toLowerCase().includes(query.toLowerCase()) &&
          !product.description.toLowerCase().includes(query.toLowerCase())) {
        return false;
      }

      // Filter by platforms
      if (filters.platforms.length > 0 && !filters.platforms.includes(product.platform)) {
        return false;
      }

      // Filter by price range
      if (filters.minPrice && product.price < filters.minPrice) {
        return false;
      }
      if (filters.maxPrice && product.price > filters.maxPrice) {
        return false;
      }

      // Filter by rating
      if (filters.minRating && product.rating < filters.minRating) {
        return false;
      }

      return true;
    });

    // Sort results
    results = this.sortProducts(results, filters.sortBy);

    return results;
  }

  static groupProductsByName(products: Product[]): Map<string, Product[]> {
    const grouped = new Map<string, Product[]>();
    
    products.forEach(product => {
      // Normalize product name for grouping (remove platform-specific variations)
      const normalizedName = product.name.split(' - ')[0].trim();
      
      if (!grouped.has(normalizedName)) {
        grouped.set(normalizedName, []);
      }
      grouped.get(normalizedName)!.push(product);
    });

    return grouped;
  }

  private static sortProducts(products: Product[], sortBy: ComparisonFilters['sortBy']): Product[] {
    const sorted = [...products];
    
    switch (sortBy) {
      case 'price-low':
        return sorted.sort((a, b) => a.price - b.price);
      case 'price-high':
        return sorted.sort((a, b) => b.price - a.price);
      case 'rating':
        return sorted.sort((a, b) => b.rating - a.rating);
      case 'reviews':
        return sorted.sort((a, b) => b.reviewCount - a.reviewCount);
      default:
        return sorted;
    }
  }
}

// Import LocationService for location string
import { LocationService } from './locationService';

