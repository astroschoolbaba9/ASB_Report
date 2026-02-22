# auth/mern_user_db.py
from __future__ import annotations

import os
from typing import Optional, Dict, Any, Tuple

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId

_client: MongoClient | None = None
_db = None


def _connect() -> MongoClient:
    global _client
    if _client is not None:
        return _client

    uri = (os.getenv("MONGODB_URI") or "").strip()
    if not uri:
        raise RuntimeError("MONGODB_URI is not set")

    _client = MongoClient(uri)
    return _client


def _pick_db_and_collection(user_id: str) -> Tuple[Any, str]:
    """
    We try to find the user across likely DBs + collection names.
    This avoids silent DB mismatch.
    """
    client = _connect()

    db_name_env = (os.getenv("DB_NAME") or "").strip()
    candidates_db = []

    # 1) If DB_NAME provided, try it first
    if db_name_env:
        candidates_db.append(db_name_env)

    # 2) Try default DB from URI (if any)
    try:
        default_db = client.get_default_database()
        if default_db and default_db.name not in candidates_db:
            candidates_db.append(default_db.name)
    except Exception:
        pass

    # 3) Fallback common names (your case)
    for nm in ["asb_store", "ocult_science_db"]:
        if nm not in candidates_db:
            candidates_db.append(nm)

    # Collection candidates (mongoose typically uses "users")
    candidates_col = ["users", "user", "Users", "User"]

    oid = ObjectId(user_id)

    checked = []
    for dbn in candidates_db:
        db = client[dbn]
        for col in candidates_col:
            checked.append(f"{dbn}.{col}")
            row = db[col].find_one({"_id": oid})
            if row:
                return db, col

    raise RuntimeError(
        "User not found in Mongo by _id. "
        f"Tried: {', '.join(checked)}. "
        "Fix your DB_NAME to match ASBCrystal DB (likely DB_NAME=asb_store) "
        "and ensure collection is 'users'."
    )


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    if not user_id:
        return None

    try:
        db, col = _pick_db_and_collection(user_id)
        row = db[col].find_one({"_id": ObjectId(user_id)})
        if not row:
            return None
        row["_id"] = str(row["_id"])
        row["_collection"] = col
        row["_db"] = db.name
        return dict(row)
    except Exception:
        return None


def update_user_profile(
    user_id: str,
    *,
    name: Optional[str] = None,
    dob: Optional[str] = None,
    gender: Optional[str] = None,
) -> Dict[str, Any]:
    if not user_id:
        raise ValueError("user_id required")

    db, col = _pick_db_and_collection(user_id)
    users = db[col]

    update: Dict[str, Any] = {}
    if name is not None:
        update["name"] = name
    if dob is not None:
        update["dob"] = dob
    if gender is not None:
        update["gender"] = gender

    try:
        users.update_one({"_id": ObjectId(user_id)}, {"$set": update})

        saved = users.find_one({"_id": ObjectId(user_id)})
        if not saved:
            raise RuntimeError("User not found after update (unexpected)")

        nm = str(saved.get("name") or "").strip()
        dbs = str(saved.get("dob") or "").strip()
        gd = str(saved.get("gender") or "").strip().lower()
        complete = bool(nm and dbs and gd in ("male", "female", "other"))

        users.update_one({"_id": ObjectId(user_id)}, {"$set": {"profileCompleted": complete}})
        saved = users.find_one({"_id": ObjectId(user_id)})

        saved["_id"] = str(saved["_id"])
        saved["_collection"] = col
        saved["_db"] = db.name
        return dict(saved)

    except PyMongoError as e:
        raise RuntimeError(f"Mongo update failed: {e}") from e
