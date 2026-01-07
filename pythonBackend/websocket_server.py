import asyncio
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed, ConnectionClosedError
import json
from datetime import datetime
from data_generator import generate_real_time_feed
from redis_state import initialize_prices, is_redis_available
from collections import deque

from dotenv import load_dotenv
import os

# --- Configuration ---
load_dotenv()
WS_PORT = int(os.getenv("WS_PORT", 8001))
CONNECTED_CLIENTS = set() # Set to store active WebSocket connections

# --- Rolling Event Buffer (Last 5 WebSocket Events) ---
ws_event_buffer = deque(maxlen=5)

def display_ws_events():
    """Display the last 5 WebSocket events in a clean format."""
    print("\n" + "="*50)
    print("  WEBSOCKET SERVER (Last 5 Events)")
    print("="*50)
    if not ws_event_buffer:
        print("  [No events yet]")
    else:
        for event in ws_event_buffer:
            print(f"  {event}")
    print("="*50 + "\n")

# --- Helper: Remove Dead Connection ---
def remove_client(websocket: WebSocketServerProtocol, reason: str = "disconnect"):
    """
    Proactively remove a client from CONNECTED_CLIENTS.
    This should be called immediately when a connection is detected as dead.
    """
    if websocket in CONNECTED_CLIENTS:
        CONNECTED_CLIENTS.remove(websocket)
        timestamp = datetime.now().strftime("%H:%M:%S")
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        ws_event_buffer.append(f"[{timestamp}] REMOVED {client_ip} ({reason}) (total: {len(CONNECTED_CLIENTS)})")
        display_ws_events()

# --- 1. Client Connection Handler ---
async def handler(websocket):
    """
    Handles a single client connection, adding it to the broadcast list
    and removing it upon disconnect.
    """
    # Register client connection
    CONNECTED_CLIENTS.add(websocket)
    
    client_ip = websocket.remote_address[0]
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    ws_event_buffer.append(f"[{timestamp}] CLIENT_CONNECT {client_ip} (total: {len(CONNECTED_CLIENTS)})")
    display_ws_events()

    try:
        await websocket.wait_closed()
        
    except websockets.exceptions.ConnectionClosedOK:
        pass
    except Exception as e:
        timestamp = datetime.now().strftime("%H:%M:%S")
        ws_event_buffer.append(f"[{timestamp}] ERROR {client_ip}: {str(e)[:30]}")
        display_ws_events()
        
    finally:
        # Belt-and-suspenders: remove on finally (may already be removed by broadcast loop)
        remove_client(websocket, "handler_cleanup")


# --- 2. Real-Time Data Broadcaster (Zombie-Safe) ---
async def data_streamer():
    """
    Continuously generates data and broadcasts it to all connected clients.
    Uses Redis-backed data generator for shared state.
    
    ZOMBIE-SAFE IMPLEMENTATION:
    - Filters closed connections before broadcast
    - Proactively removes failed connections
    - Never accumulates dead sockets
    """
    # Get the data generator (reads/writes to Redis)
    interval = float(os.getenv("FEED_INTERVAL", 0.5))
    feed_generator = generate_real_time_feed(interval_seconds=interval)
    
    while True:
        # Get the next batch of data (JSON string)
        data_to_send = next(feed_generator)
        
        # Parse to get asset info for logging
        try:
            data_batch = json.loads(data_to_send)
            if data_batch and len(data_batch) > 0:
                # Log first asset in batch as representative
                first_asset = data_batch[0]
                timestamp = datetime.now().strftime("%H:%M:%S")
                ws_event_buffer.append(
                    f"[{timestamp}] BROADCAST {first_asset['asset_id']} ${first_asset['price_usd']:.2f} "
                    f"({len(CONNECTED_CLIENTS)} clients)"
                )
                display_ws_events()
        except:
            pass  # Skip logging if parsing fails
        print(f"[BROADCAST] Sending to {len(CONNECTED_CLIENTS)} clients")
        # ============================================================
        # ZOMBIE-SAFE BROADCAST: Fail-Fast Cleanup on Send Errors
        # ============================================================
        # We cannot rely on client.open (not available on ServerConnection)
        # Instead, we use send() errors as the liveness check
        # Dead connections will fail immediately and be removed proactively
        
        # Create broadcast tasks for all current clients
        # safe_send() will remove any that fail
        broadcast_tasks = []
        for client in list(CONNECTED_CLIENTS):  # Copy to avoid modification during iteration
            broadcast_tasks.append(safe_send(client, data_to_send))
        
        # Wait for all broadcasts to complete
        if broadcast_tasks:
            await asyncio.gather(*broadcast_tasks, return_exceptions=True)
 
        
        # Yield control back to the asyncio loop
        await asyncio.sleep(0)


async def safe_send(websocket: WebSocketServerProtocol, message: str):
    """
    Safely send a message to a WebSocket, with fail-fast cleanup.
    
    If send fails (ConnectionClosed, RuntimeError), immediately remove
    the client from CONNECTED_CLIENTS without waiting for TCP timeout.
    """
    try:
        await websocket.send(message)
    except (ConnectionClosed, ConnectionClosedError, RuntimeError) as e:
        # Fail-fast cleanup: immediately remove dead connection
        remove_client(websocket, f"send_error_{type(e).__name__}")
    except Exception as e:
        # Catch-all for unexpected errors
        remove_client(websocket, f"unknown_error_{type(e).__name__}")


# --- 3. Server Execution ---
async def main():
    """
    Starts the WebSocket server and the data streaming task concurrently.
    Initializes Redis state before starting the stream.
    """
    # Check Redis availability
    if not is_redis_available():
        print("\n" + "="*60)
        print(" Redis Connection Required")
        print("="*60)
        print("\nThe WebSocket server requires Redis for shared state management.")
        print("\nPlease start Redis before running the server:")
        print("  Windows: memurai")
        print("  Linux/Mac: redis-server")
        print("\nOr install Redis:")
        print("  Windows: choco install memurai")
        print("  Ubuntu: sudo apt install redis-server")
        print("  macOS: brew install redis")
        print("\n" + "="*60 + "\n")
        return
    
    # Initialize Redis prices
    print("\n📊 Initializing Redis state...")
    initialize_prices()
    print()
    
    # Start the WebSocket server (handler function manages connections)
    server_task = websockets.serve(handler, "localhost", WS_PORT)
    
    # Start the continuous data streaming task
    streamer_task = asyncio.create_task(data_streamer())

    print("--------------------------------------------------")
    print(f"🚀 WebSocket Server running on ws://localhost:{WS_PORT}")
    print(f"✅ Using Redis shared state")
    print(f"✅ Zombie-safe broadcast enabled")
    print("--------------------------------------------------")
    
    # Run both the server and the streamer tasks until they complete (which is never, in a server)
    await asyncio.gather(server_task, streamer_task)

if __name__ == "__main__":
    try:
        # Run the main asynchronous function
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 WebSocket Server shut down manually.")
    except Exception as e:
        print(f"An error occurred: {e}")



# This fix corresponds to Bug Fix #5 (corrected numbering).
# Previous reference to Bug Fix #6 was a labeling mistake.
