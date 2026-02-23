import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = 'recentSearches';
const MAX = 6;

export async function addRecentSearch(query: string): Promise<void> {
  const q = query.trim().toLowerCase();
  if (!q) return;
  try {
    const existing = await getRecentSearches();
    const filtered = existing.filter(s => s.toLowerCase() !== q);
    const updated = [query.trim(), ...filtered].slice(0, MAX);
    await AsyncStorage.setItem(KEY, JSON.stringify(updated));
  } catch {
    // ignore storage errors silently
  }
}

export async function getRecentSearches(): Promise<string[]> {
  try {
    const raw = await AsyncStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}
