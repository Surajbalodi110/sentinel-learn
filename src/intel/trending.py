"""Trending threats via CISA KEV (no key). Caches to disk for offline use."""
import csv
import json
import os
from datetime import datetime

KEV_URL = "https://www.cisa.gov/sites/default/files/csv/known_exploited_vulnerabilities.csv"

FALLBACK = [
    {"cveID": "CVE-2024-21887", "vendorProject": "Ivanti", "product": "Connect Secure",
     "vuln": "Command injection", "dateAdded": "2024-01-16",
     "notes": "Bundled offline example. Run with internet once to refresh."},
    {"cveID": "CVE-2023-4966", "vendorProject": "Citrix", "product": "NetScaler",
     "vuln": "Session hijack (Citrix Bleed)", "dateAdded": "2023-10-18",
     "notes": "Bundled offline example."},
]

def _cache_path(cfg_path="config.yaml"):
    try:
        import yaml
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
        return cfg.get("intel", {}).get("cache_file", "data/kev_cache.json")
    except Exception:
        return "data/kev_cache.json"

def fetch_trending(top=10, cache_file="data/kev_cache.json", timeout=20):
    """Try live fetch, else return cache, else fallback. Never crashes offline."""
    import httpx
    rows = []
    try:
        r = httpx.get(KEV_URL, timeout=timeout, follow_redirects=True)
        r.raise_for_status()
        reader = csv.DictReader(r.text.splitlines())
        for row in reader:
            rows.append({
                "cveID": row.get("cveID", ""),
                "vendorProject": row.get("vendorProject", ""),
                "product": row.get("product", ""),
                "vuln": (row.get("vulnerabilityName", "") or "")[:120],
                "dateAdded": row.get("dateAdded", ""),
            })
        rows.sort(key=lambda x: x["dateAdded"] or "", reverse=True)
        rows = rows[:top]
        os.makedirs(os.path.dirname(cache_file) or ".", exist_ok=True)
        with open(cache_file, "w") as f:
            json.dump({"fetched": datetime.utcnow().isoformat(), "items": rows}, f, indent=2)
        return rows, "live"
    except Exception:
        pass
    try:
        with open(cache_file) as f:
            cached = json.load(f)
        return cached.get("items", [])[:top], "cached-offline"
    except Exception:
        return FALLBACK[:top], "bundled-offline"
