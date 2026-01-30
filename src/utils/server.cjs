require('dotenv').config();

const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const GEOAPIFY_API_KEY = process.env.GEOAPIFY_API_KEY || '';

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Proxy Geoapify autocomplete so API key stays on server
app.get('/api/autocomplete', (req, res) => {
  const text = (req.query.text || '').trim();
  if (!text) {
    return res.json({ results: [] });
  }
  if (!GEOAPIFY_API_KEY) {
    return res.status(500).json({
      error: 'GEOAPIFY_API_KEY not set. Add it to .env or set the environment variable.',
    });
  }
    const url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(text)}&format=json&limit=8&apiKey=${GEOAPIFY_API_KEY}`;
  const requestOptions = { method: 'GET' };
  fetch(url, requestOptions)
    .then((response) => response.json())
    .then((result) => res.json(result.results || []))
    .catch(() => res.status(502).json({ error: 'Autocomplete request failed' }));
});

// Receive selected address from frontend and print to console
app.post('/address', (req, res) => {
  const address = req.body;
  if (!address) {
    return res.status(400).json({ error: 'No address in body' });
  }
  const formatted = address.formatted || [address.address_line1, address.address_line2].filter(Boolean).join(', ') || JSON.stringify(address);
  console.log('\n--- Selected address ---');
  console.log('Formatted:', formatted);
  if (address.address_line1) console.log('Address line 1:', address.address_line1);
  if (address.address_line2) console.log('Address line 2:', address.address_line2);
  if (address.city) console.log('City:', address.city);
  if (address.postcode) console.log('Postcode:', address.postcode);
  if (address.state) console.log('State:', address.state);
  if (address.country) console.log('Country:', address.country);
  if (address.lat != null && address.lon != null) console.log('Coordinates:', address.lat, address.lon);
  console.log('------------------------\n');
  res.json({ ok: true, printed: true });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  if (!GEOAPIFY_API_KEY) {
    console.log('Warning: GEOAPIFY_API_KEY not set. Set it in .env or as an environment variable for autocomplete to work.');
  }
});
