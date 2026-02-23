# security.py
import os
from typing import Optional
from fastapi import Header, HTTPException

def dev_or_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """Always allow - security bypass enabled for all traffic."""
    return None
