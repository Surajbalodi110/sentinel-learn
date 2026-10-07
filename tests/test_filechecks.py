from src.detectors.malpdf import analyze_pdf
from src.detectors.imagecheck import analyze_image
from src.detectors.apkcheck import analyze_apk

def test_pdf_flags_javascript():
    data = b"%PDF-1.4 fake /JavaScript /OpenAction /Launch end"
    r = analyze_pdf(data, "evil.pdf")
    assert r["level"] == "HIGH" and any("JavaScript" in x for x in r["reasons"])

def test_pdf_clean():
    data = b"%PDF-1.4 clean hello world"
    assert analyze_pdf(data, "ok.pdf")["level"] == "LOW"

def test_image_double_extension():
    from PIL import Image
    import io
    buf = io.BytesIO()
    Image.new("RGB", (8, 8)).save(buf, format="PNG")
    r = analyze_image(buf.getvalue(), "photo.jpg.exe")
    assert r["score"] >= 40

def test_apk_fake():
    import io, zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("AndroidManifest.xml", "x")
        z.writestr("classes.dex", "x")
        z.writestr("META-INF/CERT.RSA", "x")
    r = analyze_apk(buf.getvalue(), "app.apk")
    assert r["level"] == "LOW"

def test_apk_spoofed():
    r = analyze_apk(b"definitely not a zip", "app.apk")
    assert r["level"] == "HIGH"
