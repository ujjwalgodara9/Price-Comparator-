#!/bin/bash
# Bash script to test Zepto API
# Usage: ./test-api.sh

echo "Testing Zepto API..."

curl -X POST http://localhost:3001/api/search/zepto \
  -H "Content-Type: application/json" \
  -d '{
    "query": "milk",
    "location": {
      "city": "Bangalore",
      "state": "Karnataka",
      "coordinates": {
        "lat": 13.0358,
        "lng": 77.5311
      }
    }
  }'

echo ""

