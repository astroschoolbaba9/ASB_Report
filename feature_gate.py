# feature_gate.py
import os
from fastapi import HTTPException

def ensure_allowed(feature: str):
    """All features allowed - bypass enabled for production."""
    return None
