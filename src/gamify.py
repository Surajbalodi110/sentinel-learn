"""Gamification: XP, streaks, ranks, badges. Pure logic, tested."""

XP_ROOM = 100
XP_SIM_CLEAR = 50
XP_FEEDBACK = 25
XP_DAILY = 10

RANKS = [(0, "Newbie"), (200, "Learner"), (600, "Analyst"),
         (1200, "Defender"), (2500, "Sentinel"), (5000, "Guru")]

BADGES = [
    ("first-step", "First Blood", "Complete 1 room"),
    ("halfway", "Halfway Hero", "Complete 10 rooms"),
    ("graduate", "SOC Graduate", "Complete all 20 rooms"),
    ("sim-survivor", "Sim Survivor", "Finish any simulation"),
    ("sharpshooter", "Sharpshooter", "Score 100+ in a simulation"),
    ("streak-7", "Week Warrior", "7-day streak"),
    ("streak-30", "Unstoppable", "30-day streak"),
    ("feedback", "Voice Heard", "Send feedback"),
]


def rank_for(xp: int) -> str:
    name = RANKS[0][1]
    for bar, title in RANKS:
        if xp >= bar:
            name = title
    return name


def streak(days: list) -> tuple:
    """(current, longest) from YYYY-MM-DD list. Timezone-naive, UTC days."""
    import datetime
    ds = sorted(set(days or []))
    if not ds:
        return 0, 0
    try:
        dates = [datetime.date.fromisoformat(d) for d in ds]
    except ValueError:
        return 0, 0
    longest, run = 1, 1
    for a, b in zip(dates, dates[1:]):
        run = run + 1 if (b - a).days == 1 else 1
        longest = max(longest, run)
    today = datetime.date.today()
    cur = 0
    d = today
    have = set(dates)
    if today not in have and (today - datetime.timedelta(days=1)) not in have:
        cur = 0
    else:
        while d in have:
            cur += 1
            d -= datetime.timedelta(days=1)
    return cur, longest


def earned(progress: dict) -> list:
    done = progress.get("done_lessons", [])
    bests = progress.get("sim_best", {}) or {}
    cur, _ = streak(progress.get("days", []))
    out = []
    if len(done) >= 1:
        out.append("first-step")
    if len(done) >= 10:
        out.append("halfway")
    if len(done) >= 20:
        out.append("graduate")
    if bests:
        out.append("sim-survivor")
    if any(v >= 100 for v in bests.values() if isinstance(v, int)):
        out.append("sharpshooter")
    if cur >= 7:
        out.append("streak-7")
    if cur >= 30:
        out.append("streak-30")
    if progress.get("feedback_given"):
        out.append("feedback")
    return out


def award(progress: dict, amount: int) -> dict:
    progress["xp"] = int(progress.get("xp", 0) or 0) + amount
    return progress
