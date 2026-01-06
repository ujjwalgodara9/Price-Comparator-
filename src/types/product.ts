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
}

export type Platform = 'amazon' | 'flipkart' | 'myntra' | 'nykaa' | 'meesho' | 'ajio' | 'snapdeal' | 'tatacliq';

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
  sortBy: 'price-low' | 'price-high' | 'rating' | 'reviews';
}

