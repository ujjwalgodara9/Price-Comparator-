# PowerShell script to test all API endpoints
# Usage: .\test-endpoints.ps1

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "Testing API Endpoints" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

# Test root endpoint
Write-Host "`n1. Testing root endpoint (GET /)..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "http://localhost:3001/" -ErrorAction Stop
    Write-Host "✅ Root endpoint works!" -ForegroundColor Green
    $result | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Root endpoint failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nMake sure server is running: python server.py or node server.js" -ForegroundColor Yellow
    exit
}

# Test health endpoint
Write-Host "`n2. Testing health endpoint (GET /health)..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "http://localhost:3001/health" -ErrorAction Stop
    Write-Host "✅ Health endpoint works!" -ForegroundColor Green
    $result | ConvertTo-Json
} catch {
    Write-Host "❌ Health endpoint failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test search endpoint
Write-Host "`n3. Testing search endpoint (POST /api/search/zepto)..." -ForegroundColor Yellow
$body = @{
    query = "milk"
    location = @{
        city = "Bangalore"
        state = "Karnataka"
        coordinates = @{
            lat = 13.0358
            lng = 77.5311
        }
    }
} | ConvertTo-Json -Depth 10

Write-Host "Request body:" -ForegroundColor Gray
Write-Host $body -ForegroundColor Gray

try {
    $result = Invoke-RestMethod -Uri "http://localhost:3001/api/search/zepto" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "✅ Search endpoint works!" -ForegroundColor Green
    Write-Host "Found $($result.products.Count) products" -ForegroundColor Cyan
    
    if ($result.products.Count -gt 0) {
        Write-Host "`nFirst product:" -ForegroundColor Cyan
        $result.products[0] | ConvertTo-Json -Depth 3
    }
} catch {
    Write-Host "❌ Search endpoint failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

