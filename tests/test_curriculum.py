from src.learn.curriculum import COURSE

KINDS = {"picker", "table", "stepper", "scenario", "checklist", "code"}

def test_twenty_lessons():
    assert len(COURSE) == 20
    assert len({l["id"] for l in COURSE}) == 20

def test_lesson_shape():
    from src.learn.levels import LEVELS
    from src.learn.diagrams import render
    from src.learn.stories import STORIES
    from src.learn.games import GAMES
    kinds = set()
    for l in COURSE:
        assert l["area"] and l["title"] and l["overview"] and l["try_it"]
        assert len(l["points"]) >= 3
        assert l["visual"]["kind"] in KINDS, l["id"]
        assert len(l["quiz"]) == 5, l["id"]
        for q in l["quiz"] + [l["task_q"]]:
            assert len(q["opts"]) == 3 and 0 <= q["a"] <= 2 and q["why"]
        for qi, q in enumerate(l["quiz"]):
            assert q.get("hint") or qi < 3, f"{l['id']} Q{qi+1} has no hint path"
        lv = LEVELS.get(l["id"])
        assert lv and lv["beginner"] and lv["intermediate"] and lv["advanced"]
        for k in ("beginner", "intermediate", "advanced"):
            assert len(lv[k]) >= 350, f"{l['id']}/{k} only {len(lv[k])} chars"
        assert len(render(lv["diagram"])) > 200
        kinds.add(lv["diagram"]["kind"])
        for ik in ("img_b", "img_i", "img_a"):
            assert len(render(lv[ik])) > 150, f"{l['id']}/{ik} missing"
        st_ = STORIES.get(l["id"])
        assert st_ and len(st_["story"]) > 100 and len(st_["day"]) > 40, l["id"]
        gm = GAMES.get(l["id"])
        assert gm and gm["type"] in ("spot", "order", "match"), l["id"]
        if gm["type"] == "spot":
            assert len(gm["items"]) == 3
            assert sum(1 for x in gm["items"] if x["evil"]) in (1, 2)
        elif gm["type"] == "order":
            assert len(gm["steps"]) >= 3
        else:
            assert len(gm["pairs"]) >= 3
    assert len(kinds) >= 15, f"only {len(kinds)} diagram kinds: {kinds}"
    from src.learn.depth import DEPTH
    for l in COURSE:
        dp = DEPTH.get(l["id"])
        assert dp and len(dp["deep_dive"]) >= 2 and len(" ".join(dp["deep_dive"])) > 600
        assert len(dp["mistakes"]) >= 3
        assert len(dp["interview"]) >= 2 and all(x["q"] and x["a"] for x in dp["interview"])
        assert len(dp["commands"]) >= 1
