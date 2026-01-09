import { Product, Platform, LocationData } from '../types/product';
import { PlatformScraper } from './platformScraper';

/**
 * Main API service for fast e-commerce platforms
 * This service coordinates fetching data from multiple platforms
 */

export class FastEcommerceAPI {
  private static readonly API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

  /**
   * Search products across all selected fast e-commerce platforms
   * First tries to get comparison data, then falls back to search API
   */
  static async searchProducts(
    query: string,
    location: LocationData,
    platforms: Platform[]
  ): Promise<Product[]> {
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
      // First, try to get comparison data from compare.json
      console.log('[FastEcommerceAPI] Attempting to fetch comparison data...');
      const compareProducts = await this.getCompareData();
      
      if (compareProducts && compareProducts.length > 0) {
        console.log(`[FastEcommerceAPI] Found ${compareProducts.length} products from compare.json`);
        // Filter by selected platforms
        return compareProducts.filter(p => platforms.includes(p.platform));
      }
      
      console.log('[FastEcommerceAPI] No comparison data found, using search API...');
    } catch (error) {
      console.log('[FastEcommerceAPI] Could not load comparison data, using search API:', error);
    }

    try {
      // Fallback to search API
      if (this.API_BASE_URL && this.API_BASE_URL !== '/api') {
        console.log('[FastEcommerceAPI] Using backend API:', this.API_BASE_URL);
        return await this.searchViaBackendAPI(query, location, platforms);
      }

      // If no backend URL configured, try relative /api (proxy mode)
      console.log('[FastEcommerceAPI] Using relative API path (proxy mode)');
      return await this.searchViaBackendAPI(query, location, platforms);
    } catch (error) {
      console.error('[FastEcommerceAPI] Error searching products:', error);
      // Fallback to direct scraping only if API fails
      console.log('[FastEcommerceAPI] Attempting fallback to PlatformScraper');
      try {
        return await PlatformScraper.searchProducts(query, location, platforms);
      } catch (fallbackError) {
        console.error('[FastEcommerceAPI] Fallback also failed:', fallbackError);
        return [];
      }
    }
  }

  /**
   * Get product comparison data from compare.json
   */
  private static async getCompareData(): Promise<Product[]> {
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
      return data.products || [];
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
  ): Promise<Product[]> {
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
      location,
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

