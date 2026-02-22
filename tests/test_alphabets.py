import pytest
from numerology import mystical_triangle_values_image

# ---------------------------------------------------------------------------
# Expected values per DOB, split by sections so each alphabet is checked
# ---------------------------------------------------------------------------

CASES = {
    "29-10-2001": {
        "inputs":       {"A": 2, "B": 1, "C": 2, "D": 1},
        "layer1":       {"E": 3, "F": 3, "G": 6},
        "second_layer": {"H": 9, "I": 5, "J": 4, "K": 5, "L": 4, "M": 9},
        "third_layer":  {"N": 9, "O": 9, "P": 9, "Q": 9, "R": 9},
    },
    "28-01-2005": {
        "inputs":       {"A": 1, "B": 1, "C": 2, "D": 5},
        "layer1":       {"E": 2, "F": 7, "G": 9},
        "second_layer": {"H": 6, "I": 3, "J": 3, "K": 9, "L": 3, "M": 3},
        "third_layer":  {"N": 7, "O": 2, "P": 9, "Q": 2, "R": 7},
    },
    "11-11-2011": {
        "inputs":       {"A": 2, "B": 2, "C": 2, "D": 2},
        "layer1":       {"E": 4, "F": 4, "G": 8},
        "second_layer": {"H": 3, "I": 6, "J": 6, "K": 6, "L": 6, "M": 3},
        "third_layer":  {"N": 3, "O": 3, "P": 6, "Q": 9, "R": 9},
    },
    "07-07-1999": {
        "inputs":       {"A": 7, "B": 7, "C": 1, "D": 9},
        "layer1":       {"E": 5, "F": 1, "G": 6},
        "second_layer": {"H": 6, "I": 3, "J": 3, "K": 2, "L": 1, "M": 3},
        "third_layer":  {"N": 7, "O": 2, "P": 9, "Q": 2, "R": 7},
    },
    "15-08-1985": {
        "inputs":       {"A": 6, "B": 8, "C": 1, "D": 4},
        "layer1":       {"E": 5, "F": 5, "G": 1},
        "second_layer": {"H": 6, "I": 2, "J": 4, "K": 6, "L": 9, "M": 6},
        "third_layer":  {"N": 6, "O": 6, "P": 3, "Q": 9, "R": 9},
    },
}

# Flatten into (dob, section_name, expected_section_dict)
PARAMS = [
    (dob, "inputs", data["inputs"])
    for dob, data in CASES.items()
] + [
    (dob, "layer1", data["layer1"])
    for dob, data in CASES.items()
] + [
    (dob, "second_layer", data["second_layer"])
    for dob, data in CASES.items()
] + [
    (dob, "third_layer", data["third_layer"])
    for dob, data in CASES.items()
]

@pytest.mark.parametrize("dob, section, expected", PARAMS)
def test_each_section_matches(dob, section, expected):
    """Check that each section (A–D, E–G, H–M, N–R) matches exactly for each DOB."""
    vals = mystical_triangle_values_image(dob)
    assert vals[section] == expected, f"{dob} → {section} mismatch"

# Optional: if you want truly “each alphabet separately”, parametrize down to each key:
LETTER_PARAMS = []
for dob, data in CASES.items():
    for section, section_dict in data.items():
        for letter, value in section_dict.items():
            LETTER_PARAMS.append((dob, section, letter, value))

@pytest.mark.parametrize("dob, section, letter, expected_value", LETTER_PARAMS)
def test_each_letter_individually(dob, section, letter, expected_value):
    """Pin each alphabet (A…R) to its value for multiple DOBs."""
    vals = mystical_triangle_values_image(dob)
    assert vals[section][letter] == expected_value, f"{dob} → {letter} expected {expected_value}"
