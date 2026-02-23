// Product comparison card
// Shows all platforms for a matched product, sorted cheapest first.
// Cheapest row gets a green left accent stripe + BEST badge.
// Savings banner shown at top of card when multiple platforms differ in price.

import React from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  Linking,
  StyleSheet,
} from 'react-native';
import { MatchedProduct, Platform } from '../types/product';
import { PlatformBadge } from './PlatformBadge';

interface ProductCardProps {
  matchedProduct: MatchedProduct;
}

export function ProductCard({ matchedProduct }: ProductCardProps) {
  const platforms = Object.keys(matchedProduct.platforms || {}) as Platform[];
  if (platforms.length === 0) return null;

  // Sort platforms by price ascending
  const platformEntries = platforms.map(platform => ({
    platform,
    ...matchedProduct.platforms[platform],
  }));
  const sorted = platformEntries.sort((a, b) => a.price - b.price);
  const cheapestPrice = sorted[0].price;
  const mostExpensivePrice = sorted[sorted.length - 1].price;
  const savings = mostExpensivePrice - cheapestPrice;
  const hasComparison = sorted.length > 1 && savings > 0;

  const handleOpenLink = async (link: string) => {
    if (!link || link === 'N/A' || !link.trim()) return;
    try {
      const canOpen = await Linking.canOpenURL(link);
      if (canOpen) await Linking.openURL(link);
    } catch (e) {
      console.warn('[ProductCard] Cannot open URL:', link);
    }
  };

  return (
    <View style={styles.card}>
      {/* Savings banner — full width, shown when price gap exists */}
      {hasComparison && (
        <View style={styles.savingsBanner}>
          <Text style={styles.savingsBannerText}>
            💰 Save ₹{savings.toFixed(savings % 1 === 0 ? 0 : 2)} on this product
          </Text>
          <View style={styles.platformCountPill}>
            <Text style={styles.platformCountText}>{sorted.length} platforms</Text>
          </View>
        </View>
      )}

      {/* Top row: image + name */}
      <View style={styles.topRow}>
        <Image
          source={{
            uri:
              matchedProduct.image?.trim()
                ? matchedProduct.image
                : 'https://placehold.co/120x120/ECFDF5/059669?text=Item',
          }}
          style={styles.image}
          resizeMode="cover"
        />
        <View style={styles.nameCol}>
          <Text style={styles.productName} numberOfLines={3}>
            {matchedProduct.name}
          </Text>
          {!hasComparison && sorted.length > 1 && (
            <View style={styles.samePrice}>
              <Text style={styles.samePriceText}>Same price on {sorted.length} platforms</Text>
            </View>
          )}
        </View>
      </View>

      {/* Platform rows */}
      <View style={styles.platformList}>
        {sorted.map((entry, index) => {
          const isCheapest = entry.price === cheapestPrice;
          const quantity = entry.quantity || '';

          return (
            <View
              key={`${entry.platform}-${index}`}
              style={[
                styles.platformRow,
                isCheapest ? styles.cheapestRow : styles.normalRow,
              ]}
            >
              {/* Green left accent stripe on cheapest */}
              {isCheapest && <View style={styles.cheapestStripe} />}

              <View style={styles.rowInner}>
                {/* Platform badge + price */}
                <View style={styles.rowHeader}>
                  <PlatformBadge platform={entry.platform} isCheapest={isCheapest} />
                  <View style={styles.priceBlock}>
                    <Text style={[styles.price, isCheapest && styles.cheapestPrice]}>
                      ₹{entry.price.toLocaleString()}
                    </Text>
                    {quantity ? (
                      <Text style={styles.quantity}>{quantity}</Text>
                    ) : null}
                  </View>
                </View>

                {/* Delivery time + View button */}
                <View style={styles.rowFooter}>
                  {entry.deliveryTime ? (
                    <View style={styles.deliveryChip}>
                      <Text style={styles.deliveryIcon}>🚀</Text>
                      <Text style={styles.deliveryText}>{entry.deliveryTime}</Text>
                    </View>
                  ) : (
                    <View />
                  )}
                  {entry.link && entry.link !== 'N/A' && entry.link.trim() !== '' && (
                    <TouchableOpacity
                      style={styles.viewButton}
                      onPress={() => handleOpenLink(entry.link)}
                      activeOpacity={0.7}
                    >
                      <Text style={styles.viewButtonText}>View ↗</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>
            </View>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#D1FAE5',
    overflow: 'hidden',
    shadowColor: '#059669',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.07,
    shadowRadius: 6,
    elevation: 2,
  },

  // Savings banner
  savingsBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#ECFDF5',
    borderBottomWidth: 1,
    borderBottomColor: '#6EE7B7',
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  savingsBannerText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#065F46',
    flex: 1,
  },
  platformCountPill: {
    backgroundColor: '#D1FAE5',
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginLeft: 8,
  },
  platformCountText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#059669',
  },

  topRow: {
    flexDirection: 'row',
    gap: 12,
    padding: 12,
    paddingBottom: 8,
  },
  image: {
    width: 80,
    height: 80,
    borderRadius: 10,
    backgroundColor: '#ECFDF5',
    flexShrink: 0,
  },
  nameCol: {
    flex: 1,
    gap: 6,
    justifyContent: 'flex-start',
    paddingTop: 2,
  },
  productName: {
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
    lineHeight: 20,
  },
  samePrice: {
    backgroundColor: '#F3F4F6',
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
    alignSelf: 'flex-start',
  },
  samePriceText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#6B7280',
  },

  platformList: { gap: 0, paddingHorizontal: 12, paddingBottom: 12 },

  platformRow: {
    flexDirection: 'row',
    borderRadius: 10,
    borderWidth: 1.5,
    marginTop: 8,
    overflow: 'hidden',
  },
  cheapestRow: {
    backgroundColor: '#ECFDF5',
    borderColor: '#6EE7B7',
  },
  normalRow: {
    backgroundColor: '#F9FAFB',
    borderColor: '#E5E7EB',
  },

  // Green left stripe on cheapest platform row
  cheapestStripe: {
    width: 4,
    backgroundColor: '#059669',
  },

  rowInner: {
    flex: 1,
    padding: 10,
    gap: 8,
  },

  rowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  priceBlock: { alignItems: 'flex-end' },
  price: {
    fontSize: 22,
    fontWeight: '800',
    color: '#111827',
  },
  cheapestPrice: { color: '#059669' },
  quantity: {
    fontSize: 11,
    color: '#6B7280',
    fontWeight: '500',
    marginTop: 1,
  },

  rowFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 6,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  deliveryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0F9FF',
    borderWidth: 1,
    borderColor: '#BAE6FD',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 3,
    gap: 4,
  },
  deliveryIcon: { fontSize: 11 },
  deliveryText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#0369A1',
  },

  viewButton: {
    backgroundColor: '#ECFDF5',
    borderWidth: 1,
    borderColor: '#6EE7B7',
    borderRadius: 7,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  viewButtonText: {
    color: '#059669',
    fontSize: 12,
    fontWeight: '700',
  },
});
