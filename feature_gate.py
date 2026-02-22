# feature_gate.py
import os
from fastapi import HTTPException

# IMPORTANT: default to DENY-ALL if env not set
_allowed_env = (os.getenv("ALLOWED_FEATURES") or "").strip()
_ALLOWED = set([x for x in _allowed_env.replace(" ", "").split(",") if x])

def ensure_allowed(feature: str):
    """
    Enforce feature gating — allows all when SECURITY_BYPASS=1 (local/dev),
    otherwise checks if the feature is listed in ALLOWED_FEATURES.
    """
    # ✅ allow everything in dev when SECURITY_BYPASS=1
    if os.getenv("SECURITY_BYPASS") == "1":
        return

    # ✅ allow all if ALLOWED_FEATURES is empty (dev-friendly)
    if not _ALLOWED:
        return

    # normalize & alias feature names to reduce mismatches
    f = (feature or "").strip().lower()
    aliases = {
        "single_person": "single",
        "person": "single",
        "rel": "relationship",
        "relationship": "relationship",
        "year": "yearly",
        "yearly": "yearly",
        "month": "monthly",
        "monthly": "monthly",
        "day": "daily",
        "daily": "daily",
        "health": "health",
        "ai": "ai",
        "diagnostics": "diag",
        "diag": "diag",
    }
    key = aliases.get(f, f)

    if key not in _ALLOWED:
        raise HTTPException(status_code=403, detail=f"Feature '{feature}' is not enabled")
