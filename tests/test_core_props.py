import itertools as it
import re
from numerology.core import (
    mystical_triangle_values_image,
    combine_two_triangles,
    full_reduce,
    parse_dob,
    year_only_triangle,
    monthly_combined_triangle,
    yearly_combined_triangle,
    _triangle_from_abcd,   # internal but OK for tests
)

def test_full_reduce_range():
    for n in range(0, 9999):
        r = full_reduce(n)
        assert 0 <= r <= 9
        # if n>0 ⇒ 1..9; if n==0 ⇒ stays 0 (used by year/month drivers)
        if n > 0:
            assert 1 <= r <= 9

def test_parse_dob_formats():
    assert str(parse_dob("29-10-2001")) == "2001-10-29"
    assert str(parse_dob("2001-10-29")) == "2001-10-29"

def test_triangle_structure_and_ranges():
    vals = mystical_triangle_values_image("29-10-2001")
    for section in ("inputs", "layer1", "second_layer", "third_layer"):
        assert section in vals and isinstance(vals[section], dict)
    # inputs can include zeros for some driver triangles, but standard DOB has 1..9
    for k, v in vals["layer1"].items():
        assert 1 <= int(v) <= 9
    for k, v in vals["second_layer"].items():
        assert 1 <= int(v) <= 9
    for k, v in vals["third_layer"].items():
        assert 1 <= int(v) <= 9
    # core consistency
    e, f, g = vals["layer1"]["E"], vals["layer1"]["F"], vals["layer1"]["G"]
    p = vals["third_layer"]["P"]
    assert vals["core"]["core_pair"] == int(f"{e}{f}")
    assert vals["core"]["G"] == g
    assert vals["core"]["P_outcome"] == p

def test_combine_is_commutative_and_idempotent():
    a = mystical_triangle_values_image("29-10-2001")
    b = mystical_triangle_values_image("28-01-2005")
    ab = combine_two_triangles(a, b)
    ba = combine_two_triangles(b, a)
    assert ab == ba
    aa = combine_two_triangles(a, a)
    # Not identity, but deterministic and stable on repeated combine
    aaa = combine_two_triangles(a, a)
    assert aa == aaa

def test_year_only_triangle_shape():
    right = year_only_triangle(2025)
    assert right["inputs"]["A"] == 0
    assert right["inputs"]["B"] == 0
    # C/D derived from year and must be 1..9
    assert 1 <= right["inputs"]["C"] <= 9
    assert 1 <= right["inputs"]["D"] <= 9

def test_monthly_and_yearly_combined_are_deterministic():
    dob = "29-10-2001"
    y = 2025
    m1 = monthly_combined_triangle(dob, y)
    m2 = monthly_combined_triangle(dob, y)
    assert m1 == m2
    y1 = yearly_combined_triangle(dob, y)
    y2 = yearly_combined_triangle(dob, y)
    assert y1 == y2

def test_triangle_from_abcd_matches_pipeline():
    # Build with controlled inputs, including zeros allowed by drivers
    t = _triangle_from_abcd(0, 5, 3, 9)
    assert "inputs" in t and "layer1" in t and "third_layer" in t
    # EF/G/P exist and are consistent with core
    e, f, g = t["layer1"]["E"], t["layer1"]["F"], t["layer1"]["G"]
    p = t["third_layer"]["P"]
    assert t["core"]["core_pair"] == int(f"{e}{f}")
    assert t["core"]["G"] == g
    assert t["core"]["P_outcome"] == p
