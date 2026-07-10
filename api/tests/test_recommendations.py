from services.recommendations import DISCLAIMER, adaptive_line, get_phase_content

PHASES = ("menstrual", "follicular", "ovulatory", "luteal")


def test_every_phase_has_content():
    for phase in PHASES:
        content = get_phase_content(phase)
        assert content["phase_summary"]
        assert content["workout"]["intensity_label"]
        assert 3 <= len(content["workout"]["plan"]) <= 4
        assert content["workout"]["avoid"]
        assert content["nutrition"]["focus"]
        assert 6 <= len(content["nutrition"]["foods"]) <= 8
        assert content["nutrition"]["tip"]


def test_disclaimer_is_present_and_nonempty():
    assert "emerging" in DISCLAIMER.lower()


def test_adaptive_line_none_with_no_data():
    assert adaptive_line() is None


def test_adaptive_line_none_with_normal_sleep():
    assert adaptive_line(sleep_min=480) is None


def test_adaptive_line_fires_on_low_sleep():
    line = adaptive_line(sleep_min=200)
    assert line is not None
    assert "lighter session" in line


def test_adaptive_line_low_sleep_takes_priority_over_low_activity():
    line = adaptive_line(sleep_min=200, steps=100, active_min=2)
    assert "lighter session" in line


def test_adaptive_line_fires_on_low_activity_when_sleep_is_fine():
    line = adaptive_line(sleep_min=480, steps=500, active_min=5)
    assert line is not None
    assert "low-movement" in line
