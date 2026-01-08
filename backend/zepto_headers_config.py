"""
Zepto API Headers Configuration

This module provides headers required for making requests to Zepto's API endpoints.
"""

import uuid


def get_zepto_headers():
    """
    Returns headers required for Zepto API requests.
    
    These headers mimic a browser request to avoid being blocked.
    """
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://www.zepto.com',
        'Referer': 'https://www.zepto.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        # Add a unique request ID if needed
        'X-Request-ID': str(uuid.uuid4()),
    }

