from src.scoring.coverage import CHECKED, NOT_CHECKED, scan_summary
from src.state.store import load, save


def test_coverage_content():
    assert len(CHECKED) >= 3 and len(NOT_CHECKED) >= 3
    s = scan_summary(8, 5, 2, 5)
    assert "8 auth" in s and "threshold 5" in s
    assert "not proof of safety" in s


def test_store_roundtrip(tmp_path, monkeypatch):
    import src.state.store as S
    monkeypatch.setattr(S, "PATH", str(tmp_path / "p.json"))
    state = {"hist": [["user", "hi"], ["bot", "hello"]], "done_lessons": ["a"],
             "reviewed": ["x"], "lesson_idx": 3, "last_findings": [{"a": 1}],
             "room_applied": "iam"}
    save(state)
    back = load()
    assert back["lesson_idx"] == 3 and back["done_lessons"] == ["a"]
    assert back["hist"][0] == ["user", "hi"]


def test_store_missing_file(tmp_path, monkeypatch):
    import src.state.store as S
    monkeypatch.setattr(S, "PATH", str(tmp_path / "nope.json"))
    assert load() == {}
