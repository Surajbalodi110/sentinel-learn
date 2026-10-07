from src.learn.arcade import GAMES, get
from src.sim.library import SIMS


def test_five_games():
    assert len(GAMES) == 5
    ids = [g[0] for g in GAMES]
    assert len(set(ids)) == 5
    for gid, title, desc in GAMES:
        assert title and desc
        html = get(gid)
        assert "<script>" in html and "</script>" in html
        assert "Score" in html or "Moves" in html


def test_five_sims_plus_night_shift():
    from src.sim.scenario import TICKS
    assert len(TICKS) == 6
    assert len(SIMS) == 5
    for s in SIMS:
        for k in ("id", "title", "briefing", "ticks"):
            assert s[k], k
        assert len(s["ticks"]) >= 4
        for t in s["ticks"]:
            for k in ("title", "brief", "auth", "web", "urls", "correct", "why", "rooms"):
                assert k in t, (s["id"], k)
            from src.sim.scenario import ACTIONS
            for a in t["correct"]:
                assert a in ACTIONS
