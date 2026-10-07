from src.sim.scenario import ACTIONS, TICKS, grade, score_action


def test_scenario_shape():
    assert len(TICKS) == 6
    assert len(ACTIONS) == 6
    for t in TICKS:
        for k in ("title", "brief", "auth", "web", "urls", "correct", "why", "rooms"):
            assert k in t, k
        assert t["correct"], t["title"]
        for a in t["correct"]:
            assert a in ACTIONS, (t["title"], a)


def test_scoring():
    assert score_action(TICKS[1], "Block IP / domain") == 20
    assert score_action(TICKS[1], "Do nothing") == -15
    assert score_action(TICKS[1], "Isolate host") == -10
    assert score_action(TICKS[0], "Do nothing") == 20


def test_grades():
    assert grade(120, 120).startswith("S")
    assert grade(84, 120).startswith("A")
    assert grade(60, 120).startswith("B")
    assert grade(0, 120).startswith("C")


def test_fp_trap_exists():
    traps = [t for t in TICKS if t["correct"] == ["Mark FP & close"]]
    assert traps, "simulation needs a false-positive trap tick"


def test_start_flag_logic():
    import re
    import os
    s = open(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "dashboard.py")),
             encoding="utf-8").read()
    assert '"sim_started": False' in s, "start flag must default falsy-but-explicit"
    assert "sim_started = True" in s, "start handler must flip the flag (0 is falsy!)"
