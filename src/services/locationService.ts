import { LocationData } from '../types/product';
import { reverseGeocode, type GeoapifyResult } from './geoapifyService';

export class LocationService {
  static async getCurrentLocation(): Promise<LocationData> {
    return new Promise((resolve, _reject) => {
      if (!navigator.geolocation) {
        resolve({
          city: 'Mumbai',
          state: 'Maharashtra',
          country: 'India',
        });
        return;
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          try {
            const result = await reverseGeocode(latitude, longitude);
            if (result) {
              const location = this.extractLocationFromGeoapify(result);
              resolve({
                ...location,
                coordinates: { lat: latitude, lng: longitude },
              });
              return;
            }
          } catch (e) {
            console.warn('Geoapify reverse geocode not available, using fallback:', e);
          }
          const location = this.getLocationFromCoordinates(latitude, longitude);
          resolve({
            ...location,
            coordinates: { lat: latitude, lng: longitude },
          });
        },
        (error) => {
          console.warn('Geolocation error:', error);
          resolve({
            city: 'Mumbai',
            state: 'Maharashtra',
            country: 'India',
          });
        }
      );
    });
  }

  /**
   * Convert address + coordinates (and optional city/state/country from Geoapify) to LocationData
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
        const location = this.extractLocationFromGeoapify(result);
        return { ...location, coordinates: { lat, lng } };
      }
    } catch (e) {
      console.warn('Geoapify reverse geocode failed, parsing from address:', e);
    }
    const parsed = this.parseLocationFromAddress(address);
    return { ...parsed, coordinates: { lat, lng } };
  }

  /** @deprecated Use convertAddressToLocationData */
  static async convertGooglePlacesToLocationData(
    address: string,
    lat: number,
    lng: number,
    options?: { city?: string; state?: string; country?: string }
  ): Promise<LocationData> {
    return this.convertAddressToLocationData(address, lat, lng, options);
  }

  private static extractLocationFromGeoapify(result: GeoapifyResult): LocationData {
    return {
      city: result.city || 'Mumbai',
      state: result.state || 'Maharashtra',
      country: result.country || 'India',
    };
  }

  private static parseLocationFromAddress(address: string): LocationData {
    const parts = address.split(',').map((p) => p.trim());
    let city = 'Mumbai';
    let state = 'Maharashtra';
    let country = 'India';
    if (parts.length >= 2) {
      city = parts[parts.length - 3] || parts[parts.length - 2] || 'Mumbai';
      state = parts[parts.length - 2] || parts[parts.length - 1] || 'Maharashtra';
      country = parts[parts.length - 1] || 'India';
    } else if (parts.length === 1) {
      city = parts[0];
    }
    return { city, state, country };
  }

  private static getLocationFromCoordinates(lat: number, lng: number): LocationData {
    if (lat > 19 && lat < 20 && lng > 72 && lng < 73) return { city: 'Mumbai', state: 'Maharashtra', country: 'India' };
    if (lat > 28 && lat < 29 && lng > 76 && lng < 78) return { city: 'Delhi', state: 'Delhi', country: 'India' };
    if (lat > 12 && lat < 13 && lng > 77 && lng < 78) return { city: 'Bangalore', state: 'Karnataka', country: 'India' };
    if (lat > 18 && lat < 19 && lng > 72 && lng < 73) return { city: 'Pune', state: 'Maharashtra', country: 'India' };
    return { city: 'Mumbai', state: 'Maharashtra', country: 'India' };
  }

  static getLocationString(location: LocationData): string {
    return `${location.city}, ${location.state}`;
  }
}
