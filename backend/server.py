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
        data = request.get_json()
        query = data.get('query', '')
        location = data.get('location', {})
        platforms = data.get('platforms', ['zepto'])
        
        all_products = []
        
        # Search each platform
        for platform in platforms:
            try:
                products = search_platform(platform, query, location)
                all_products.extend(products)
            except Exception as error:
                print(f'Error searching {platform}: {error}')
                # Continue with other platforms even if one fails
                continue
        
        return jsonify({'products': all_products})
    except Exception as error:
        print(f'Search error: {error}')
        return jsonify({'error': 'Failed to search products'}), 500


@app.route('/api/search/<platform>', methods=['POST'])
def search_platform_endpoint(platform):
    """Platform-specific search endpoint"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        location = data.get('location', {})
        
        products = search_platform(platform, query, location)
        return jsonify({'products': products})
    except Exception as error:
        print(f'Error searching {platform}: {error}')
        return jsonify({'error': f'Failed to search on {platform}'}), 500


def search_platform(platform, query, location):
    """Search a specific platform"""
    platform_map = {
        'zepto': scrape_zepto,
        'swiggy-instamart': scrape_swiggy_instamart,
        'bigbasket': scrape_bigbasket,
        'blinkit': scrape_blinkit,
        'dunzo': scrape_dunzo,
    }
    
    scraper = platform_map.get(platform)
    if scraper:
        return scraper(query, location)
    return []


def scrape_zepto(query, location):
    """Zepto Scraper - Uses actual Zepto API endpoint"""
    try:
        lat = location.get('coordinates', {}).get('lat', 13.035819079405993)
        lng = location.get('coordinates', {}).get('lng', 77.53113274824308)
        
        # Zepto's actual API endpoint
        api_url = 'https://bff-gateway.zepto.com/lms/api/v2/get_page'
        
        # Get all required headers from config
        headers = get_zepto_headers()
        
        params = {
            'latitude': lat,
            'longitude': lng,
            'page_type': 'SEARCH' if query else 'HOME',
            'version': 'v2',
            'show_new_eta_banner': True,
            'page_size': 50,
            'enforce_platform_type': 'DESKTOP',
        }
        
        if query:
            params['query'] = query
        
        response = requests.get(api_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse response - adjust based on actual response structure
        data = response.json()
        
        # Extract products from response (adjust path based on actual structure)
        items = []
        if 'data' in data and 'products' in data['data']:
            items = data['data']['products']
        elif 'data' in data and 'items' in data['data']:
            items = data['data']['items']
        elif 'results' in data:
            items = data['results']
        elif 'items' in data:
            items = data['items']
        elif 'products' in data:
            items = data['products']
        elif isinstance(data, list):
            items = data
        
        # Map to our product format
        products = []
        for index, item in enumerate(items):
            product = {
                'id': item.get('id') or item.get('product_id') or item.get('productId') or f'zepto-{index}',
                'name': item.get('name') or item.get('title') or item.get('product_name') or item.get('productName') or '',
                'description': item.get('description') or item.get('short_description') or item.get('desc') or '',
                'image': item.get('image') or item.get('image_url') or item.get('imageUrl') or item.get('thumbnail') or item.get('img') or 'https://via.placeholder.com/400',
                'price': float(item.get('price') or item.get('final_price') or item.get('finalPrice') or item.get('selling_price') or item.get('sellingPrice') or item.get('amount') or 0),
                'currency': 'INR',
                'platform': 'zepto',
                'availability': item.get('in_stock', True) is not False and item.get('available', True) is not False and item.get('is_available', True) is not False,
                'rating': float(item.get('rating') or item.get('avg_rating') or item.get('averageRating') or item.get('avgRating') or 0),
                'reviewCount': int(item.get('review_count') or item.get('reviews') or item.get('reviewCount') or 0),
                'features': item.get('features') or item.get('highlights') or item.get('tags') or [],
                'link': item.get('url') or item.get('link') or item.get('product_url') or f"https://www.zepto.com/product/{item.get('slug') or item.get('id') or item.get('product_id')}",
                'location': f"{location.get('city', '')}, {location.get('state', '')}",
                'deliveryTime': item.get('delivery_time') or item.get('deliveryTime') or item.get('estimated_delivery') or item.get('eta') or '10-15 mins',
                'deliveryFee': float(item.get('delivery_fee') or item.get('deliveryFee') or item.get('shipping_charge') or item.get('shippingCharge') or 0),
                'originalPrice': float(item.get('original_price') or item.get('originalPrice') or item.get('mrp') or item.get('list_price') or item.get('listPrice') or 0) or None,
            }
            
            # Filter products based on search query if provided
            if query:
                search_lower = query.lower()
                if search_lower not in product['name'].lower() and search_lower not in product['description'].lower():
                    continue
            
            # Filter out invalid products
            if product['name'] and product['price'] > 0:
                products.append(product)
        
        print(f'Zepto: Found {len(products)} products')
        return products
    except requests.exceptions.RequestException as error:
        print(f'Zepto scraping error: {error}')
        return []
    except Exception as error:
        print(f'Zepto parsing error: {error}')
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


def scrape_dunzo(query, location):
    """Dunzo Scraper"""
    # Implement Dunzo scraping
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

