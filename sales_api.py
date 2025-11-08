import os
import json
import time
import requests

API_URL = "https://sandbox.mkonnekt.net/ch-portal/api/v1/orders/recent"

# Simple in-memory cache (60s)
_CACHE = {"data": None, "ts": 0}
_TTL_SECONDS = 60

def fetch_recent_orders():
    """Fetch recent orders from the sandbox API with flexible format handling."""
    now = time.time()
    if _CACHE["data"] is not None and now - _CACHE["ts"] < _TTL_SECONDS:
        return _CACHE["data"]

    try:
        resp = requests.get(API_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # ✅ The API might return a dict with "orders" instead of a top-level list
        if isinstance(data, dict) and "orders" in data:
            orders = data["orders"]
        elif isinstance(data, list):
            orders = data
        else:
            raise ValueError("Unexpected response format: missing 'orders' key or list.")

        _CACHE["data"] = orders
        _CACHE["ts"] = now
        return orders

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Sales API request failed: {e}")
    except ValueError as ve:
        raise RuntimeError(f"Sales API returned invalid JSON: {ve}")
