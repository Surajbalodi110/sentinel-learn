from src.feedback.store import entry, forward_email, forward_endpoint, submit, validate


def test_validate():
    assert validate({"name": "", "love": "x", "improve": "y"})
    assert validate({"name": "A", "love": "", "improve": "y"})
    assert validate({"name": "A", "love": "x", "improve": "y"}) == []
    assert validate({"name": "A", "love": "x", "improve": "y", "rating": 9})


def test_submit_saves_locally(tmp_path, monkeypatch):
    import src.feedback.store as S
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("FEEDBACK_ENDPOINT", raising=False)
    monkeypatch.delenv("SMTP_HOST", raising=False)
    e, errs, ch = submit("Priya", "p@x.com", 5, "Hindi mode", "faster tutor")
    assert not errs and e["ref"].startswith("FB-") and ch == ["local"]
    assert "Priya" in open("data/feedback.jsonl", encoding="utf-8").read()


def test_email_off_without_config(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    assert forward_email({"ref": "X", "name": "N", "contact": "", "rating": 5,
                          "love": "a", "improve": "b"}) == "off"
    monkeypatch.delenv("FEEDBACK_ENDPOINT", raising=False)
    assert forward_endpoint({"ref": "X"}) == "off"


def test_entry_shape():
    e = entry(" A ", " c ", 5, "l", "i")
    assert e["name"] == "A" and e["rating"] == 5 and len(e["ref"]) == 11
