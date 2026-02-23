// Adapted from web src/services/productService.ts
// Changes:
//   - Uses GroeaseAPI instead of FastEcommerceAPI
//   - Added sortProducts() helper (sorting logic moved here from App.tsx)
//   - Removed web-only imports

import { LocationData, MatchedProduct, ComparisonFilters } from '../types/product';
import { GroeaseAPI } from './api';

export class ProductService {
  private static cache: Map<string, { products: MatchedProduct[]; timestamp: number }> = new Map();
  private static readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  static async searchProducts(
    query: string,
    location: LocationData,
    filters: ComparisonFilters
  ): Promise<MatchedProduct[]> {
    const cacheKey = `${query}-${JSON.stringify(location)}-${filters.platforms.join(',')}`;
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return cached.products;
    }

    if (!query.trim()) return [];

    try {
      const results = await GroeaseAPI.searchProducts(query, location, filters.platforms);
      this.cache.set(cacheKey, { products: results, timestamp: Date.now() });
      return results;
    } catch (error) {
      console.error('[ProductService] Error fetching products:', error);
      return [];
    }
  }

  /**
   * Sort + filter matched products based on ComparisonFilters.
   * Handles: price-low, price-high, delivery-time, rating, platform filter, max price.
   */
  static sortProducts(
    products: MatchedProduct[],
    filters?: Pick<ComparisonFilters, 'sortBy' | 'maxPrice' | 'platforms'>
  ): MatchedProduct[] {
    let list = [...products];

    // 1. Filter to only the requested platforms
    if (filters?.platforms && filters.platforms.length > 0) {
      list = list
        .map(p => {
          const filteredPlatforms: typeof p.platforms = {} as any;
          const filteredNames: typeof p.original_names = {} as any;
          for (const plat of filters.platforms) {
            if (p.platforms[plat]) {
              filteredPlatforms[plat] = p.platforms[plat];
              if (p.original_names?.[plat]) filteredNames[plat] = p.original_names[plat];
            }
          }
          return { ...p, platforms: filteredPlatforms, original_names: filteredNames };
        })
        .filter(p => Object.keys(p.platforms).length > 0);
    }

    // 2. Filter by max price (cheapest platform price must be ≤ maxPrice)
    if (filters?.maxPrice) {
      list = list.filter(p => {
        const prices = Object.values(p.platforms).map(d => d.price).filter(Boolean);
        return prices.length > 0 && Math.min(...prices) <= filters.maxPrice!;
      });
    }

    // 3. Sort
    const sortBy = filters?.sortBy ?? 'price-low';

    const cheapestPrice = (p: MatchedProduct) => {
      const prices = Object.values(p.platforms).map(d => d.price).filter(Boolean);
      return prices.length > 0 ? Math.min(...prices) : Infinity;
    };

    const fastestDelivery = (p: MatchedProduct) => {
      // Parse "10-20 min" → take lower bound; default 999 if missing
      const times = Object.values(p.platforms)
        .map(d => {
          const match = d.deliveryTime?.match(/(\d+)/);
          return match ? parseInt(match[1], 10) : 999;
        });
      return times.length > 0 ? Math.min(...times) : 999;
    };

    if (sortBy === 'price-low') {
      list.sort((a, b) => cheapestPrice(a) - cheapestPrice(b));
    } else if (sortBy === 'price-high') {
      list.sort((a, b) => cheapestPrice(b) - cheapestPrice(a));
    } else if (sortBy === 'delivery-time') {
      list.sort((a, b) => fastestDelivery(a) - fastestDelivery(b));
    } else {
      // Default: multi-platform products first, then alphabetical
      list.sort((a, b) => {
        const ca = Object.keys(a.platforms).length;
        const cb = Object.keys(b.platforms).length;
        if (ca !== cb) return cb - ca;
        return a.name.localeCompare(b.name, undefined, { sensitivity: 'base', numeric: true });
      });
    }

    return list;
  }
}
