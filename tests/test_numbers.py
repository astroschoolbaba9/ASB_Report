import pytest
from numerology import full_reduce, mystical_triangle_values_image

def test_full_reduce_single_digits():
    assert full_reduce(5) == 5
    assert full_reduce(9) == 9

def test_full_reduce_multi_digit():
    assert full_reduce(28) == 1  # 2+8=10 → 1+0=1
    assert full_reduce(2005) == 7  # 2+0+0+5 = 7 (standalone behavior)

def test_year_split_logic():
    vals = mystical_triangle_values_image("28-01-2005")
    # Year 2005 → "20" → 2 ; "05" → 5
    assert vals["inputs"]["C"] == 2
    assert vals["inputs"]["D"] == 5
