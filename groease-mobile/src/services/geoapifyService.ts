// Adapted from web src/services/geoapifyService.ts
// Change: removed import.meta.env — uses config.ts instead

import { API_BASE_URL } from '../config';

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
 * Fetch location autocomplete suggestions (proxied through Flask backend)
 */
export async function fetchAutocomplete(text: string): Promise<GeoapifyResult[]> {
  const url = `${API_BASE_URL}/api/autocomplete?text=${encodeURIComponent(text.trim())}`;
  const res = await fetch(url, { method: 'GET' });
  if (!res.ok) {
    if (res.status === 500) {
      const err = await res.json().catch(() => ({}));
      throw new Error((err as any)?.error || 'Geoapify autocomplete not configured');
    }
    throw new Error(`Autocomplete failed: ${res.statusText}`);
  }
  const data = await res.json();
  return Array.isArray(data) ? data : [];
}

/**
 * Reverse geocode: lat/lon -> address (proxied through Flask backend)
 */
export async function reverseGeocode(lat: number, lon: number): Promise<GeoapifyResult | null> {
  const url = `${API_BASE_URL}/api/geocode/reverse?lat=${lat}&lon=${lon}`;
  const res = await fetch(url, { method: 'GET' });
  if (!res.ok) return null;
  const data = await res.json();
  return data && (data.lat != null || data.lon != null) ? (data as GeoapifyResult) : null;
}
