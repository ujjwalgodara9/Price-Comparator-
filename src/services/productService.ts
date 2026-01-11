import { Product, ComparisonFilters, LocationData } from '../types/product';
import { FastEcommerceAPI } from './fastEcommerceAPI';

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

  /**
   * Check if all products in a group have matching quantities
   * Returns true only if all products have the same quantity (or all have no quantity)
   * Uses tolerance-based matching similar to backend (allows quantities within 2x range)
   */
  static hasMatchingQuantities(products: Product[]): boolean {
    if (products.length <= 1) {
      return true; // Single product or empty, no comparison needed
    }

    // Extract and parse quantities
    const parsedQuantities = products
      .map(p => p.quantity ? this.parseQuantity(p.quantity) : null)
      .filter(qty => qty !== null) as Array<{ value: number; unit: string }>;

    // If no products have quantities, consider them matching
    if (parsedQuantities.length === 0) {
      return true;
    }

    // If some products have quantities and others don't, they don't match
    if (parsedQuantities.length < products.length) {
      return false;
    }

    // Convert all to kg for comparison
    const quantitiesInKg = parsedQuantities.map(qty => {
      if (qty.unit === 'g' || qty.unit === 'gm' || qty.unit === 'gram') {
        return qty.value / 1000; // Convert grams to kg
      } else if (qty.unit === 'kg' || qty.unit === 'kilogram') {
        return qty.value;
      } else {
        // For packs or unknown units, can't compare, so return null
        return null;
      }
    });

    // If any quantity couldn't be converted, check if they're all the same string
    if (quantitiesInKg.some(qty => qty === null)) {
      // Fallback to string comparison
      const quantityStrings = products
        .map(p => p.quantity?.trim().toLowerCase())
        .filter(qty => qty);
      if (quantityStrings.length === 0) return true;
      const firstQty = quantityStrings[0];
      return quantityStrings.every(qty => qty === firstQty);
    }

    // Check if all quantities are within tolerance (2x range, similar to backend)
    const firstQty = quantitiesInKg[0]!;
    const toleranceRatio = 2.0;
    
    return quantitiesInKg.every(qty => {
      if (qty === null) return false;
      // Exact match (within floating point tolerance)
      if (Math.abs(qty - firstQty) < 0.01) return true;
      // Tolerance-based matching: allow quantities within 2x range
      const ratio = Math.max(qty, firstQty) / Math.min(qty, firstQty);
      return ratio <= toleranceRatio;
    });
  }

  /**
   * Parse quantity string to extract value and unit
   * Returns { value: number, unit: string } or null if can't parse
   */
  private static parseQuantity(quantity: string): { value: number; unit: string } | null {
    const normalized = quantity.trim().toLowerCase();
    
    // Extract numeric value and unit
    const match = normalized.match(/(\d+(?:\.\d+)?)\s*(kg|g|gm|gram|kilograms?|grams?|pack|pcs?|pieces?)/);
    if (!match) {
      return null;
    }

    const value = parseFloat(match[1]);
    let unit = match[2].toLowerCase();

    // Normalize units
    if (unit === 'gram' || unit === 'grams' || unit === 'gm') {
      unit = 'g';
    } else if (unit === 'kilogram' || unit === 'kilograms') {
      unit = 'kg';
    } else if (unit === 'pc' || unit === 'pcs' || unit === 'pieces') {
      unit = 'pack';
    }

    return { value, unit };
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

