# PowerShell script to test Zepto API
# Usage: .\test-api.ps1

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

Write-Host "Testing Zepto API..." -ForegroundColor Cyan
Write-Host "Request body:" -ForegroundColor Yellow
Write-Host $body

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3001/api/search/zepto" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "`n✅ Success!" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json -Depth 10)
} catch {
    Write-Host "`n❌ Error:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host "`nMake sure the server is running: node server.js" -ForegroundColor Yellow
}

