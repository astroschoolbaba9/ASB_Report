from __future__ import annotations
from typing import Dict

# ── Reads (Excel-style concatenations, no reduction) ──────────────────────────
def build_reads(vals: Dict[str, Dict[str, int]]) -> Dict[str, int]:
    v = {**vals["inputs"], **vals["layer1"], **vals["second_layer"], **vals["third_layer"]}
    def cat(a: str, b: str) -> int:
        return int(f"{v[a]}{v[b]}")
    return {
        # left column examples
        "G": v["G"],
        "EF(CORE)": cat("E", "F"),
        "AB": cat("A", "B"),
        "CD": cat("C", "D"),
        "AE": cat("A", "E"),
        "BE": cat("B", "E"),
        "CF": cat("C", "F"),
        "DF": cat("D", "F"),
        "IJ": cat("I", "J"),
        "KL": cat("K", "L"),
        "JG": cat("J", "G"),
        "GK": cat("G", "K"),
        # right column examples
        "EG": cat("E", "G"),
        "FG": cat("F", "G"),
        "NO": cat("N", "O"),
        "NP": cat("N", "P"),
        "OP": cat("O", "P"),
        "PQ": cat("P", "Q"),
        "PR": cat("P", "R"),
    }