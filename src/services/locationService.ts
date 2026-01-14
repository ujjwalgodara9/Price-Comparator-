import { LocationData } from '../types/product';
import { loadGoogleMaps } from '../utils/loadGoogleMaps';

export class LocationService {
  static async getCurrentLocation(): Promise<LocationData> {
    return new Promise((resolve, _reject) => {
      if (!navigator.geolocation) {
        // Fallback to default location if geolocation not available
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
          
          // Try to use Google Maps reverse geocoding if available
          try {
            await loadGoogleMaps();
            if (window.google && window.google.maps) {
              const geocoder = new window.google.maps.Geocoder();
              geocoder.geocode(
                { location: { lat: latitude, lng: longitude } },
                (results, status) => {
                  if (window.google && status === window.google.maps.GeocoderStatus.OK && results && results.length > 0) {
                    const location = this.extractLocationFromGeocodeResult(results[0]);
                    resolve({
                      ...location,
                      coordinates: { lat: latitude, lng: longitude },
                    });
                  } else {
                    // Fallback to mock location
                    const location = this.getLocationFromCoordinates(latitude, longitude);
                    resolve({
                      ...location,
                      coordinates: { lat: latitude, lng: longitude },
                    });
                  }
                }
              );
              return;
            }
          } catch (error) {
            console.warn('Google Maps not available, using fallback:', error);
          }
          
          // Fallback to mock location
          const location = this.getLocationFromCoordinates(latitude, longitude);
          resolve({
            ...location,
            coordinates: { lat: latitude, lng: longitude },
          });
        },
        (error) => {
          // Fallback to default location
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
   * Convert Google Places location data to LocationData format
   */
  static async convertGooglePlacesToLocationData(
    address: string,
    lat: number,
    lng: number
  ): Promise<LocationData> {
    try {
      await loadGoogleMaps();
      if (window.google && window.google.maps) {
        const geocoder = new window.google.maps.Geocoder();
        return new Promise((resolve) => {
          geocoder.geocode(
            { location: { lat, lng } },
            (results, status) => {
              if (window.google && status === window.google.maps.GeocoderStatus.OK && results && results.length > 0) {
                const location = this.extractLocationFromGeocodeResult(results[0]);
                resolve({
                  ...location,
                  coordinates: { lat, lng },
                });
              } else {
                // Fallback: try to parse from address string
                const parsed = this.parseLocationFromAddress(address);
                resolve({
                  ...parsed,
                  coordinates: { lat, lng },
                });
              }
            }
          );
        });
      }
    } catch (error) {
      console.warn('Google Maps not available, parsing from address:', error);
    }

    // Fallback: parse from address string
    const parsed = this.parseLocationFromAddress(address);
    return {
      ...parsed,
      coordinates: { lat, lng },
    };
  }

  /**
   * Extract city, state, country from Google Geocoder result
   */
  private static extractLocationFromGeocodeResult(result: any): LocationData {
    let city = '';
    let state = '';
    let country = 'India';

    for (const component of result.address_components || []) {
      const types = component.types;
      
      if (types.includes('locality') || types.includes('sublocality') || types.includes('sublocality_level_1')) {
        city = component.long_name;
      } else if (types.includes('administrative_area_level_1')) {
        state = component.long_name;
      } else if (types.includes('country')) {
        country = component.long_name;
      }
    }

    // Fallback if city not found
    if (!city) {
      for (const component of result.address_components || []) {
        if (component.types.includes('administrative_area_level_2')) {
          city = component.long_name;
          break;
        }
      }
    }

    // Fallback values
    if (!city) city = 'Mumbai';
    if (!state) state = 'Maharashtra';
    if (!country) country = 'India';

    return { city, state, country };
  }

  /**
   * Parse location from address string (fallback method)
   */
  private static parseLocationFromAddress(address: string): LocationData {
    // Try to extract city and state from address
    // Common format: "Street, City, State, Country"
    const parts = address.split(',').map(p => p.trim());
    
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
    // Mock location mapping - in production, use reverse geocoding API
    // This is a simplified version for demo purposes
    if (lat > 19 && lat < 20 && lng > 72 && lng < 73) {
      return { city: 'Mumbai', state: 'Maharashtra', country: 'India' };
    } else if (lat > 28 && lat < 29 && lng > 76 && lng < 78) {
      return { city: 'Delhi', state: 'Delhi', country: 'India' };
    } else if (lat > 12 && lat < 13 && lng > 77 && lng < 78) {
      return { city: 'Bangalore', state: 'Karnataka', country: 'India' };
    } else if (lat > 18 && lat < 19 && lng > 72 && lng < 73) {
      return { city: 'Pune', state: 'Maharashtra', country: 'India' };
    }
    
    return { city: 'Mumbai', state: 'Maharashtra', country: 'India' };
  }

  static getLocationString(location: LocationData): string {
    return `${location.city}, ${location.state}`;
  }
}

