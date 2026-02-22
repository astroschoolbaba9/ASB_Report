# security.py
import os
from typing import Optional
from fastapi import Header, HTTPException

def dev_or_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    # Bypass entirely in local/dev
    if os.getenv("SECURITY_BYPASS", "0") == "1":
        return
    # Enforce key if configured
    expected = os.getenv("API_KEY", "")
    if expected:  # if a key is set, require it
        if not x_api_key or x_api_key != expected:
            raise HTTPException(status_code=403, detail="Forbidden")
    # If no key set, allow (useful in dev)
