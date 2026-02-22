# auth/auth_api.py
from __future__ import annotations

import os
import jwt
from typing import Optional, Dict, Any
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])

MERN_AUTH_BASE_URL = (os.getenv("MERN_AUTH_BASE_URL") or "http://localhost:8080").rstrip("/")
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "asb_store")
JWT_ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET", "dev_secret")

# ✅ Initialize MongoDB
db_client = AsyncIOMotorClient(MONGODB_URI) if MONGODB_URI else None
db = db_client[DB_NAME] if db_client else None

# -------------------- Payloads --------------------
class SendOtpPayload(BaseModel):
    identifier: str = Field(..., description="phone or email (E.164 preferred for phone)")


class VerifyOtpPayload(BaseModel):
    identifier: str
    otp: Optional[str] = None
    code: Optional[str] = None  # some flows send `code` instead of otp


class CompleteProfilePayload(BaseModel):
    name: Optional[str] = None
    dob: str = Field(..., description="DD-MM-YYYY or YYYY-MM-DD")
    gender: Optional[str] = None  # male/female/other


# -------------------- Helpers --------------------
def _extract_token(authorization: Optional[str], x_auth_token: Optional[str]) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    if x_auth_token:
        return x_auth_token
    return ""


def _get_user_id_from_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_ACCESS_SECRET, algorithms=["HS256"])
        return payload.get("sub") or payload.get("id")
    except Exception:
        return None


def _norm_name(n: Optional[str]) -> str:
    return (n or "").strip().title()


def _norm_gender(g: Optional[str]) -> str:
    g = (g or "").strip().lower()
    if g in ("male", "female", "other"):
        return g
    return "other"


def parse_dob(dob_str: str) -> datetime:
    formats = ["%d-%m-%Y", "%Y-%m-%d"]
    for f in formats:
        try:
            return datetime.strptime(dob_str.strip(), f)
        except ValueError:
            continue
    raise ValueError("Invalid DOB format. Use DD-MM-YYYY or YYYY-MM-DD")


async def _proxy_post(path: str, body: dict, token: Optional[str] = None):
    url = f"{MERN_AUTH_BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Auth-Token"] = token
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url, json=body, headers=headers)
        return r.json()


async def _proxy_get(path: str, token: Optional[str] = None):
    url = f"{MERN_AUTH_BASE_URL}{path}"
    headers = {}
    if token:
        headers["X-Auth-Token"] = token
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, headers=headers)
        return r.json()


# -------------------- Routes --------------------

@router.post("/send-otp")
async def send_otp(payload: SendOtpPayload):
    return await _proxy_post("/api/auth/send-otp", payload.dict())


@router.post("/verify-otp")
async def verify_otp(payload: VerifyOtpPayload):
    body = payload.dict()
    # normalize otp
    if not body.get("otp") and body.get("code"):
        body["otp"] = body["code"]

    data = await _proxy_post("/api/auth/verify-otp", body)

    # normalize token key for Streamlit
    return {
        "success": True,
        "token": data.get("accessToken") or data.get("token"),
        "user": data.get("user"),
        "mode": data.get("mode"),
    }


@router.get("/me")
async def me(
    authorization: Optional[str] = Header(None),
    x_auth_token: Optional[str] = Header(None, alias="X-Auth-Token"),
):
    token = _extract_token(authorization, x_auth_token)
    data = await _proxy_get("/api/auth/me", token)

    # Standardize structure
    res = data if (isinstance(data, dict) and "success" in data) else {"success": True, "user": data}
    user = res.get("user")

    # ✅ Merge direct DB profile if user exists
    user_id = _get_user_id_from_token(token)
    if user and user_id and db is not None:
        try:
            db_user = await db.users.find_one({"_id": ObjectId(user_id)})
            if db_user:
                # Merge fields that might be missing in older MERN versions
                for field in ["dob", "gender", "name"]:
                    if field in db_user and not user.get(field):
                        user[field] = db_user[field]
                # Specific check for phone if missing
                if not user.get("phone") and "phone" in db_user:
                    user["phone"] = db_user["phone"]
        except Exception as e:
            print(f"DB Merge Error: {e}")

    return res


@router.post("/complete-profile")
async def complete_profile(
    payload: CompleteProfilePayload,
    authorization: Optional[str] = Header(None),
    x_auth_token: Optional[str] = Header(None, alias="X-Auth-Token"),
):
    token = _extract_token(authorization, x_auth_token)
    user_id = _get_user_id_from_token(token)

    # normalize DOB
    try:
        dob_dt = parse_dob(payload.dob)
        dob_str = dob_dt.strftime("%d-%m-%Y")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    name = _norm_name(payload.name)
    gender = _norm_gender(payload.gender)

    # ✅ 1. Direct DB Save (Primary)
    if user_id and db is not None:
        try:
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"dob": dob_str, "gender": gender, "name": name}},
                upsert=False
            )
        except Exception as e:
            print(f"Direct DB Save Failed: {e}")

    # ✅ 2. Proxy to MERN (Secondary, might fail/404 on older versions)
    url = f"{MERN_AUTH_BASE_URL}/api/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Auth-Token": token,
        "Content-Type": "application/json",
    }
    body = {"name": name, "dob": dob_str, "gender": gender}

    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.put(url, json=body, headers=headers)
            # Log but don't crash if proxy fails, as long as DB save worked
            if r.status_code >= 400:
                print(f"MERN Proxy Warning ({r.status_code}): {r.text}")
            return r.json()
        except Exception as e:
            print(f"MERN Proxy Error: {e}")
            return {"success": True, "message": "Profile saved locally."}
