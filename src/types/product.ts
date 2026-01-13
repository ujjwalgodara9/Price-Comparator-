export interface Product {
  id: string;
  name: string;
  description: string;
  image: string;
  price: number;
  currency: string;
  platform: Platform;
  availability: boolean;
  rating: number;
  reviewCount: number;
  features: string[];
  link: string;
  location: string;
  deliveryTime?: string; // e.g., "10-15 mins", "30 mins", "1 hour"
  deliveryFee?: number;
  originalPrice?: number; // For showing discounts
  quantity?: string; // e.g., "5 kg", "10 kg", "1 kg"
}

// Matched product structure from backend (contains all platforms in one object)
export interface MatchedProduct {
  name: string;
  image: string;
  original_names: Record<Platform, string>;
  platforms: Record<Platform, {
    price: number;
    quantity: string;
    deliveryTime: string;
    link: string;
  }>;
}

export type Platform = 
  | 'zepto' 
  | 'swiggy-instamart' 
  | 'bigbasket' 
  | 'blinkit'
  | 'dmart';

export interface LocationData {
  city: string;
  state: string;
  country: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
}

export interface ComparisonFilters {
  platforms: Platform[];
  minPrice?: number;
  maxPrice?: number;
  minRating?: number;
  sortBy: 'price-low' | 'price-high' | 'rating' | 'reviews' | 'delivery-time';
  maxDeliveryTime?: number; // Maximum delivery time in minutes
}

