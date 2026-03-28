from typing import Dict, Tuple, Optional
from datetime import datetime, date
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle   # (kept import unchanged)
from .core import (mystical_triangle_values_image, 
                   mystical_triangle_today,
                   combine_two_triangles,
                   year_only_triangle,
                   mystical_triangle_values_image,
                   combine_two_triangles,
                   parse_dob,
                   _header_chunks,
                   month_year_driver_triangle_selected,  # ← use selected month
                   _resolve_right_day,    
)

# ──────────────────────────────────────────────────────────────────────────────
# Inverted 4–2–1 layout WITH labels + numbers (A B C D | E F | G)
# ──────────────────────────────────────────────────────────────────────────────
def _draw_inverted_421(ax: plt.Axes,
                       A: int, B: int, C: int, D: int,
                       E: int, F: int, G: int,
                       show_labels: bool = True):
    """
    Draw the structure in your reference (top band 4 cols, middle band center split,
    short lower bar) and render the values inside each cell. No page titles.
    """
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")

    # Outer triangle edges
    ax.plot([0, 5], [10, 0], color="black", linewidth=3.0)
    ax.plot([10, 5], [10, 0], color="black", linewidth=3.0)
    ax.plot([0, 10], [10, 10], color="black", linewidth=3.0)

    # Helper: x of sides at a given y
    def x_left(y):   return -0.5*y + 5.0
    def x_right(y):  return  0.5*y + 5.0

    # Horizontal bars — tuned to match your sketch
    y1 = 7.4
    y2 = 5.0
    y3 = 2.8

    # Full-width horizontals (edge-to-edge along sides)
    ax.plot([x_left(y1), x_right(y1)], [y1, y1], color="black", linewidth=3.0)
    ax.plot([x_left(y2), x_right(y2)], [y2, y2], color="black", linewidth=3.0)
    # ax.plot([x_left(y3), x_right(y3)], [y3, y3], color="black", linewidth=3.0)

    # Top band 4 columns (verticals down to y1 only)
    for x in (2.5, 5.0, 7.5):
        ax.plot([x, x], [10, y1], color="black", linewidth=3.0)

    # Middle band center split from y1 → y3
    ax.plot([5.0, 5.0], [y1, y2], color="black", linewidth=3.0)

    # ---- Place numbers (and optional small labels) ----
    def put(lbl: str, val: int, x: float, y: float):
        if show_labels:
            ax.text(x, y + 0.55, lbl, ha="center", va="center", fontsize=9, color="#000")
        ax.text(x, y - 0.15, str(val), ha="center", va="center",
                fontsize=16, fontweight="bold")

    # Centers for each cell
    # Top band: fixed 4 equal columns on the top band
    cxA, cyA = 1.25, 0.5*(10 + y1)
    cxB, cyB = 3.75, cyA
    cxC, cyC = 6.25, cyA
    cxD, cyD = 8.75, cyA

    # Middle band: compute mid y, then average edges to center
    ym = 0.5*(y1 + y2)
    cxE = 0.5*(x_left(ym) + 5.0); cyE = ym
    cxF = 0.5*(5.0 + x_right(ym)); cyF = ym

    # Tip region G
    cxG, cyG = 5.0, 0.55*y3

    put("A", A, cxA, cyA); put("B", B, cxB, cyB)
    put("C", C, cxC, cyC); put("D", D, cxD, cyD)
    put("E", E, cxE, cyE); put("F", F, cxF, cyF)
    put("G", G, cxG, cyG)


def plot_mystical_triangle_excel_exact(
    dob_str: str,
    save_path: Optional[str] = None,
) -> Tuple[plt.Figure, Dict]:
    vals = mystical_triangle_values_image(dob_str)

    # Draw only up to G
    A=vals["inputs"]["A"]; B=vals["inputs"]["B"]; C=vals["inputs"]["C"]; D=vals["inputs"]["D"]
    E=vals["layer1"]["E"]; F=vals["layer1"]["F"]; G=vals["layer1"]["G"]

    # Keep header parsing for API compatibility (not rendered)
    dob = parse_dob(dob_str)
    dd, mm, yy1, yy2 = _header_chunks(dob)

    # Bigger canvas so the structure fills the page nicely
    fig = plt.figure(figsize=(5.5, 4.2))
    ax = fig.add_subplot(111)

    _draw_inverted_421(ax, A, B, C, D, E, F, G, show_labels=True)

    if save_path:
        fig.savefig(save_path, dpi=170, bbox_inches="tight")
    return fig, vals

# ── Export helpers ────────────────────────────────────────────────────────────
def build_triangle_png_bytes(dob_str: str) -> bytes:
    fig, _ = plot_mystical_triangle_excel_exact(dob_str, save_path=None)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=170, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()

def build_triangle_pdf_bytes(dob_str: str) -> bytes:
    fig, _ = plot_mystical_triangle_excel_exact(dob_str, save_path=None)
    buf = io.BytesIO()
    fig.savefig(buf, format="pdf", dpi=170, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()

def _draw_triangle_on(ax: plt.Axes, vals: Dict[str, Dict[str, int]], title: str):
    """
    Side-by-side helper for other plots.
    Renders the same 4–2–1 layout WITH labels + numbers.
    """
    A=vals["inputs"]["A"]; B=vals["inputs"]["B"]; C=vals["inputs"]["C"]; D=vals["inputs"]["D"]
    E=vals["layer1"]["E"]; F=vals["layer1"]["F"]; G=vals["layer1"]["G"]
    _draw_inverted_421(ax, A, B, C, D, E, F, G, show_labels=True)

def plot_three_triangles(
    left_dob: str,
    right_dob_or_today: str = "today",
    left_title: str = "Left",
    right_title: str = "Right",
    combined_title: str = "Combined",     # kept for API compatibility; not used visually
    save_path: Optional[str] = None,
):
    """
    Plot two structures side-by-side (Left & Right).
    Combined is computed for return payload compatibility but NOT drawn.
    """
    vals_left = mystical_triangle_values_image(left_dob)
    if right_dob_or_today.lower() == "today":
        vals_right = mystical_triangle_today()
        right_title = f"Today ({date.today().strftime('%d-%m-%Y')})"
        right_caption = right_title
    else:
        vals_right = mystical_triangle_values_image(right_dob_or_today)
        right_caption = f"{right_title} — {right_dob_or_today}" if right_title else right_dob_or_today

    # still compute combined values for callers that may depend on them
    vals_combined = combine_two_triangles(vals_left, vals_right)

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2))
    _draw_triangle_on(axes[0], vals_left, f"{left_title} — {left_dob}")
    _draw_triangle_on(axes[1], vals_right, right_caption)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=170, bbox_inches="tight")
    return fig, {"left": vals_left, "right": vals_right, "combined": vals_combined}


def plot_yearly_triptych(
    dob: str,
    year: int,
    left_title: str = "DOB",
    right_title: str = None,
    combined_title: str = "Combined (Yearly)",  # kept for compatibility
    save_path: Optional[str] = None,
):
    """
    Combined (DOB ⊕ Year) triangle ONLY, drawn in inverted 4–2–1 layout.
    Still returns left/right/combined values for compatibility.
    """
    vals_left = mystical_triangle_values_image(dob)
    vals_right = year_only_triangle(year)
    vals_combined = combine_two_triangles(vals_left, vals_right)

    if right_title is None:
        right_title = f"Year {year}"

    fig, ax = plt.subplots(1, 1, figsize=(4.8, 4.0))

    # 👉 draw ONLY the combined triangle
    _draw_triangle_on(ax, vals_combined, f"{dob} ⊕ {year}")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=170, bbox_inches="tight")
    return fig, {"left": vals_left, "right": vals_right, "combined": vals_combined}


def plot_monthly_triptych(
    dob: str,
    year: int,
    month: int,
    left_title: str = "DOB",
    right_title: Optional[str] = None,
    combined_title: str = "Combined (Monthly)",  # kept for compatibility
    save_path: Optional[str] = None,
):
    """
    Combined (DOB ⊕ Month–Year driver) triangle ONLY, in inverted 4–2–1 layout.
    Still returns left/right/combined values for compatibility.
    """
    vals_left = mystical_triangle_values_image(dob)
    vals_right = month_year_driver_triangle_selected(month, year)
    vals_combined = combine_two_triangles(vals_left, vals_right)

    if right_title is None:
        right_title = f"{datetime(year, month, 1).strftime('%B %Y')}"

    fig, ax = plt.subplots(1, 1, figsize=(4.8, 4.0))

    # 👉 draw ONLY the combined triangle
    label = f"{dob} ⊕ {datetime(year, month, 1).strftime('%b %Y')}"
    _draw_triangle_on(ax, vals_combined, label)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=170, bbox_inches="tight")
    return fig, {"left": vals_left, "right": vals_right, "combined": vals_combined}



def plot_daily_triptych(
    dob: str,
    target_day: str,
    left_title: str = "DOB",
    right_title: Optional[str] = None,
    combined_title: str = "Combined (Daily)",  # kept for compatibility
    save_path: Optional[str] = None,
):
    """
    Combined (DOB ⊕ Day driver) triangle ONLY, in inverted 4–2–1 layout.
    Still returns left/right/combined values for compatibility.
    """
    vals_left = mystical_triangle_values_image(dob)
    vals_right, label = _resolve_right_day(target_day)
    vals_combined = combine_two_triangles(vals_left, vals_right)

    if right_title is None:
        right_title = f"Day {target_day}"

    fig, ax = plt.subplots(1, 1, figsize=(4.8, 4.0))

    # 👉 draw ONLY the combined triangle
    combo_label = f"{dob} ⊕ {label}"
    _draw_triangle_on(ax, vals_combined, combo_label)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=170, bbox_inches="tight")
    return fig, {"left": vals_left, "right": vals_right, "combined": vals_combined}

