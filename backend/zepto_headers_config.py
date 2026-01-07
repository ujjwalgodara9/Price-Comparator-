"""
Zepto Headers Configuration

Extracted from cURL command - all headers needed for Zepto API
Some headers may need to be dynamic (device_id, session_id, etc.)
"""

import uuid
import json

# Generate or reuse these IDs (should be consistent per session)
_device_id = None
_session_id = None


def get_device_id():
    """Get or generate device ID (consistent per session)"""
    global _device_id
    if not _device_id:
        _device_id = str(uuid.uuid4())
    return _device_id


def get_session_id():
    """Get or generate session ID (consistent per session)"""
    global _session_id
    if not _session_id:
        _session_id = str(uuid.uuid4())
    return _session_id


def generate_request_id():
    """Generate unique request ID for each request"""
    return str(uuid.uuid4())


def get_zepto_headers(options=None):
    """
    Get all headers needed for Zepto API
    
    Args:
        options (dict): Optional overrides for headers
        
    Returns:
        dict: Headers object
    """
    if options is None:
        options = {}
    
    device_id = options.get('deviceId') or get_device_id()
    session_id = options.get('sessionId') or get_session_id()
    request_id = options.get('requestId') or generate_request_id()
    
    headers = {
        # Standard browser headers
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,en-IN;q=0.8',
        'origin': 'https://www.zepto.com',
        'referer': 'https://www.zepto.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # Zepto-specific headers
        'app_sub_platform': 'WEB',
        'app_version': '14.4.4',
        'appversion': '14.4.4',
        'auth_from_cookie': 'true',
        'auth_revamp_flow': 'v2',
        'device_id': device_id,
        'deviceid': device_id,
        'marketplace_type': options.get('marketplaceType', 'SUPER_SAVER'),
        'platform': 'WEB',
        'priority': 'u=1, i',
        'request_id': request_id,
        'requestid': request_id,
        'session_id': session_id,
        'sessionid': session_id,
        'source': 'DIRECT',
        'tenant': 'ZEPTO',
        
        # Security headers
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        
        # Compatible components (static - from cURL)
        'compatible_components': 'CONVENIENCE_FEE,RAIN_FEE,EXTERNAL_COUPONS,STANDSTILL,BUNDLE,MULTI_SELLER_ENABLED,PIP_V1,ROLLUPS,SCHEDULED_DELIVERY,SAMPLING_ENABLED,ETA_NORMAL_WITH_149_DELIVERY,ETA_NORMAL_WITH_199_DELIVERY,HOMEPAGE_V2,NEW_ETA_BANNER,VERTICAL_FEED_PRODUCT_GRID,AUTOSUGGESTION_PAGE_ENABLED,AUTOSUGGESTION_PIP,AUTOSUGGESTION_AD_PIP,BOTTOM_NAV_FULL_ICON,COUPON_WIDGET_CART_REVAMP,DELIVERY_UPSELLING_WIDGET,MARKETPLACE_CATEGORY_GRID,NO_PLATFORM_CHECK_ENABLED_V2,SUPER_SAVER:1,SUPERSTORE_V1,PROMO_CASH:0,24X7_ENABLED_V1,TABBED_CAROUSEL_V2,HP_V4_FEED,WIDGET_BASED_ETA,PC_REVAMP_1,NO_COST_EMI_V1,PRE_SEARCH,ITEMISATION_ENABLED,ZEPTO_PASS,ZEPTO_PASS:5,BACHAT_FOR_ALL,SAMPLING_UPSELL_CAMPAIGN,DISCOUNTED_ADDONS_ENABLED,UPSELL_COUPON_SS:0,ENABLE_FLOATING_CART_BUTTON,NEW_FEE_STRUCTURE,NEW_BILL_INFO,RE_PROMISE_ETA_ORDER_SCREEN_ENABLED,SUPERSTORE_V1,MANUALLY_APPLIED_DELIVERY_FEE_RECEIVABLE,MARKETPLACE_REPLACEMENT,ZEPTO_PASS,ZEPTO_PASS:5,ZEPTO_PASS_RENEWAL,CART_REDESIGN_ENABLED,SHIPMENT_WIDGETIZATION_ENABLED,TABBED_CAROUSEL_V2,24X7_ENABLED_V1,PROMO_CASH:0,HOMEPAGE_V2,SUPER_SAVER:1,NO_PLATFORM_CHECK_ENABLED_V2,HP_V4_FEED,GIFT_CARD,SCLP_ADD_MONEY,GIFTING_ENABLED,OFSE,WIDGET_BASED_ETA,PC_REVAMP_1,NEW_ETA_BANNER,NO_COST_EMI_V1,ITEMISATION_ENABLED,SWAP_AND_SAVE_ON_CART,WIDGET_RESTRUCTURE,PRICING_CAMPAIGN_ID,BACHAT_FOR_ALL,TABBED_CAROUSEL_V3,CART_LMS:2,SAMPLING_UPSELL_CAMPAIGN,DISCOUNTED_ADDONS_ENABLED,UPSELL_COUPON_SS:0,SIZE_EXCHANGE_ENABLED,ENABLE_FLOATING_CART_BUTTON,SAMPLING_V3,HYBRID_CAMPAIGN',
    }
    
    # Optional headers (uncomment if needed)
    if options.get('csrfSecret'):
        headers['x-csrf-secret'] = options['csrfSecret']
    if options.get('timezone'):
        headers['x-timezone'] = options['timezone']
    if options.get('xsrfToken'):
        headers['x-xsrf-token'] = options['xsrfToken']
    if options.get('storeId'):
        headers['store_id'] = options['storeId']
        headers['storeid'] = options['storeId']
    if options.get('storeIds'):
        headers['store_ids'] = options['storeIds']
    if options.get('storeEtas'):
        headers['store_etas'] = json.dumps(options['storeEtas'])
    if options.get('requestSignature'):
        headers['request-signature'] = options['requestSignature']
    if options.get('cookies'):
        headers['Cookie'] = options['cookies']
    
    return headers

