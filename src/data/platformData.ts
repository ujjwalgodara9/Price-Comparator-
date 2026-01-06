import { Platform } from '../types/product';

export const platformNames: Record<Platform, string> = {
  'zepto': 'Zepto',
  'swiggy-instamart': 'Swiggy Instamart',
  'bigbasket': 'BigBasket',
  'flipkart-minutes': 'Flipkart Minutes',
  'blinkit': 'Blinkit',
  'dunzo': 'Dunzo',
  'demart-ready': 'Demart Ready',
  'amazon-prime-now': 'Amazon Prime Now',
};

export const platformColors: Record<Platform, string> = {
  'zepto': 'bg-purple-500',
  'swiggy-instamart': 'bg-orange-500',
  'bigbasket': 'bg-green-500',
  'flipkart-minutes': 'bg-blue-500',
  'blinkit': 'bg-yellow-500',
  'dunzo': 'bg-red-500',
  'demart-ready': 'bg-indigo-500',
  'amazon-prime-now': 'bg-teal-500',
};

export const platformIcons: Record<Platform, string> = {
  'zepto': '⚡',
  'swiggy-instamart': '🛒',
  'bigbasket': '🛍️',
  'flipkart-minutes': '⚡',
  'blinkit': '⚡',
  'dunzo': '🚚',
  'demart-ready': '📦',
  'amazon-prime-now': '📦',
};

export const allPlatforms: Platform[] = Object.keys(platformNames) as Platform[];

