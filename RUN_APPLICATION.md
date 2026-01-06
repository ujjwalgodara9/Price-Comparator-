# How to Run the Full Application

## Quick Start

### Step 1: Start the Backend Server

Open **Terminal 1**:
```bash
cd backend-example
pip install -r requirements.txt
python server.py
```

You should see:
```
Fast E-commerce API server (Flask) running on port 3001
```

### Step 2: Start the Frontend

Open **Terminal 2** (new terminal window):
```bash
# Make sure you're in the project root
cd ..
npm install
npm run dev
```

You should see:
```
VITE v5.x.x ready in xxx ms
➜  Local:   http://localhost:5173/
```

### Step 3: Open in Browser

Open: `http://localhost:5173/`

## Complete Commands

### Windows PowerShell

**Terminal 1 (Backend):**
```powershell
cd backend-example
pip install -r requirements.txt
python server.py
```

**Terminal 2 (Frontend):**
```powershell
npm install
npm run dev
```

### Mac/Linux

**Terminal 1 (Backend):**
```bash
cd backend-example
pip install -r requirements.txt
python server.py
```

**Terminal 2 (Frontend):**
```bash
npm install
npm run dev
```

## Using Startup Scripts

I've created startup scripts to make it easier:

### Windows
```powershell
.\start-backend.ps1    # Start backend in one terminal
.\start-frontend.ps1   # Start frontend in another terminal
```

Or use the combined script:
```powershell
.\start-all.ps1        # Starts both (requires multiple terminals)
```

### Mac/Linux
```bash
./start-backend.sh     # Start backend
./start-frontend.sh    # Start frontend
```

## Environment Setup

### Backend Environment Variables (Optional)

Create `backend-example/.env`:
```env
PORT=3001
```

### Frontend Environment Variables

Create `.env` in project root:
```env
VITE_API_BASE_URL=http://localhost:3001
```

## Verify Everything is Working

1. **Backend Health Check:**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:3001/health"
   ```
   Should return: `{"status": "ok", "message": "Server is running"}`

2. **Frontend:**
   - Open `http://localhost:5173/`
   - You should see the product comparison interface

3. **Test Search:**
   - Enter a product name (e.g., "milk")
   - Click search
   - Should fetch products from Zepto API

## Troubleshooting

### Backend won't start
- Check if port 3001 is available
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.7+)

### Frontend won't start
- Install dependencies: `npm install`
- Check Node.js version: `node --version` (should be 18+)
- Check if port 5173 is available

### API calls failing
- Make sure backend is running on port 3001
- Check `VITE_API_BASE_URL` in `.env` file
- Check browser console for CORS errors

### Port already in use
- Change backend port in `server.py`: `PORT = 3002`
- Update frontend `.env`: `VITE_API_BASE_URL=http://localhost:3002`

## Production Build

### Build Frontend
```bash
npm run build
```

### Serve Production Build
```bash
npm run preview
```

## Architecture

```
┌─────────────┐         HTTP Requests         ┌──────────────┐
│   Frontend  │ ────────────────────────────> │   Backend    │
│  (React)    │                                │   (Flask)    │
│ Port 5173   │ <────────────────────────────  │  Port 3001   │
└─────────────┘         JSON Response          └──────────────┘
                                                      │
                                                      │ API Calls
                                                      ▼
                                              ┌──────────────┐
                                              │   Zepto API  │
                                              │   Swiggy API │
                                              │   etc.       │
                                              └──────────────┘
```

