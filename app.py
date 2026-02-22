# app.py (Reload triggered)
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from main_api import router as main_router

app = FastAPI(title="ASB")

# ✅ CORS for Production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://asbreports.in",
        "https://www.asbreports.in",
        "http://localhost:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include router ONCE (main_api.py already has prefix="/api")
app.include_router(main_router)

@app.get("/", tags=["Health"])
def health_check():
    return {"ok": True, "service": "ASB API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
