# Backend API Server for Fast E-commerce Product Scraping

This is a **Python/Flask** backend server that handles scraping product data from fast e-commerce platforms to avoid CORS issues when running from the browser.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
```

3. Set environment variable in your frontend `.env` file:
```
VITE_API_BASE_URL=http://localhost:3001
```

## Implementation Notes

### Scraping Approaches

1. **Requests + BeautifulSoup** (for static HTML):
   - Good for simple HTML pages
   - Fast and lightweight
   - Python's requests library for HTTP calls
   - BeautifulSoup for HTML parsing

2. **Selenium** (for dynamic content):
   - Handles JavaScript-rendered pages
   - Can interact with pages (click, scroll, etc.)
   - Slower but more reliable for modern SPAs
   - Better Python ecosystem than Puppeteer

3. **API Endpoints** (if available):
   - Some platforms may have public/internal APIs
   - Check network requests in browser DevTools
   - Most reliable but may require authentication
   - Use Python's `requests` library

### Platform-Specific Notes

#### Zepto
- Search URL: `https://www.zepto.com/search?q={query}`
- May require location headers
- Products are likely in JSON format in page source

#### Swiggy Instamart
- Uses API endpoints: `https://www.swiggy.com/api/instamart/search`
- May require authentication tokens
- Check browser network requests for exact endpoints

#### BigBasket
- Search URL: `https://www.bigbasket.com/ps/?q={query}`
- May have rate limiting
- Products in HTML structure

#### Blinkit
- Search URL: `https://blinkit.com/search?q={query}`
- May use API endpoints similar to Swiggy
- Check network requests for API structure

#### Dunzo
- May have API endpoints
- Check network requests in browser DevTools

### Legal Considerations

⚠️ **Important**: 
- Always check robots.txt and Terms of Service
- Respect rate limits
- Consider using official APIs if available
- Some platforms may block automated access

### Rate Limiting

Implement rate limiting to avoid being blocked:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per 15 minutes"]
)

@app.route('/api/search')
@limiter.limit("10 per minute")
def search():
    # Your code here
    pass
```

### Error Handling

- Implement retry logic with exponential backoff
- Cache results to reduce API calls
- Handle timeouts gracefully
- Log errors for debugging

### Production Considerations

- Use a proper database to cache results
- Implement authentication for API access
- Add monitoring and logging
- Use a queue system (e.g., Bull) for async scraping
- Consider using a proxy service for IP rotation

