import { Product, ComparisonFilters, LocationData } from '../types/product';
import { FastEcommerceAPI } from './fastEcommerceAPI';
import { LocationService } from './locationService';

export class ProductService {
  private static cachedProducts: Map<string, { products: Product[]; timestamp: number }> = new Map();
  private static readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  /**
   * Search products across fast e-commerce platforms
   */
  static async searchProducts(
    query: string,
    location: LocationData,
    filters: ComparisonFilters
  ): Promise<Product[]> {
    // Use cached results if available and fresh
    const cacheKey = `${query}-${JSON.stringify(location)}-${filters.platforms.join(',')}`;
    const cached = this.cachedProducts.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return this.applyFilters(cached.products, filters);
    }

    // Fetch fresh data from APIs
    let results: Product[] = [];
    
    if (query.trim()) {
      try {
        results = await FastEcommerceAPI.searchProducts(query, location, filters.platforms);
        
        // Cache the results
        this.cachedProducts.set(cacheKey, {
          products: results,
          timestamp: Date.now(),
        });
      } catch (error) {
        console.error('Error fetching products:', error);
        // Return empty array on error
        return [];
      }
    }

    // Apply filters
    results = this.applyFilters(results, filters);

    return results;
  }

  /**
   * Apply filters to product results
   */
  private static applyFilters(products: Product[], filters: ComparisonFilters): Product[] {
    let filtered = products.filter(product => {
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

      // Filter by delivery time
      if (filters.maxDeliveryTime && product.deliveryTime) {
        const deliveryMinutes = this.parseDeliveryTime(product.deliveryTime);
        if (deliveryMinutes > filters.maxDeliveryTime) {
          return false;
        }
      }

      return true;
    });

    // Sort results
    filtered = this.sortProducts(filtered, filters.sortBy);

    return filtered;
  }

  /**
   * Parse delivery time string to minutes
   * e.g., "10-15 mins" -> 15, "30 mins" -> 30, "1 hour" -> 60
   */
  private static parseDeliveryTime(deliveryTime: string): number {
    const timeStr = deliveryTime.toLowerCase();
    
    // Handle hour format
    const hourMatch = timeStr.match(/(\d+)\s*hour/);
    if (hourMatch) {
      return parseInt(hourMatch[1]) * 60;
    }

    // Handle minute range (e.g., "10-15 mins")
    const rangeMatch = timeStr.match(/(\d+)-(\d+)\s*min/);
    if (rangeMatch) {
      return parseInt(rangeMatch[2]); // Return max time
    }

    // Handle single minute format
    const minMatch = timeStr.match(/(\d+)\s*min/);
    if (minMatch) {
      return parseInt(minMatch[1]);
    }

    return 999; // Default to high value if can't parse
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
        return sorted.sort((a, b) => {
          const totalA = a.price + (a.deliveryFee || 0);
          const totalB = b.price + (b.deliveryFee || 0);
          return totalA - totalB;
        });
      case 'price-high':
        return sorted.sort((a, b) => {
          const totalA = a.price + (a.deliveryFee || 0);
          const totalB = b.price + (b.deliveryFee || 0);
          return totalB - totalA;
        });
      case 'rating':
        return sorted.sort((a, b) => b.rating - a.rating);
      case 'reviews':
        return sorted.sort((a, b) => b.reviewCount - a.reviewCount);
      case 'delivery-time':
        return sorted.sort((a, b) => {
          const timeA = a.deliveryTime ? this.parseDeliveryTime(a.deliveryTime) : 999;
          const timeB = b.deliveryTime ? this.parseDeliveryTime(b.deliveryTime) : 999;
          return timeA - timeB;
        });
      default:
        return sorted;
    }
  }
}

