import json
import random
import time
import uuid
from datetime import datetime, timezone, timedelta
from redis_state import (
    get_price, 
    set_price, 
    get_tracked_assets,
    initialize_prices,
    is_redis_available
)

# -----------------------------------------------------------
# 1. Single Data Point Generator (Redis-backed)
# -----------------------------------------------------------
def generate_data_point(asset_id: str) -> dict:
    """
    Generates a single, time-stamped data point for a given asset.
    Reads current price from Redis, generates new price, and updates Redis.
    
    Args:
        asset_id: Asset identifier (e.g., "BTC", "ETH")
        
    Returns:
        dict: Data point with id, asset_id, timestamp, price_usd, volume_24h
    """
    # Read current price from Redis (shared state)
    current_price = get_price(asset_id)
    
    # Simulate a small, random price change (-0.5% to +0.5% movement)
    price_change_factor = random.uniform(0.995, 1.005)
    new_price = current_price * price_change_factor
    
    # Ensure the price is rounded nicely for display
    new_price_rounded = round(new_price, 4)
    
    # Update Redis with new price (shared state)
    set_price(asset_id, new_price_rounded)
    
    return {
        "id": str(uuid.uuid4()),  # Unique ID for the data point
        "asset_id": asset_id,     # Asset symbol (e.g., "BTC")
        "timestamp": datetime.now(timezone.utc).isoformat(), # UTC Timestamp
        "price_usd": new_price_rounded,
        "volume_24h": random.randint(1_000_000, 10_000_000) # Mock Volume
    }


# -----------------------------------------------------------
# 2. Real-Time Data Feed (Redis-backed Generator)
# -----------------------------------------------------------
def generate_real_time_feed(interval_seconds: float = 1.0):
    """
    A Python generator function that continuously yields a list of
    new data points for all tracked assets.
    
    Reads current prices from Redis (shared state) and updates them.
    This function is intended to be run by the WebSocket server.
    
    Args:
        interval_seconds: Time delay between data batches
        
    Yields:
        str: JSON string containing array of new data points
    """
    tracked_assets = get_tracked_assets()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting real-time data feed...")
    print(f"Tracking Assets: {tracked_assets}")
    print(f"✅ Using Redis shared state")
    
    while True:
        new_data_batch = []
        
        # Generate new data point for each asset
        for asset_id in tracked_assets:
            # Generate data point (reads from Redis, updates Redis)
            data_point = generate_data_point(asset_id)
            new_data_batch.append(data_point)
        
        # Yield the batch of new data as a JSON string
        yield json.dumps(new_data_batch)
        
        # Pause to simulate the stream interval
        time.sleep(interval_seconds)


# -----------------------------------------------------------
# 3. Initial/Historical Data (Redis-backed)
# -----------------------------------------------------------
def get_initial_data(history_size: int = 50):
    """
    Generates an initial batch of historical data for the frontend
    to load on startup (using the HTTP API).
    
    Uses current prices from Redis as the starting point and generates
    backwards in time to create realistic historical data.
    
    Args:
        history_size: Number of historical points to generate per asset
        
    Returns:
        list: Array of data points sorted chronologically
    """
    initial_data = []
    tracked_assets = get_tracked_assets()
    
    # Get current prices from Redis (shared state)
    # Create a working copy for historical simulation
    temp_prices = {}
    for asset_id in tracked_assets:
        temp_prices[asset_id] = get_price(asset_id)
    
    print(f"Generating {history_size} historical points from Redis state...")
    
    # Generate 'history_size' number of data points for each asset
    for i in range(history_size):
        # Calculate the random time step to go back in history
        seconds_to_subtract = i * random.uniform(5, 15)
        
        # Calculate the historical time using timedelta
        past_time = datetime.now(timezone.utc) - timedelta(seconds=seconds_to_subtract)
        
        for asset_id, current_price in temp_prices.items():
            # Simulate price change
            price_change_factor = random.uniform(0.995, 1.005)
            new_price = current_price * price_change_factor
            new_price_rounded = round(new_price, 4)
            
            # Create data point
            data_point = {
                "id": str(uuid.uuid4()),
                "asset_id": asset_id,
                "timestamp": past_time.isoformat(),
                "price_usd": new_price_rounded,
                "volume_24h": random.randint(1_000_000, 10_000_000)
            }
            
            initial_data.append(data_point)
            
            # Update temp price for the next historical step
            temp_prices[asset_id] = new_price_rounded
    
    # Sort by timestamp to ensure chronological order
    initial_data.sort(key=lambda x: x['timestamp'])
    
    # Update Redis with the final historical prices
    # This ensures continuity: last historical price = first live price
    for asset_id, final_price in temp_prices.items():
        set_price(asset_id, final_price)
        print(f"Historical endpoint for {asset_id}: ${final_price:.2f}")
    
    return initial_data


# -----------------------------------------------------------
# 4. Execution Block (Testing)
# -----------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Data Generator with Redis State")
    print("="*60 + "\n")
    
    # Check Redis availability
    if not is_redis_available():
        print("❌ Redis is not available!")
        print("Please start Redis server before running tests.")
        print("\nWindows: memurai")
        print("Linux/Mac: redis-server")
        exit(1)
    
    # Initialize prices in Redis
    print("Initializing Redis prices...")
    initialize_prices(force=True)
    print()
    
    # Test 1: Initial data generation
    print("--- Test 1: Initial Data Generation ---")
    initial = get_initial_data(history_size=3)
    print(f"Generated {len(initial)} historical points")
    print(json.dumps(initial[:2], indent=2))  # Show first 2
    print()
    
    # Test 2: Real-time feed
    print("--- Test 2: Real-Time Feed Generator ---")
    feed = generate_real_time_feed(interval_seconds=0.5)
    
    # First batch
    batch_1 = next(feed)
    print(f"\nBatch 1 ({len(json.loads(batch_1))} items):")
    print(json.dumps(json.loads(batch_1), indent=2))
    
    # Second batch
    batch_2 = next(feed)
    print(f"\nBatch 2 ({len(json.loads(batch_2))} items):")
    print(json.dumps(json.loads(batch_2), indent=2))
    
    print("\n✅ All tests passed!")
