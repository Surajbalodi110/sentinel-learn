import os

DASH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "dashboard.py"))

def _src():
    return open(DASH, encoding="utf-8").read()

def test_dark_toggle_and_sync():
    s = _src()
    assert "theme-link" in s
    assert "classList.toggle('dark'" in s
    assert "body.dark" in s
    assert "def _link(" in s and "&theme=" in s and "&s=" in s
    assert '🌙 Dark' in s and '☀️ Light' in s

def test_graphical_system():
    s = _src()
    for cls in (".def", ".tdots", ".fab-live", "stCodeBlock", ".kpi", ".sec-title"):
        assert cls in s, f"missing style {cls}"

def test_no_selectbox_popups():
    import re
    for rel in ("dashboard.py", os.path.join("src", "learn", "games.py")):
        p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", rel))
        s = open(p, encoding="utf-8").read()
        assert not re.search(r"st\.selectbox\(", s), f"selectbox in {rel}; use radio"
        assert not re.search(r"\.multiselect\(", s), f"multiselect in {rel}; use checkboxes"

def test_tutor_console():
    s = _src()
    assert "def _related(" in s
    assert "tutor_page_form" in s
    assert "Related room:" in s
    assert "room={room" in s
    assert "chat_input" not in s, "page-level chat_input gets buried; use the form"

def test_home_art_and_dark_contrast():
    s = _src()
    assert "_home_art('home_learn')" in s
    assert "_home_art('home_analyze')" in s
    assert "_home_art('home_ask')" in s
    for rule in ("stMetricValue", 'button[kind="secondary"]', "stLinkButton",
                 "stCheckbox", "stCaptionContainer"):
        assert rule in s, f"missing dark rule {rule}"
