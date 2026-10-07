"""Image triage: spoofing + metadata-exposure check. Never executes. Offline."""
from io import BytesIO

DOUBLE_EXT = (".pdf", ".exe", ".scr", ".bat", ".ps1", ".js", ".apk")

def extract_gps(data: bytes) -> dict | None:
    """Return {'lat': float, 'lon': float} if EXIF GPS present, else None."""
    try:
        from PIL import Image
        from io import BytesIO
        im = Image.open(BytesIO(data))
        exif = im.getexif() if hasattr(im, "getexif") else {}
        if not exif:
            return None
        gps = exif.get_ifd(0x8825) if hasattr(exif, "get_ifd") else exif.get(34853)
        if not gps:
            return None
        lat = _dms(gps.get(2))
        lon = _dms(gps.get(4))
        if lat is None or lon is None:
            return None
        if str(gps.get(1, "N")).upper().startswith("S"):
            lat = -lat
        if str(gps.get(3, "E")).upper().startswith("W"):
            lon = -lon
        return {"lat": round(lat, 6), "lon": round(lon, 6)}
    except Exception:
        return None

def _dms(v) -> float | None:
    try:
        d, m, s = v
        return float(d) + float(m) / 60 + float(s) / 3600
    except Exception:
        return None

def analyze_image(data: bytes, filename: str = "") -> dict:
    reasons, score, meta = [], 0, {"size_kb": round(len(data) / 1024, 1)}
    low = filename.lower()
    # double-extension trick: photo.jpg.exe
    base = low.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    parts = base.split(".")
    if len(parts) > 2 and parts[-1] in ("exe", "scr", "bat", "ps1", "js", "apk", "pdf"):
        reasons.append(f"double extension '{base}' — classic malware disguise")
        score += 40
    try:
        from PIL import Image, ExifTags
        im = Image.open(BytesIO(data))
        im.load()
        meta.update({"format": im.format, "size_px": f"{im.width}x{im.height}", "mode": im.mode})
        real_fmt = (im.format or "").lower()
        if base.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")):
            claimed = base.rsplit(".", 1)[-1].replace("jpg", "jpeg")
            if claimed != real_fmt and not (claimed == "jpg" and real_fmt == "jpeg"):
                reasons.append(f"extension says .{claimed} but content is {real_fmt} (spoofed?)")
                score += 25
        exif = im.getexif() if hasattr(im, "getexif") else {}
        if exif:
            tags = {ExifTags.TAGS.get(k, k) for k in exif.keys()}
            meta["exif_fields"] = len(tags)
            if "GPSInfo" in tags:
                reasons.append("contains GPS location — strips privacy if shared publicly")
                score += 20
            else:
                reasons.append("has metadata (device/software traces possible) — strip before sharing")
                score += 5
    except Exception:
        reasons.append("not a readable image — may be corrupt or not an image at all")
        score += 20
    score = min(100, score)
    level = "HIGH" if score >= 70 else ("MEDIUM" if score >= 30 else "LOW")
    if not reasons:
        reasons = ["looks like a normal image, no metadata red flags"]
    return {"kind": "image", "file": filename, "score": score, "level": level,
            "reasons": reasons, "meta": meta}
