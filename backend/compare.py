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

# Matching configuration (can be overridden by config.json)
DEFAULT_MATCHING_CONFIG = {
    'similarity_threshold': 0.6,
    'strict_matching': False,
    'quantity_tolerance_ratio': 2.0,
    'quantity_tolerance_absolute': 0.5,
    'boost_similarity_on_quantity_match': 0.2,
    'word_similarity_weight': 0.4,
    'sequence_similarity_weight': 0.6
}

# Global matching config (loaded from config.json)
MATCHING_CONFIG = DEFAULT_MATCHING_CONFIG.copy()


def load_matching_config():
    """Load matching configuration from config.json"""
    global MATCHING_CONFIG
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            matching_config = config.get('matching', {})
            # Merge with defaults, keeping defaults for missing values
            MATCHING_CONFIG = {**DEFAULT_MATCHING_CONFIG, **matching_config}
            print(f'[Compare] Matching config loaded: threshold={MATCHING_CONFIG["similarity_threshold"]}, strict={MATCHING_CONFIG["strict_matching"]}')
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f'[Compare] Warning: Could not load matching config from config.json: {e}')
        print(f'[Compare] Using default matching config')
        MATCHING_CONFIG = DEFAULT_MATCHING_CONFIG.copy()

# Load config on module import
load_matching_config()


def normalize_product_name(name: str) -> str:
    """
    Normalize product name for better matching:
    - Remove everything after first "|" (pipe character) - descriptive suffixes
    - Remove text in brackets (parentheses, square brackets, curly braces)
    - Convert to lowercase
    - Remove special characters and extra spaces
    - Remove common words that don't help matching
    """
    # First, remove everything after first "|" character
    # Example: "Aashirvaad Chakki MP Sehori Atta | Gahu Lot | Gahu Peet" -> "Aashirvaad Chakki MP Sehori Atta"
    if '|' in name:
        normalized = name.split('|')[0].strip()
    else:
        normalized = name
    
    # Remove text within brackets (parentheses, square brackets, curly braces)
    # This removes things like "(5 kg)", "[Premium]", "{Organic}" etc.
    normalized = re.sub(r'[\(\[\{][^\)\]\}]*[\)\]\}]', '', normalized)
    
    # Convert to lowercase
    normalized = normalized.lower()
    
    # Remove common prefixes/suffixes that don't help matching
    normalized = re.sub(r'\b(100%|0%|with|without|for|the|a|an)\b', '', normalized)
    
    # Remove special characters but keep spaces
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized.strip()


def extract_quantity(name: str, description: str = None) -> Optional[str]:
    """
    Extract quantity/weight from product name or description
    Examples: "5 kg", "10 kg", "1 kg", "500 g", "1 pack (1 kg)"
    Checks description field if provided (new format stores quantity there)
    """
    # First check description if provided (new format)
    text_to_search = description if description else name
    
    # Pattern to match weight/quantity
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:kg|g|gm|gram|kilograms?|grams?)',  # Standard weight formats
        r'\((\d+(?:\.\d+)?)\s*(?:kg|g|gm|gram|kilograms?|grams?)\)',  # Weight in parentheses like "(1 kg)"
        r'(\d+(?:\.\d+)?)\s*(?:pack|pcs?|pieces?)(?:\s*\([^\)]*\))?',  # Pack/pieces with optional weight in parentheses
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_to_search, re.IGNORECASE)
        if match:
            value = match.group(1)
            # Try to find unit in the match
            full_match = match.group(0)
            if 'kg' in full_match.lower() or 'kilogram' in full_match.lower():
                return f"{value} kg"
            elif 'g' in full_match.lower() or 'gram' in full_match.lower():
                return f"{value} g"
            elif 'pack' in full_match.lower() or 'pc' in full_match.lower() or 'piece' in full_match.lower():
                # If it's a pack, try to extract weight from parentheses
                weight_match = re.search(r'\((\d+(?:\.\d+)?)\s*(?:kg|g)', full_match, re.IGNORECASE)
                if weight_match:
                    weight_val = weight_match.group(1)
                    weight_unit = 'kg' if 'kg' in weight_match.group(0).lower() else 'g'
                    return f"{value} pack ({weight_val} {weight_unit})"
                return full_match
            return full_match
    
    return None


def calculate_similarity(name1: str, name2: str, config: Dict = None) -> float:
    """
    Calculate similarity between two product names
    Returns a value between 0 and 1
    Uses configurable weights from matching config
    """
    if config is None:
        config = MATCHING_CONFIG
    
    normalized1 = normalize_product_name(name1)
    normalized2 = normalize_product_name(name2)
    
    # Use SequenceMatcher for similarity
    sequence_similarity = SequenceMatcher(None, normalized1, normalized2).ratio()
    
    # Boost similarity if key words match
    words1 = set(normalized1.split())
    words2 = set(normalized2.split())
    
    word_similarity = 0.0
    if words1 and words2:
        common_words = words1.intersection(words2)
        word_similarity = len(common_words) / max(len(words1), len(words2))
    
    # Combine both metrics using configurable weights
    seq_weight = config.get('sequence_similarity_weight', 0.6)
    word_weight = config.get('word_similarity_weight', 0.4)
    similarity = (sequence_similarity * seq_weight) + (word_similarity * word_weight)
    
    return similarity


def compare_quantities(qty1: Optional[str], qty2: Optional[str], config: Dict = None) -> bool:
    """
    Compare two quantity strings to see if they represent the same quantity
    Returns True if quantities match or are similar
    Uses configurable tolerance-based matching
    """
    if config is None:
        config = MATCHING_CONFIG
    
    if not qty1 or not qty2:
        # In strict mode, reject matches if quantity is missing
        if config.get('strict_matching', False):
            return False
        return True  # If one doesn't have quantity, don't reject the match
    
    # Extract numeric values and units
    def parse_quantity(qty_str: str):
        # Extract number and unit
        match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|gm|gram|kilograms?|grams?|pack|pcs?|pieces?)', qty_str, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            unit = match.group(2).lower()
            # Normalize units
            if unit in ['kg', 'kilogram', 'kilograms']:
                return (value, 'kg')
            elif unit in ['g', 'gm', 'gram', 'grams']:
                return (value / 1000, 'kg')  # Convert to kg for comparison
            elif unit in ['pack', 'pcs', 'pieces', 'pc']:
                # Try to extract weight from parentheses in pack description
                # e.g., "1 pack (1 kg)" -> extract weight
                weight_match = re.search(r'\((\d+(?:\.\d+)?)\s*(kg|g|gm|gram)', qty_str, re.IGNORECASE)
                if weight_match:
                    weight_val = float(weight_match.group(1))
                    weight_unit = weight_match.group(2).lower()
                    if weight_unit in ['g', 'gm', 'gram', 'grams']:
                        weight_val = weight_val / 1000  # Convert to kg
                    return (weight_val * value, 'kg')  # Total weight = pack_count * weight_per_pack
                return (value, 'pack')
        return None
    
    qty1_parsed = parse_quantity(qty1)
    qty2_parsed = parse_quantity(qty2)
    
    if not qty1_parsed or not qty2_parsed:
        return True  # If we can't parse, don't reject the match
    
    value1, unit1 = qty1_parsed
    value2, unit2 = qty2_parsed
    
    # If units are different and one is 'pack', we can't directly compare
    # In that case, allow match (don't reject)
    if (unit1 == 'pack' and unit2 != 'pack') or (unit1 != 'pack' and unit2 == 'pack'):
        return True  # Can't compare pack with weight, don't reject
    
    # Both are weight-based (kg) - compare with tolerance
    if unit1 == 'kg' and unit2 == 'kg':
        # Exact match (within floating point tolerance)
        if abs(value1 - value2) < 0.01:
            return True
        
        # Tolerance-based matching: allow quantities within configurable range
        # This handles cases like 500g vs 1kg, 1kg vs 2kg, etc.
        # where products might be sold in slightly different sizes
        tolerance_ratio = config.get('quantity_tolerance_ratio', 2.0)
        tolerance_absolute = config.get('quantity_tolerance_absolute', 0.5)
        
        if config.get('strict_matching', False):
            # Strict mode: only exact matches or very close matches
            tolerance_ratio = 1.1  # Only 10% difference allowed
            tolerance_absolute = 0.1  # Only 0.1kg difference allowed
        
        ratio = max(value1, value2) / min(value1, value2) if min(value1, value2) > 0 else float('inf')
        if ratio <= tolerance_ratio:  # Within configured range (e.g., 0.5kg to 1kg, or 1kg to 2kg)
            return True
        
        # For very small differences, still allow match if within absolute tolerance
        # e.g., 0.5kg vs 0.45kg or 1kg vs 0.9kg
        if min(value1, value2) < 1.0 and abs(value1 - value2) < tolerance_absolute:
            return True
    
    # Same unit and same value (for pack quantities)
    if unit1 == unit2 and abs(value1 - value2) < 0.01:
        return True
    
    return False


def find_matching_products(products1: List[Dict], products2: List[Dict], 
                          similarity_threshold: float = None, config: Dict = None) -> List[Dict]:
    """
    Find matching products between two product lists
    Returns a list of matched products with platform-specific data
    First matches by name similarity, then checks quantity matching
    Uses configurable thresholds and scoring
    """
    if config is None:
        config = MATCHING_CONFIG
    
    if similarity_threshold is None:
        similarity_threshold = config.get('similarity_threshold', 0.6)
    
    print(f"similarity_threshold: {similarity_threshold}")
    boost_amount = config.get('boost_similarity_on_quantity_match', 0.2)
    strict_mode = config.get('strict_matching', False)
    
    matched_products = []
    used_indices_1 = set()
    used_indices_2 = set()
    
    # Try to match products
    for i, product1 in enumerate(products1):
        if i in used_indices_1:
            continue
        
        # Extract quantity from product1 name or description
        qty1 = extract_quantity(product1.get('name', ''), product1.get('description'))
            
        best_match_idx = None
        best_similarity = 0
        best_quantity_match = False
        
        # First pass: Find all potential matches and prioritize quantity matches
        potential_matches = []
        
        for j, product2 in enumerate(products2):
            if j in used_indices_2:
                continue
            
            # First check name similarity (with configurable weights)
            similarity = calculate_similarity(product1.get('name', ''), product2.get('name', ''), config)
            
            if similarity >= similarity_threshold:
                # Extract quantity from product2 name or description
                qty2 = extract_quantity(product2.get('name', ''), product2.get('description'))
                
                # Check if quantities match (with configurable tolerance)
                quantity_matches = compare_quantities(qty1, qty2, config)
                
                # In strict mode, require both name similarity AND quantity match
                if strict_mode and not quantity_matches:
                    continue
                
                # Store potential match with metadata
                boosted_similarity = min(1.0, similarity + boost_amount) if quantity_matches else similarity
                potential_matches.append({
                    'index': j,
                    'similarity': similarity,
                    'quantity_matches': quantity_matches,
                    'boosted_similarity': boosted_similarity
                })
        
        # Now select the best match: prioritize quantity matches, then by similarity
        if potential_matches:
            # Sort: quantity matches first, then by boosted similarity
            potential_matches.sort(
                key=lambda x: (not x['quantity_matches'], -x['boosted_similarity']),
                reverse=False
            )
            
            best_match = potential_matches[0]
            best_match_idx = best_match['index']
            best_similarity = best_match['similarity']  # Use original similarity for score
            best_quantity_match = best_match['quantity_matches']
        
        if best_match_idx is not None:
            # Found a match
            product2 = products2[best_match_idx]
            used_indices_1.add(i)
            used_indices_2.add(best_match_idx)
            
            # Extract quantities (we already have qty1, just extract qty2)
            qty2 = extract_quantity(product2.get('name', ''), product2.get('description'))
            
            # Use the more normalized name as the product name
            name1_norm = normalize_product_name(product1.get('name', ''))
            name2_norm = normalize_product_name(product2.get('name', ''))
            
            # Use the shorter normalized name (usually cleaner)
            if len(name1_norm) <= len(name2_norm):
                product_name = name1_norm.title()
            else:
                product_name = name2_norm.title()
            
            # Get image from first product (when matched, show only one image)
            product_image = product1.get('image', '') or product2.get('image', '')
            
            matched_product = {
                'name': product_name,
                'image': product_image,  # Single image for matched product
                'original_names': {
                    product1.get('platform', 'unknown'): product1.get('name', ''),
                    product2.get('platform', 'unknown'): product2.get('name', '')
                },
                'platforms': {
                    product1.get('platform', 'unknown'): {
                        'price': product1.get('price', 0),
                        'quantity': qty1,
                        'deliveryTime': product1.get('deliveryTime', 'N/A'),
                        'link': product1.get('link', '')
                    },
                    product2.get('platform', 'unknown'): {
                        'price': product2.get('price', 0),
                        'quantity': qty2,
                        'deliveryTime': product2.get('deliveryTime', 'N/A'),
                        'link': product2.get('link', '')
                    }
                },
                'similarity_score': best_similarity
            }
            
            matched_products.append(matched_product)
    
    # Add unmatched products from both lists
    for i, product1 in enumerate(products1):
        if i not in used_indices_1:
            qty1 = extract_quantity(product1.get('name', ''), product1.get('description'))
            matched_products.append({
                'name': normalize_product_name(product1.get('name', '')).title(),
                'image': product1.get('image', ''),  # Image at product level
                'original_names': {
                    product1.get('platform', 'unknown'): product1.get('name', '')
                },
                'platforms': {
                    product1.get('platform', 'unknown'): {
                        'price': product1.get('price', 0),
                        'quantity': qty1,
                        'deliveryTime': product1.get('deliveryTime', 'N/A'),
                        'link': product1.get('link', '')
                    }
                },
                'similarity_score': None
            })
    
    for j, product2 in enumerate(products2):
        if j not in used_indices_2:
            qty2 = extract_quantity(product2.get('name', ''), product2.get('description'))
            matched_products.append({
                'name': normalize_product_name(product2.get('name', '')).title(),
                'image': product2.get('image', ''),  # Image at product level
                'original_names': {
                    product2.get('platform', 'unknown'): product2.get('name', '')
                },
                'platforms': {
                    product2.get('platform', 'unknown'): {
                        'price': product2.get('price', 0),
                        'quantity': qty2,
                        'deliveryTime': product2.get('deliveryTime', 'N/A'),
                        'link': product2.get('link', '')
                    }
                },
                'similarity_score': None
            })
    
    return matched_products


def _normalize_link(link_value):
    """Helper to normalize link field - handles both string and array formats"""
    if isinstance(link_value, list):
        # If it's an array, take the first element or return empty string
        return link_value[0] if len(link_value) > 0 else ''
    return link_value if link_value else ''


def normalize_product_data(raw_product: dict, platform_name: str) -> dict:
    """
    Normalize product data from zepto/blinkit/instamart format to standard format
    Handles fields like product_name -> name, price string -> number, etc.
    Can be used for both raw scraped data and JSON file data
    """
    import re
    
    # Extract price as number (remove ₹ and commas)
    price_str = raw_product.get('price', '0')
    if isinstance(price_str, str):
        # Remove ₹, commas, and whitespace, then convert to float/int
        price_clean = re.sub(r'[₹,\s]', '', price_str)
        try:
            # Try to convert to float first to handle decimals
            price_value = float(price_clean)
            # Convert to int if it's a whole number
            price = int(price_value) if price_value.is_integer() else price_value
        except (ValueError, TypeError):
            price = 0
    else:
        price = float(price_str) if price_str else 0
    
    # Map field names from zepto/blinkit format to standard format
    # Handle image field - check both 'image' and 'image_url' (scrapers use 'image_url')
    image_value = raw_product.get('image') or raw_product.get('image_url') or ''
    
    normalized = {
        'name': raw_product.get('product_name', raw_product.get('name', '')),
        'price': price,
        'currency': 'INR',
        'description': raw_product.get('description', ''),
        'deliveryTime': raw_product.get('delivery_time', raw_product.get('deliveryTime', 'N/A')),
        'deliveryFee': raw_product.get('deliveryFee', 0),
        'link': _normalize_link(raw_product.get('product_link', raw_product.get('link', ''))),
        'image': image_value,
        'rating': raw_product.get('rating', 0),
        'reviewCount': raw_product.get('reviewCount', raw_product.get('review_count', 0)),
        'availability': raw_product.get('availability', True),
        'platform': platform_name
    }
    
    return normalized


def load_platform_json(file_path: str, platform_name: str = None) -> Dict[str, Any]:
    """Load and parse a platform JSON file
    Returns normalized products and metadata
    Handles both array format and wrapped format
    """
    # try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both formats:
    # 1. Array directly: [...]
    # 2. Wrapped format: {"products": [...], "search_query": "...", ...}
    if isinstance(data, list):
        # Direct array format - normalize each product
        products = [normalize_product_data(p, platform_name or 'unknown') for p in data if p.get('product_name') or p.get('name')]
        return {
            'products': products,
            'search_query': '',
            'location': {}
        }
    elif isinstance(data, dict):
        # Wrapped format
        products = data.get('products', [])
        # Normalize products if they have product_name field (new format)
        if products and len(products) > 0 and ('product_name' in products[0] or 'product_link' in products[0]):
            products = [normalize_product_data(p, platform_name or 'unknown') for p in products if p.get('product_name') or p.get('name')]
        else:
            # Already in normalized format, just ensure platform field
            products = [{**p, 'platform': platform_name or p.get('platform', 'unknown')} for p in products]
        
        return {
            'products': products,
            'search_query': data.get('search_query', ''),
            'location': data.get('location', {})
        }
    else:
        return {'products': [], 'search_query': '', 'location': {}}
            
    # except FileNotFoundError:
    #     print(f"Error: File not found: {file_path}")
    #     return {'products': [], 'search_query': '', 'location': {}}
    # except json.JSONDecodeError as e:
    #     print(f"Error: Invalid JSON in {file_path}: {e}")
    #     return {'products': [], 'search_query': '', 'location': {}}


def compare_platforms(blinkit_file: str, zepto_file: str, output_file: str = 'compare.json'):
    """
    Main function to compare products from Blinkit and Zepto
    Handles new JSON format (array of products with product_name, product_link, etc.)
    JSON format: Array directly [{"product_name": "...", "price": "₹...", "description": "...", ...}, ...]
    """
    print(f"Loading Blinkit data from: {blinkit_file}")
    blinkit_data = load_platform_json(blinkit_file, platform_name='blinkit')
    
    print(f"Loading Zepto data from: {zepto_file}")
    zepto_data = load_platform_json(zepto_file, platform_name='zepto')
    
    if not blinkit_data or not zepto_data:
        print("Error: Could not load one or both JSON files")
        return
    
    blinkit_products = blinkit_data.get('products', [])
    zepto_products = zepto_data.get('products', [])
    
    print(f"Found {len(blinkit_products)} Blinkit products")
    print(f"Found {len(zepto_products)} Zepto products")
    
    # Filter out invalid products (like the location message from Blinkit)
    blinkit_products = [p for p in blinkit_products if p.get('name') and 
                       'Please provide your delivery location' not in p.get('name', '') and
                       p.get('name') != 'N/A']
    
    zepto_products = [p for p in zepto_products if p.get('name') and p.get('name') != 'N/A']
    
    print(f"After filtering: {len(blinkit_products)} Blinkit products, {len(zepto_products)} Zepto products")
    
    # Find matching products
    print("\nMatching products across platforms...")
    matched_products = find_matching_products(blinkit_products, zepto_products, 
                                             similarity_threshold=0.6)
    
    # Create output structure
    output_data = {
        'search_query': blinkit_data.get('search_query', '') or zepto_data.get('search_query', '') or 'atta',
        'timestamp': datetime.now().isoformat(),
        'total_products': len(matched_products),
        'matched_products': len([p for p in matched_products if p.get('similarity_score') is not None]),
        'location': blinkit_data.get('location', {}) or zepto_data.get('location', {}),
        'products': matched_products
    }
    
    # Save to output file - handle both absolute and relative paths
    if os.path.isabs(output_file):
        output_path = output_file
    else:
        output_path = os.path.join(os.path.dirname(__file__), output_file)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nComparison complete!")
    print(f"Total products: {len(matched_products)}")
    print(f"Matched products: {output_data['matched_products']}")
    print(f"Output saved to: {output_path}")


def compare_products_in_memory(all_products: list, query: str, location: dict, config: Dict = None) -> list:
    """
    Compare products from multiple platforms in memory
    Groups products by platform and runs comparison algorithm
    Returns matched and unmatched products in comparison format
    Uses configurable matching parameters
    """
    if config is None:
        config = MATCHING_CONFIG
    
    try:
        if len(all_products) == 0:
            return []
        
        # Group products by platform
        products_by_platform = {}
        platform_counts = {}
        for product in all_products:
            platform = product.get('platform', 'unknown')
            if platform == 'unknown':
                # Debug: log products without platform field
                print(f'[Compare] Warning: Product without platform field: {product.get("name", "N/A")[:50]}')
                # Try to infer platform from other fields or skip
                continue
            if platform not in products_by_platform:
                products_by_platform[platform] = []
                platform_counts[platform] = 0
            products_by_platform[platform].append(product)
            platform_counts[platform] += 1
        
        print(f'[Compare] Grouped products by platform: {list(products_by_platform.keys())}')
        for platform, count in platform_counts.items():
            print(f'[Compare]   - {platform}: {count} products')
        
        # Get platform lists for comparison
        platform_names = list(products_by_platform.keys())
        
        if len(platform_names) < 2:
            # If only one platform, no need to compare, just format for comparison structure
            print(f'[Compare] Only one platform found, skipping comparison')
            matched_products = []
            for platform, products in products_by_platform.items():
                for product in products:
                    qty = extract_quantity(product.get('name', ''), product.get('description'))
                    matched_products.append({
                        'name': normalize_product_name(product.get('name', '')).title(),
                        'original_names': {
                            platform: product.get('name', '')
                        },
                        'platforms': {
                            platform: {
                                'price': product.get('price', 0),
                                'quantity': qty,
                                'deliveryTime': product.get('deliveryTime', 'N/A'),
                                'image': product.get('image', ''),
                                'link': product.get('link', '')
                            }
                        },
                        'similarity_score': None
                    })
            return matched_products
        
        # Compare products across all platforms
        # Start with first platform as base, then match remaining platforms incrementally
        similarity_threshold = config.get('similarity_threshold', 0.6)
        print(f'[Compare] Using similarity threshold: {similarity_threshold}, strict mode: {config.get("strict_matching", False)}')
        
        # Initialize with first platform's products
        base_platform = platform_names[0]
        base_products = products_by_platform[base_platform]
        matched_products = []
        
        # Convert base products to matched format
        for product in base_products:
            qty = extract_quantity(product.get('name', ''), product.get('description'))
            matched_products.append({
                'name': normalize_product_name(product.get('name', '')).title(),
                'image': product.get('image', ''),  # Image at product level
                'original_names': {
                    base_platform: product.get('name', '')
                },
                'platforms': {
                    base_platform: {
                        'price': product.get('price', 0),
                        'quantity': qty,
                        'deliveryTime': product.get('deliveryTime', 'N/A'),
                        'link': product.get('link', '')
                    }
                },
                'similarity_score': None
            })
        
        # Match remaining platforms against already matched products
        for platform in platform_names[1:]:
            products = products_by_platform[platform]
            print(f'[Compare] Matching {len(products)} {platform} products against {len(matched_products)} existing products')
            
            # Track which products from this platform have been matched
            used_product_indices = set()
            
            # Try to match each product from this platform with existing matched products
            for idx, product in enumerate(products):
                product_name = product.get('name', '')
                qty = extract_quantity(product_name, product.get('description'))
                normalized_name = normalize_product_name(product_name)
                
                best_match_idx = None
                best_similarity = 0.0
                
                # Find best match among existing matched products
                for idx, matched_product in enumerate(matched_products):
                    # Check if this matched product already has this platform
                    if platform in matched_product.get('platforms', {}):
                        continue
                    
                    # Get the normalized name from the matched product
                    matched_name = matched_product.get('name', '')
                    matched_normalized = normalize_product_name(matched_name)
                    
                    # Calculate similarity
                    similarity = calculate_similarity(product_name, matched_name, config)
                    
                    # Check quantity match if both have quantities
                    matched_qty = None
                    for plat_data in matched_product.get('platforms', {}).values():
                        matched_qty = plat_data.get('quantity')
                        break
                    
                    quantity_matches = compare_quantities(qty, matched_qty, config)
                    
                    # In strict mode, require quantity match
                    if config.get('strict_matching', False) and not quantity_matches:
                        continue
                    
                    # Update best match if this is better
                    if similarity >= similarity_threshold and similarity > best_similarity:
                        best_similarity = similarity
                        best_match_idx = idx
                
                # If found a match, add this platform to the matched product
                if best_match_idx is not None:
                    matched_product = matched_products[best_match_idx]
                    matched_product['original_names'][platform] = product_name
                    matched_product['platforms'][platform] = {
                        'price': product.get('price', 0),
                        'quantity': qty,
                        'deliveryTime': product.get('deliveryTime', 'N/A'),
                        'link': product.get('link', '')
                    }
                    # Set image if not already set (use first platform's image)
                    if not matched_product.get('image'):
                        matched_product['image'] = product.get('image', '')
                    # Update similarity score if it was None or if this match is better
                    if matched_product.get('similarity_score') is None or best_similarity > matched_product.get('similarity_score', 0):
                        matched_product['similarity_score'] = best_similarity
                    used_product_indices.add(idx)
            
            # Add unmatched products from this platform
            for idx, product in enumerate(products):
                if idx not in used_product_indices:
                    qty = extract_quantity(product.get('name', ''), product.get('description'))
                    matched_products.append({
                        'name': normalize_product_name(product.get('name', '')).title(),
                        'image': product.get('image', ''),  # Image at product level
                        'original_names': {
                            platform: product.get('name', '')
                        },
                        'platforms': {
                            platform: {
                                'price': product.get('price', 0),
                                'quantity': qty,
                                'deliveryTime': product.get('deliveryTime', 'N/A'),
                                'link': product.get('link', '')
                            }
                        },
                        'similarity_score': None
                    })
        
        print(f'[Compare] Comparison complete: {len(matched_products)} total products, {len([p for p in matched_products if p.get("similarity_score") is not None])} matched')
        
        return matched_products
        
    except Exception as error:
        print(f'[Compare] Error during comparison: {error}')
        import traceback
        traceback.print_exc()
        return []


def save_comparison_to_json(matched_products: list, query: str, location: dict, output_file: str = 'compare.json'):
    """
    Save comparison results to compare.json
    """
    try:
        output_data = {
            'search_query': query,
            'timestamp': datetime.now().isoformat(),
            'total_products': len(matched_products),
            'matched_products': len([p for p in matched_products if p.get('similarity_score') is not None]),
            'location': location,
            'products': matched_products
        }
        
        output_path = os.path.join(os.path.dirname(__file__), output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f'[Compare] Comparison results saved to: {output_path}')
        return output_path
    except Exception as error:
        print(f'[Compare] Error saving comparison to JSON: {error}')
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    # Default file paths - use os.path.join for cross-platform compatibility
    # Paths relative to backend directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blinkit_file = os.path.join(script_dir, 'product_data', 'run-2026-01-10_21-17-07', 'blinkit.json')
    zepto_file = os.path.join(script_dir, 'product_data', 'run-2026-01-10_21-17-07', 'zepto.json')
    output_file = os.path.join(script_dir, 'compare.json')
    
    print(f"Script directory: {script_dir}")
    print(f"Blinkit file: {blinkit_file}")
    print(f"Zepto file: {zepto_file}")
    print(f"Output file: {output_file}")
    print()
    
    compare_platforms(blinkit_file, zepto_file, output_file)
