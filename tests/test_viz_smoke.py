import io
from numerology.viz import build_triangle_png_bytes, build_triangle_pdf_bytes

def test_triangle_png_bytes_nonempty():
    b = build_triangle_png_bytes("29-10-2001")
    assert isinstance(b, (bytes, bytearray))
    assert len(b) > 10_000  # image should be at least this big

def test_triangle_pdf_bytes_nonempty():
    b = build_triangle_pdf_bytes("29-10-2001")
    assert isinstance(b, (bytes, bytearray))
    # simple PDF magic header check
    assert b[:5] == b"%PDF-"
