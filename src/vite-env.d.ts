/// <reference types="vite/client" />

declare global {
  interface Window {
    google?: {
      maps: {
        places: {
          AutocompleteService: new () => any;
          PlacesService: new (element: HTMLElement) => any;
          PlacesServiceStatus: {
            OK: string;
          };
        };
        Geocoder: new () => {
          geocode: (request: any, callback: (results: any[], status: string) => void) => void;
        };
        GeocoderStatus: {
          OK: string;
        };
      };
    };
  }
}

export {};

