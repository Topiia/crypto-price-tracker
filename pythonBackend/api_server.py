import http.server
import socketserver
import json
from urllib.parse import urlparse
from data_generator import get_initial_data  # Import the function from 1.1

import os
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
PORT = int(os.getenv("PORT", 8000))
API_ENDPOINT = os.getenv("API_ENDPOINT", "/api/initial_data")

# --- Define the Custom Request Handler ---
class SimpleAPIHandler(http.server.SimpleHTTPRequestHandler):
    """
    A custom HTTP request handler that specifically serves the initial data
    and handles CORS for cross-domain requests from the React app.
    """

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
        self._set_headers(204) # 204 No Content for successful OPTIONS

    def do_GET(self):
        """Handle GET requests."""
        # Parse the URL to get the path
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == API_ENDPOINT:
            print(f"[{self.date_time_string()}] GET request for {API_ENDPOINT} received.")
            
            # 1. Generate the initial data
            data = get_initial_data(history_size=50) # Request 50 historical points
            
            # 2. Convert data to JSON string
            json_response = json.dumps(data)
            
            # 3. Send successful headers
            self._set_headers(200)
            
            # 4. Write the JSON response body
            self.wfile.write(json_response.encode('utf-8'))
            
        else:
            # Handle unknown paths with 404
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

# --- Server Execution ---
def run_http_server():
    """Starts the simple HTTP server."""
    # Use socketserver to handle incoming connections
    with socketserver.TCPServer(("", PORT), SimpleAPIHandler) as httpd:
        print("--------------------------------------------------")
        print(f"📡 HTTP API Server serving at port {PORT}")
        print(f"✅ Initial Data Endpoint: http://localhost:{PORT}{API_ENDPOINT}")
        print("--------------------------------------------------")
        
        try:
            # Activate the server; it will run indefinitely until stopped
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 HTTP Server shut down manually.")
            httpd.shutdown()

if __name__ == "__main__":
    # Ensure data_generator.py is in the same directory!
    run_http_server()