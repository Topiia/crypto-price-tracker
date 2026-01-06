# Windows PowerShell Setup Guide
# Complete Installation & Running Instructions

## 📋 Prerequisites Check

Before starting, ensure you have:
- Administrator access (for Chocolatey/Memurai installation)
- Internet connection
- Windows 10/11

---

## 🚀 Complete Setup Commands

### STEP 1: Install Redis (Memurai for Windows)

**Option A - Using Chocolatey (Recommended):**

```powershell
# Install Chocolatey (if not already installed) - Run as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Memurai
choco install memurai -y

# Start Memurai
memurai
```

**Option B - Manual Download:**
1. Download from: https://www.memurai.com/get-memurai
2. Install the `.msi` file
3. Memurai starts automatically as a Windows service

**Verify Redis:**
```powershell
redis-cli ping
# Expected output: PONG
```

---

### STEP 2: Navigate to Project Directory

```powershell
cd c:\python\revision\Cryptocurrency-price-project
```

---

### STEP 3: Install Backend Dependencies

```powershell
cd pythonBackend
pip install -r requirements.txt
cd ..
```

**What gets installed:**
- `redis>=5.0.0`
- `websockets>=12.0`
- `python-dotenv>=1.0.0`

---

### STEP 4: Install Frontend Dependencies

```powershell
cd frontend-react-app
npm install
cd ..
```

---

### STEP 5: Run the Application (3 Terminals)

Open **3 separate PowerShell windows** in the project directory.

#### Terminal 1 - HTTP Server
```powershell
cd pythonBackend
python api_server.py
```

**Expected Output:**
```
📊 Initializing Redis state...
Initialized BTC: $60000.0
Initialized ETH: $3500.0
Initialized SOL: $150.0
Initialized DOGE: $0.15

--------------------------------------------------
📡 HTTP API Server serving at port 8000
✅ Initial Data Endpoint: http://localhost:8000/api/initial_data
✅ Using Redis shared state
--------------------------------------------------
```

---

#### Terminal 2 - WebSocket Server
```powershell
cd pythonBackend
python websocket_server.py
```

**Expected Output:**
```
📊 Initializing Redis state...
Using existing BTC: $60000.0
Using existing ETH: $3500.0
Using existing SOL: $150.0
Using existing DOGE: $0.15

--------------------------------------------------
🚀 WebSocket Server running on ws://localhost:8001
✅ Using Redis shared state
--------------------------------------------------
[HH:MM:SS] Starting real-time data feed...
Tracking Assets: ['BTC', 'ETH', 'SOL', 'DOGE']
✅ Using Redis shared state
```

---

#### Terminal 3 - Frontend (React)
```powershell
cd frontend-react-app
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

### STEP 6: Open Browser

Navigate to: **http://localhost:5173**

You should see:
- ✅ Live status indicator showing "Live"
- ✅ Real-time price chart
- ✅ Price table with 4 cryptocurrencies
- ✅ Animated ticker at the bottom

---

## 🧪 Quick Test Commands

### Test Redis Connection
```powershell
redis-cli ping
# Should return: PONG
```

### Test Redis State
```powershell
redis-cli GET price:BTC
# Should return a price like: "60234.50"
```

### Test HTTP API
```powershell
curl http://localhost:8000/api/initial_data
# Should return JSON array of historical data
```

---

## 🛑 Stopping the Application

To stop all servers:
1. Press `Ctrl+C` in each terminal window
2. Servers will shut down gracefully

---

## 🔄 Restart All Services (Quick)

If you need to restart everything:

```powershell
# Stop all (Ctrl+C in each terminal)

# Restart in order:
# Terminal 1:
cd pythonBackend
python api_server.py

# Terminal 2:
cd pythonBackend
python websocket_server.py

# Terminal 3:
cd frontend-react-app
npm run dev
```

---

## ⚙️ Optional: Configure Update Interval

To slow down or speed up price updates:

```powershell
# Set custom interval (in seconds)
$env:FEED_INTERVAL = "2.0"
python websocket_server.py
```

Default is 0.5 seconds (2 updates per second).

---

## 🐛 Troubleshooting

### Error: "Redis is not available"
```powershell
# Check if Memurai service is running
Get-Service Memurai

# Start Memurai service
Start-Service Memurai

# Or run manually
memurai
```

### Error: "Port 8000 already in use"
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual PID)
taskkill /PID <PID> /F
```

### Error: "ModuleNotFoundError"
```powershell
# Reinstall Python dependencies
cd pythonBackend
pip install -r requirements.txt --force-reinstall
```

### Frontend won't connect
1. Verify HTTP server is running: http://localhost:8000/api/initial_data
2. Verify WebSocket server is running (check terminal output)
3. Clear browser cache and reload

---

## 📊 Complete Installation Summary

### One-Time Setup:
```powershell
# 1. Install Redis/Memurai
choco install memurai -y

# 2. Install backend dependencies
cd pythonBackend
pip install -r requirements.txt

# 3. Install frontend dependencies
cd ../frontend-react-app
npm install
```

### Every Time You Run:
```powershell
# Terminal 1: HTTP Server
cd pythonBackend
python api_server.py

# Terminal 2: WebSocket Server
cd pythonBackend
python websocket_server.py

# Terminal 3: Frontend
cd frontend-react-app
npm run dev
```

### Open Browser:
**http://localhost:5173**

---

## ✅ Success Checklist

After following all steps, you should have:
- [x] Redis/Memurai running and responding to `ping`
- [x] HTTP server running on port 8000
- [x] WebSocket server running on port 8001
- [x] Frontend running on port 5173
- [x] Dashboard showing live price updates
- [x] "Live" status indicator in top right

---

**🎉 You're all set! The dashboard is now streaming live cryptocurrency prices with Redis-backed shared state.**
