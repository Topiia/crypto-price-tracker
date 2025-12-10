import json
import random
import time
import uuid
from datetime import datetime, timezone, timedelta # Make sure timedelta is imported!

# -----------------------------------------------------------
# 1. State Management (Current Prices)
# -----------------------------------------------------------
# This dictionary holds the current price for each simulated asset.
# It acts as a simple in-memory database of the last known price.
ASSET_PRICES = {
    "BTC": 60000.00,  # Bitcoin
    "ETH": 3500.00,   # Ethereum
    "SOL": 150.00,    # Solana
    "DOGE": 0.15      # Dogecoin
}

# -----------------------------------------------------------
# 2. Single Data Point Generator
# -----------------------------------------------------------
def generate_data_point(asset_id: str, base_price: float) -> dict:
    """
    Generates a single, time-stamped data point for a given asset.
    The price is slightly varied from the base_price to simulate movement.
    """
    # Simulate a small, random price change (e.g., -0.5% to +0.5% movement)
    price_change_factor = random.uniform(0.995, 1.005)
    new_price = base_price * price_change_factor

    # Ensure the price is rounded nicely for display
    new_price_rounded = round(new_price, 4)

    return {
        "id": str(uuid.uuid4()),  # Unique ID for the data point
        "asset_id": asset_id,     # Asset symbol (e.g., "BTC")
        "timestamp": datetime.now(timezone.utc).isoformat(), # UTC Timestamp
        "price_usd": new_price_rounded,
        "volume_24h": random.randint(1_000_000, 10_000_000) # Mock Volume
    }

# -----------------------------------------------------------
# 3. Real-Time Data Feed (The Generator Function)
# -----------------------------------------------------------
def generate_real_time_feed(interval_seconds: float = 1.0):
    """
    A Python generator function that continuously yields a list of
    new data points for all tracked assets.

    This function is intended to be run by the WebSocket server (1.3).
    """
    global ASSET_PRICES  # Access the global price state

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting real-time data feed...")
    print(f"Tracking Assets: {list(ASSET_PRICES.keys())}")

    while True:
        new_data_batch = []

        # Iterate through all assets to generate a new price for each
        for asset, current_price in ASSET_PRICES.items():
            # 1. Generate the new data point
            data_point = generate_data_point(asset, current_price)
            new_data_batch.append(data_point)

            # 2. Update the global state with the new price 
            #    (This keeps the simulation continuous)
            ASSET_PRICES[asset] = data_point['price_usd']
        
        # Yield the batch of new data as a JSON string
        yield json.dumps(new_data_batch)

        # Pause to simulate the stream interval
        time.sleep(interval_seconds)

# -----------------------------------------------------------
# 4. Initial/Historical Data (Used by the HTTP API)
# -----------------------------------------------------------
# data_generator.py (Updated function)


# -----------------------------------------------------------
# 4. Initial/Historical Data (Used by the HTTP API)
# -----------------------------------------------------------
def get_initial_data(history_size: int = 50):
    """
    Generates an initial batch of historical data for the frontend
    to load on startup (using the simple HTTP server 1.2).
    """
    initial_data = []
    # Temporarily reset prices for a clean history simulation
    temp_prices = {k: v for k, v in ASSET_PRICES.items()} 

    # Generate 'history_size' number of data points for each asset
    for i in range(history_size):
        # Calculate the random time step to go back in history
        seconds_to_subtract = i * random.uniform(5, 15) 
        
        # Calculate the historical time using timedelta
        # FIX: The float must be converted to a timedelta object for subtraction
        past_time = datetime.now(timezone.utc) - timedelta(seconds=seconds_to_subtract)
        
        for asset, price in temp_prices.items():
            # Generate the point using the current temp price
            data_point = generate_data_point(asset, price)
            
            # Apply the calculated historical timestamp
            data_point['timestamp'] = past_time.isoformat()
            
            initial_data.append(data_point)
            
            # Update temp price for the next historical step (ensuring price change over time)
            temp_prices[asset] = data_point['price_usd']
            
    # Sort by timestamp to ensure chronological order
    initial_data.sort(key=lambda x: x['timestamp'])
    
    return initial_data


# -----------------------------------------------------------
# 5. Execution Block (Optional - for quick testing)
# -----------------------------------------------------------
if __name__ == "__main__":
    print("--- Testing Initial Data Generation (for HTTP API 1.2) ---")
    initial = get_initial_data(history_size=3)
    print(json.dumps(initial, indent=2))
    
    print("\n--- Testing Real-Time Feed Generator (for WebSocket 1.3) ---")
    
    # Use next() to get the first 2 batches of data from the generator
    feed = generate_real_time_feed(interval_seconds=0.5) 
    
    # First batch
    batch_1 = next(feed)
    print(f"\nBatch 1 ({len(json.loads(batch_1))} items):\n{batch_1}")

    # Second batch
    batch_2 = next(feed)
    print(f"\nBatch 2 ({len(json.loads(batch_2))} items):\n{batch_2}")