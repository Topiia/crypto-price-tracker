"""
Redis State Manager for Cryptocurrency Price Tracker

This module provides a shared state layer using Redis to ensure
both HTTP and WebSocket servers read/write the same price data,
eliminating the process-local state divergence issue.

Key Functions:
- get_redis() - Get Redis connection (singleton pattern)
- initialize_prices() - Set initial asset prices
- get_price(asset_id) - Read current price for an asset
- set_price(asset_id, price) - Update price for an asset
- get_all_prices() - Get all asset prices as dict
"""

import redis
import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Initial asset prices (used for first-time initialization)
INITIAL_PRICES = {
    "BTC": 60000.00,
    "ETH": 3500.00,
    "SOL": 150.00,
    "DOGE": 0.15
}

# Price key prefix in Redis
PRICE_KEY_PREFIX = "price:"

# Singleton Redis connection
_redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """
    Get or create Redis connection (singleton pattern).
    
    Returns:
        redis.Redis: Active Redis connection
        
    Raises:
        redis.ConnectionError: If Redis server is not available
    """
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,  # Automatically decode bytes to strings
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            _redis_client.ping()
            print(f"✅ Redis connected: {REDIS_HOST}:{REDIS_PORT}")
        except redis.ConnectionError as e:
            print(f"❌ Redis connection failed: {e}")
            print(f"Make sure Redis is running on {REDIS_HOST}:{REDIS_PORT}")
            raise
    
    return _redis_client


def initialize_prices(force: bool = False) -> None:
    """
    Initialize asset prices in Redis if they don't exist.
    
    Args:
        force: If True, overwrite existing prices with initial values
    """
    r = get_redis()
    
    for asset_id, initial_price in INITIAL_PRICES.items():
        price_key = f"{PRICE_KEY_PREFIX}{asset_id}"
        
        # Only set if key doesn't exist (unless force=True)
        if force or not r.exists(price_key):
            r.set(price_key, initial_price)
            print(f"Initialized {asset_id}: ${initial_price}")
        else:
            current_price = float(r.get(price_key))
            print(f"Using existing {asset_id}: ${current_price}")


def get_price(asset_id: str) -> float:
    """
    Get current price for an asset from Redis.
    
    Args:
        asset_id: Asset identifier (e.g., "BTC", "ETH")
        
    Returns:
        float: Current price in USD
        
    Raises:
        ValueError: If asset doesn't exist in Redis
    """
    r = get_redis()
    price_key = f"{PRICE_KEY_PREFIX}{asset_id}"
    
    price_str = r.get(price_key)
    if price_str is None:
        raise ValueError(f"Asset {asset_id} not found in Redis. Call initialize_prices() first.")
    
    return float(price_str)


def set_price(asset_id: str, price: float) -> None:
    """
    Update price for an asset in Redis.
    
    Args:
        asset_id: Asset identifier (e.g., "BTC", "ETH")
        price: New price in USD
    """
    r = get_redis()
    price_key = f"{PRICE_KEY_PREFIX}{asset_id}"
    r.set(price_key, price)


def get_all_prices() -> Dict[str, float]:
    """
    Get all asset prices from Redis.
    
    Returns:
        dict: Mapping of asset_id -> price (e.g., {"BTC": 60123.45, "ETH": 3521.00})
    """
    r = get_redis()
    prices = {}
    
    for asset_id in INITIAL_PRICES.keys():
        price_key = f"{PRICE_KEY_PREFIX}{asset_id}"
        price_str = r.get(price_key)
        if price_str:
            prices[asset_id] = float(price_str)
    
    return prices


def get_tracked_assets() -> list:
    """
    Get list of all tracked asset IDs.
    
    Returns:
        list: Asset identifiers (e.g., ["BTC", "ETH", "SOL", "DOGE"])
    """
    return list(INITIAL_PRICES.keys())


# Graceful fallback if Redis is not available (for development)
def is_redis_available() -> bool:
    """
    Check if Redis is available without raising an error.
    
    Returns:
        bool: True if Redis is connected, False otherwise
    """
    try:
        r = get_redis()
        r.ping()
        return True
    except (redis.ConnectionError, Exception):
        return False


if __name__ == "__main__":
    """
    Test the Redis state manager.
    Run: python redis_state.py
    """
    print("\n" + "="*50)
    print("Testing Redis State Manager")
    print("="*50 + "\n")
    
    try:
        # Test connection
        r = get_redis()
        print(f"✅ Redis ping successful\n")
        
        # Initialize prices
        print("Initializing prices...")
        initialize_prices(force=True)
        print()
        
        # Test get/set
        print("Testing get_price()...")
        btc_price = get_price("BTC")
        print(f"BTC current price: ${btc_price}\n")
        
        print("Testing set_price()...")
        new_price = btc_price * 1.01
        set_price("BTC", new_price)
        print(f"BTC updated to: ${get_price('BTC')}\n")
        
        # Test get_all_prices
        print("Testing get_all_prices()...")
        all_prices = get_all_prices()
        for asset, price in all_prices.items():
            print(f"  {asset}: ${price:.2f}")
        
        print("\n✅ All tests passed!")
        
    except redis.ConnectionError as e:
        print(f"\n❌ Redis is not running. Please start Redis server.")
        print(f"Error: {e}")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
