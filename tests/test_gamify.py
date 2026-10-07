from src.gamify import BADGES, XP_FEEDBACK, XP_ROOM, award, earned, rank_for, streak


def _days(n, end_today=True):
    import datetime
    t = datetime.date.today()
    return [(t - datetime.timedelta(days=i)).isoformat() for i in range(n - 1, -1, -1)] if end_today else []


def test_ranks():
    assert rank_for(0) == "Newbie" or rank_for(0)
    assert rank_for(50) != rank_for(600)
    assert rank_for(99999) == "Guru"


def test_streak_counts():
    cur, long = streak(_days(5))
    assert cur == 5 and long == 5
    cur2, _ = streak([])
    assert cur2 == 0
    import datetime
    old = [(datetime.date.today() - datetime.timedelta(days=40)).isoformat()]
    cur3, _ = streak(old)
    assert cur3 == 0


def test_streak_gap():
    import datetime
    t = datetime.date.today()
    ds = [(t - datetime.timedelta(days=i)).isoformat() for i in (0, 1, 3, 4)]
    cur, long = streak(ds)
    assert cur == 2 and long == 2


def test_earned_badges():
    p = {"done_lessons": list(range(10)), "sim_best": {"night-shift": 110},
         "days": _days(8), "feedback_given": True}
    got = earned(p)
    for b in ("first-step", "halfway", "sim-survivor", "sharpshooter", "streak-7", "feedback"):
        assert b in got
    assert "graduate" not in got and "streak-30" not in got


def test_award_accumulates():
    p = {}
    award(p, XP_ROOM)
    award(p, XP_FEEDBACK)
    assert p["xp"] == XP_ROOM + XP_FEEDBACK


def test_badge_ids_unique():
    ids = [b[0] for b in BADGES]
    assert len(ids) == len(set(ids)) == 8


def test_navbar_identity():
    import os
    s = open(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "dashboard.py")),
             encoding="utf-8").read()
    assert "nvat" in s and "Join FREE" in s and "Log In" in s
