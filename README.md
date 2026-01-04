# CryptoDash - Real-Time Cryptocurrency Dashboard

A high-performance, responsive cryptocurrency dashboard featuring real-time price updates via WebSockets and a modern "Crypto Dark Mode" aesthetic.

## Features

- **Real-Time Data**: Live price updates using WebSockets.
- **Interactive Charts**: Dynamic price history visualization with Recharts.
- **Live Status**: Visual indicator for WebSocket connection health.
- **Responsive Design**: Fully responsive layout for desktop and mobile.
- **Dark Mode**: Sleek, neon-accented dark theme.

## Tech Stack

- **Frontend**: React, Vite, Recharts, Lucide React, CSS Modules.
- **Backend**: Python (http.server, websockets), AsyncIO.

## Getting Started

### Prerequisites

- Node.js (v16+)
- Python (v3.8+)

### 1. Backend Setup

Navigate to the backend directory and install dependencies (if any, standard library mostly used).

```bash
cd pythonBackend
pip install -r requirements.txt # or just pip install python-dotenv websockets
```

(Note: Ensure you have `websockets` installed: `pip install websockets`)

Create a `.env` file (optional, defaults provided):
```bash
cp .env.example .env
```

Start the HTTP API (Historical Data):
```bash
python api_server.py
```

Start the WebSocket Server (Real-Time Data):
```bash
python websocket_server.py
```
### Configurable WebSocket Update Interval

The WebSocket price stream interval is configurable via an environment variable.

By default, the server emits updates every 0.5 seconds.  
This can be adjusted without modifying code, which is useful for demos, debugging, or performance testing.

**Environment Variable:**
- `FEED_INTERVAL` — update interval in seconds (float)

**Example (slower updates for clarity):**

Windows (PowerShell):
```powershell
$env:FEED_INTERVAL="5"
python websocket_server.py


### 2. Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend-react-app
npm install
```

Start the development server:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

## Project Structure

- `pythonBackend/`: Python servers and data generator.
- `frontend-react-app/`: React application.
    - `src/components/`: Reusable UI components (Header, Charts, Tables).
    - `src/views/`: Main page layouts.
    - `src/hooks/`: Custom React hooks for data fetching.

## License

MIT
