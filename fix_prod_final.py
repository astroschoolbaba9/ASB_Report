#!/usr/bin/env python3
import os

BASE_DIR = "/var/www/asb-main"

# 1. DEFINE CORRECT CONTENT FOR ALL FILES
DOT_ENV = """PYTHONUNBUFFERED=1

LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=REPLACED_FOR_GITHUB

AI_TIMEOUT=300
AI_CONNECT_TIMEOUT=10
ALLOWED_FEATURES=single,relationship,yearly,monthly,daily,health,ai,profession

SECURITY_BYPASS=1
ASB_API_BASE=https://api.asbreports.in

MONGODB_URI=mongodb+srv://ocult_science:AstroSchoolBabaStore@cluster0.t8nyto3.mongodb.net/asb_store?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=asb_store

MERN_AUTH_BASE_URL=https://api.asbcrystal.in

JWT_ACCESS_SECRET=3631e8fc22131412860a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2
JWT_ACCESS_EXPIRES_IN=15m

ASB=https://api.asbreports.in
FRONTEND_URL=https://asbreports.in

# MetaReach SMS (Synced from MERN)
METAREACH_API_KEY=i0caSeRfCMXWdVij
METAREACH_SENDER_ID=AGPKAC
METAREACH_TEMPLATE_ID=1707177071739047190
"""

SECURITY_PY = """# security.py
import os
from typing import Optional
from fastapi import Header, HTTPException

def dev_or_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    \"\"\"Always allow - security bypass enabled for all traffic.\"\"\"
    return None
"""

FEATURE_GATE_PY = """# feature_gate.py
import os
from fastapi import HTTPException

def ensure_allowed(feature: str):
    \"\"\"All features allowed - bypass enabled for production.\"\"\"
    return None
"""

APP_PY = """# app.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main_api import router as main_router

app = FastAPI(title="ASB")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)

@app.get("/", tags=["Health"])
def health_check():
    return {"ok": True, "service": "ASB API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
"""

def write_file(filename, content):
    path = os.path.join(BASE_DIR, filename)
    print(f"Writing {path}...")
    with open(path, "w") as f:
        f.write(content)

if __name__ == "__main__":
    # Ensure BASE_DIR exists
    if not os.path.exists(BASE_DIR):
        print(f"Error: {BASE_DIR} does not exist.")
        exit(1)

    # Write all files
    write_file(".env", DOT_ENV)
    write_file("security.py", SECURITY_PY)
    write_file("feature_gate.py", FEATURE_GATE_PY)
    write_file("app.py", APP_PY)
    
    print("\\nDONE: All critical files overwritten with clean, bypassed versions.")
    print("Please restart services manually: systemctl restart asb_api asb_app")
