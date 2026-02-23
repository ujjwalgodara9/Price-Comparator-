// Adapted from web src/services/locationService.ts
// Key change: navigator.geolocation replaced with expo-location
// Everything else (address parsing, Geoapify integration) is identical

import * as ExpoLocation from 'expo-location';
import { LocationData } from '../types/product';
import { reverseGeocode, type GeoapifyResult } from './geoapifyService';

export class LocationService {
  /**
   * Request location permission from the OS
   */
  static async requestPermission(): Promise<boolean> {
    const { status } = await ExpoLocation.requestForegroundPermissionsAsync();
    return status === 'granted';
  }

  /**
   * Get current device location (uses expo-location instead of navigator.geolocation)
   */
  static async getCurrentLocation(): Promise<LocationData> {
    try {
      const hasPermission = await this.requestPermission();
      if (!hasPermission) return this.getDefaultLocation();

      const position = await ExpoLocation.getCurrentPositionAsync({
        accuracy: ExpoLocation.Accuracy.Balanced,
      });

      const { latitude, longitude } = position.coords;

      try {
        const result = await reverseGeocode(latitude, longitude);
        if (result) {
          return {
            city: result.city || 'Mumbai',
            state: result.state || 'Maharashtra',
            country: result.country || 'India',
            coordinates: { lat: latitude, lng: longitude },
          };
        }
      } catch (e) {
        console.warn('[LocationService] Reverse geocode failed:', e);
      }

      return {
        ...this.getCoordBasedLocation(latitude, longitude),
        coordinates: { lat: latitude, lng: longitude },
      };
    } catch (error) {
      console.warn('[LocationService] Location error:', error);
      return this.getDefaultLocation();
    }
  }

  /**
   * Convert a selected Geoapify address to LocationData
   * Identical logic to web version
   */
  static async convertAddressToLocationData(
    address: string,
    lat: number,
    lng: number,
    options?: { city?: string; state?: string; country?: string }
  ): Promise<LocationData> {
    if (options?.city || options?.state || options?.country) {
      return {
        city: options.city || 'Mumbai',
        state: options.state || 'Maharashtra',
        country: options.country || 'India',
        coordinates: { lat, lng },
      };
    }
    try {
      const result = await reverseGeocode(lat, lng);
      if (result) {
        return {
          city: result.city || 'Mumbai',
          state: result.state || 'Maharashtra',
          country: result.country || 'India',
          coordinates: { lat, lng },
        };
      }
    } catch (e) {
      console.warn('[LocationService] Reverse geocode failed:', e);
    }
    const parsed = this.parseLocationFromAddress(address);
    return { ...parsed, coordinates: { lat, lng } };
  }

  static getLocationString(location: LocationData): string {
    return `${location.city}, ${location.state}`;
  }

  private static getDefaultLocation(): LocationData {
    return { city: 'Mumbai', state: 'Maharashtra', country: 'India' };
  }

  private static parseLocationFromAddress(address: string): LocationData {
    const parts = address.split(',').map(p => p.trim());
    if (parts.length >= 2) {
      return {
        city: parts[parts.length - 3] || parts[parts.length - 2] || 'Mumbai',
        state: parts[parts.length - 2] || 'Maharashtra',
        country: parts[parts.length - 1] || 'India',
      };
    }
    return { city: parts[0] || 'Mumbai', state: 'Maharashtra', country: 'India' };
  }

  // Fallback coordinate-based city detection (same as web)
  private static getCoordBasedLocation(lat: number, lng: number): LocationData {
    if (lat > 19 && lat < 20 && lng > 72 && lng < 73) return { city: 'Mumbai', state: 'Maharashtra', country: 'India' };
    if (lat > 28 && lat < 29 && lng > 76 && lng < 78) return { city: 'Delhi', state: 'Delhi', country: 'India' };
    if (lat > 12 && lat < 13 && lng > 77 && lng < 78) return { city: 'Bangalore', state: 'Karnataka', country: 'India' };
    if (lat > 17 && lat < 19 && lng > 73 && lng < 74) return { city: 'Pune', state: 'Maharashtra', country: 'India' };
    return { city: 'Mumbai', state: 'Maharashtra', country: 'India' };
  }
}
