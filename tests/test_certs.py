from src.certs.make import SKILLS, ROOM_TITLES, build, build_resume, cred_id
from src.learn.curriculum import COURSE


def test_skill_coverage():
    ids = {l["id"] for l in COURSE}
    assert set(SKILLS) == ids
    assert set(ROOM_TITLES) == ids
    for v in SKILLS.values():
        assert 2 <= len(v) <= 6


def test_cred_id_stable():
    a, b = cred_id("Cyberguru", "room:iam"), cred_id("cyberguru ", "room:iam")
    assert a == b and a.startswith("CG-")


def test_cert_png():
    png = build("Test Learner", "SOC Operations", "7. SOC Operations", "room:soc-ops")
    assert png[:8] == bytes([137, 80, 78, 71, 13, 10, 26, 10])
    assert len(png) > 5000


def test_herobg_and_logo_lookup():
    from src.certs.make import _bg_image, _logo_file
    img = _bg_image(120, 85)
    assert img.size == (120, 85)
    assert img.getpixel((5, 5)) != img.getpixel((110, 80)), "gradient expected"
    assert _logo_file() is not None


def test_resume_builder():
    md = build_resume("Asha", ["soc-ops", "siem"], {"night-shift": 100})
    assert "Asha" in md and "Alert triage" in md and "SPL" in md
    assert "Night Shift (best 100)" in md and "1/20" not in md and "2/20" in md
    empty = build_resume("", [], {})
    assert "Your Name" in empty and "0/20" in empty
