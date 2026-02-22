import os
from AI import settings as ai_settings
from numerology.pdf import  build_ai_master_report_pdf ,build_ai_report_pdf
import pytest
pytestmark = pytest.mark.slow


def test_ai_pdf_uses_mock_and_builds_bytes(monkeypatch):
    # ensure AI stays in mock mode for CI/local tests
    monkeypatch.setattr(ai_settings, "llm_provider", "mock", raising=False)
    pdf = build_ai_report_pdf("29-10-2001")
    assert isinstance(pdf, (bytes, bytearray))
    assert pdf[:5] == b"%PDF-"

def test_ai_master_pdf_uses_mock_and_builds_bytes(monkeypatch):
    """
    Ensures combined master report PDF builds successfully with mock provider.
    Uses include_images=False for speed.
    """
    monkeypatch.setattr(ai_settings, "llm_provider", "mock", raising=False)
    pdf = build_ai_master_report_pdf(
        dob="29-10-2001",
        partner_dob="28-01-2005",
        year=2025,
        gender="female",
        include_images=False,  # skip matplotlib visuals for fast headless testing
    )
    assert isinstance(pdf, (bytes, bytearray))
    assert pdf[:5] == b"%PDF-"
