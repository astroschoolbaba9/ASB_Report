from __future__ import annotations
from datetime import datetime, date
from typing import Dict, Tuple, Optional


# ── Reducers & parsing helpers ────────────────────────────────────────────────
def full_reduce(n: int) -> int:
    """Always reduce to a single digit (1–9)."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

def parse_dob(dob_str: str) -> date:
    dob_str = dob_str.strip().replace("/", "-")
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(dob_str, fmt).date()
        except ValueError:
            pass
    raise ValueError("Use DD-MM-YYYY or YYYY-MM-DD")

def _header_chunks(d: date) -> tuple[str, str, str, str]:
    day = f"{d.day:02d}"
    mon = f"{d.month:02d}"
    year = f"{d.year:04d}"
    return day, mon, year[:2], year[2:]

def _collect_used_numbers(vals: Dict[str, Dict[str, int]]) -> set[int]:
    used: set[int] = set()
    for section in ("inputs", "layer1", "second_layer", "third_layer"):
        for n in vals[section].values():
            used.add(int(n))
    return used


# ── Core math ─────────────────────────────────────────────────────────────────
def mystical_triangle_values_image(dob_str: str) -> Dict[str, Dict[str, int]]:
    dob = parse_dob(dob_str)
    day, mon, year = dob.day, dob.month, dob.year
    year_str = f"{year:04d}"

    # A = full reduce of day
    A = full_reduce(day)
    # B = full reduce of month
    B = full_reduce(mon)
    # C = full reduce of first 2 digits of year
    first2 = int(year_str[:2])
    C = full_reduce(first2)
    # D = full reduce of last 2 digits of year
    last2  = int(year_str[2:])
    D = full_reduce(last2)

    # E,F,G
    E = full_reduce(A + B)
    F = full_reduce(C + D)
    G = full_reduce(E + F)

    # Baseline & clusters
    I = full_reduce(A + E)
    J = full_reduce(B + E)
    H = full_reduce(I + J)
    K = full_reduce(C + F)
    L = full_reduce(D + F)
    M = full_reduce(K + L)

    N = full_reduce(F + G)
    O = full_reduce(E + G)
    P = full_reduce(N + O)
    Q = full_reduce(O + P)
    R = full_reduce(N + P)

    return {
        "inputs": {"A": A, "B": B, "C": C, "D": D},
        "layer1": {"E": E, "F": F, "G": G},
        "core": {"core_pair": int(f"{E}{F}"), "G": G, "P_outcome": P},
        "second_layer": {"H": H, "I": I, "J": J, "K": K, "L": L, "M": M},
        "third_layer": {"N": N, "O": O, "P": P, "Q": Q, "R": R},
    }




# ──────────────────────────────────────────────────────────────────────────────
# ADDITIONS: second triangle + combined + triptych plot
# ──────────────────────────────────────────────────────────────────────────────

def mystical_triangle_today() -> Dict[str, Dict[str, int]]:
    """Build triangle values using today's date."""
    today_str = date.today().strftime("%d-%m-%Y")
    return mystical_triangle_values_image(today_str)

def combine_two_triangles(vals1: Dict[str, Dict[str, int]],
                          vals2: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
    """
    Combine two triangles by adding corresponding fields then full-reducing.
    Rebuilds `core` from the combined E/F/P so it is coherent.
    """
    def add_reduce(a: int, b: int) -> int:
        return full_reduce(a + b)

    combined = {
        "inputs": {k: add_reduce(vals1["inputs"][k], vals2["inputs"][k]) for k in vals1["inputs"]},
        "layer1": {k: add_reduce(vals1["layer1"][k], vals2["layer1"][k]) for k in vals1["layer1"]},
        "second_layer": {k: add_reduce(vals1["second_layer"][k], vals2["second_layer"][k]) for k in vals1["second_layer"]},
        "third_layer": {k: add_reduce(vals1["third_layer"][k], vals2["third_layer"][k]) for k in vals1["third_layer"]},
    }
    # Rebuild core from combined E/F/G and P
    E = combined["layer1"]["E"]
    F = combined["layer1"]["F"]
    G = combined["layer1"]["G"]
    P = combined["third_layer"]["P"]
    combined["core"] = {"core_pair": int(f"{E}{F}"), "G": G, "P_outcome": P}
    return combined


# --- Right-hand (day) helpers -------------------------------------------------

def _resolve_right_day(day_str: Optional[str]) -> tuple[Dict[str, Dict[str, int]], str]:
    """
    Build the right-hand triangle from a calendar day.
    If day_str is None or 'today' (case-insensitive), use today's date.
    Returns: (right_triangle_values, right_label_string_DD-MM-YYYY)
    """
    if not day_str or str(day_str).strip().lower() == "today":
        label = date.today().strftime("%d-%m-%Y")
        return mystical_triangle_today(), label
    # accepts DD-MM-YYYY or YYYY-MM-DD (your parse_dob already supports both)
    vals = mystical_triangle_values_image(day_str)
    # keep the label exactly as provided so UI echoes back what caller sent
    return vals, day_str

def daily_combined_triangle(dob_str: str, day: Optional[str] = None) -> Dict[str, Dict[str, int]]:
    """
    Left = DOB triangle; Right = day triangle (today by default or a manual date);
    Combined = fieldwise add + full-reduce.
    Use this from daily_report.py / API to support manual right-hand date.
    """
    left = mystical_triangle_values_image(dob_str)
    right, _label = _resolve_right_day(day)
    return combine_two_triangles(left, right)



# --- put near your other helpers ---
def _triangle_from_abcd(A: int, B: int, C: int, D: int) -> Dict[str, Dict[str, int]]:
    """Build a triangle starting from given A,B,C,D using the same pipeline."""
    E = full_reduce(A + B)
    F = full_reduce(C + D)
    G = full_reduce(E + F)

    I = full_reduce(A + E)
    J = full_reduce(B + E)
    H = full_reduce(I + J)

    K = full_reduce(C + F)
    L = full_reduce(D + F)
    M = full_reduce(K + L)

    N = full_reduce(F + G)
    O = full_reduce(E + G)
    P = full_reduce(N + O)
    Q = full_reduce(O + P)
    R = full_reduce(N + P)

    return {
        "inputs": {"A": A, "B": B, "C": C, "D": D},
        "layer1": {"E": E, "F": F, "G": G},
        "core": {"core_pair": int(f"{E}{F}"), "G": G, "P_outcome": P},
        "second_layer": {"H": H, "I": I, "J": J, "K": K, "L": L, "M": M},
        "third_layer": {"N": N, "O": O, "P": P, "Q": Q, "R": R},
    }

def year_only_triangle(year: int) -> Dict[str, Dict[str, int]]:
    """
    Right-side 'year triangle' used for yearly prediction:
    A=0, B=0; C = reduce(first two digits), D = reduce(last two digits).
    """
    y = f"{int(year):04d}"
    A = 0
    B = 0
    C = full_reduce(int(y[:2]))
    D = full_reduce(int(y[2:]))
    return _triangle_from_abcd(A, B, C, D)

def yearly_combined_triangle(dob_str: str, year: int) -> Dict[str, Dict[str, int]]:
    """
    Left = DOB triangle, Right = year-only triangle, Combined = add+reduce fieldwise.
    """
    left = mystical_triangle_values_image(dob_str)
    right = year_only_triangle(year)
    return combine_two_triangles(left, right)


# in numerology/core.py

def month_year_driver_triangle(dob_str: str, year: int) -> dict:
    """
    Driver triangle for monthly prediction:
      A = 0            (day zeroed)
      B = reduce(M.M)  (month from DOB)
      C = reduce(first two digits of year)
      D = reduce(last two digits of year)
    Then build the full triangle via the same A,B,C,D pipeline.
    """
    d = parse_dob(dob_str)               # you already have this
    y = f"{int(year):04d}"
    A = 0
    B = full_reduce(d.month)
    C = full_reduce(int(y[:2]))
    D = full_reduce(int(y[2:]))
    return _triangle_from_abcd(A, B, C, D)  # reuse your shared math

def monthly_combined_triangle(dob_str: str, year: int) -> dict:
    """Left = DOB triangle; Right = month-year driver; Combined = add+reduce."""
    left  = mystical_triangle_values_image(dob_str)
    right = month_year_driver_triangle(dob_str, year)
    return combine_two_triangles(left, right)


def month_year_driver_triangle_selected(month: int, year: int) -> Dict[str, Dict[str, int]]:
    """
    Right-hand driver for a user-selected month and year:
      A = 0
      B = full_reduce(month)
      C = full_reduce(first two digits of year)
      D = full_reduce(last two digits of year)
    """
    y = f"{int(year):04d}"
    A = 0
    B = full_reduce(int(month))
    C = full_reduce(int(y[:2]))
    D = full_reduce(int(y[2:]))
    return _triangle_from_abcd(A, B, C, D)


def mulank_bhagyank_from_dob(dob_str: str) -> tuple[int, int]:
    """
    Returns:
      • Mulank  = A  (input day reduced)
      • Bhagyank = G (E+F reduced)
    without modifying mystical_triangle_values_image structure.
    """
    vals = mystical_triangle_values_image(dob_str)
    mulank = vals["inputs"]["A"]      # A = mulank
    bhagyank = vals["layer1"]["G"]    # G = bhagyank
    return mulank, bhagyank
