import http.server
import socketserver
import json
from urllib.parse import urlparse
from data_generator import get_initial_data
from redis_state import initialize_prices, is_redis_available
from datetime import datetime
from collections import deque

import os
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
PORT = int(os.getenv("PORT", 8000))
API_ENDPOINT = os.getenv("API_ENDPOINT", "/api/initial_data")

# --- Rolling Event Buffer (Last 5 HTTP Events) ---
http_event_buffer = deque(maxlen=5)

def display_http_events():
    """Display the last 5 HTTP events in a clean format."""
    print("\n" + "="*50)
    print("  HTTP SERVER (Last 5 Events)")
    print("="*50)
    if not http_event_buffer:
        print("  [No events yet]")
    else:
        for event in http_event_buffer:
            print(f"  {event}")
    print("="*50 + "\n")

# --- Define the Custom Request Handler ---
class SimpleAPIHandler(http.server.SimpleHTTPRequestHandler):
    """
    A custom HTTP request handler that specifically serves the initial data
    and handles CORS for cross-domain requests from the React app.
    """

    def log_message(self, format, *args):
        """Override to suppress default request logging."""
        pass  # Suppress default logs

    def _set_headers(self, status_code=200):
        """Sets standard headers, including required CORS headers."""
        self.send_response(status_code)
        
        # 1. CORS Headers: Must allow the React app's origin (e.g., localhost:3000)
        self.send_header('Access-Control-Allow-Origin', '*') 
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        
        # 2. Content Type Header
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_OPTIONS(self):
        """Handle pre-flight OPTIONS request required by CORS."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        http_event_buffer.append(f"[{timestamp}] OPTIONS {self.path}")
        display_http_events()
        self._set_headers(204) # 204 No Content for successful OPTIONS

    def do_GET(self):
        """Handle GET requests."""
        # Parse the URL to get the path
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if path == API_ENDPOINT:
            http_event_buffer.append(f"[{timestamp}] GET {API_ENDPOINT} → 200 OK")
            display_http_events()
            
            # 1. Generate the initial data (reads from Redis)
            data = get_initial_data(history_size=50) # Request 50 historical points
            
            # 2. Convert data to JSON string
            json_response = json.dumps(data)
            
            # 3. Send successful headers
            self._set_headers(200)
            
            # 4. Write the JSON response body
            self.wfile.write(json_response.encode('utf-8'))
            
        else:
            http_event_buffer.append(f"[{timestamp}] GET {path} → 404 Not Found")
            display_http_events()
            
            # Handle unknown paths with 404
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

# --- Server Execution ---
def run_http_server():
    """Starts the simple HTTP server with Redis state."""
    # Check Redis availability
    if not is_redis_available():
        print("\n" + "="*60)
        print(" Redis Connection Required")
        print("="*60)
        print("\nThe HTTP server requires Redis for shared state management.")
        print("\nPlease start Redis before running the server:")
        print("  Windows: memurai")
        print("  Linux/Mac: redis-server")
        print("\nOr install Redis:")
        print("  Windows: choco install memurai")
        print("  Ubuntu: sudo apt install redis-server")
        print("  macOS: brew install redis")
        print("\n" + "="*60 + "\n")
        exit(1)
    
    # Initialize Redis prices
    print("\n📊 Initializing Redis state...")
    initialize_prices()
    print()
    
    # Use socketserver to handle incoming connections
    with socketserver.TCPServer(("", PORT), SimpleAPIHandler) as httpd:
        print("--------------------------------------------------")
        print(f"📡 HTTP API Server serving at port {PORT}")
        print(f"✅ Initial Data Endpoint: http://localhost:{PORT}{API_ENDPOINT}")
        print(f"✅ Using Redis shared state")
        print("--------------------------------------------------")
        
        try:
            # Activate the server; it will run indefinitely until stopped
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 HTTP Server shut down manually.")
            httpd.shutdown()

if __name__ == "__main__":
    run_http_server()
