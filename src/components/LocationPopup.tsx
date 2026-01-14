import { useEffect, useState, useRef } from "react";
import { loadGoogleMaps } from "../utils/loadGoogleMaps";

interface LocationPopupProps {
  onClose: (location: {
    address: string;
    lat: number;
    lng: number;
  }) => void;
}

export const LocationPopup = ({ onClose }: LocationPopupProps) => {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // These keep the Google services active without reloading them
  const autocompleteService = useRef<any>(null);
  const placesService = useRef<any>(null);
  const geocoder = useRef<any>(null);

  // 1. Initialize Google Maps Services
  useEffect(() => {
    loadGoogleMaps().then(() => {
      if (window.google && window.google.maps && window.google.maps.places) {
        autocompleteService.current = new window.google.maps.places.AutocompleteService();
        placesService.current = new window.google.maps.places.PlacesService(document.createElement("div"));
        geocoder.current = new window.google.maps.Geocoder();
      }
    }).catch(() => {
      console.error("Failed to load Google Maps API");
    });
  }, []);

  // 2. Fetch Suggestions when query changes
  useEffect(() => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }

    // Debounce to avoid too many requests
    const delay = setTimeout(() => {
      if (!autocompleteService.current) return;

      const request = {
        input: query,
        componentRestrictions: { country: "in" }, // Restrict to India
      };

      autocompleteService.current.getPlacePredictions(request, (predictions: any, status: any) => {
        if (window.google && status === window.google.maps.places.PlacesServiceStatus.OK && predictions) {
          setSuggestions(predictions);
        } else {
          setSuggestions([]);
        }
      });
    }, 400);

    return () => clearTimeout(delay);
  }, [query]);

  // 3. Handle User Selection
  const handleSelect = (place: any) => {
    if (!placesService.current) return;

    setLoading(true);
    const request = {
      placeId: place.place_id,
      fields: ["geometry", "formatted_address", "address_components"],
    };

    placesService.current.getDetails(request, (placeDetails: any, status: any) => {
      if (window.google && status === window.google.maps.places.PlacesServiceStatus.OK) {
        const location = placeDetails.geometry.location;
        onClose({
          address: placeDetails.formatted_address,
          lat: location.lat(),
          lng: location.lng(),
        });
      } else {
        console.error("Failed to fetch place details");
        setLoading(false);
      }
    });
  };


  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div 
        className="bg-white w-full max-w-[420px] rounded-lg shadow-xl border border-blue-100 overflow-hidden"
      >
        {/* Header with blue gradient */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Set Your Location</h2>
              <p className="text-sm text-blue-100 mt-1">
                Provide your delivery location to see products
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="relative">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search delivery location"
              className="w-full border-2 border-blue-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 px-4 py-3 rounded-lg text-sm transition-colors outline-none"
              disabled={loading}
            />
            {loading && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <div className="h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              </div>
            )}
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="border-2 border-blue-100 rounded-lg mt-3 max-h-60 overflow-y-auto bg-white shadow-lg">
              {suggestions.map((item: any) => (
                <div
                  key={item.place_id}
                  onClick={() => handleSelect(item)}
                  className="px-4 py-3 cursor-pointer hover:bg-blue-50 border-b border-blue-50 last:border-b-0 transition-colors"
                >
                  <p className="font-medium text-sm text-gray-900">
                    {item.structured_formatting.main_text}
                  </p>
                  <p className="text-xs text-blue-600 mt-0.5">
                    {item.structured_formatting.secondary_text}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};