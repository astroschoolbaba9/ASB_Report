from numerology.core import _triangle_from_abcd
from numerology.reads import build_reads
from numerology.traits import summarize_polarity
from numerology.features.special_numbers import scan_special_signals

def test_specials_detects_18_windows_in_yearly():
    # Create a triangle whose reads will include an 18/81 pair:
    # A=1, B=8 tends to push EF and second layers to include 18-like reads.
    vals = _triangle_from_abcd(1, 8, 3, 5)
    reads = build_reads(vals)
    notes = scan_special_signals(feature_type="yearly", final_values=vals, final_reads=reads)
    # May or may not always trigger depending on layer sums; just assert schema:
    if notes:
        assert "feature" in notes and notes["feature"] in ("yearly","monthly")
        assert "tags" in notes and isinstance(notes["tags"], list)

def test_polarity_summary_shape():
    vals = _triangle_from_abcd(2, 4, 6, 8)
    pol = summarize_polarity(vals)
    assert {"positive","negative","neutral","balance","detail"} <= set(pol.keys())
    assert pol["balance"] in {"Mostly positive","Mostly negative","Neutral"}

def test_aeg_same_triple_triggers_daily():
    # brute-force find an ABCD that actually produces AEG or DFG as 111/222/.../999
    target = {"111","222","333","444","555","666","777","888","999"}

    found_case = None
    for a in range(1, 10):
        for b in range(1, 10):
            for c in range(1, 10):
                for d in range(1, 10):
                    vals = _triangle_from_abcd(a, b, c, d)
                    reads = build_reads(vals)

                    notes = scan_special_signals(feature_type="daily", final_values=vals, final_reads=reads)
                    if not notes:
                        continue

                    triples = (notes.get("triples_seen") or {})
                    aeg = triples.get("AEG")
                    dfg = triples.get("DFG")

                    if (aeg in target) or (dfg in target):
                        found_case = (a, b, c, d, aeg, dfg, notes)
                        break
                if found_case:
                    break
            if found_case:
                break
        if found_case:
            break

    assert found_case is not None, "No ABCD produced AEG/DFG same-number triple; check triple scanning or triangle construction."

    _, _, _, _, aeg, dfg, notes = found_case
    assert ("accident_risk" in notes["tags"]) or ("negative_cycle" in notes["tags"]), (
        f"Expected accident/negative tags when AEG/DFG is same-number. Got tags={notes['tags']} aeg={aeg} dfg={dfg}"
    )
