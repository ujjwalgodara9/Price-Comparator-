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
    Normalize product name for better matching - STABLE VERSION
    Creates a consistent normalized key that is order-independent and quantity-agnostic
    - Remove everything after first "|" (pipe character) - descriptive suffixes
    - Remove text in brackets (parentheses, square brackets, curly braces)
    - Remove quantity/weight information (e.g., "5kg", "500g", "1 pack")
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
    
    # Remove quantity/weight information - comprehensive patterns for all product types
    # This is critical for stable matching - quantities should not affect name matching
    
    # Pattern 1: Standard quantity formats (kg, g, ml, ltr, pack, pcs, bottle, can, etc.)
    normalized = re.sub(
        r'\b\d+(?:\.\d+)?\s*(?:kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter|pack|packs|pcs|pieces?|can|cans|bottle|bottles|tablet|tablets|strip|strips|jar|jars|packet|pkts?|box|boxes)\b',
        '',
        normalized,
        flags=re.IGNORECASE
    )
    
    # Pattern 2: Multi-pack patterns like "12 x 500ml", "6pk", "2x2ltr", "4pks"
    normalized = re.sub(
        r'\b\d+\s*[x×]\s*\d+(?:\.\d+)?\s*(?:kg|g|ltr|ml|pcs?|pack|bottle|can|box)\b',
        '',
        normalized,
        flags=re.IGNORECASE
    )
    
    # Pattern 3: Suffixes/prefixes like "500ml pack", "5kg bag", ", 5kg pack"
    normalized = re.sub(
        r'(?:,\s*)?\b\d+(?:\.\d+)?\s*(?:kg|g|ltr|ml|pcs?|pack|bottle|can|box)\s*(?:pack|bag|pouch|container)?\b',
        '',
        normalized,
        flags=re.IGNORECASE
    )
    
    # Convert to lowercase
    normalized = normalized.lower()
    
    # Remove common prefixes/suffixes that don't help matching
    normalized = re.sub(r'\b(100%|0%|with|without|for|the|a|an)\b', '', normalized)
    
    # Remove special characters but keep spaces
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    
    # Clean up extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized


def extract_quantity(name: str, description: str = None) -> Optional[str]:
    """
    Extract quantity/weight from product name or description
    Examples: "5 kg", "10 kg", "1 kg", "500 g", "1 pack (1 kg)", "500ml", "2ltr", "12 x 500ml"
    Checks description field if provided (new format stores quantity there)
    Supports comprehensive unit types: kg, g, ml, ltr, pack, pcs, bottle, can, tablet, strip, jar, packet, box, etc.
    """
    # First check description if provided (new format)
    text_to_search = description if description else name
    
    # Comprehensive patterns to match all quantity/weight formats
    patterns = [
        # Pattern 1: Multi-pack patterns like "12 x 500ml", "6pk", "2x2ltr", "4pks"
        r'(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter|pcs?|pack|packs|bottle|bottles|can|cans|box|boxes)',
        # Pattern 2: Standard quantity formats with all units
        r'(\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter|pack|packs|pcs|pieces?|can|cans|bottle|bottles|tablet|tablets|strip|strips|jar|jars|packet|pkts?|box|boxes)',
        # Pattern 3: Weight in parentheses like "(1 kg)", "(500ml)"
        r'\((\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter)\)',
        # Pattern 4: Pack/pieces with optional weight in parentheses like "1 pack (1 kg)"
        r'(\d+(?:\.\d+)?)\s*(pack|packs|pcs|pieces?)(?:\s*\((\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter)\))?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_to_search, re.IGNORECASE)
        if match:
            groups = match.groups()
            
            # Handle multi-pack pattern (Pattern 1)
            if len(groups) == 3 and 'x' in match.group(0).lower() or '×' in match.group(0):
                count = groups[0]
                value = groups[1]
                unit = groups[2].lower()
                # Normalize unit
                normalized_unit = normalize_unit(unit)
                return f"{count} x {value} {normalized_unit}"
            
            # Handle standard quantity pattern (Pattern 2)
            elif len(groups) == 2:
                value = groups[0]
                unit = groups[1].lower()
                normalized_unit = normalize_unit(unit)
                return f"{value} {normalized_unit}"
            
            # Handle weight in parentheses (Pattern 3)
            elif len(groups) == 2 and match.group(0).startswith('('):
                value = groups[0]
                unit = groups[1].lower()
                normalized_unit = normalize_unit(unit)
                return f"{value} {normalized_unit}"
            
            # Handle pack with weight in parentheses (Pattern 4)
            elif len(groups) >= 2 and ('pack' in groups[1].lower() or 'pc' in groups[1].lower() or 'piece' in groups[1].lower()):
                pack_count = groups[0]
                pack_unit = groups[1].lower()
                if len(groups) >= 4 and groups[2] and groups[3]:
                    # Has weight in parentheses
                    weight_val = groups[2]
                    weight_unit = groups[3].lower()
                    normalized_weight_unit = normalize_unit(weight_unit)
                    return f"{pack_count} {pack_unit} ({weight_val} {normalized_weight_unit})"
                else:
                    # Just pack count
                    return f"{pack_count} {pack_unit}"
    
    return None


def normalize_unit(unit: str) -> str:
    """
    Normalize unit string to standard format
    Converts various unit formats to standard abbreviations
    """
    unit_lower = unit.lower().strip()
    
    # Weight units
    if unit_lower in ['kg', 'kilogram', 'kilograms', 'kilogramme', 'kilogrammes']:
        return 'kg'
    elif unit_lower in ['g', 'gm', 'gram', 'grams']:
        return 'g'
    elif unit_lower in ['lb', 'lbs', 'pound', 'pounds']:
        return 'lb'
    elif unit_lower in ['oz', 'ounce', 'ounces']:
        return 'oz'
    
    # Volume units
    elif unit_lower in ['ltr', 'litre', 'liter', 'litres', 'liters']:
        return 'ltr'
    elif unit_lower in ['ml', 'millilitre', 'milliliter', 'millilitres', 'milliliters']:
        return 'ml'
    
    # Count/package units
    elif unit_lower in ['pack', 'packs', 'pkt', 'pkts', 'packet', 'packets']:
        return 'pack'
    elif unit_lower in ['pc', 'pcs', 'piece', 'pieces']:
        return 'pcs'
    elif unit_lower in ['can', 'cans']:
        return 'can'
    elif unit_lower in ['bottle', 'bottles']:
        return 'bottle'
    elif unit_lower in ['tablet', 'tablets']:
        return 'tablet'
    elif unit_lower in ['strip', 'strips']:
        return 'strip'
    elif unit_lower in ['jar', 'jars']:
        return 'jar'
    elif unit_lower in ['box', 'boxes']:
        return 'box'
    
    # Return original if not recognized
    return unit_lower


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
        """
        Parse quantity string to extract value and normalized unit
        Handles all unit types: kg, g, ml, ltr, pack, pcs, bottle, can, tablet, strip, jar, packet, box, etc.
        Also handles multi-pack patterns like "12 x 500ml"
        """
        # Handle multi-pack pattern like "12 x 500ml"
        multi_pack_match = re.search(r'(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter|pcs?|pack|packs|bottle|bottles|can|cans|box|boxes)', qty_str, re.IGNORECASE)
        if multi_pack_match:
            count = float(multi_pack_match.group(1))
            value = float(multi_pack_match.group(2))
            unit = normalize_unit(multi_pack_match.group(3))
            # Convert to base unit and multiply by count
            base_value = convert_to_base_unit(value, unit)
            return (base_value * count, 'base')
        
        # Handle standard quantity pattern with all units
        match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter|pack|packs|pcs|pieces?|can|cans|bottle|bottles|tablet|tablets|strip|strips|jar|jars|packet|pkts?|box|boxes)', qty_str, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            unit = normalize_unit(match.group(2))
            
            # Check if it's a pack/pcs with weight in parentheses
            if unit in ['pack', 'pcs']:
                # Try to extract weight from parentheses in pack description
                # e.g., "1 pack (1 kg)" -> extract weight
                weight_match = re.search(r'\((\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter)\)', qty_str, re.IGNORECASE)
                if weight_match:
                    weight_val = float(weight_match.group(1))
                    weight_unit = normalize_unit(weight_match.group(2))
                    # Convert to base unit
                    base_weight = convert_to_base_unit(weight_val, weight_unit)
                    return (base_weight * value, 'base')  # Total = pack_count * weight_per_pack
                return (value, unit)
            
            # Convert to base unit for comparison
            base_value = convert_to_base_unit(value, unit)
            return (base_value, 'base')
        
        return None


def convert_to_base_unit(value: float, unit: str) -> float:
    """
    Convert various units to a base unit for comparison
    Weight units -> kg, Volume units -> ltr, Count units -> keep as-is
    """
    unit_lower = unit.lower()
    
    # Weight units -> convert to kg
    if unit_lower == 'kg':
        return value
    elif unit_lower == 'g':
        return value / 1000  # Convert grams to kg
    elif unit_lower == 'lb':
        return value * 0.453592  # Convert pounds to kg
    elif unit_lower == 'oz':
        return value * 0.0283495  # Convert ounces to kg
    
    # Volume units -> convert to ltr
    elif unit_lower == 'ltr':
        return value
    elif unit_lower == 'ml':
        return value / 1000  # Convert ml to ltr
    
    # Count/package units -> keep as-is (will be compared separately)
    elif unit_lower in ['pack', 'pcs', 'can', 'bottle', 'tablet', 'strip', 'jar', 'box']:
        return value
    
    # Default: return as-is
    return value


def compare_quantities(qty1: Optional[str], qty2: Optional[str], config: Dict = None) -> bool:
    """
    Compare two quantity strings to see if they represent the same quantity
    Returns True if quantities match or are similar
    Uses configurable tolerance-based matching
    Supports all unit types: kg, g, ml, ltr, pack, pcs, bottle, can, tablet, strip, jar, packet, box, etc.
    """
    if config is None:
        config = MATCHING_CONFIG
    
    if not qty1 or not qty2:
        # In strict mode, reject matches if quantity is missing
        if config.get('strict_matching', False):
            return False
        return True  # If one doesn't have quantity, don't reject the match
    
    # Extract numeric values and units using the comprehensive parser
    def parse_quantity(qty_str: str):
        """
        Parse quantity string to extract value and normalized unit
        Handles all unit types: kg, g, ml, ltr, pack, pcs, bottle, can, tablet, strip, jar, packet, box, etc.
        Also handles multi-pack patterns like "12 x 500ml"
        """
        # Handle multi-pack pattern like "12 x 500ml"
        multi_pack_match = re.search(r'(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter|pcs?|pack|packs|bottle|bottles|can|cans|box|boxes)', qty_str, re.IGNORECASE)
        if multi_pack_match:
            count = float(multi_pack_match.group(1))
            value = float(multi_pack_match.group(2))
            unit = normalize_unit(multi_pack_match.group(3))
            # Convert to base unit and multiply by count
            base_value = convert_to_base_unit(value, unit)
            return (base_value * count, 'base')
        
        # Handle standard quantity pattern with all units
        match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter|pack|packs|pcs|pieces?|can|cans|bottle|bottles|tablet|tablets|strip|strips|jar|jars|packet|pkts?|box|boxes)', qty_str, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            unit = normalize_unit(match.group(2))
            
            # Check if it's a pack/pcs with weight in parentheses
            if unit in ['pack', 'pcs']:
                # Try to extract weight from parentheses in pack description
                # e.g., "1 pack (1 kg)" -> extract weight
                weight_match = re.search(r'\((\d+(?:\.\d+)?)\s*(kg|g|gm|gram|grams?|kilogrammes?|kilograms?|lbs?|lb|oz|ltr|litre|liter|ml|millilitre|milliliter)\)', qty_str, re.IGNORECASE)
                if weight_match:
                    weight_val = float(weight_match.group(1))
                    weight_unit = normalize_unit(weight_match.group(2))
                    # Convert to base unit
                    base_weight = convert_to_base_unit(weight_val, weight_unit)
                    return (base_weight * value, 'base')  # Total = pack_count * weight_per_pack
                return (value, unit)
            
            # Convert to base unit for comparison
            base_value = convert_to_base_unit(value, unit)
            return (base_value, 'base')
        
        return None
    
    qty1_parsed = parse_quantity(qty1)
    qty2_parsed = parse_quantity(qty2)
    
    qty1_parsed = parse_quantity(qty1)
    qty2_parsed = parse_quantity(qty2)
    
    if not qty1_parsed or not qty2_parsed:
        return True  # If we can't parse, don't reject the match
    
    value1, unit1 = qty1_parsed
    value2, unit2 = qty2_parsed
    
    # If one is base unit and other is count unit, or vice versa, can't directly compare
    # In that case, allow match (don't reject)
    if (unit1 == 'base' and unit2 != 'base') or (unit1 != 'base' and unit2 == 'base'):
        return True  # Can't compare different unit types, don't reject
    
    # Both converted to base units - compare with tolerance
    if unit1 == 'base' and unit2 == 'base':
        # Exact match (within floating point tolerance)
        if abs(value1 - value2) < 0.01:
            return True
        
        # Tolerance-based matching: allow quantities within configurable range
        # This handles cases like 500g vs 1kg, 1kg vs 2kg, 500ml vs 1ltr, etc.
        # where products might be sold in slightly different sizes
        tolerance_ratio = config.get('quantity_tolerance_ratio', 2.0)
        tolerance_absolute = config.get('quantity_tolerance_absolute', 0.5)
        
        if config.get('strict_matching', False):
            # Strict mode: only exact matches or very close matches
            tolerance_ratio = 1.1  # Only 10% difference allowed
            tolerance_absolute = 0.1  # Only 0.1 base unit difference allowed
        
        ratio = max(value1, value2) / min(value1, value2) if min(value1, value2) > 0 else float('inf')
        if ratio <= tolerance_ratio:  # Within configured range (e.g., 0.5kg to 1kg, or 1kg to 2kg)
            return True
        
        # For very small differences, still allow match if within absolute tolerance
        # e.g., 0.5kg vs 0.45kg or 1kg vs 0.9kg
        if min(value1, value2) < 1.0 and abs(value1 - value2) < tolerance_absolute:
            return True
    
    # Same unit and same value (for count/package quantities like pack, pcs, can, bottle, etc.)
    if unit1 == unit2 and unit1 not in ['base'] and abs(value1 - value2) < 0.01:
        return True
    
    # If both are count units but different types (e.g., pack vs pcs), allow match if same value
    # This handles cases where platforms use different terminology
    if unit1 in ['pack', 'pcs', 'can', 'bottle', 'tablet', 'strip', 'jar', 'box'] and \
       unit2 in ['pack', 'pcs', 'can', 'bottle', 'tablet', 'strip', 'jar', 'box'] and \
       abs(value1 - value2) < 0.01:
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
        
        # FIX 2: Global product usage guard - track used products across all platforms
        # Key: (platform, product_id) where product_id is a unique identifier
        # We'll use (platform, name, price, link) as a composite key for uniqueness
        used_products = set()
        
        def get_product_key(platform: str, product: dict) -> tuple:
            """Create a unique key for a product to prevent duplicates"""
            return (
                platform,
                product.get('name', ''),
                product.get('price', 0),
                product.get('link', '')
            )
        
        # Compare products across all platforms
        similarity_threshold = config.get('similarity_threshold', 0.6)
        print(f'[Compare] Using similarity threshold: {similarity_threshold}, strict mode: {config.get("strict_matching", False)}')
        
        # Initialize matched products list
        matched_products = []
        
        # Process all platforms - match products to existing groups or create new groups
        for platform in platform_names:
            products = products_by_platform[platform]
            print(f'[Compare] Processing {len(products)} {platform} products')
            
            for product in products:
                # FIX 2: Check if this product is already used
                product_key = get_product_key(platform, product)
                if product_key in used_products:
                    print(f'[Compare] Skipping already-used product: {product.get("name", "")[:50]}')
                    continue
                
                product_name = product.get('name', '')
                qty = extract_quantity(product_name, product.get('description'))
                # FIX 1: Store normalized name for stable matching
                product_norm_name = normalize_product_name(product_name)
                
                best_match_idx = None
                best_similarity = 0.0
                
                # FIX 3: Find best match among existing matched products
                # Compare against all variants in each group, not just canonical name
                for idx, matched_product in enumerate(matched_products):
                    # Check if this matched product already has this platform
                    if platform in matched_product.get('platforms', {}):
                        continue
                    
                    # FIX 3: Match against all variants in the group, not just canonical name
                    # Get all normalized names from original_names in this group
                    group_variants = []
                    for orig_name in matched_product.get('original_names', {}).values():
                        group_variants.append(normalize_product_name(orig_name))
                    
                    # Also include the canonical name
                    canonical_norm = normalize_product_name(matched_product.get('name', ''))
                    if canonical_norm not in group_variants:
                        group_variants.append(canonical_norm)
                    
                    # Calculate similarity against all variants, take the best
                    max_variant_similarity = 0.0
                    for variant_norm in group_variants:
                        # Use normalized names for comparison
                        similarity = calculate_similarity(product_norm_name, variant_norm, config)
                        if similarity > max_variant_similarity:
                            max_variant_similarity = similarity
                    
                    similarity = max_variant_similarity
                    
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
                    # FIX 2: Mark product as used immediately
                    used_products.add(product_key)
                else:
                    # FIX 2: Safe unmatched creation - only create if not already used
                    if product_key not in used_products:
                        qty = extract_quantity(product.get('name', ''), product.get('description'))
                        matched_products.append({
                            'name': normalize_product_name(product.get('name', '')).title(),
                            'image': product.get('image', ''),
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
                        # FIX 2: Mark as used immediately
                        used_products.add(product_key)
        
        # FIX 4: Post-pass deduplication - merge similar groups
        print(f'[Compare] Running post-pass deduplication on {len(matched_products)} groups')
        merged_indices = set()
        final_matched_products = []
        
        for i, group1 in enumerate(matched_products):
            if i in merged_indices:
                continue
            
            # Try to merge with other groups
            current_group = group1.copy()
            group1_norm = normalize_product_name(group1.get('name', ''))
            
            for j, group2 in enumerate(matched_products[i+1:], start=i+1):
                if j in merged_indices:
                    continue
                
                group2_norm = normalize_product_name(group2.get('name', ''))
                similarity = calculate_similarity(group1_norm, group2_norm, config)
                
                # Merge if very similar (higher threshold for post-pass)
                if similarity >= 0.9:  # Very high threshold for merging
                    # print(f'[Compare] Merging groups: "{group1.get("name", "")[:50]}" and "{group2.get("name", "")[:50]}" (similarity: {similarity:.2f})')
                    # Merge platforms and original_names
                    current_group['platforms'].update(group2.get('platforms', {}))
                    current_group['original_names'].update(group2.get('original_names', {}))
                    # Keep best image
                    if not current_group.get('image') and group2.get('image'):
                        current_group['image'] = group2.get('image')
                    # Update similarity score
                    if group2.get('similarity_score') and (not current_group.get('similarity_score') or group2.get('similarity_score', 0) > current_group.get('similarity_score', 0)):
                        current_group['similarity_score'] = group2.get('similarity_score')
                    merged_indices.add(j)
            
            final_matched_products.append(current_group)
            merged_indices.add(i)
        
        print(f'[Compare] Comparison complete: {len(final_matched_products)} total products (after dedup), {len([p for p in final_matched_products if p.get("similarity_score") is not None])} matched')
        
        return final_matched_products
        
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
