import os

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")

def test_logos_exist_and_live():
    for f in ("cyberguru_logo.svg", "tutor_teacher.svg"):
        p = os.path.normpath(os.path.join(ASSETS, f))
        assert os.path.exists(p), f"missing {f}"
        s = open(p, encoding="utf-8").read()
        assert "<svg" in s and "</svg>" in s

def test_rings_legend_clear_of_circles():
    import sys
    sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
    import importlib
    import src.learn.diagrams as D
    importlib.reload(D)
    svg = D.render({"kind": "rings", "title": "t", "rings": [{"label": "A"}, {"label": "B"}]})
    assert 'viewBox="0 0 470 300"' in svg
    assert 'x="322"' in svg

def test_teacher_is_animated():
    p = os.path.normpath(os.path.join(ASSETS, "tutor_teacher.svg"))
    s = open(p, encoding="utf-8").read()
    assert "animate" in s, "teacher avatar must have SMIL animation (blink)"
    assert "2456a0" in s or "2f6db3" in s, "teacher avatar must wear the blue tie"

def test_avatar_wiring_present():
    dash = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "dashboard.py"))
    s = open(dash, encoding="utf-8").read()
    assert "_tutor_avatar_uri()" in s and "__AVATAR__" in s
    assert "assets/tutor.png" in s
