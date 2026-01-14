import { Product, Platform, LocationData, MatchedProduct } from '../types/product';

/**
 * Main API service for fast e-commerce platforms
 * This service coordinates fetching data from multiple platforms
 */

export class FastEcommerceAPI {
  private static readonly API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

  /**
   * Search products across all selected fast e-commerce platforms
   * Always calls search API which triggers scraping, comparison, and returns results
   * The backend automatically scrapes, compares, and returns comparison results
   */
  static async searchProducts(
    query: string,
    location: LocationData,
    platforms: Platform[]
  ): Promise<MatchedProduct[]> {
    console.log('[FastEcommerceAPI] searchProducts called:', {
      query,
      location,
      platforms,
      API_BASE_URL: this.API_BASE_URL,
    });
    
    if (!query.trim()) {
      console.log('[FastEcommerceAPI] Empty query, returning empty array');
      return [];
    }

    try {
      // Always call search API which triggers:
      // 1. Scraping from all platforms
      // 2. Automatic comparison
      // 3. Saving to compare.json
      // 4. Returning comparison results directly
      console.log('[FastEcommerceAPI] Calling search API (will scrape, compare, and return results)...');
      const products = await this.searchViaBackendAPI(query, location, platforms);
      
      if (products && products.length > 0) {
        console.log(`[FastEcommerceAPI] Received ${products.length} matched products from search API`);
        // Filter platforms within each matched product
        return products.map(matchedProduct => {
          const filteredPlatforms: Record<Platform, any> = {} as any;
          const filteredOriginalNames: Record<Platform, string> = {} as any;
          
          Object.keys(matchedProduct.platforms || {}).forEach(platform => {
            if (platforms.includes(platform as Platform)) {
              filteredPlatforms[platform as Platform] = matchedProduct.platforms[platform as Platform];
              if (matchedProduct.original_names?.[platform as Platform]) {
                filteredOriginalNames[platform as Platform] = matchedProduct.original_names[platform as Platform];
              }
            }
          });
          
          return {
            ...matchedProduct,
            platforms: filteredPlatforms,
            original_names: filteredOriginalNames
          };
        }).filter(matchedProduct => Object.keys(matchedProduct.platforms).length > 0);
      }
      
      console.log('[FastEcommerceAPI] No products found in search results');
      return [];
      
    } catch (error) {
      console.error('[FastEcommerceAPI] Error searching products:', error);
      // Fallback to PlatformScraper if API fails
      try {
        console.log('[FastEcommerceAPI] Fallback: attempting direct scraping');
        // Note: PlatformScraper returns Product[], but we need MatchedProduct[]
        // For now, return empty array on fallback
        console.warn('[FastEcommerceAPI] Fallback scraping not supported for MatchedProduct format');
        return [];
      } catch (fallbackError) {
        console.error('[FastEcommerceAPI] Fallback also failed:', fallbackError);
        return [];
      }
    }
  }

  /**
   * Get product comparison data from compare.json
   */
  static async getCompareData(): Promise<MatchedProduct[]> {
    let url: string;
    if (this.API_BASE_URL.startsWith('http')) {
      url = `${this.API_BASE_URL}/api/compare`;
    } else {
      url = `/api/compare`;
    }
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          console.log('[FastEcommerceAPI] compare.json not found, will use search API');
        }
        throw new Error(`Failed to fetch comparison data: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('[FastEcommerceAPI] Comparison data received:', {
        productCount: data.products?.length || 0,
      });
      return data.products || []; // Returns MatchedProduct[]
    } catch (error) {
      console.error('[FastEcommerceAPI] Error fetching comparison data:', error);
      throw error;
    }
  }

  /**
   * Search via backend API (recommended approach)
   */
  private static async searchViaBackendAPI(
    query: string,
    location: LocationData,
    platforms: Platform[]
  ): Promise<MatchedProduct[]> {
    // Build API URL - handle both absolute and relative paths
    let url: string;
    if (this.API_BASE_URL.startsWith('http')) {
      // Absolute URL (e.g., http://localhost:3001)
      url = `${this.API_BASE_URL}/api/search`;
    } else {
      // Relative URL (e.g., /api or empty)
      url = `/api/search`;
    }
    
    const payload = {
      query,
      location: {
        address: (location as any).address || `${location.city}, ${location.state}`,
        city: location.city,
        state: location.state,
        country: location.country || 'India',
        coordinates: location.coordinates
      },
      platforms,
    };
    
    console.log('[FRONTEND] Making API request:', {
      url,
      method: 'POST',
      payload,
      apiBaseUrl: this.API_BASE_URL,
    });
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      console.log('[FRONTEND] API Response:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[FRONTEND] API Error Response:', errorText);
        throw new Error(`API request failed: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('[FRONTEND] API Data received:', {
        productCount: data.products?.length || 0,
      });
      return data.products || [];
    } catch (error) {
      console.error('[FRONTEND] API Request Error:', error);
      throw error;
    }
  }

  /**
   * Get product details for a specific product ID
   */
  static async getProductDetails(
    productId: string,
    platform: Platform
  ): Promise<Product | null> {
    try {
      const response = await fetch(
        `${this.API_BASE_URL}/product/${platform}/${productId}`
      );

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      return data.product || null;
    } catch (error) {
      console.error('Error fetching product details:', error);
      return null;
    }
  }

  /**
   * Check availability of a product on a platform for a location
   */
  static async checkAvailability(
    productId: string,
    platform: Platform,
    location: LocationData
  ): Promise<boolean> {
    try {
      const response = await fetch(`${this.API_BASE_URL}/availability`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          productId,
          platform,
          location,
        }),
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      return data.available || false;
    } catch (error) {
      console.error('Error checking availability:', error);
      return false;
    }
  }
}

