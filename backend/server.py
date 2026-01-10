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
from ecommerce_platform.zepto import run_zepto_flow
from ecommerce_platform.blinkit import run_blinkit_flow

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
    """Search endpoint - searches across all platforms"""
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
        
        all_products = []
        
        # Search each platform
        for platform in platforms:
            try:
                print(f'[API] Searching platform: {platform}')
                products = search_platform(platform, query, location)
                print(f'[API] Platform {platform} returned {len(products)} products')
                all_products.extend(products)
            except Exception as error:
                print(f'[API] Error searching {platform}: {error}')
                import traceback
                traceback.print_exc()
                # Continue with other platforms even if one fails
                continue
        
        print(f'[API] Total products found: {len(all_products)}')
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
        
        products = search_platform(platform, query, location)
        print(f'[API] Platform {platform} returned {len(products)} products')
        return jsonify({'products': products})
    except Exception as error:
        print(f'[API] Error searching {platform}: {error}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to search on {platform}: {str(error)}'}), 500


def search_platform(platform, query, location):
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
        return scraper(query, location, platform_config)
    return []


def scrape_zepto(query, location, platform_config=None):
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
        products = run_zepto_flow(
            search_query=query,
            location=location,
            headless=headless,
            max_products=50
        )
        
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


def scrape_swiggy_instamart(query, location, platform_config=None):
    """Swiggy Instamart Scraper"""
    # Implement Swiggy Instamart scraping
    # Note: Swiggy uses API endpoints that may require authentication
    return []


def scrape_bigbasket(query, location, platform_config=None):
    """BigBasket Scraper"""
    # Implement BigBasket scraping
    return []


def scrape_blinkit(query, location, platform_config=None):
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
        products = run_blinkit_flow(
            search_query=query,
            location=location,
            headless=headless,
            max_products=50
        )
        
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
    print('\n[Config] Platform scraping configuration:')
    for platform, config in PLATFORM_CONFIG.items():
        status = '✓ ENABLED' if config.get('scrape', False) else '✗ DISABLED'
        headless = 'headless' if config.get('headless', True) else 'visible'
        print(f'  {platform}: {status} ({headless})')
    print()
    app.run(host='0.0.0.0', port=PORT, debug=True)

