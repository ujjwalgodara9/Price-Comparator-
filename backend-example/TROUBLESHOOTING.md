# Troubleshooting Guide

## "Not Found" Error

If you're getting a "Not Found" error, here's how to fix it:

### 1. Check if Server is Running

**Flask:**
```bash
python server.py
```
You should see: `Fast E-commerce API server (Flask) running on port 3001`

**Node.js:**
```bash
node server.js
```
You should see: `Fast E-commerce API server running on port 3001`

### 2. Test Server is Running

Open browser or use curl:
```bash
# Test root endpoint
curl http://localhost:3001/

# Test health endpoint
curl http://localhost:3001/health
```

### 3. Check Correct Endpoints

**Available Endpoints:**

- `GET /` - API information
- `GET /health` - Health check
- `POST /api/search` - Search all platforms
- `POST /api/search/<platform>` - Search specific platform
- `GET /api/product/<platform>/<product_id>` - Get product details
- `POST /api/availability` - Check availability

### 4. Common Mistakes

**Wrong HTTP Method:**
```bash
# ❌ Wrong - GET instead of POST
curl http://localhost:3001/api/search/zepto

# ✅ Correct - POST with JSON body
curl -X POST http://localhost:3001/api/search/zepto \
  -H "Content-Type: application/json" \
  -d '{"query":"milk","location":{"city":"Bangalore","state":"Karnataka","coordinates":{"lat":13.0358,"lng":77.5311}}}'
```

**Missing Content-Type Header:**
```bash
# ❌ Wrong - Missing Content-Type
curl -X POST http://localhost:3001/api/search/zepto -d '{"query":"milk"}'

# ✅ Correct - With Content-Type
curl -X POST http://localhost:3001/api/search/zepto \
  -H "Content-Type: application/json" \
  -d '{"query":"milk","location":{"city":"Bangalore"}}'
```

**Wrong Port:**
```bash
# Check what port server is actually running on
# Default is 3001, but might be different
```

### 5. Test with PowerShell

**Flask/Node.js:**
```powershell
# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:3001/health"

# Test search
$body = '{"query":"milk","location":{"city":"Bangalore","state":"Karnataka","coordinates":{"lat":13.0358,"lng":77.5311}}}'
Invoke-RestMethod -Uri "http://localhost:3001/api/search/zepto" -Method POST -ContentType "application/json" -Body $body
```

### 6. Check Server Logs

Look at the terminal where server is running. You should see:
- Request logs
- Error messages
- Which endpoint was hit

### 7. Verify Route Exists

**For Flask:**
```python
# In server.py, check if route is defined:
@app.route('/api/search/<platform>', methods=['POST'])
```

**For Node.js:**
```javascript
// In server.js, check if route is defined:
app.post('/api/search/:platform', async (req, res) => {
```

### 8. CORS Issues

If you're calling from browser and getting CORS errors:
- Make sure `flask-cors` is installed (Flask)
- Make sure `cors` middleware is enabled (Node.js)
- Check browser console for CORS errors

### 9. Port Already in Use

If port 3001 is busy:
```bash
# Change port in server.py or server.js
PORT = 3002  # Python
const PORT = process.env.PORT || 3002;  # Node.js

# Or kill process using port 3001
# Windows:
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

### 10. Quick Test Script

Create `test-endpoints.ps1`:
```powershell
Write-Host "Testing API endpoints..." -ForegroundColor Cyan

# Test root
Write-Host "`n1. Testing root endpoint..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "http://localhost:3001/"
    Write-Host "✅ Root endpoint works!" -ForegroundColor Green
    $result | ConvertTo-Json
} catch {
    Write-Host "❌ Root endpoint failed: $_" -ForegroundColor Red
}

# Test health
Write-Host "`n2. Testing health endpoint..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "http://localhost:3001/health"
    Write-Host "✅ Health endpoint works!" -ForegroundColor Green
    $result | ConvertTo-Json
} catch {
    Write-Host "❌ Health endpoint failed: $_" -ForegroundColor Red
}

# Test search
Write-Host "`n3. Testing search endpoint..." -ForegroundColor Yellow
$body = '{"query":"milk","location":{"city":"Bangalore","state":"Karnataka","coordinates":{"lat":13.0358,"lng":77.5311}}}'
try {
    $result = Invoke-RestMethod -Uri "http://localhost:3001/api/search/zepto" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ Search endpoint works!" -ForegroundColor Green
    Write-Host "Found $($result.products.Count) products" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Search endpoint failed: $_" -ForegroundColor Red
    Write-Host $_.Exception.Response
}
```

Run it:
```powershell
.\test-endpoints.ps1
```

## Still Having Issues?

1. Check server console for error messages
2. Verify all dependencies are installed
3. Make sure you're using the correct HTTP method (GET vs POST)
4. Check the request body format (must be valid JSON)
5. Verify the endpoint URL is correct

