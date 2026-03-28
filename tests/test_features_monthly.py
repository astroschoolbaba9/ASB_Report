from numerology.features.monthly_report import monthly_prediction_report

def test_monthly_position_mapping():
    rep = monthly_prediction_report("29-10-2001", 2025)
    months = rep["months"]
    # spot-check mapping per spec
    assert months["1"]["position"] == "E"
    assert months["2"]["position"] == "E"
    assert months["3"]["position"] == "F"
    assert months["4"]["position"] == "F"
    assert months["5"]["position"] == "H"
    assert months["6"]["position"] == "I"
    assert months["7"]["position"] == "J"
    assert months["8"]["position"] == "K"
    assert months["9"]["position"] == "N"
    assert months["10"]["position"] == "O"
    assert months["11"]["position"] == "Q"
    assert months["12"]["position"] == "R"

def test_monthly_core_glance_present():
    rep = monthly_prediction_report("28-01-2005", 2026)
    glance = rep["summary"]["glance"]
    for k in ("E","F","G","EF","P"):
        assert k in glance
