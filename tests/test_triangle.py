import pytest
from datetime import date

# Core math from package
from numerology import (
    mystical_triangle_values_image,
    mystical_triangle_today,
    combine_two_triangles,
    full_reduce,
)

# New module splits:
from numerology.reads import build_reads           # moved out of core
from numerology.viz import plot_three_triangles    # plotting lives in viz


def test_triangle_29_10_2001():
    vals = mystical_triangle_values_image("29-10-2001")
    assert vals["inputs"] == {"A": 2, "B": 1, "C": 2, "D": 1}
    assert vals["layer1"] == {"E": 3, "F": 3, "G": 6}
    assert vals["third_layer"]["P"] == 9  # outcome P


def test_triangle_28_01_2005():
    vals = mystical_triangle_values_image("28-01-2005")
    assert vals["inputs"] == {"A": 1, "B": 1, "C": 2, "D": 5}
    assert vals["layer1"] == {"E": 2, "F": 7, "G": 9}
    assert vals["second_layer"]["H"] == 6
    assert vals["third_layer"]["P"] == 9


def test_triangle_11_11_2011():
    vals = mystical_triangle_values_image("11-11-2011")
    assert vals["inputs"] == {"A": 2, "B": 2, "C": 2, "D": 2}
    assert vals["layer1"]["E"] == 4
    assert vals["layer1"]["F"] == 4
    assert vals["layer1"]["G"] == 8
    assert vals["third_layer"]["P"] == 6  # fixed from 3 → 6

def test_triangle_07_07_1999():
    vals = mystical_triangle_values_image("07-07-1999")
    assert vals["inputs"] == {"A": 7, "B": 7, "C": 1, "D": 9}
    assert vals["layer1"]["E"] == 5
    assert vals["layer1"]["F"] == 1
    assert vals["layer1"]["G"] == 6
    assert vals["third_layer"]["P"] == 9  # fixed from 2 → 9

def test_triangle_15_08_1985():
    vals = mystical_triangle_values_image("15-08-1985")
    assert vals["inputs"] == {"A": 6, "B": 8, "C": 1, "D": 4}
    assert vals["layer1"]["E"] == 5
    assert vals["layer1"]["F"] == 5
    assert vals["layer1"]["G"] == 1
    assert vals["third_layer"]["P"] == 3  # fixed from 9 → 3



def test_mystical_triangle_today():
    vals = mystical_triangle_today()
    assert "inputs" in vals
    assert "layer1" in vals
    assert "second_layer" in vals
    assert "third_layer" in vals


def test_combine_two_triangles():
    v1 = mystical_triangle_values_image("29-10-2001")
    v2 = mystical_triangle_values_image("28-01-2005")
    combined = combine_two_triangles(v1, v2)
    assert set(combined.keys()) == {"inputs", "layer1", "second_layer", "third_layer", "core"}
    assert combined["inputs"]["A"] == full_reduce(v1["inputs"]["A"] + v2["inputs"]["A"])


def test_build_reads_matches_values():
    vals = mystical_triangle_values_image("29-10-2001")
    reads = build_reads(vals)
    E, F = vals["layer1"]["E"], vals["layer1"]["F"]
    assert reads["EF(CORE)"] == int(f"{E}{F}")


def test_plot_three_triangles(tmp_path):
    fig, result = plot_three_triangles(
        "29-10-2001", "28-01-2005",
        left_title="Person A", right_title="Person B",
        combined_title="Combined",
        save_path=tmp_path / "triptych.png"
    )
    assert "left" in result
    assert "right" in result
    assert "combined" in result
    assert (tmp_path / "triptych.png").exists()
