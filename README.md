# Real-Time Cryptocurrency Price Tracker

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![React](https://img.shields.io/badge/react-18.x-61dafb)
![Redis](https://img.shields.io/badge/redis-5.0%2B-red)

A production-grade, real-time cryptocurrency dashboard demonstrating distributed systems architecture, WebSocket streaming, and shared state management with Redis.

---

## 🎯 Overview

This project implements a high-performance real-time price tracking system with:
- **Dual-protocol data delivery** (HTTP for historical, WebSocket for live)
- **Redis-backed shared state** ensuring data continuity across services
- **React frontend** with auto-reconnection and error boundaries
- **Python async backend** with concurrent WebSocket broadcasting

**Key Engineering Concepts Demonstrated:**
- Distributed state management with Redis
- WebSocket auto-reconnection with exponential backoff
- React error boundaries for resilience
- Data validation and schema enforcement
- Graceful degradation and fault tolerance

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────┐
│           Redis (Port 6379)                 │
│         Single Source of Truth              │
│  ┌───────────────────────────────────────┐  │
│  │ price:BTC  → 60234.50                 │  │
│  │ price:ETH  → 3521.75                  │  │
│  │ price:SOL  → 151.20                   │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         ↑                           ↑
         │ read/write                │ read/write
         │                           │
┌────────┴──────────┐      ┌────────┴──────────┐
│  HTTP Server      │      │ WebSocket Server  │
│  (Port 8000)      │      │ (Port 8001)       │
│                   │      │                   │
│ • Historical data │      │ • Live streaming  │
│ • 50 data points  │      │ • 0.5s interval   │
└───────────────────┘      └───────────────────┘
         ↓                           ↓
         └───────────────┬───────────┘
                         │
                ┌────────┴─────────┐
                │ React Frontend   │
                │ (Port 5173)      │
                │                  │
                │ • Recharts       │
                │ • Auto-reconnect │
                │ • Error boundary │
                └──────────────────┘
```

---

## 🚀 Features

### Backend
- ✅ **Redis Shared State** - Eliminates process-local state divergence
- ✅ **Price Continuity** - Last historical price = first live price
- ✅ **Async WebSocket** - Non-blocking concurrent client handling
- ✅ **CORS Support** - Cross-origin requests enabled
- ✅ **Environment Configuration** - `.env` based settings

### Frontend
- ✅ **Auto-Reconnection** - Exponential backoff (1s → 30s max)
- ✅ **Error Boundaries** - Graceful error recovery with fallback UI
- ✅ **Data Validation** - Schema enforcement prevents invalid data crashes
- ✅ **Real-Time Charts** - Recharts with sliding window (500 points)
- ✅ **Connection Status** - Live/Disconnected indicator

---

## 📋 Prerequisites

### Required
- **Node.js** v16+ ([Download](https://nodejs.org/))
- **Python** 3.8+ ([Download](https://www.python.org/))
- **Redis** 5.0+ (see installation below)

### Redis Installation

**Windows:**
```powershell
# Option 1: Memurai (native Windows port)
choco install memurai
memurai

# Option 2: WSL + Redis
wsl --install
wsl -d Ubuntu
sudo apt update && sudo apt install redis-server -y
redis-server
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install redis-server -y
redis-server
```

**macOS:**
```bash
brew install redis
redis-server
```

**Verify Redis is running:**
```bash
redis-cli ping
# Expected: PONG
```

---

## 🔧 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd Cryptocurrency-price-project
```

### 2. Backend Setup
```bash
cd pythonBackend
pip install -r requirements.txt
```

**Dependencies installed:**
- `redis>=5.0.0` - Redis client
- `websockets>=12.0` - WebSocket server
- `python-dotenv>=1.0.0` - Environment variables

### 3. Frontend Setup
```bash
cd ../frontend-react-app
npm install
```

---

## ▶️ Running the Application

### Environment Context

This application requires specific terminal environments for each service:
- **Redis:** WSL/Ubuntu terminal (mandatory on Windows)
- **Backend Servers:** Windows PowerShell (recommended) or CMD
- **Frontend:** Windows PowerShell (recommended) or CMD

**Critical:** Backend servers must run on Windows localhost to avoid cross-OS networking issues with the frontend.

---

### Execution Order

Services must be started in this order:

```
Redis → Backend (HTTP + WebSocket) → Frontend
```

Starting services out of order will cause connection failures.

---

### Step 1: Start Redis (WSL Terminal - MANDATORY)

#### 1.1 Open WSL Terminal

From Windows PowerShell:
```powershell
wsl -d Ubuntu
```

#### 1.2 Start Redis Server

Inside WSL terminal:
```bash
redis-server
```

**Expected Output:**
```
* Ready to accept connections on port 6379
```

**Leave this terminal running. Do not close it.**

#### 1.3 Verify Redis (New WSL Terminal)

Open a second WSL terminal:
```powershell
# From Windows PowerShell:
wsl -d Ubuntu
```

Verify Redis is running:
```bash
redis-cli ping
```

**Expected Output:**
```
PONG
```

If you don't see `PONG`, Redis is not running. Return to Step 1.2.

---

### Step 2: Start Backend Servers (Windows PowerShell)

The backend requires **two separate processes** running simultaneously:
1. HTTP API Server (port 8000) - serves historical data
2. WebSocket Server (port 8001) - streams live updates

Both servers share state via Redis, ensuring price continuity.

#### 2.1 Start HTTP API Server

**Terminal 1 (Windows PowerShell):**

```powershell
cd c:\python\revision\Cryptocurrency-price-project\pythonBackend
python api_server.py
```

**Expected Output:**
```
✅ Redis connected: localhost:6379
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

**Leave this terminal running.**

**Critical Check:** Verify you see "Using Redis shared state". If you see "Redis connection failed", Redis is not accessible from Windows.

#### 2.2 Start WebSocket Server

**Terminal 2 (Windows PowerShell):**

Open a new PowerShell window:

```powershell
cd c:\python\revision\Cryptocurrency-price-project\pythonBackend
python websocket_server.py
```

**Expected Output:**
```
✅ Redis connected: localhost:6379
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

**Leave this terminal running.**

**Critical Check:** Verify prices match the HTTP server (e.g., BTC: $60000.0). This confirms both servers are reading from the same Redis state.

---

### Step 3: Start Frontend (Windows PowerShell)

**Terminal 3 (Windows PowerShell):**

Open a new PowerShell window:

```powershell
cd c:\python\revision\Cryptocurrency-price-project\frontend-react-app
npm run dev
```

**Expected Output:**
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Leave this terminal running.**

---

### Step 4: Open Browser

Navigate to: **http://localhost:5173**

**Expected Dashboard State:**
- Green "Live" status indicator (top right)
- Real-time price chart showing BTC
- Price table with BTC, ETH, SOL, DOGE
- Prices updating every 0.5 seconds
- Animated ticker at bottom

**Browser Console Should Show:**
```
✅ WebSocket connected to Python server.
```

---

### Verification Steps

#### Verify Redis Connection

From WSL terminal:
```bash
redis-cli GET price:BTC
```

**Expected:** Returns a numeric value (e.g., `"60123.45"`)

#### Verify HTTP API

From Windows PowerShell:
```powershell
curl http://localhost:8000/api/initial_data
```

Or open in browser: http://localhost:8000/api/initial_data

**Expected:** JSON array of historical data points (200 items)

#### Verify WebSocket Streaming

Check Terminal 2 (websocket_server.py) console. You should see periodic activity.

#### Verify Frontend Connection

Browser console must show:
```
✅ WebSocket connected to Python server.
```

If you see "Could not connect to Python HTTP API", the HTTP server is not running or not accessible.

---

### Common Mistakes to Avoid

#### Mistake 1: Running Backend from WSL

**Incorrect:**
```bash
# Inside WSL terminal:
cd /mnt/c/python/revision/Cryptocurrency-price-project/pythonBackend
python api_server.py
```

**Correct:**
```powershell
# Windows PowerShell:
cd c:\python\revision\Cryptocurrency-price-project\pythonBackend
python api_server.py
```

**Reason:** Frontend runs on Windows localhost. Backend must run on Windows localhost to avoid cross-OS networking issues.

#### Mistake 2: Starting Services Out of Order

**Incorrect Order:**
```
Frontend → Backend → Redis  ❌
```

**Correct Order:**
```
Redis → Backend → Frontend  ✅
```

**Reason:** Backend requires Redis connection on startup. Frontend requires backend API on startup.

#### Mistake 3: Redis Not Running in WSL

**Symptom:** Backend shows error:
```
❌ Redis connection failed: [WinError 10061] No connection could be made
```

**Fix:** Start Redis in WSL terminal (Step 1.2). Verify with `redis-cli ping`.

#### Mistake 4: Running Multiple Redis Instances

**Incorrect:**
```bash
# Terminal 1:
redis-server

# Terminal 2:
redis-server  # ❌ Creates port conflict
```

**Correct:** Only one Redis instance should run. Verify with `redis-cli ping`.

#### Mistake 5: Using Wrong Python Environment

**Symptom:** `ModuleNotFoundError: No module named 'redis'`

**Fix:** Ensure dependencies are installed:
```powershell
cd pythonBackend
pip install -r requirements.txt
```

---

### Port Summary

| Service | Port | Protocol | Terminal Environment |
|---------|------|----------|---------------------|
| Redis | 6379 | TCP | WSL/Ubuntu |
| HTTP API | 8000 | HTTP | Windows PowerShell |
| WebSocket | 8001 | WS | Windows PowerShell |
| Frontend | 5173 | HTTP | Windows PowerShell |

---

### Shutdown Procedure

Stop services in reverse order:

1. **Frontend:** Press `Ctrl+C` in Terminal 3 (Windows)
2. **WebSocket Server:** Press `Ctrl+C` in Terminal 2 (Windows)
3. **HTTP Server:** Press `Ctrl+C` in Terminal 1 (Windows)
4. **Redis:** Press `Ctrl+C` in WSL terminal

---

### Quick Reference

```powershell
# Terminal WSL-1 (Ubuntu):
wsl -d Ubuntu
redis-server

# Terminal WIN-1 (PowerShell):
cd c:\python\revision\Cryptocurrency-price-project\pythonBackend
python api_server.py

# Terminal WIN-2 (PowerShell):
cd c:\python\revision\Cryptocurrency-price-project\pythonBackend
python websocket_server.py

# Terminal WIN-3 (PowerShell):
cd c:\python\revision\Cryptocurrency-price-project\frontend-react-app
npm run dev

# Browser:
# http://localhost:5173
```

---

## 🧪 Manual Testing Instructions

### Test 1: Verify Redis Shared State (Price Continuity)

**Objective:** Confirm HTTP and WebSocket servers share the same price state.

**Steps:**
1. Start Redis, both backend servers, and frontend
2. Open browser to `http://localhost:5173`
3. **Watch the chart during initial load:**
   - Historical data (50 points) loads first
   - WebSocket connects (status changes to "Live")
   - Live data starts flowing
4. **Expected:** Smooth transition with NO price jump
5. **Failure case (before fix):** Price jumps when transitioning from historical to live

**Verification:**
- Check backend console logs:
  ```
  HTTP server  → Historical endpoint for BTC: $60234.50
  WS server    → Using existing BTC: $60234.50  ← Must match!
  ```

---

### Test 2: WebSocket Auto-Reconnection

**Objective:** Verify automatic reconnection with exponential backoff.

**Steps:**
1. With dashboard running, observe "Live" status
2. Stop WebSocket server: `Ctrl+C` in the WebSocket terminal
3. **Observe frontend:** Status changes to "Disconnected"
4. **Open browser console:** Should see:
   ```
   Attempting to reconnect in 1s (attempt 1)...
   Reconnecting to WebSocket... (attempt 1)
   Attempting to reconnect in 2s (attempt 2)...
   ```
5. Restart WebSocket server: `python websocket_server.py`
6. **Expected:** Dashboard automatically reconnects, status shows "Live"

**Verification:**
- Reconnection delays increase: 1s → 2s → 4s → 8s → 16s → 30s (max)
- Data flow resumes without manual page refresh

---

### Test 3: Error Boundary (Malformed Data Handling)

**Objective:** Verify dashboard doesn't crash on invalid data.

**Steps:**
1. Stop WebSocket server
2. Open `pythonBackend/data_generator.py`
3. **Temporarily modify line 72:**
   ```python
   # FROM:
   yield json.dumps(new_data_batch)
   
   # TO:
   yield json.dumps({"bad": "data"})
   ```
4. Restart WebSocket server
5. **Observe browser console:**
   ```
   ⚠️ Invalid data format: expected array, got: object
   ⚠️ No valid data points in batch, skipping update
   ```
6. **Expected:** Dashboard continues working, shows warnings but no crash

**Verification:**
- App does NOT show white screen or error
- Valid data keeps flowing
- Console shows validation warnings

**Cleanup:** Revert the change in `data_generator.py`

---

### Test 4: Data Continuity Across Server Restarts

**Objective:** Verify prices persist in Redis across server restarts.

**Steps:**
1. Note current BTC price from dashboard (e.g., $60,234.50)
2. Stop **only** the WebSocket server (leave Redis and HTTP running)
3. Wait 5 seconds
4. Restart WebSocket server: `python websocket_server.py`
5. **Expected:** Prices continue from last known value (no reset to $60,000)

**Verification:**
- Check WebSocket startup logs:
  ```
  Using existing BTC: $60234.50  ← Continues from last value
  ```

---

### Test 5: Multiple Client Handling

**Objective:** Verify server handles concurrent connections.

**Steps:**
1. Open dashboard in 3 different browser tabs
2. **Observe WebSocket console:**
   ```
   Client connected from 127.0.0.1. Total active connections: 1
   Client connected from 127.0.0.1. Total active connections: 2
   Client connected from 127.0.0.1. Total active connections: 3
   ```
3. Close one tab
4. **Expected:** Connection count decrements, other tabs unaffected

**Verification:**
- All tabs receive identical real-time updates
- Server handles disconnects gracefully

---

## 🛠 Configuration

### Environment Variables

Create `.env` file in `pythonBackend/`:

```ini
# HTTP Server
PORT=8000
API_ENDPOINT=/api/initial_data

# WebSocket Server
WS_PORT=8001
FEED_INTERVAL=0.5

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

---

## 📁 Project Structure

```
Cryptocurrency-price-project/
├── pythonBackend/
│   ├── redis_state.py          # Redis state manager
│   ├── data_generator.py       # Price simulation engine
│   ├── api_server.py           # HTTP server (historical data)
│   ├── websocket_server.py     # WebSocket server (live data)
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment template
│
├── frontend-react-app/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ErrorBoundary.jsx      # Error recovery
│   │   │   ├── Header.jsx             # App header
│   │   │   ├── RealTimeChart.jsx      # Recharts line chart
│   │   │   ├── PriceTable.jsx         # Live prices table
│   │   │   └── VanillaTicker.jsx      # Bottom price ticker
│   │   ├── hooks/
│   │   │   └── useDataFetcher.js      # WebSocket + HTTP hook
│   │   ├── views/
│   │   │   └── Dashboard.jsx          # Main view
│   │   └── App.jsx                    # Root component
│   ├── package.json
│   └── vite.config.js
│
└── README.md                   # This file
```

---

## 🐛 Troubleshooting

### Issue: "Redis is not available"
**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis
redis-server
```

### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Find and kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Issue: Frontend shows "Could not connect to Python HTTP API"
**Solution:**
1. Verify HTTP server is running on port 8000
2. Check CORS is enabled in `api_server.py`
3. Ensure frontend is requesting `http://localhost:8000/api/initial_data`

### Issue: WebSocket won't reconnect
**Solution:**
1. Open browser console
2. Check for reconnection attempts
3. Verify WebSocket server is running on port 8001
4. Clear browser cache and reload

---

## 📊 Performance Considerations

- **Sliding Window:** Frontend keeps last 500 data points (prevents memory bloat)
- **Redis In-Memory:** Sub-millisecond read/write performance
- **Async WebSocket:** Non-blocking I/O for 1000+ concurrent clients
- **Memoization:** React `useMemo` prevents unnecessary chart re-renders

---

## 🎓 Learning Outcomes

This project demonstrates:
- **Distributed Systems:** Redis as shared state layer
- **Real-Time Communication:** WebSocket streaming patterns
- **Resilient Frontend:** Auto-reconnection, error boundaries, validation
- **Modern React:** Custom hooks, error boundaries, concurrent rendering
- **Python Async:** `asyncio` event loop and concurrent task management

---

## 📜 License

MIT License - see LICENSE file for details

---

## 👨‍💻 Development Notes

### Key Fixes Implemented:
1. **Bug #2:** WebSocket auto-reconnection with exponential backoff
2. **Bug #10:** Error boundaries + schema validation
3. **Bug #11:** Redis shared state (eliminates price discontinuity)

### Testing Checklist:
- [x] Redis connection
- [x] Price continuity (HTTP → WebSocket)
- [x] Auto-reconnection on disconnect
- [x] Invalid data handling
- [x] Multiple concurrent clients
- [x] Server restart resilience

---

**Built with ❤️ for demonstrating production-grade real-time systems architecture**
