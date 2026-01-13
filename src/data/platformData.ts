import { Platform } from '../types/product';

export const platformNames: Record<Platform, string> = {
  'zepto': 'Zepto',
  'swiggy-instamart': 'Swiggy Instamart',
  'bigbasket': 'BigBasket',
  'blinkit': 'Blinkit',
  'dmart': 'Dmart',
};

export const platformColors: Record<Platform, string> = {
  'zepto': 'bg-blue-600 text-white',
  'swiggy-instamart': 'bg-orange-500 text-white',
  'bigbasket': 'bg-green-600 text-white',
  'blinkit': 'bg-yellow-500 text-gray-900',
  'dmart': 'bg-red-500 text-white',
};

export const platformIcons: Record<Platform, string> = {
  'zepto': '⚡',
  'swiggy-instamart': '🛒',
  'bigbasket': '🛍️',
  'blinkit': '⚡',
  'dmart': '🛒',
};

export const allPlatforms: Platform[] = Object.keys(platformNames) as Platform[];

