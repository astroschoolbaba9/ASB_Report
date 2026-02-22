from fastapi.testclient import TestClient
from app import app
import pytest
pytestmark = pytest.mark.slow


def test_docs_available():
    c = TestClient(app)
    r = c.get("/docs")
    assert r.status_code == 200

def test_numerology_basic_json():
    c = TestClient(app)
    r = c.get("/numerology/mystical-triangle.json", params={"dob": "29-10-2001"})
    assert r.status_code == 200
    js = r.json()
    assert "layer1" in js and "third_layer" in js

def test_triptych_png_ok():
    c = TestClient(app)
    r = c.get(
        "/numerology/mystical-triangle-triptych.png",
        params={"left": "29-10-2001", "right": "today"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/png")

def test_ai_summary_mock_provider(monkeypatch):
    # pin mock provider for stability
    from AI import settings as ai_settings
    monkeypatch.setattr(ai_settings, "llm_provider", "mock", raising=False)
    c = TestClient(app)
    r = c.get("/ai/summary", params={"dob": "29-10-2001"})
    assert r.status_code == 200
    js = r.json()
    assert isinstance(js.get("interpretation", ""), str) and js["interpretation"].strip()

def test_ai_report_pdf_bytes(monkeypatch):
    from AI import settings as ai_settings
    monkeypatch.setattr(ai_settings, "llm_provider", "mock", raising=False)
    c = TestClient(app)
    r = c.get("/ai/report.pdf", params={"dob": "29-10-2001"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"

def test_ai_master_report_pdf_bytes(monkeypatch):
    """
    New test: hits the combined master report endpoint.
    We disable images for speed/stability in CI, but you can set include_images=True if you prefer.
    """
    from AI import settings as ai_settings
    monkeypatch.setattr(ai_settings, "llm_provider", "mock", raising=False)
    c = TestClient(app)
    r = c.get(
        "/ai/master-report.pdf",
        params={
            "dob": "29-10-2001",
            "year": 2025,
            "day": "today",
            "gender": "female",
            "include_images": False,   # faster & avoids matplotlib on headless CI
        },
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
