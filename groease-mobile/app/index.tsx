// Home screen — app-like design inspired by Savvio
// Features:
//   - Gradient header with location bar
//   - Prominent search card
//   - Quick-search category chips
//   - Platform tiles grid
//   - Recent searches (AsyncStorage)

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  SafeAreaView,
  FlatList,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SearchBar } from '../src/components/SearchBar';
import { LocationModal } from '../src/components/LocationModal';
import { LocationService } from '../src/services/locationService';
import { addRecentSearch, getRecentSearches } from '../src/services/searchHistoryService';
import { LocationData } from '../src/types/product';
import { platformNames, platformBgColors, platformIcons } from '../src/data/platformData';

const LOCATION_KEY = 'userLocation';

const QUICK_CHIPS = [
  'Milk', 'Eggs', 'Bread', 'Rice', 'Atta',
  'Chicken', 'Dal', 'Oil', 'Chips', 'Butter',
];

const PLATFORM_TILES = [
  { key: 'zepto' as const,    label: 'Zepto' },
  { key: 'blinkit' as const,  label: 'Blinkit' },
  { key: 'bigbasket' as const, label: 'BigBasket' },
  { key: 'dmart' as const,    label: 'D-Mart' },
];

export default function HomeScreen() {
  const router = useRouter();
  const [location, setLocation] = useState<LocationData | null>(null);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  // Load saved location + recent searches on mount
  useEffect(() => {
    (async () => {
      try {
        const [savedLoc, recent] = await Promise.all([
          AsyncStorage.getItem(LOCATION_KEY),
          getRecentSearches(),
        ]);
        if (savedLoc) {
          setLocation(JSON.parse(savedLoc));
        } else {
          setShowLocationModal(true);
        }
        setRecentSearches(recent);
      } catch {
        setShowLocationModal(true);
      } finally {
        setInitializing(false);
      }
    })();
  }, []);

  const handleLocationSelect = useCallback(async (raw: {
    address: string;
    lat: number;
    lng: number;
    city?: string;
    state?: string;
    country?: string;
  }) => {
    if (!raw.address || raw.lat === 0) return;
    const locationData = await LocationService.convertAddressToLocationData(
      raw.address,
      raw.lat,
      raw.lng,
      raw.city != null || raw.state != null || raw.country != null
        ? { city: raw.city, state: raw.state, country: raw.country }
        : undefined
    );
    setLocation(locationData);
    await AsyncStorage.setItem(LOCATION_KEY, JSON.stringify(locationData));
    setShowLocationModal(false);
  }, []);

  const handleSearch = useCallback(async (query: string) => {
    const q = query.trim();
    if (!q) return;
    if (!location) {
      setShowLocationModal(true);
      return;
    }
    await addRecentSearch(q);
    setRecentSearches(await getRecentSearches());
    router.push({
      pathname: '/results',
      params: { query: q, location: JSON.stringify(location) },
    });
  }, [location]);

  const locationLabel = location
    ? LocationService.getLocationString(location)
    : 'Set location';

  if (initializing) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#059669" />
        <Text style={styles.loadingText}>PricePulse</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <LocationModal
        visible={showLocationModal}
        onSelect={handleLocationSelect}
        onClose={location ? () => setShowLocationModal(false) : undefined}
      />

      {/* Gradient header */}
      <LinearGradient
        colors={['#1D4ED8', '#0284C7']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.header}
      >
        {/* App name row */}
        <View style={styles.headerTop}>
          <View style={styles.brandRow}>
            <Text style={styles.logo}>PricePulse</Text>
            <Text style={styles.logoEmoji}>⚡</Text>
          </View>
          <Text style={styles.tagline}>Compare. Choose. Save.</Text>
        </View>

        {/* Location row */}
        <TouchableOpacity
          style={styles.locationBar}
          onPress={() => setShowLocationModal(true)}
          activeOpacity={0.8}
        >
          <Text style={styles.locationPin}>📍</Text>
          <Text style={styles.locationText} numberOfLines={1}>{locationLabel}</Text>
          <Text style={styles.locationChevron}>▼</Text>
        </TouchableOpacity>
      </LinearGradient>

      {/* Search card — overlaps header by 20px */}
      <View style={styles.searchCard}>
        <SearchBar onSearch={handleSearch} />

        {/* Quick category chips */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.chipsScroll}
          contentContainerStyle={styles.chipsContent}
        >
          {QUICK_CHIPS.map(chip => (
            <TouchableOpacity
              key={chip}
              style={styles.chip}
              onPress={() => handleSearch(chip)}
              activeOpacity={0.75}
            >
              <Text style={styles.chipText}>{chip}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <ScrollView
        style={styles.scroll}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* Recent searches */}
        {recentSearches.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>🕐 Recent</Text>
              <TouchableOpacity
                onPress={async () => {
                  await AsyncStorage.removeItem('recentSearches');
                  setRecentSearches([]);
                }}
                activeOpacity={0.7}
              >
                <Text style={styles.clearText}>Clear</Text>
              </TouchableOpacity>
            </View>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.recentRow}
            >
              {recentSearches.map(q => (
                <TouchableOpacity
                  key={q}
                  style={styles.recentChip}
                  onPress={() => handleSearch(q)}
                  activeOpacity={0.75}
                >
                  <Text style={styles.recentChipText}>🔍 {q}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}

        {/* Platform tiles */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🛒 We compare from</Text>
          <View style={styles.platformGrid}>
            {PLATFORM_TILES.map(p => (
              <View
                key={p.key}
                style={[styles.platformTile, { borderColor: platformBgColors[p.key] + '44' }]}
              >
                <View style={[styles.platformIconCircle, { backgroundColor: platformBgColors[p.key] }]}>
                  <Text style={styles.platformIconEmoji}>{platformIcons[p.key]}</Text>
                </View>
                <Text style={styles.platformTileLabel}>{platformNames[p.key]}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* How it works */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>⚡ How it works</Text>
          <View style={styles.stepsRow}>
            {[
              { icon: '🔍', label: 'Search a product' },
              { icon: '⚖️', label: 'Compare prices' },
              { icon: '🛍️', label: 'Order smart' },
            ].map((s, i) => (
              <React.Fragment key={s.label}>
                <View style={styles.step}>
                  <View style={styles.stepBubble}>
                    <Text style={styles.stepEmoji}>{s.icon}</Text>
                  </View>
                  <Text style={styles.stepLabel}>{s.label}</Text>
                </View>
                {i < 2 && <Text style={styles.stepArrow}>›</Text>}
              </React.Fragment>
            ))}
          </View>
        </View>

        <View style={{ height: 32 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#F0F9FF' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 14, backgroundColor: '#F0F9FF' },
  loadingText: { color: '#1D4ED8', fontWeight: '900', fontSize: 22, letterSpacing: 1 },

  // Gradient header
  header: {
    paddingTop: 12,
    paddingBottom: 30,
    paddingHorizontal: 20,
    gap: 10,
  },
  headerTop: { gap: 2 },
  brandRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  logo: { fontSize: 26, fontWeight: '900', color: '#FFFFFF', letterSpacing: 0.5 },
  logoEmoji: { fontSize: 22 },
  tagline: { fontSize: 13, color: 'rgba(255,255,255,0.75)', fontWeight: '500' },

  // Location bar inside header
  locationBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 8,
    gap: 6,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.25)',
  },
  locationPin: { fontSize: 14 },
  locationText: { flex: 1, fontSize: 13, fontWeight: '600', color: '#FFFFFF' },
  locationChevron: { fontSize: 10, color: 'rgba(255,255,255,0.7)' },

  // Search card overlapping header
  searchCard: {
    marginHorizontal: 16,
    marginTop: -20,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 14,
    shadowColor: '#1D4ED8',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 12,
    elevation: 6,
    gap: 12,
  },

  chipsScroll: { marginHorizontal: -4 },
  chipsContent: {
    paddingHorizontal: 4,
    gap: 8,
    flexDirection: 'row',
  },
  chip: {
    backgroundColor: '#EFF6FF',
    borderWidth: 1.5,
    borderColor: '#BFDBFE',
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 6,
  },
  chipText: { fontSize: 13, fontWeight: '600', color: '#1D4ED8' },

  scroll: { flex: 1 },
  scrollContent: { paddingTop: 20, paddingHorizontal: 16 },

  // Sections
  section: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 14,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 1,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 12,
  },
  clearText: { fontSize: 13, fontWeight: '600', color: '#DC2626' },

  // Recent searches
  recentRow: { gap: 8, flexDirection: 'row' },
  recentChip: {
    backgroundColor: '#F3F4F6',
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  recentChipText: { fontSize: 13, fontWeight: '600', color: '#374151' },

  // Platform tiles grid
  platformGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  platformTile: {
    width: '47%',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    borderWidth: 1.5,
    padding: 12,
  },
  platformIconCircle: {
    width: 38,
    height: 38,
    borderRadius: 19,
    alignItems: 'center',
    justifyContent: 'center',
  },
  platformIconEmoji: { fontSize: 18 },
  platformTileLabel: { fontSize: 13, fontWeight: '700', color: '#111827', flex: 1 },

  // Steps
  stepsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  step: { alignItems: 'center', gap: 8, flex: 1 },
  stepBubble: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: '#ECFDF5',
    borderWidth: 2,
    borderColor: '#6EE7B7',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepEmoji: { fontSize: 22 },
  stepLabel: { fontSize: 11, fontWeight: '600', color: '#374151', textAlign: 'center', lineHeight: 15 },
  stepArrow: { fontSize: 22, color: '#D1D5DB', marginBottom: 20 },
});
