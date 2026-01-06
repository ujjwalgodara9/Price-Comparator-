# How to Start the Server

## Step 1: Install Dependencies

```bash
cd backend-example
npm install
```

## Step 2: Start the Server

```bash
node server.js
```

You should see:
```
Fast E-commerce API server running on port 3001
Set VITE_API_BASE_URL=http://localhost:3001 in your .env file
```

## Step 3: Test the API

### Option A: Using PowerShell (Windows)

```powershell
.\test-api.ps1
```

Or manually:
```powershell
$body = '{"query":"milk","location":{"city":"Bangalore","state":"Karnataka","coordinates":{"lat":13.0358,"lng":77.5311}}}'
Invoke-RestMethod -Uri "http://localhost:3001/api/search/zepto" -Method POST -ContentType "application/json" -Body $body
```

### Option B: Using curl (Windows - Git Bash or WSL)

```bash
curl -X POST http://localhost:3001/api/search/zepto \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"milk\",\"location\":{\"city\":\"Bangalore\",\"state\":\"Karnataka\",\"coordinates\":{\"lat\":13.0358,\"lng\":77.5311}}}"
```

### Option C: Using Postman or Insomnia

1. Method: POST
2. URL: `http://localhost:3001/api/search/zepto`
3. Headers: `Content-Type: application/json`
4. Body (JSON):
```json
{
  "query": "milk",
  "location": {
    "city": "Bangalore",
    "state": "Karnataka",
    "coordinates": {
      "lat": 13.0358,
      "lng": 77.5311
    }
  }
}
```

## Troubleshooting

### Server won't start
- Make sure port 3001 is not in use
- Check if Node.js is installed: `node --version`
- Install dependencies: `npm install`

### Connection refused
- Make sure server is running
- Check if server started on port 3001
- Try a different port: `PORT=3002 node server.js`

### API returns empty results
- Check server console for errors
- Verify Zepto API is accessible
- May need to add cookies (see HEADERS_EXTRACTED.md)

