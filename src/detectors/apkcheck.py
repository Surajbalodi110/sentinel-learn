"""APK triage. Static ZIP-based scan + optional androguard. Never installs/runs. Offline."""
import hashlib
import io
import zipfile

DANGEROUS = {
    "android.permission.SEND_SMS": 20, "android.permission.READ_SMS": 20,
    "android.permission.RECEIVE_SMS": 15, "android.permission.CALL_PHONE": 10,
    "android.permission.READ_CONTACTS": 10, "android.permission.READ_CALL_LOG": 15,
    "android.permission.RECORD_AUDIO": 15, "android.permission.CAMERA": 10,
    "android.permission.ACCESS_FINE_LOCATION": 10, "android.permission.READ_EXTERNAL_STORAGE": 5,
    "android.permission.WRITE_EXTERNAL_STORAGE": 5, "android.permission.REQUEST_INSTALL_PACKAGES": 25,
    "android.permission.BIND_DEVICE_ADMIN": 30, "android.permission.SYSTEM_ALERT_WINDOW": 15,
    "android.permission.RECEIVE_BOOT_COMPLETED": 5, "android.permission.INTERNET": 0,
}

def _perms_androguard(data: bytes):
    from androguard.misc import AnalyzeAPK
    _, _, dx = AnalyzeAPK(io.BytesIO(data))
    return sorted(dx.get_permissions([]) if hasattr(dx, "get_permissions") else [])

def analyze_apk(data: bytes, filename: str = "") -> dict:
    reasons, score = [], 0
    meta = {"size_mb": round(len(data) / 1048576, 2),
            "sha256": hashlib.sha256(data).hexdigest()[:16] + "..."}
    if not data.startswith(b"PK"):
        return {"kind": "apk", "file": filename, "score": 85, "level": "HIGH",
                "reasons": ["not a ZIP/APK at all — spoofed extension?"], "meta": meta}
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        names = z.namelist()
        meta["files"] = len(names)
        has_manifest = "AndroidManifest.xml" in names
        has_dex = any(n.endswith(".dex") for n in names)
        has_sig = any(n.startswith("META-INF/") and n.endswith((".RSA", ".DSA", ".EC")) for n in names)
        has_so = any(n.endswith(".so") for n in names)
        if not (has_manifest and has_dex):
            reasons.append("ZIP but missing Android app parts — not a real APK?")
            score += 30
        if not has_sig:
            reasons.append("no app signature found — unofficial/repackaged build?")
            score += 20
        if has_so:
            reasons.append("contains native code (.so) — harder to inspect, common in spyware")
            score += 10
        try:
            perms = _perms_androguard(data)
            meta["engine"] = "androguard"
        except Exception:
            perms, meta["engine"] = [], "basic (install androguard for permissions)"
        for p in perms:
            if p in DANGEROUS and DANGEROUS[p]:
                reasons.append(f"requests {p}")
                score += DANGEROUS[p]
        if perms:
            meta["permissions"] = len(perms)
    except zipfile.BadZipFile:
        reasons.append("corrupt ZIP — cannot inspect")
        score += 20
    score = min(100, score)
    level = "HIGH" if score >= 70 else ("MEDIUM" if score >= 30 else "LOW")
    if not reasons:
        reasons = ["no static red flags — still install only from Play Store, check VirusTotal hash"]
    reasons.append("tip: upload the SHA256 to VirusTotal for a real multi-engine verdict")
    return {"kind": "apk", "file": filename, "score": score, "level": level,
            "reasons": reasons, "meta": meta}
