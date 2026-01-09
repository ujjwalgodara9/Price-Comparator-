"""
Product Comparison Algorithm
Takes platform-specific JSON files and finds matching products across platforms
Uses similarity matching to handle name variations
"""

import json
import os
import re
from difflib import SequenceMatcher
from typing import Dict, List, Any, Optional
from datetime import datetime


def normalize_product_name(name: str) -> str:
    """
    Normalize product name for better matching:
    - Remove text in brackets (parentheses, square brackets, curly braces)
    - Convert to lowercase
    - Remove special characters and extra spaces
    - Remove common words that don't help matching
    """
    # Remove text within brackets (parentheses, square brackets, curly braces)
    # This removes things like "(5 kg)", "[Premium]", "{Organic}" etc.
    normalized = re.sub(r'[\(\[\{][^\)\]\}]*[\)\]\}]', '', name)
    
    # Convert to lowercase
    normalized = normalized.lower()
    
    # Remove common prefixes/suffixes that don't help matching
    normalized = re.sub(r'\b(100%|0%|with|without|for|the|a|an)\b', '', normalized)
    
    # Remove special characters but keep spaces
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized.strip()


def extract_quantity(name: str) -> Optional[str]:
    """
    Extract quantity/weight from product name
    Examples: "5 kg", "10 kg", "1 kg", "500 g"
    """
    # Pattern to match weight/quantity
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:kg|g|gm|gram|kilograms?|grams?)',  # Standard weight formats
        r'\((\d+(?:\.\d+)?)\s*(?:kg|g|gm|gram|kilograms?|grams?)\)',  # Weight in parentheses
        r'(\d+(?:\.\d+)?)\s*(?:pack|pcs?|pieces?)',  # Pack/pieces
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            value = match.group(1)
            unit = match.group(2) if len(match.groups()) > 1 else ''
            # Try to find unit in the match
            full_match = match.group(0)
            if 'kg' in full_match.lower() or 'kilogram' in full_match.lower():
                return f"{value} kg"
            elif 'g' in full_match.lower() or 'gram' in full_match.lower():
                return f"{value} g"
            return full_match
    
    return None


def calculate_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two product names
    Returns a value between 0 and 1
    """
    normalized1 = normalize_product_name(name1)
    normalized2 = normalize_product_name(name2)
    
    # Use SequenceMatcher for similarity
    similarity = SequenceMatcher(None, normalized1, normalized2).ratio()
    
    # Boost similarity if key words match
    words1 = set(normalized1.split())
    words2 = set(normalized2.split())
    
    if words1 and words2:
        common_words = words1.intersection(words2)
        word_similarity = len(common_words) / max(len(words1), len(words2))
        # Combine both metrics
        similarity = (similarity * 0.6) + (word_similarity * 0.4)
    
    return similarity


def find_matching_products(products1: List[Dict], products2: List[Dict], 
                          similarity_threshold: float = 0.6) -> List[Dict]:
    """
    Find matching products between two product lists
    Returns a list of matched products with platform-specific data
    """
    matched_products = []
    used_indices_1 = set()
    used_indices_2 = set()
    
    # Try to match products
    for i, product1 in enumerate(products1):
        if i in used_indices_1:
            continue
            
        best_match_idx = None
        best_similarity = 0
        
        for j, product2 in enumerate(products2):
            if j in used_indices_2:
                continue
            
            similarity = calculate_similarity(product1['name'], product2['name'])
            
            if similarity > best_similarity and similarity >= similarity_threshold:
                best_similarity = similarity
                best_match_idx = j
        
        if best_match_idx is not None:
            # Found a match
            product2 = products2[best_match_idx]
            used_indices_1.add(i)
            used_indices_2.add(best_match_idx)
            
            # Extract quantity from names
            qty1 = extract_quantity(product1['name'])
            qty2 = extract_quantity(product2['name'])
            
            # Use the more normalized name as the product name
            name1_norm = normalize_product_name(product1['name'])
            name2_norm = normalize_product_name(product2['name'])
            
            # Use the shorter normalized name (usually cleaner)
            if len(name1_norm) <= len(name2_norm):
                product_name = name1_norm.title()
            else:
                product_name = name2_norm.title()
            
            matched_product = {
                'name': product_name,
                'original_names': {
                    product1['platform']: product1['name'],
                    product2['platform']: product2['name']
                },
                'platforms': {
                    product1['platform']: {
                        'price': product1.get('price', 0),
                        'currency': product1.get('currency', 'INR'),
                        'quantity': qty1,
                        'deliveryTime': product1.get('deliveryTime', 'N/A'),
                        'deliveryFee': product1.get('deliveryFee', 0),
                        'image': product1.get('image', ''),
                        'link': product1.get('link', ''),
                        'rating': product1.get('rating', 0),
                        'reviewCount': product1.get('reviewCount', 0),
                        'availability': product1.get('availability', True)
                    },
                    product2['platform']: {
                        'price': product2.get('price', 0),
                        'currency': product2.get('currency', 'INR'),
                        'quantity': qty2,
                        'deliveryTime': product2.get('deliveryTime', 'N/A'),
                        'deliveryFee': product2.get('deliveryFee', 0),
                        'image': product2.get('image', ''),
                        'link': product2.get('link', ''),
                        'rating': product2.get('rating', 0),
                        'reviewCount': product2.get('reviewCount', 0),
                        'availability': product2.get('availability', True)
                    }
                },
                'similarity_score': best_similarity
            }
            
            matched_products.append(matched_product)
    
    # Add unmatched products from both lists
    for i, product1 in enumerate(products1):
        if i not in used_indices_1:
            qty1 = extract_quantity(product1['name'])
            matched_products.append({
                'name': normalize_product_name(product1['name']).title(),
                'original_names': {
                    product1['platform']: product1['name']
                },
                'platforms': {
                    product1['platform']: {
                        'price': product1.get('price', 0),
                        'currency': product1.get('currency', 'INR'),
                        'quantity': qty1,
                        'deliveryTime': product1.get('deliveryTime', 'N/A'),
                        'deliveryFee': product1.get('deliveryFee', 0),
                        'image': product1.get('image', ''),
                        'link': product1.get('link', ''),
                        'rating': product1.get('rating', 0),
                        'reviewCount': product1.get('reviewCount', 0),
                        'availability': product1.get('availability', True)
                    }
                },
                'similarity_score': None
            })
    
    for j, product2 in enumerate(products2):
        if j not in used_indices_2:
            qty2 = extract_quantity(product2['name'])
            matched_products.append({
                'name': normalize_product_name(product2['name']).title(),
                'original_names': {
                    product2['platform']: product2['name']
                },
                'platforms': {
                    product2['platform']: {
                        'price': product2.get('price', 0),
                        'currency': product2.get('currency', 'INR'),
                        'quantity': qty2,
                        'deliveryTime': product2.get('deliveryTime', 'N/A'),
                        'deliveryFee': product2.get('deliveryFee', 0),
                        'image': product2.get('image', ''),
                        'link': product2.get('link', ''),
                        'rating': product2.get('rating', 0),
                        'reviewCount': product2.get('reviewCount', 0),
                        'availability': product2.get('availability', True)
                    }
                },
                'similarity_score': None
            })
    
    return matched_products


def load_platform_json(file_path: str) -> Dict[str, Any]:
    """Load and parse a platform JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return {}


def compare_platforms(blinkit_file: str, zepto_file: str, output_file: str = 'compare.json'):
    """
    Main function to compare products from Blinkit and Zepto
    """
    print(f"Loading Blinkit data from: {blinkit_file}")
    blinkit_data = load_platform_json(blinkit_file)
    
    print(f"Loading Zepto data from: {zepto_file}")
    zepto_data = load_platform_json(zepto_file)
    
    if not blinkit_data or not zepto_data:
        print("Error: Could not load one or both JSON files")
        return
    
    blinkit_products = blinkit_data.get('products', [])
    zepto_products = zepto_data.get('products', [])
    
    print(f"Found {len(blinkit_products)} Blinkit products")
    print(f"Found {len(zepto_products)} Zepto products")
    
    # Filter out invalid products (like the location message from Blinkit)
    blinkit_products = [p for p in blinkit_products if p.get('name') and 
                       'Please provide your delivery location' not in p.get('name', '')]
    
    print(f"After filtering: {len(blinkit_products)} Blinkit products")
    
    # Find matching products
    print("\nMatching products across platforms...")
    matched_products = find_matching_products(blinkit_products, zepto_products, 
                                             similarity_threshold=0.6)
    
    # Create output structure
    output_data = {
        'search_query': blinkit_data.get('search_query', '') or zepto_data.get('search_query', ''),
        'timestamp': datetime.now().isoformat(),
        'total_products': len(matched_products),
        'matched_products': len([p for p in matched_products if p.get('similarity_score') is not None]),
        'location': blinkit_data.get('location', {}) or zepto_data.get('location', {}),
        'products': matched_products
    }
    
    # Save to output file
    output_path = os.path.join(os.path.dirname(__file__), output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nComparison complete!")
    print(f"Total products: {len(matched_products)}")
    print(f"Matched products: {output_data['matched_products']}")
    print(f"Output saved to: {output_path}")


if __name__ == '__main__':
    # Default file paths
    blinkit_file = 'ecommerce_platform/product_data/blinkit_search_atta_20260109_192209.json'
    zepto_file = 'ecommerce_platform/product_data/zepto_search_atta_20260109_193151.json'
    output_file = 'compare.json'
    
    compare_platforms(blinkit_file, zepto_file, output_file)
