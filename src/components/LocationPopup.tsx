import { useEffect, useState } from "react";
import { fetchAutocomplete, type GeoapifyResult } from "../services/geoapifyService";

interface LocationPopupProps {
  onClose: (location: {
    address: string;
    lat: number;
    lng: number;
    city?: string;
    state?: string;
    country?: string;
  }) => void;
}

export const LocationPopup = ({ onClose }: LocationPopupProps) => {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<GeoapifyResult[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch suggestions when query changes (Geoapify autocomplete via backend)
  useEffect(() => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }

    const delay = setTimeout(() => {
      fetchAutocomplete(query)
        .then(setSuggestions)
        .catch((err) => {
          console.warn("[LocationPopup] Autocomplete error:", err);
          setSuggestions([]);
        });
    }, 400);

    return () => clearTimeout(delay);
  }, [query]);

  const handleSelect = (result: GeoapifyResult) => {
    setLoading(true);
    const lat = result.lat ?? 0;
    const lon = result.lon ?? 0;
    const address = result.formatted || [result.address_line1, result.address_line2].filter(Boolean).join(", ") || `${result.city || ""}, ${result.state || ""}`.trim() || "Unknown";
    onClose({
      address,
      lat,
      lng: lon,
      city: result.city,
      state: result.state,
      country: result.country,
    });
    setLoading(false);
  };

  return (
    <div
      className="fixed inset-0 flex items-center justify-center p-4"
      style={{
        zIndex: 9999,
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        className="bg-white w-full max-w-[420px] rounded-lg shadow-xl border border-blue-100 overflow-hidden"
        style={{ position: "relative", zIndex: 10000 }}
      >
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

          {suggestions.length > 0 && (
            <div className="border-2 border-blue-100 rounded-lg mt-3 max-h-60 overflow-y-auto bg-white shadow-lg">
              {suggestions.map((item, idx) => (
                <div
                  key={`${item.lat}-${item.lon}-${idx}`}
                  onClick={() => handleSelect(item)}
                  className="px-4 py-3 cursor-pointer hover:bg-blue-50 border-b border-blue-50 last:border-b-0 transition-colors"
                >
                  <p className="font-medium text-sm text-gray-900">
                    {item.address_line1 || item.city || item.formatted || "Address"}
                  </p>
                  <p className="text-xs text-blue-600 mt-0.5">
                    {[item.city, item.state, item.country].filter(Boolean).join(", ") || item.formatted}
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
