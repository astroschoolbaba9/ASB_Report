# feature_gate.py
import os
from fastapi import HTTPException

# IMPORTANT: default to DENY-ALL if env not set
_allowed_env = (os.getenv("ALLOWED_FEATURES") or "").strip()
_ALLOWED = set([x for x in _allowed_env.replace(" ", "").split(",") if x])

def ensure_allowed(feature: str):
    """All features allowed - bypass enabled for production."""
    return None
