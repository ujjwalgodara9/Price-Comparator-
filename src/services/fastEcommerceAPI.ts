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
   */
  static async searchProducts(
    query: string,
    location: LocationData,
    platforms: Platform[]
  ): Promise<Product[]> {
    if (!query.trim()) {
      return [];
    }

    try {
      // Try to use backend API first
      if (this.API_BASE_URL !== '/api') {
        return await this.searchViaBackendAPI(query, location, platforms);
      }

      // Fallback to direct scraping (may have CORS issues)
      return await PlatformScraper.searchProducts(query, location, platforms);
    } catch (error) {
      console.error('Error searching products:', error);
      return [];
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
    const response = await fetch(`${this.API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        location,
        platforms,
      }),
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.products || [];
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

