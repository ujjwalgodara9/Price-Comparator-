/**
 * Geoapify geocoding service (API key proxied via backend; reference: server.js)
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export interface GeoapifyResult {
  lat: number;
  lon: number;
  formatted?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postcode?: string;
  country?: string;
  [key: string]: unknown;
}

/**
 * Fetch location autocomplete suggestions (proxied through backend)
 */
export async function fetchAutocomplete(text: string): Promise<GeoapifyResult[]> {
  const base = API_BASE.replace(/\/$/, '');
  const url = `${base}/api/autocomplete?text=${encodeURIComponent(text.trim())}`;
  const res = await fetch(url, { method: 'GET' });
  if (!res.ok) {
    if (res.status === 500) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err?.error || 'Geoapify autocomplete not configured');
    }
    throw new Error(`Autocomplete failed: ${res.statusText}`);
  }
  const data = await res.json();
  return Array.isArray(data) ? data : [];
}

/**
 * Reverse geocode: lat/lon -> address (proxied through backend)
 */
export async function reverseGeocode(lat: number, lon: number): Promise<GeoapifyResult | null> {
  const base = API_BASE.replace(/\/$/, '');
  const url = `${base}/api/geocode/reverse?lat=${lat}&lon=${lon}`;
  const res = await fetch(url, { method: 'GET' });
  if (!res.ok) return null;
  const data = await res.json();
  return data && (data.lat != null || data.lon != null) ? data : null;
}
