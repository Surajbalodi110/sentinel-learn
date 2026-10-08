import src.auth.store as S


def _fresh(tmp_path, monkeypatch):
    monkeypatch.setenv(S.DB_ENV, str(tmp_path / "u.db"))


def test_register_login_roundtrip(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    u, err = S.register("Asha", "asha@x.com", "password123")
    assert not err and u["name"] == "Asha"
    v, err2 = S.verify("asha@x.com", "password123")
    assert not err2 and v["id"] == u["id"]


def test_duplicate_and_bad_password(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    S.register("A", "a@x.com", "password123")
    _, err = S.register("B", "a@x.com", "password123")
    assert "already registered" in err
    _, err2 = S.register("B", "b@x.com", "short")
    assert "8 characters" in err2
    _, err3 = S.verify("a@x.com", "wrongpass1")
    assert "Wrong" in err3


def test_session_lifecycle(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    u, _ = S.register("A", "a@x.com", "password123")
    tok = S.new_session(u["id"])
    assert len(tok) == 64
    me = S.check_session(tok)
    assert me and me["email"] == "a@x.com"
    assert S.check_session("bogus") is None
    S.end_session(tok)
    assert S.check_session(tok) is None


def test_progress_roundtrip(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    u, _ = S.register("A", "a@x.com", "password123")
    assert S.load_progress(u["id"]) == {}
    S.save_progress(u["id"], {"done_lessons": ["iam"], "lesson_idx": 4})
    back = S.load_progress(u["id"])
    assert back["done_lessons"] == ["iam"] and back["lesson_idx"] == 4


def test_gates_present():
    import os
    p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "dashboard.py"))
    s = open(p, encoding="utf-8").read()
    assert s.count("_need_login()") >= 4, "Learn, Simulation, Arcade must be gated"
    assert 'if nav == "account":' in s
    assert "Log in before accessing this module" in s
    lines = s.splitlines()
    defline = next(i for i, l in enumerate(lines) if l.startswith("def _need_login"))
    calls = [i for i, l in enumerate(lines) if "_need_login()" in l and not l.startswith("def ")]
    assert all(defline < c for c in calls), "gate helper must be defined before first use"


def test_no_tracebacks_for_users():
    import os
    p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".streamlit",
                                      "config.toml"))
    assert os.path.exists(p), "production config must ship"
    s = open(p, encoding="utf-8").read()
    compact = s.replace(" ", "")
    assert "showErrorDetails=false" in compact


def test_restore_runs_once_per_session():
    import os
    s = open(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "dashboard.py")),
             encoding="utf-8").read()
    assert 'if "_restored" not in st.session_state:' in s, \
        "guest restore must run once per session or it wipes in-flight state"
