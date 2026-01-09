import { Platform } from '../types/product';

export const platformNames: Record<Platform, string> = {
  'zepto': 'Zepto',
  'swiggy-instamart': 'Swiggy Instamart',
  'bigbasket': 'BigBasket',
  'blinkit': 'Blinkit',
};

export const platformColors: Record<Platform, string> = {
  'zepto': 'bg-purple-500',
  'swiggy-instamart': 'bg-orange-500',
  'bigbasket': 'bg-green-500',
  'blinkit': 'bg-yellow-500',
};

export const platformIcons: Record<Platform, string> = {
  'zepto': '⚡',
  'swiggy-instamart': '🛒',
  'bigbasket': '🛍️',
  'blinkit': '⚡',
};

export const allPlatforms: Platform[] = Object.keys(platformNames) as Platform[];

