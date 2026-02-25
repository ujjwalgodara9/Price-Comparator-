// Results screen — search results + filter/sort controls
//
// Added vs original:
//   - FilterSheet integration (sort + platform toggles + max price)
//   - Active filter chips row showing current active filters
//   - Client-side re-sort/filter when user changes options (no re-fetch needed)
//   - Slowness notice while loading (Playwright scraping takes 30-60s)

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { useLocalSearchParams, useNavigation } from 'expo-router';
import { ProductCard } from '../src/components/ProductCard';
import { ProgressBar } from '../src/components/ProgressBar';
import { FilterSheet } from '../src/components/FilterSheet';
import { LocationModal } from '../src/components/LocationModal';
import { ProductService } from '../src/services/productService';
import { allPlatforms } from '../src/data/platformData';
import {
  LocationData,
  MatchedProduct,
  Platform,
  ComparisonFilters,
} from '../src/types/product';

const DEFAULT_FILTERS: ComparisonFilters = {
  platforms: [...allPlatforms],
  sortBy: 'rating',
};

const SORT_LABELS: Record<ComparisonFilters['sortBy'], string> = {
  'price-low': 'Price ↑',
  'price-high': 'Price ↓',
  'delivery-time': 'Fastest',
  'rating': 'Rated',
  'reviews': 'Reviews',
};

export default function ResultsScreen() {
  const { query, location: locationStr } = useLocalSearchParams<{
    query: string;
    location: string;
  }>();

  const navigation = useNavigation();

  // Raw results from backend (never mutated after fetch)
  const [rawProducts, setRawProducts] = useState<MatchedProduct[]>([]);
  // Displayed results (re-computed whenever filters change)
  const [products, setProducts] = useState<MatchedProduct[]>([]);

  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<ComparisonFilters>(DEFAULT_FILTERS);
  const [showFilter, setShowFilter] = useState(false);
  const [showLocationModal, setShowLocationModal] = useState(false);

  const parsedLocation: LocationData | null = locationStr
    ? JSON.parse(locationStr as string)
    : null;
  const [currentLocation, setCurrentLocation] = useState<LocationData | null>(parsedLocation);

  // Update nav title
  useEffect(() => {
    if (query) {
      navigation.setOptions({ title: `"${query}"` });
    }
  }, [query]);

  // Re-sort/filter whenever raw results or filters change
  useEffect(() => {
    if (rawProducts.length > 0) {
      setProducts(ProductService.sortProducts(rawProducts, filters));
    } else {
      setProducts([]);
    }
  }, [rawProducts, filters]);

  // Progress bar animation
  useEffect(() => {
    if (!loading) {
      setProgress(0);
      return;
    }
    const startTime = Date.now();
    const durationTo90 = 25000; // 25s to reach 90%
    const easeInOutCubic = (t: number) =>
      t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const t = Math.min(elapsed / durationTo90, 1);
      setProgress(Math.min(easeInOutCubic(t) * 90, 90));
    }, 100);

    return () => clearInterval(interval);
  }, [loading]);

  // Handle location change from modal
  const handleLocationChange = useCallback((selected: {
    address: string; lat: number; lng: number;
    city?: string; state?: string; country?: string;
  }) => {
    const newLocation: LocationData = {
      city: selected.city || selected.address,
      state: selected.state || '',
      country: selected.country || 'India',
      coordinates: { lat: selected.lat, lng: selected.lng },
    };
    setCurrentLocation(newLocation);
    setShowLocationModal(false);
  }, []);

  // Fetch products from backend
  useEffect(() => {
    if (!query || !currentLocation) return;

    (async () => {
      setLoading(true);
      setError(null);
      setRawProducts([]);

      try {
        const results = await ProductService.searchProducts(
          query as string,
          currentLocation,
          { ...DEFAULT_FILTERS, platforms: [...allPlatforms] }
        );
        setRawProducts(results);
        setProgress(100);
        setTimeout(() => {
          setLoading(false);
          setProgress(0);
        }, 400);
      } catch (err) {
        console.error('[ResultsScreen] Search error:', err);
        setError('Failed to fetch results. Check your network and backend URL in config.ts.');
        setLoading(false);
      }
    })();
  }, [query, currentLocation]);

  const handleApplyFilters = useCallback((newFilters: ComparisonFilters) => {
    setFilters(newFilters);
    setShowFilter(false);
  }, []);

  const locationDisplay = currentLocation
    ? (currentLocation.city || currentLocation.state || 'Unknown location')
    : 'Location not set';

  // Active filter chips — show non-default settings
  const activeChips: string[] = [];
  if (filters.sortBy !== 'price-low') activeChips.push(`Sort: ${SORT_LABELS[filters.sortBy]}`);
  if (filters.platforms.length < allPlatforms.length)
    activeChips.push(`${filters.platforms.length} platform${filters.platforms.length !== 1 ? 's' : ''}`);
  if (filters.maxPrice) activeChips.push(`≤ ₹${filters.maxPrice}`);
  const hasActiveFilters = activeChips.length > 0;

  return (
    <SafeAreaView style={styles.safe}>
      {/* Info bar: query + count + filter button */}
      <View style={styles.infoBar}>
        <View style={styles.infoLeft}>
          <Text style={styles.queryText}>
            {loading ? 'Searching ' : 'Results for '}
            <Text style={styles.queryBold}>"{query}"</Text>
          </Text>
          {!loading && (
            <Text style={styles.countText}>
              {products.length} result{products.length !== 1 ? 's' : ''}
            </Text>
          )}
        </View>
        <TouchableOpacity
          style={[styles.filterBtn, hasActiveFilters && styles.filterBtnActive]}
          onPress={() => setShowFilter(true)}
          activeOpacity={0.7}
        >
          <Text style={[styles.filterBtnIcon, hasActiveFilters && styles.filterBtnIconActive]}>⚙</Text>
          <Text style={[styles.filterBtnText, hasActiveFilters && styles.filterBtnTextActive]}>
            Filter
          </Text>
          {hasActiveFilters && <View style={styles.filterDot} />}
        </TouchableOpacity>
      </View>

      {/* Location bar */}
      <View style={styles.locationBar}>
        <Text style={styles.locationPin} numberOfLines={1}>📍 {locationDisplay}</Text>
        <TouchableOpacity
          style={styles.changeLocationBtn}
          onPress={() => setShowLocationModal(true)}
          activeOpacity={0.7}
        >
          <Text style={styles.changeLocationText}>Change</Text>
        </TouchableOpacity>
      </View>

      {/* Active filter chips */}
      {hasActiveFilters && !loading && (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.chipsRow}
          contentContainerStyle={styles.chipsContent}
        >
          {activeChips.map(chip => (
            <View key={chip} style={styles.chip}>
              <Text style={styles.chipText}>{chip}</Text>
            </View>
          ))}
          <TouchableOpacity
            style={styles.clearChip}
            onPress={() => setFilters(DEFAULT_FILTERS)}
            activeOpacity={0.7}
          >
            <Text style={styles.clearChipText}>✕ Clear</Text>
          </TouchableOpacity>
        </ScrollView>
      )}

      {/* Progress bar */}
      {loading && <ProgressBar progress={progress} label="⚡ 🟡 🛒 🏪  Comparing prices..." />}

      {/* Slowness notice */}
      {loading && (
        <View style={styles.slowNote}>
          <Text style={styles.slowNoteText}>
            ⏳ First search takes 30–60s — we open each platform live to get real prices
          </Text>
        </View>
      )}

      {/* Error */}
      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* No results after filter */}
      {!loading && !error && products.length === 0 && rawProducts.length > 0 && (
        <View style={styles.emptyBox}>
          <Text style={styles.emptyIcon}>🔍</Text>
          <Text style={styles.emptyTitle}>No results match your filters</Text>
          <TouchableOpacity onPress={() => setFilters(DEFAULT_FILTERS)} activeOpacity={0.7}>
            <Text style={styles.emptyAction}>Clear filters</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* No results from backend */}
      {!loading && !error && rawProducts.length === 0 && (
        <View style={styles.emptyBox}>
          <Text style={styles.emptyIcon}>✨</Text>
          <Text style={styles.emptyTitle}>No products found</Text>
          <Text style={styles.emptySub}>
            Try grocery items like "milk", "bread", "chips" or "atta"
          </Text>
        </View>
      )}

      {/* Product list — single column so multi-platform rows are readable */}
      {!loading && products.length > 0 && (
        <FlatList
          data={products}
          keyExtractor={(item, index) => `${item.name}-${index}`}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          ItemSeparatorComponent={() => <View style={{ height: 10 }} />}
          renderItem={({ item }) => <ProductCard matchedProduct={item} />}
        />
      )}

      {/* Filter sheet */}
      <FilterSheet
        visible={showFilter}
        filters={filters}
        onApply={handleApplyFilters}
        onClose={() => setShowFilter(false)}
      />

      {/* Location change modal */}
      <LocationModal
        visible={showLocationModal}
        onSelect={handleLocationChange}
        onClose={() => setShowLocationModal(false)}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#F8FAFF' },

  infoBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#DBEAFE',
  },
  infoLeft: { flex: 1, gap: 2 },
  queryText: { fontSize: 13, color: '#3B82F6' },
  queryBold: { fontWeight: '700', color: '#1D4ED8' },
  countText: { fontSize: 12, color: '#6B7280' },

  filterBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 20,
    borderWidth: 1.5,
    borderColor: '#D1D5DB',
    backgroundColor: '#F9FAFB',
    gap: 4,
  },
  filterBtnActive: { borderColor: '#059669', backgroundColor: '#ECFDF5' },
  filterBtnIcon: { fontSize: 14, color: '#6B7280' },
  filterBtnIconActive: { color: '#059669' },
  filterBtnText: { fontSize: 13, fontWeight: '600', color: '#374151' },
  filterBtnTextActive: { color: '#059669' },
  filterDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#059669', marginLeft: 2 },

  locationBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 7,
    backgroundColor: '#F0FDFA',
    borderBottomWidth: 1,
    borderBottomColor: '#99F6E4',
  },
  locationPin: { fontSize: 13, color: '#374151', flex: 1, marginRight: 8 },
  changeLocationBtn: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    backgroundColor: '#EFF6FF',
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  changeLocationText: { fontSize: 12, fontWeight: '700', color: '#2563EB' },

  chipsRow: {
    maxHeight: 44,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#DBEAFE',
  },
  chipsContent: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    gap: 8,
    flexDirection: 'row',
    alignItems: 'center',
  },
  chip: {
    backgroundColor: '#EFF6FF',
    borderWidth: 1,
    borderColor: '#BFDBFE',
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  chipText: { fontSize: 12, fontWeight: '600', color: '#1D4ED8' },
  clearChip: {
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#FECACA',
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  clearChipText: { fontSize: 12, fontWeight: '600', color: '#DC2626' },

  slowNote: {
    marginHorizontal: 16,
    marginTop: 10,
    padding: 12,
    backgroundColor: '#FFFBEB',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#FDE68A',
  },
  slowNoteText: { fontSize: 12, color: '#92400E', lineHeight: 18 },

  errorBox: {
    margin: 16,
    padding: 16,
    backgroundColor: '#FEF2F2',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#FECACA',
    alignItems: 'center',
    gap: 8,
  },
  errorIcon: { fontSize: 28 },
  errorText: { color: '#DC2626', fontSize: 13, textAlign: 'center', lineHeight: 20 },

  emptyBox: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 10, padding: 32 },
  emptyIcon: { fontSize: 44 },
  emptyTitle: { fontSize: 16, fontWeight: '700', color: '#1E3A5F', textAlign: 'center' },
  emptySub: { fontSize: 13, color: '#6B7280', textAlign: 'center' },
  emptyAction: { fontSize: 14, fontWeight: '700', color: '#2563EB', textDecorationLine: 'underline' },

  listContent: { padding: 12 },
});
