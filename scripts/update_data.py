#!/usr/bin/env python3
"""
Monthly data update for erikafashion.cz Share of Search dashboard.
Pulls fresh data from Ahrefs API and appends to data/history.json.

Usage:
    python scripts/update_data.py

Requires:
    AHREFS_API_KEY environment variable
"""

import os
import sys
import json
from datetime import date
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

API_KEY = os.environ.get("AHREFS_API_KEY", "")
BASE_URL = "https://api.ahrefs.com/v3"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "history.json")

BRAND_KEYWORDS = {
    "erikafashion": ["erikafashion", "erika fashion"],
    "sinsay": ["sinsay"],
    "shein": ["shein"],
    "aboutyou": ["about you", "aboutyou"],
    "reserved": ["reserved"],
    "bonprix": ["bonprix"],
    "zalando": ["zalando"],
    "mohito": ["mohito"],
    "lelosi": ["lelosi"],
    "glami": ["glami"],
    "orsay": ["orsay"],
    "buga": ["buga"],
    "evona": ["evona"],
    "miadresses": ["miadresses"],
    "blankastraka": ["blankastraka"],
    "londonclub": ["londonclub", "london club"],
    "coolboutique": ["coolboutique"],
    "bestmoda": ["bestmoda"],
}


def ahrefs_get(endpoint, params):
    if not API_KEY:
        print("ERROR: AHREFS_API_KEY not set")
        sys.exit(1)
    url = f"{BASE_URL}/{endpoint}?" + urlencode(params)
    req = Request(url)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Accept", "application/json")
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"  API error {e.code}: {e.read().decode()[:200]}")
        return None


def get_snapshot(domain):
    data = ahrefs_get("site-explorer/metrics", {
        "target": domain,
        "date": date.today().isoformat(),
        "mode": "subdomains",
        "country": "CZ",
        "output": "json",
    })
    if data and "metrics" in data:
        m = data["metrics"]
        return {
            "orgTraffic": m.get("org_traffic", 0),
            "orgKeywords": m.get("org_keywords", 0),
            "orgKeywords1_3": m.get("org_keywords_1_3"),
        }
    return None


def get_branded_volume(keywords):
    data = ahrefs_get("keywords-explorer/overview", {
        "select": "keyword,volume",
        "country": "CZ",
        "keywords": ",".join(keywords),
        "output": "json",
    })
    if data and "keywords" in data:
        return sum(kw.get("volume", 0) or 0 for kw in data["keywords"])
    return 0


def get_org_traffic_latest(domain):
    today = date.today()
    data = ahrefs_get("site-explorer/metrics-history", {
        "target": domain,
        "date_from": f"{today.year}-{today.month:02d}-01",
        "mode": "subdomains",
        "history_grouping": "monthly",
        "select": "date,org_traffic",
        "output": "json",
    })
    if data and "metrics" in data and data["metrics"]:
        return data["metrics"][-1].get("org_traffic")
    return None


def get_gsc_latest(project_id):
    today = date.today()
    data = ahrefs_get("gsc/performance-history", {
        "project_id": project_id,
        "date_from": f"{today.year}-{today.month - 1:02d}-01",
        "history_grouping": "monthly",
        "output": "json",
    })
    if data and "metrics" in data:
        for m in data["metrics"]:
            d = m["date"][:7].replace("T", "")
            return {
                "date": f"{today.year}-{today.month - 1:02d}",
                "clicks": m.get("clicks", 0),
                "impressions": m.get("impressions", 0),
                "ctr": round(m.get("ctr", 0), 2),
                "position": round(m.get("position", 0), 2),
            }
    return None


def main():
    print(f"=== Monthly update: {date.today().isoformat()} ===\n")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    new_month = f"{date.today().year}-{date.today().month:02d}"

    if new_month in db["dates"]:
        print(f"Month {new_month} already exists in database. Updating snapshot only.")
    else:
        db["dates"].append(new_month)
        print(f"Adding new month: {new_month}")

    # 1. Branded search volumes
    print("\n--- Branded search volumes ---")
    for brand_id, keywords in BRAND_KEYWORDS.items():
        vol = get_branded_volume(keywords)
        print(f"  {brand_id}: {vol:,}")
        if new_month not in db["dates"][:-1]:
            db["brandSearch"].setdefault(brand_id, []).append(vol)

    # 2. Organic traffic for .cz domains
    print("\n--- Organic traffic (global, .cz domains) ---")
    cz_brands = [b for b in db["brands"] if b["domain"].endswith(".cz") or b["id"] == "erikafashion"]
    for brand in cz_brands:
        traffic = get_org_traffic_latest(brand["domain"])
        if traffic is not None:
            print(f"  {brand['domain']}: {traffic:,}")
            if new_month not in db["dates"][:-1]:
                db["organicTraffic"].setdefault(brand["id"], []).append(traffic)
        else:
            print(f"  {brand['domain']}: skipped")

    # 3. CZ snapshots
    print("\n--- CZ snapshots ---")
    for brand in db["brands"]:
        snap = get_snapshot(brand["domain"])
        if snap:
            db["snapshot"][brand["id"]] = snap
            print(f"  {brand['domain']}: traffic={snap['orgTraffic']:,}, kw={snap['orgKeywords']}")
        else:
            print(f"  {brand['domain']}: failed")

    # 4. GSC (project 7274954)
    print("\n--- GSC ---")
    gsc = get_gsc_latest(7274954)
    if gsc and gsc["date"] not in db["gsc"]["dates"]:
        db["gsc"]["dates"].append(gsc["date"])
        db["gsc"]["clicks"].append(gsc["clicks"])
        db["gsc"]["impressions"].append(gsc["impressions"])
        db["gsc"]["ctr"].append(gsc["ctr"])
        db["gsc"]["position"].append(gsc["position"])
        print(f"  Added {gsc['date']}: {gsc['clicks']:,} clicks")
    else:
        print("  No new GSC data")

    # 5. Update metadata
    db["lastUpdated"] = date.today().isoformat()

    # Save
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\nDatabase saved to {DATA_PATH}")
    print("Done!")


if __name__ == "__main__":
    main()
