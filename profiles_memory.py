# auth/profiles_memory.py
from __future__ import annotations
from typing import Optional, Dict, Any

_STORE: Dict[str, Dict[str, Any]] = {}

def upsert_profile(user_id: str, dob: str, gender: Optional[str]) -> None:
    _STORE[user_id] = {"user_id": user_id, "dob": dob, "gender": gender}

def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    return _STORE.get(user_id)
