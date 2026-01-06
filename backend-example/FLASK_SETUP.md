# Flask Backend Setup

The backend has been converted to Flask (Python) from Node.js/Express.

## Installation

### Step 1: Install Python Dependencies

```bash
cd backend-example
pip install -r requirements.txt
```

Or if you prefer virtual environment (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start the Server

```bash
python server.py
```

You should see:
```
Fast E-commerce API server (Flask) running on port 3001
Set VITE_API_BASE_URL=http://localhost:3001 in your .env file
```

### Step 3: Test the API

**Using PowerShell:**
```powershell
$body = '{"query":"milk","location":{"city":"Bangalore","state":"Karnataka","coordinates":{"lat":13.0358,"lng":77.5311}}}'
Invoke-RestMethod -Uri "http://localhost:3001/api/search/zepto" -Method POST -ContentType "application/json" -Body $body
```

**Using curl:**
```bash
curl -X POST http://localhost:3001/api/search/zepto \
  -H "Content-Type: application/json" \
  -d '{"query":"milk","location":{"city":"Bangalore","state":"Karnataka","coordinates":{"lat":13.0358,"lng":77.5311}}}'
```

## Why Flask?

### Flask (Python) ✅
- **Pros:**
  - Great for web scraping (BeautifulSoup, requests)
  - Easy to use with Selenium for JS-heavy sites
  - Large ecosystem for data processing
  - Good for ML/AI integration if needed later
  - Simple syntax
  - Better scraping libraries than Node.js
  
- **Cons:**
  - Slightly slower than Node.js for I/O operations
  - Requires Python environment

This project uses Flask as the backend for better web scraping capabilities.

## Troubleshooting

### Module not found errors
```bash
pip install -r requirements.txt
```

### Port already in use
Change port in `server.py`:
```python
PORT = 3002  # Change from 3001
```

### Virtual environment issues
Make sure virtual environment is activated before installing/running.

