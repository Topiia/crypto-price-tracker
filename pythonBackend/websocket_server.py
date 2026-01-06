import asyncio
import websockets
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
        # Unregister the client connection
        CONNECTED_CLIENTS.remove(websocket)
        timestamp = datetime.now().strftime("%H:%M:%S")
        ws_event_buffer.append(f"[{timestamp}] CLIENT_DISCONNECT {client_ip} (total: {len(CONNECTED_CLIENTS)})")
        display_ws_events()


# --- 2. Real-Time Data Broadcaster ---
async def data_streamer():
    """
    Continuously generates data and broadcasts it to all connected clients.
    Uses Redis-backed data generator for shared state.
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
        
        # Create a set of tasks for broadcasting the data
        broadcast_tasks = [client.send(data_to_send) for client in CONNECTED_CLIENTS]
        
        # Wait for all broadcasts to complete without blocking
        if broadcast_tasks:
             # Use gather to run all send operations concurrently
            await asyncio.gather(*broadcast_tasks, return_exceptions=True) 
        
        # Crucial: yield control back to the asyncio loop to allow other tasks (like new client handlers) to run
        await asyncio.sleep(0) 


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
