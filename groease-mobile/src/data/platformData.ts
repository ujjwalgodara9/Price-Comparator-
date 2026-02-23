// Adapted from web src/data/platformData.ts
// Change: removed Tailwind CSS class strings, replaced with React Native color values

import { Platform } from '../types/product';

export const platformNames: Record<Platform, string> = {
  'zepto': 'Zepto',
  'swiggy-instamart': 'Instamart',
  'bigbasket': 'BigBasket',
  'blinkit': 'Blinkit',
  'dmart': 'D-Mart',
};

// Emoji icons per platform
export const platformIcons: Record<Platform, string> = {
  'zepto': '⚡',
  'swiggy-instamart': '🔶',
  'bigbasket': '🛒',
  'blinkit': '🟡',
  'dmart': '🏪',
};

// Background colors for platform badges
export const platformBgColors: Record<Platform, string> = {
  'zepto': '#7C3AED',          // purple
  'swiggy-instamart': '#EA580C', // orange-600
  'bigbasket': '#059669',      // emerald-600
  'blinkit': '#D97706',        // amber-600
  'dmart': '#DC2626',          // red-600
};

// Text colors for platform badges
export const platformTextColors: Record<Platform, string> = {
  'zepto': '#FFFFFF',
  'swiggy-instamart': '#FFFFFF',
  'bigbasket': '#FFFFFF',
  'blinkit': '#FFFFFF',
  'dmart': '#FFFFFF',
};

export const allPlatforms: Platform[] = Object.keys(platformNames) as Platform[];
