# Backend API Server

Flask server for web scraping product data from quick delivery platforms.

## Setup

```bash
pip install -r requirements.txt
python server.py
```

Server runs on: `http://localhost:3001`

## Endpoints

- `GET /health` - Health check
- `POST /search` - Search products across platforms

## Configuration

Edit `zepto_headers_config.py` to update API headers and endpoints for different platforms.