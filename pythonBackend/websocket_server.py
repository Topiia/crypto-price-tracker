import asyncio
import websockets
import json
from datetime import datetime
from data_generator import generate_real_time_feed # Import the generator function from 1.1

from dotenv import load_dotenv
import os

# --- Configuration ---
load_dotenv()
WS_PORT = int(os.getenv("WS_PORT", 8001))
CONNECTED_CLIENTS = set() # Set to store active WebSocket connections

# --- 1. Client Connection Handler ---
# --- 1. Client Connection Handler (FIXED) ---
async def handler(websocket): # <-- REMOVE 'path' argument here
    """
    Handles a single client connection, adding it to the broadcast list
    and removing it upon disconnect.
    """
    # ... rest of the function logic ...
    # Note: If you ever needed to check the path (e.g., /ws/btc or /ws/eth), 
    # you would keep 'path' and use it. Since we are using one simple path, we remove it.

    # Register client connection
    CONNECTED_CLIENTS.add(websocket)
    
    # ... rest of the function is unchanged ...

    client_ip = websocket.remote_address[0]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Client connected from {client_ip}. Total active connections: {len(CONNECTED_CLIENTS)}")

    try:
        await websocket.wait_closed()
        
    except websockets.exceptions.ConnectionClosedOK:
        pass
    except Exception as e:
        print(f"Connection error with {client_ip}: {e}")
        
    finally:
        # Unregister the client connection
        CONNECTED_CLIENTS.remove(websocket)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Client disconnected from {client_ip}. Remaining: {len(CONNECTED_CLIENTS)}")


# --- 2. Real-Time Data Broadcaster ---
async def data_streamer():
    """
    Continuously generates data and broadcasts it to all connected clients.
    """
    # Get the data generator (which handles the time.sleep internally)
    # feed_generator = generate_real_time_feed(interval_seconds=0.5) 
    interval = float(os.getenv("FEED_INTERVAL", 0.5))
    feed_generator = generate_real_time_feed(interval_seconds=interval)
    
    while True:
        # Get the next batch of data (JSON string)
        data_to_send = next(feed_generator)
        
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
    """
    # Start the WebSocket server (handler function manages connections)
    server_task = websockets.serve(handler, "localhost", WS_PORT)
    
    # Start the continuous data streaming task
    streamer_task = asyncio.create_task(data_streamer())

    print("--------------------------------------------------")
    print(f"🚀 WebSocket Server running on ws://localhost:{WS_PORT}")
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