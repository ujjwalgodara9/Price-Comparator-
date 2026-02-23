// Displays a colored platform badge with emoji prefix + optional "BEST" tag

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Platform } from '../types/product';
import { platformNames, platformBgColors, platformTextColors, platformIcons } from '../data/platformData';

interface PlatformBadgeProps {
  platform: Platform;
  isCheapest?: boolean;
}

export function PlatformBadge({ platform, isCheapest }: PlatformBadgeProps) {
  return (
    <View style={styles.row}>
      <View style={[styles.badge, { backgroundColor: platformBgColors[platform] }]}>
        <Text style={styles.badgeIcon}>{platformIcons[platform]}</Text>
        <Text style={[styles.badgeText, { color: platformTextColors[platform] }]}>
          {platformNames[platform]}
        </Text>
      </View>
      {isCheapest && (
        <View style={styles.bestBadge}>
          <Text style={styles.bestText}>BEST</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    gap: 6,
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 9,
    paddingVertical: 4,
    borderRadius: 8,
  },
  badgeIcon: {
    fontSize: 11,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '700',
  },
  bestBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    backgroundColor: '#059669',
  },
  bestText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '700',
  },
});
