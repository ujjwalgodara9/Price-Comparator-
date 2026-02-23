// Bottom sheet for sort + platform filter + max price
// Slides up from bottom, same pattern as LocationModal

import React, { useState } from 'react';
import {
  Modal,
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  TextInput,
  StyleSheet,
  Platform as RNPlatform,
} from 'react-native';
import { ComparisonFilters, Platform } from '../types/product';
import { platformNames, platformBgColors } from '../data/platformData';
import { allPlatforms } from '../data/platformData';

interface FilterSheetProps {
  visible: boolean;
  filters: ComparisonFilters;
  onApply: (filters: ComparisonFilters) => void;
  onClose: () => void;
}

const SORT_OPTIONS: { value: ComparisonFilters['sortBy']; label: string; icon: string }[] = [
  { value: 'price-low', label: 'Price: Low → High', icon: '💰' },
  { value: 'price-high', label: 'Price: High → Low', icon: '💎' },
  { value: 'delivery-time', label: 'Fastest Delivery', icon: '🚀' },
  { value: 'rating', label: 'Best Rated', icon: '⭐' },
];

export function FilterSheet({ visible, filters, onApply, onClose }: FilterSheetProps) {
  const [localFilters, setLocalFilters] = useState<ComparisonFilters>(filters);
  const [maxPriceText, setMaxPriceText] = useState(
    filters.maxPrice ? String(filters.maxPrice) : ''
  );

  const togglePlatform = (platform: Platform) => {
    const current = localFilters.platforms;
    const next = current.includes(platform)
      ? current.filter(p => p !== platform)
      : [...current, platform];
    // Require at least 1 platform
    if (next.length === 0) return;
    setLocalFilters(f => ({ ...f, platforms: next }));
  };

  const handleApply = () => {
    const maxPrice = maxPriceText.trim() ? Number(maxPriceText) : undefined;
    onApply({ ...localFilters, maxPrice });
  };

  const handleReset = () => {
    const reset: ComparisonFilters = {
      platforms: [...allPlatforms],
      sortBy: 'price-low',
      maxPrice: undefined,
    };
    setLocalFilters(reset);
    setMaxPriceText('');
  };

  return (
    <Modal visible={visible} animationType="slide" transparent statusBarTranslucent>
      <View style={styles.overlay}>
        <View style={styles.sheet}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.title}>Filter & Sort</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
              <Text style={styles.closeBtnText}>✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView showsVerticalScrollIndicator={false} style={styles.body}>
            {/* Sort section */}
            <Text style={styles.sectionTitle}>Sort by</Text>
            <View style={styles.sortOptions}>
              {SORT_OPTIONS.map(opt => {
                const active = localFilters.sortBy === opt.value;
                return (
                  <TouchableOpacity
                    key={opt.value}
                    style={[styles.sortOption, active && styles.sortOptionActive]}
                    onPress={() => setLocalFilters(f => ({ ...f, sortBy: opt.value }))}
                    activeOpacity={0.7}
                  >
                    <Text style={styles.sortIcon}>{opt.icon}</Text>
                    <Text style={[styles.sortLabel, active && styles.sortLabelActive]}>
                      {opt.label}
                    </Text>
                    {active && <Text style={styles.checkmark}>✓</Text>}
                  </TouchableOpacity>
                );
              })}
            </View>

            {/* Platforms section */}
            <Text style={styles.sectionTitle}>Platforms</Text>
            <View style={styles.platformGrid}>
              {allPlatforms.map(platform => {
                const active = localFilters.platforms.includes(platform);
                return (
                  <TouchableOpacity
                    key={platform}
                    style={[
                      styles.platformChip,
                      active
                        ? { backgroundColor: platformBgColors[platform], borderColor: platformBgColors[platform] }
                        : styles.platformChipInactive,
                    ]}
                    onPress={() => togglePlatform(platform)}
                    activeOpacity={0.7}
                  >
                    <Text style={[styles.platformChipText, !active && styles.platformChipTextInactive]}>
                      {platformNames[platform]}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>

            {/* Max price section */}
            <Text style={styles.sectionTitle}>Max Price (₹)</Text>
            <TextInput
              style={styles.priceInput}
              value={maxPriceText}
              onChangeText={setMaxPriceText}
              placeholder="e.g. 500 (leave blank for no limit)"
              placeholderTextColor="#9CA3AF"
              keyboardType="numeric"
              returnKeyType="done"
            />

            <View style={{ height: 20 }} />
          </ScrollView>

          {/* Action buttons */}
          <View style={styles.actions}>
            <TouchableOpacity style={styles.resetBtn} onPress={handleReset} activeOpacity={0.7}>
              <Text style={styles.resetBtnText}>Reset</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.applyBtn} onPress={handleApply} activeOpacity={0.7}>
              <Text style={styles.applyBtnText}>Apply Filters</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '88%',
    paddingBottom: RNPlatform.OS === 'android' ? 16 : 32,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#2563EB',
    paddingHorizontal: 20,
    paddingTop: 24,
    paddingBottom: 20,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  title: { fontSize: 18, fontWeight: '800', color: '#FFFFFF' },
  closeBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeBtnText: { color: '#FFFFFF', fontSize: 16, fontWeight: '700' },

  body: { paddingHorizontal: 20, paddingTop: 16 },

  sectionTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#374151',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 12,
    marginTop: 20,
  },

  sortOptions: { gap: 8 },
  sortOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
    gap: 10,
  },
  sortOptionActive: {
    borderColor: '#2563EB',
    backgroundColor: '#EFF6FF',
  },
  sortIcon: { fontSize: 16 },
  sortLabel: { flex: 1, fontSize: 14, color: '#374151', fontWeight: '500' },
  sortLabelActive: { color: '#1D4ED8', fontWeight: '700' },
  checkmark: { fontSize: 14, color: '#2563EB', fontWeight: '700' },

  platformGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  platformChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1.5,
  },
  platformChipInactive: {
    backgroundColor: '#F9FAFB',
    borderColor: '#D1D5DB',
  },
  platformChipText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  platformChipTextInactive: {
    color: '#6B7280',
  },

  priceInput: {
    height: 48,
    borderWidth: 1.5,
    borderColor: '#D1D5DB',
    borderRadius: 10,
    paddingHorizontal: 14,
    fontSize: 15,
    color: '#111827',
    backgroundColor: '#F9FAFB',
  },

  actions: {
    flexDirection: 'row',
    gap: 12,
    paddingHorizontal: 20,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  resetBtn: {
    flex: 1,
    height: 48,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: '#D1D5DB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  resetBtnText: { fontSize: 14, fontWeight: '700', color: '#374151' },
  applyBtn: {
    flex: 2,
    height: 48,
    borderRadius: 12,
    backgroundColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  applyBtnText: { fontSize: 14, fontWeight: '700', color: '#FFFFFF' },
});
