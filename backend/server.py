"""
Flask Backend API Server for Fast E-commerce Product Scraping

This is a Python/Flask server that handles scraping from various platforms
to avoid CORS issues. Run this separately and point VITE_API_BASE_URL to it.

Installation:
pip install flask flask-cors requests beautifulsoup4 lxml

Usage:
python server.py

Then set VITE_API_BASE_URL=http://localhost:3001 in your .env file
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import uuid
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from ecommerce_platform.zepto import run_zepto_flow
from ecommerce_platform.blinkit import run_blinkit_flow
from ecommerce_platform.instamart import run_instamart_flow
from datetime import datetime
from ecommerce_platform.zepto_itemlist import scrape_zepto_products
from ecommerce_platform.blinkit_itemlist import scrape_blinkit_products
# Import comparison functions from compare.py
from compare import (
    find_matching_products,
    extract_quantity,
    normalize_product_name
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

PORT = 3001

# Load configuration from config.json
def load_config():
    """Load configuration from config.json file"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f'[Config] Warning: config.json not found at {config_path}, using defaults')
        return {}
    except json.JSONDecodeError as e:
        print(f'[Config] Error: Invalid JSON in config.json: {e}')
        return {}

# Load config on startup
CONFIG = load_config()
PLATFORM_CONFIG = CONFIG.get('platform', {})
SEARCH_DEBUG = CONFIG.get('search_debug', False)

def get_platform_config(platform_name):
    """Get configuration for a specific platform"""
    platform_config = PLATFORM_CONFIG.get(platform_name, {})
    return {
        'scrape': platform_config.get('scrape', True),  # Default to True if not specified
        'headless': platform_config.get('headless', True)  # Default to True if not specified
    }

# Mock data structure - replace with actual scraping logic
mock_products = {
    'zepto': [
        {
            'id': 'z1',
            'name': 'Sample Product',
            'description': 'Product description',
            'image': 'https://via.placeholder.com/400',
            'price': 299,
            'currency': 'INR',
            'platform': 'zepto',
            'availability': True,
            'rating': 4.5,
            'reviewCount': 120,
            'features': [],
            'link': 'https://www.zepto.com/product/1',
            'location': 'Mumbai, Maharashtra',
            'deliveryTime': '10-15 mins',
            'deliveryFee': 0,
        },
    ],
}


@app.route('/api/search', methods=['POST'])
def search_all_platforms():
    """Search endpoint - searches across all platforms in parallel"""
    try:
        # Get request data
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json() or {}
        query = data.get('query', '')
        location = data.get('location', {})
        platforms = data.get('platforms', ['zepto'])
        
        print(f'[API] Received search request: query="{query}", platforms={platforms}, location={location}')
        
        if not query or not query.strip():
            return jsonify({'error': 'Query is required'}), 400
        
        # Generate shared timestamp for this search if search_debug is enabled
        search_timestamp = None
        if SEARCH_DEBUG:
            search_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            print(f'[API] Search debug enabled - using timestamp folder: {search_timestamp}')
        
        all_products = []
        
        # Store products by platform for comparison
        products_by_platform = {}
        
        # Run all platforms in parallel using ThreadPoolExecutor
        print(f'[API] Starting parallel search for {len(platforms)} platform(s)')
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=len(platforms)) as executor:
            # Submit all tasks
            future_to_platform = {
                executor.submit(search_platform, platform, query, location): platform
                for platform in platforms
            }
            
            # Wait for all to complete and collect results
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    products = future.result()  # This waits for the result
                    # Ensure products is a list before processing
                    if products is None:
                        products = []
                    print(f'[API] ✓ Platform {platform} returned {len(products)} products')
                    all_products.extend(products)
                except Exception as error:
                    print(f'[API] ✗ Error searching {platform}: {error}')
                    import traceback
                    traceback.print_exc()
                    # Continue with other platforms even if one fails
                    continue
        # Search each platform
        for platform in platforms:
            try:
                print(f'[API] Searching platform: {platform}')
                products = search_platform(platform, query, location, search_timestamp=search_timestamp)
                print(f'[API] Platform {platform} returned {len(products)} products')
                all_products.extend(products)
                products_by_platform[platform] = products
            except Exception as error:
                print(f'[API] Error searching {platform}: {error}')
                import traceback
                traceback.print_exc()
                # Continue with other platforms even if one fails
                continue
        
        elapsed = time.time() - start_time
        print(f'[API] Total products found: {len(all_products)} (completed in {elapsed:.2f}s)')
        return jsonify({'products': all_products, 'execution_time': elapsed})
        print(f'[API] Total products found: {len(all_products)}')
        
        # Automatically run comparison after search
        matched_products = []
        if len(all_products) > 0:
            print(f'[API] Running automatic comparison...')
            try:
                matched_products = compare_products_in_memory(all_products, query, location)
                
                if matched_products:
                    # Save comparison results to compare.json
                    save_comparison_to_json(matched_products, query, location)
                    print(f'[API] Comparison complete: {len(matched_products)} products compared')
                else:
                    print(f'[API] Comparison returned no products')
            except Exception as compare_error:
                print(f'[API] Error during automatic comparison: {compare_error}')
                import traceback
                traceback.print_exc()
                # Continue with returning all products even if comparison fails
        
        # If we have comparison results and multiple platforms, return comparison format
        # Otherwise return raw products
        if matched_products and len(platforms) >= 1:
            # Transform comparison results to Product[] format for frontend
            products_for_frontend = []
            for item in matched_products:
                for platform_name, platform_data in item.get('platforms', {}).items():
                    # Only include products from requested platforms
                    if platform_name in platforms:
                        product = {
                            'id': f"{platform_name}-{item.get('name', '').lower().replace(' ', '-')[:20]}",
                            'name': item.get('name', ''),
                            'description': item.get('original_names', {}).get(platform_name, ''),
                            'image': platform_data.get('image', ''),
                            'price': platform_data.get('price', 0),
                            'currency': platform_data.get('currency', 'INR'),
                            'platform': platform_name,
                            'availability': platform_data.get('availability', True),
                            'rating': platform_data.get('rating', 0),
                            'reviewCount': platform_data.get('reviewCount', 0),
                            'features': [],
                            'link': platform_data.get('link', ''),
                            'location': location.get('city', '') + ', ' + location.get('state', '') if isinstance(location, dict) else str(location),
                            'deliveryTime': platform_data.get('deliveryTime', 'N/A'),
                            'deliveryFee': platform_data.get('deliveryFee', 0),
                            'originalPrice': None,
                            'quantity': platform_data.get('quantity', None)
                        }
                        products_for_frontend.append(product)
            
            if products_for_frontend:
                print(f'[API] Returning {len(products_for_frontend)} comparison results')
                return jsonify({'products': products_for_frontend})
        
        # Fallback: return raw products if comparison failed or single platform
        print(f'[API] Returning {len(all_products)} raw products')
        return jsonify({'products': all_products})
    except Exception as error:
        print(f'[API] Search error: {error}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to search products: {str(error)}'}), 500


@app.route('/api/search/<platform>', methods=['POST'])
def search_platform_endpoint(platform):
    """Platform-specific search endpoint"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json() or {}
        query = data.get('query', '')
        location = data.get('location', {})
        
        print(f'[API] Platform-specific search: platform={platform}, query="{query}"')
        
        if not query or not query.strip():
            return jsonify({'error': 'Query is required'}), 400
        
        # Generate shared timestamp for this search if search_debug is enabled
        search_timestamp = None
        if SEARCH_DEBUG:
            search_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            print(f'[API] Search debug enabled - using timestamp folder: {search_timestamp}')
        
        products = search_platform(platform, query, location, search_timestamp=search_timestamp)
        print(f'[API] Platform {platform} returned {len(products)} products')
        return jsonify({'products': products})
    except Exception as error:
        print(f'[API] Error searching {platform}: {error}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to search on {platform}: {str(error)}'}), 500


def compare_products_in_memory(all_products: list, query: str, location: dict) -> list:
    """
    Compare products from multiple platforms in memory
    Groups products by platform and runs comparison algorithm
    Returns matched and unmatched products in comparison format
    """
    try:
        if len(all_products) == 0:
            return []
        
        # Group products by platform
        products_by_platform = {}
        for product in all_products:
            platform = product.get('platform', 'unknown')
            if platform not in products_by_platform:
                products_by_platform[platform] = []
            products_by_platform[platform].append(product)
        
        print(f'[Compare] Grouped products by platform: {list(products_by_platform.keys())}')
        
        # Get platform lists for comparison
        platform_names = list(products_by_platform.keys())
        
        if len(platform_names) < 2:
            # If only one platform, no need to compare, just format for comparison structure
            print(f'[Compare] Only one platform found, skipping comparison')
            matched_products = []
            for platform, products in products_by_platform.items():
                for product in products:
                    qty = extract_quantity(product.get('name', ''))
                    matched_products.append({
                        'name': normalize_product_name(product.get('name', '')).title(),
                        'original_names': {
                            platform: product.get('name', '')
                        },
                        'platforms': {
                            platform: {
                                'price': product.get('price', 0),
                                'currency': product.get('currency', 'INR'),
                                'quantity': qty,
                                'deliveryTime': product.get('deliveryTime', 'N/A'),
                                'deliveryFee': product.get('deliveryFee', 0),
                                'image': product.get('image', ''),
                                'link': product.get('link', ''),
                                'rating': product.get('rating', 0),
                                'reviewCount': product.get('reviewCount', 0),
                                'availability': product.get('availability', True)
                            }
                        },
                        'similarity_score': None
                    })
            return matched_products
        
        # Compare products from first two platforms (can be extended for more platforms)
        platform1 = platform_names[0]
        platform2 = platform_names[1] if len(platform_names) > 1 else None
        
        products1 = products_by_platform[platform1]
        products2 = products_by_platform[platform2] if platform2 else []
        
        print(f'[Compare] Comparing {len(products1)} {platform1} products with {len(products2)} {platform2} products')
        
        # Run comparison
        matched_products = find_matching_products(products1, products2, similarity_threshold=0.6)
        
        # Add products from remaining platforms (if any)
        for platform in platform_names[2:]:
            products = products_by_platform[platform]
            # Compare with already matched products (simplified - could be improved)
            for product in products:
                qty = extract_quantity(product.get('name', ''))
                matched_products.append({
                    'name': normalize_product_name(product.get('name', '')).title(),
                    'original_names': {
                        platform: product.get('name', '')
                    },
                    'platforms': {
                        platform: {
                            'price': product.get('price', 0),
                            'currency': product.get('currency', 'INR'),
                            'quantity': qty,
                            'deliveryTime': product.get('deliveryTime', 'N/A'),
                            'deliveryFee': product.get('deliveryFee', 0),
                            'image': product.get('image', ''),
                            'link': product.get('link', ''),
                            'rating': product.get('rating', 0),
                            'reviewCount': product.get('reviewCount', 0),
                            'availability': product.get('availability', True)
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


def search_platform(platform, query, location, search_timestamp=None):
    """Search a specific platform"""
    # Check if platform scraping is enabled in config
    platform_config = get_platform_config(platform)
    if not platform_config['scrape']:
        print(f'[API] Platform {platform} is disabled in config.json, skipping...')
        return []
    
    platform_map = {
        'zepto': scrape_zepto,
        'swiggy-instamart': scrape_swiggy_instamart,
        'bigbasket': scrape_bigbasket,
        'blinkit': scrape_blinkit
    }
    
    scraper = platform_map.get(platform)
    if scraper:
        return scraper(query, location, platform_config, search_timestamp=search_timestamp)
    return []


def scrape_zepto(query, location, platform_config=None, search_timestamp=None):
    """Zepto Scraper - Uses Playwright to scrape Zepto website"""
    try:
        if not query:
            print('[Zepto] Empty query, returning empty list')
            return []
        
        # Get headless setting from config
        if platform_config is None:
            platform_config = get_platform_config('zepto')
        headless = platform_config.get('headless', True)
        
        print(f'[Zepto] Starting scrape for query: "{query}" (headless={headless})')
        
        # Use the Playwright-based scraper from zepto_itemlist
        # JSON saving is handled within run_zepto_flow
        products = run_zepto_flow(
            product_name=query,
            location=location["city"],
            headless=headless,
            max_products=50,
            search_debug=SEARCH_DEBUG,
            search_timestamp=search_timestamp
        )
        
        # Ensure products is a list
        if products is None:
            products = []
        
        print(f'[Zepto] Scrape completed: Found {len(products)} products for query "{query}"')
        return products
    except ImportError as error:
        print(f'[Zepto] Import error - Playwright may not be installed: {error}')
        import traceback
        traceback.print_exc()
        return []
    except Exception as error:
        print(f'[Zepto] Scraping error: {error}')
        import traceback
        traceback.print_exc()
        return []


def scrape_swiggy_instamart(query, location, platform_config=None, search_timestamp=None):
    """instamart Scraper - Uses Playwright to scrape instamart website"""
    try:
        if not query:
            print('[instamart] Empty query, returning empty list')
            return []
        
        # Get headless setting from config
        if platform_config is None:
            platform_config = get_platform_config('instamart')
        headless = platform_config.get('headless', True)
        
        print(f'[instamart] Starting scrape for query: "{query}" (headless={headless})')
        
        # Use the Playwright-based scraper from instamart_itemlist
        # JSON saving is handled within run_instamart_flow
        products = run_instamart_flow(
            product_name=query,
            location=location["city"],
            headless=headless,
            max_products=50,
            search_debug=SEARCH_DEBUG,
            search_timestamp=search_timestamp
        )
        
        # Ensure products is a list
        if products is None:
            products = []
        
        print(f'[instamart] Scrape completed: Found {len(products)} products for query "{query}"')
        return products
    except ImportError as error:
        print(f'[instamart] Import error - Playwright may not be installed: {error}')
        import traceback
        traceback.print_exc()
        return []
    except Exception as error:
        print(f'[instamart] Scraping error: {error}')
        import traceback
        traceback.print_exc()
        return []


def scrape_bigbasket(query, location, platform_config=None):
    """BigBasket Scraper"""
    # Implement BigBasket scraping
    return []


def scrape_blinkit(query, location, platform_config=None, search_timestamp=None):
    """Blinkit Scraper - Uses Playwright to scrape Blinkit website"""
    try:
        if not query:
            print('[Blinkit] Empty query, returning empty list')
            return []
        
        # Get headless setting from config
        if platform_config is None:
            platform_config = get_platform_config('blinkit')
        headless = platform_config.get('headless', True)
        
        print(f'[Blinkit] Starting scrape for query: "{query}" (headless={headless})')
        
        # Use the Playwright-based scraper from blinkit_itemlist
        # JSON saving is handled within run_blinkit_flow
        products = run_blinkit_flow(
            product_name=query,
            location=location["city"],
            headless=headless,
            max_products=50,
            search_debug=SEARCH_DEBUG,
            search_timestamp=search_timestamp
        )
        
        # Ensure products is a list
        if products is None:
            products = []
        
        print(f'[Blinkit] Scrape completed: Found {len(products)} products for query "{query}"')
        return products
    except ImportError as error:
        print(f'[Blinkit] Import error - Playwright may not be installed: {error}')
        import traceback
        traceback.print_exc()
        return []
    except Exception as error:
        print(f'[Blinkit] Scraping error: {error}')
        import traceback
        traceback.print_exc()
        return []

@app.route('/api/product/<platform>/<product_id>', methods=['GET'])
def get_product_details(platform, product_id):
    """Get product details"""
    # Implement product details fetching
    return jsonify({'product': None})


@app.route('/api/availability', methods=['POST'])
def check_availability():
    """Check availability"""
    data = request.get_json()
    # Implement availability checking
    return jsonify({'available': True})


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current scraping configuration"""
    return jsonify({
        'platform_config': PLATFORM_CONFIG,
        'loaded': True
    })

@app.route('/api/compare', methods=['GET'])
def get_compare_data():
    """Get product comparison data from compare.json"""
    try:
        compare_path = os.path.join(os.path.dirname(__file__), 'compare.json')
        
        if not os.path.exists(compare_path):
            return jsonify({
                'error': 'compare.json not found',
                'message': 'Please run compare.py to generate comparison data'
            }), 404
        
        with open(compare_path, 'r', encoding='utf-8') as f:
            compare_data = json.load(f)
        
        # Transform compare.json structure to Product[] format
        products = []
        for item in compare_data.get('products', []):
            # Each item has a 'platforms' object with platform-specific data
            for platform_name, platform_data in item.get('platforms', {}).items():
                product = {
                    'id': f"{platform_name}-{item.get('name', '').lower().replace(' ', '-')[:20]}",
                    'name': item.get('name', ''),
                    'description': item.get('original_names', {}).get(platform_name, ''),
                    'image': platform_data.get('image', ''),
                    'price': platform_data.get('price', 0),
                    'currency': platform_data.get('currency', 'INR'),
                    'platform': platform_name,
                    'availability': platform_data.get('availability', True),
                    'rating': platform_data.get('rating', 0),
                    'reviewCount': platform_data.get('reviewCount', 0),
                    'features': [],
                    'link': platform_data.get('link', ''),
                    'location': compare_data.get('location', {}).get('city', '') + ', ' + compare_data.get('location', {}).get('state', ''),
                    'deliveryTime': platform_data.get('deliveryTime', 'N/A'),
                    'deliveryFee': platform_data.get('deliveryFee', 0),
                    'originalPrice': None,
                    'quantity': platform_data.get('quantity', None)
                }
                products.append(product)
        
        return jsonify({
            'products': products,
            'search_query': compare_data.get('search_query', ''),
            'total_products': len(products),
            'matched_products': compare_data.get('matched_products', 0),
            'location': compare_data.get('location', {})
        })
    except FileNotFoundError:
        return jsonify({
            'error': 'compare.json not found',
            'message': 'Please run compare.py to generate comparison data'
        }), 404
    except json.JSONDecodeError as e:
        return jsonify({
            'error': 'Invalid JSON in compare.json',
            'message': str(e)
        }), 500
    except Exception as error:
        print(f'[API] Error loading compare.json: {error}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to load comparison data',
            'message': str(error)
        }), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint - API information"""
    return jsonify({
        'message': 'Fast E-commerce API Server (Flask)',
        'version': '1.0.0',
        'endpoints': {
            'search_all': 'POST /api/search',
            'search_platform': 'POST /api/search/<platform>',
            'product_details': 'GET /api/product/<platform>/<product_id>',
            'availability': 'POST /api/availability',
            'health': 'GET /health'
        },
        'supported_platforms': ['zepto', 'swiggy-instamart', 'bigbasket', 'blinkit']
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested URL was not found on the server.',
        'available_endpoints': {
            'search_all': 'POST /api/search',
            'search_platform': 'POST /api/search/<platform>',
            'product_details': 'GET /api/product/<platform>/<product_id>',
            'availability': 'POST /api/availability',
            'health': 'GET /health',
            'root': 'GET /'
        }
    }), 404


if __name__ == '__main__':
    print(f'Fast E-commerce API server (Flask) running on port {PORT}')
    print(f'Set VITE_API_BASE_URL=http://localhost:{PORT} in your .env file')
    print(f'\n[Config] Search Debug: {"✓ ENABLED (timestamped folders)" if SEARCH_DEBUG else "✗ DISABLED (overwrite mode)"}')
    print('\n[Config] Platform scraping configuration:')
    for platform, config in PLATFORM_CONFIG.items():
        status = '✓ ENABLED' if config.get('scrape', False) else '✗ DISABLED'
        headless = 'headless' if config.get('headless', True) else 'visible'
        print(f'  {platform}: {status} ({headless})')
    print()
    app.run(host='0.0.0.0', port=PORT, debug=True)

