from numerology.features.daily_report import daily_triangle_report
from numerology.features.yearly_report import yearly_triangle_report

def test_daily_all_panels_and_time_slots():
    rep = daily_triangle_report("29-10-2001")
    assert rep["type"] == "daily"
    # panels present
    for k in ("left_dob", "right_day", "right_today", "combined"):
        assert k in rep["panels"]
    # time bands present and ordered
    slots = rep["panels"]["combined"]["time_slots"]
    assert len(slots) == 5
    assert slots[0]["start"] == "00:01" and slots[-1]["end"] == "00:00"

def test_yearly_panels_and_glance():
    rep = yearly_triangle_report("28-01-2005", 2025)
    for k in ("left_dob", "right_year", "combined"):
        assert k in rep["panels"]
    g = rep["summary"]["glance"]
    assert {"G","EF","P"} <= set(g.keys())
