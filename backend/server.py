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
from zepto_headers_config import get_zepto_headers
from ecommerce_platform.zepto_itemlist import scrape_zepto_products

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

PORT = 3001

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
    platform_map = {
        'zepto': scrape_zepto,
        'swiggy-instamart': scrape_swiggy_instamart,
        'bigbasket': scrape_bigbasket,
        'blinkit': scrape_blinkit
    }
    
    scraper = platform_map.get(platform)
    if scraper:
        return scraper(query, location)
    return []


def scrape_zepto(query, location):
    """Zepto Scraper - Uses Playwright to scrape Zepto website"""
    try:
        if not query:
            print('[Zepto] Empty query, returning empty list')
            return []
        
        print(f'[Zepto] Starting scrape for query: "{query}"')
        
        # Use the Playwright-based scraper from zepto_itemlist
        # Run in headless mode for production
        products = scrape_zepto_products(
            search_query=query,
            location=location,
            headless=True,
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


def scrape_swiggy_instamart(query, location):
    """Swiggy Instamart Scraper"""
    # Implement Swiggy Instamart scraping
    # Note: Swiggy uses API endpoints that may require authentication
    return []


def scrape_bigbasket(query, location):
    """BigBasket Scraper"""
    # Implement BigBasket scraping
    return []


def scrape_blinkit(query, location):
    """Blinkit Scraper"""
    # Implement Blinkit scraping
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
        'supported_platforms': ['zepto', 'swiggy-instamart', 'bigbasket', 'blinkit', 'dunzo']
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
    app.run(host='0.0.0.0', port=PORT, debug=True)

