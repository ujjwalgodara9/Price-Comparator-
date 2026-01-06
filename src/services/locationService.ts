import { LocationData } from '../types/product';

export class LocationService {
  static async getCurrentLocation(): Promise<LocationData> {
    return new Promise((resolve, reject) => {
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
          
          // In a real app, you'd call a reverse geocoding API
          // For now, we'll use a simple mock based on coordinates
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

