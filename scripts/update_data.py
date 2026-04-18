#!/usr/bin/env python3
"""
Monthly data update script for erikafashion.cz Share of Search dashboard.
Pulls fresh CZ metrics from Ahrefs API and updates the dashboard HTML.

Usage:
    python scripts/update_data.py

Requires:
    AHREFS_API_KEY environment variable
"""

import os
import sys
import json
import re
from datetime import datetime, date
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_KEY = os.environ.get("AHREFS_API_KEY", "")
BASE_URL = "https://api.ahrefs.com/v3"
DASHBOARD_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")

# All tracked domains with their brand IDs
DOMAINS = {
    "erikafashion": "erikafashion.cz",
    "sinsay": "sinsay.com",
    "shein": "shein.com",
    "aboutyou": "aboutyou.cz",
    "reserved": "reserved.com",
    "bonprix": "bonprix.cz",
    "zalando": "zalando.cz",
    "mohito": "mohito.com",
    "lelosi": "lelosi.cz",
    "glami": "glami.cz",
    "orsay": "orsay.cz",
    "buga": "buga.cz",
    "evona": "evona.cz",
    "miadresses": "miadresses.cz",
    "blankastraka": "blankastraka.cz",
    "londonclub": "londonclub.cz",
    "coolboutique": "coolboutique.cz",
    "bestmoda": "bestmoda.cz",
}

# Brand search keywords (brand_id -> list of keyword variants)
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


def ahrefs_request(endpoint, params):
    """Make a request to Ahrefs API v3."""
    if not API_KEY:
        print("ERROR: AHREFS_API_KEY not set")
        sys.exit(1)

    url = f"{BASE_URL}/{endpoint}?"
    url += "&".join(f"{k}={v}" for k, v in params.items())

    req = Request(url)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Accept", "application/json")

    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"API error {e.code} for {endpoint}: {e.read().decode()}")
        return None


def get_site_metrics(domain):
    """Get current CZ organic metrics for a domain."""
    today = date.today().isoformat()
    data = ahrefs_request("site-explorer/metrics", {
        "target": domain,
        "date": today,
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
            "orgCost": m.get("org_cost"),
        }
    return None


def get_branded_volumes(keywords):
    """Get current monthly search volume for branded keywords in CZ."""
    kw_str = ",".join(keywords)
    data = ahrefs_request("keywords-explorer/overview", {
        "select": "keyword,volume",
        "country": "CZ",
        "keywords": kw_str,
        "output": "json",
    })
    if data and "keywords" in data:
        total = 0
        for kw_data in data["keywords"]:
            total += kw_data.get("volume", 0) or 0
        return total
    return 0


def get_organic_traffic_latest(domain):
    """Get latest month organic traffic (global, for .cz domains)."""
    today = date.today()
    date_from = f"{today.year}-{today.month:02d}-01"
    data = ahrefs_request("site-explorer/metrics-history", {
        "target": domain,
        "date_from": date_from,
        "mode": "subdomains",
        "history_grouping": "monthly",
        "select": "date,org_traffic",
        "output": "json",
    })
    if data and "metrics" in data and len(data["metrics"]) > 0:
        return data["metrics"][-1].get("org_traffic", 0)
    return None


def update_dashboard(new_date, snapshots, brand_volumes, traffic_updates):
    """Update the dashboard HTML with new data."""
    with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Update the date in the badge/footer
    old_date_pattern = r"duben 2026"
    months_cz = {
        1: "leden", 2: "unor", 3: "brezen", 4: "duben",
        5: "kveten", 6: "cerven", 7: "cervenec", 8: "srpen",
        9: "zari", 10: "rijen", 11: "listopad", 12: "prosinec"
    }
    today = date.today()
    new_date_str = f"{months_cz[today.month]} {today.year}"

    html = html.replace("duben 2026", new_date_str)
    html = html.replace("2026-04-18", today.isoformat())

    # Update SNAPSHOT object
    # This is a simplified approach - for production, use proper JS AST parsing
    for brand_id, metrics in snapshots.items():
        if metrics:
            old_pattern = f"{brand_id}: {{orgTraffic:{{}}"
            # Simple regex replacement for snapshot values
            pattern = rf'({brand_id}:\s*\{{orgTraffic:)\d+(,\s*orgKeywords:)\d+'
            replacement = rf'\g<1>{metrics["orgTraffic"]}\g<2>{metrics["orgKeywords"]}'
            html = re.sub(pattern, replacement, html)

    # Append new date to DATES array
    new_month = f"{today.year}-{today.month:02d}"
    html = html.replace(
        '"2026-04"',
        f'"2026-04","{new_month}"'
    )

    # Append new branded search volumes
    for brand_id, volume in brand_volumes.items():
        pattern = rf'({brand_id}:\s*\[[\d,]+)'
        html = re.sub(pattern, rf'\1,{volume}', html)

    # Append new organic traffic for domains with history
    for brand_id, traffic in traffic_updates.items():
        if traffic is not None:
            pattern = rf'(ORG_TRAFFIC_HISTORY\s*=\s*\{{[^}}]*{brand_id}:\s*\[[\d,]+)'
            html = re.sub(pattern, rf'\1,{traffic}', html)

    with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard updated for {new_date_str}")


def main():
    print("Starting monthly Share of Search update...")
    print(f"Date: {date.today().isoformat()}")
    print()

    # 1. Get CZ snapshots for all domains
    print("Fetching CZ metrics...")
    snapshots = {}
    for brand_id, domain in DOMAINS.items():
        print(f"  {domain}...", end=" ")
        metrics = get_site_metrics(domain)
        if metrics:
            snapshots[brand_id] = metrics
            print(f"OK (traffic: {metrics['orgTraffic']:,})")
        else:
            print("FAILED")

    # 2. Get branded search volumes
    print("\nFetching branded search volumes...")
    brand_volumes = {}
    for brand_id, keywords in BRAND_KEYWORDS.items():
        print(f"  {brand_id}...", end=" ")
        volume = get_branded_volumes(keywords)
        brand_volumes[brand_id] = volume
        print(f"OK ({volume:,})")

    # 3. Get organic traffic for .cz domains (history append)
    print("\nFetching organic traffic for .cz domains...")
    traffic_updates = {}
    cz_domains = {k: v for k, v in DOMAINS.items() if v.endswith(".cz") or k == "erikafashion"}
    for brand_id, domain in cz_domains.items():
        print(f"  {domain}...", end=" ")
        traffic = get_organic_traffic_latest(domain)
        if traffic is not None:
            traffic_updates[brand_id] = traffic
            print(f"OK ({traffic:,})")
        else:
            print("SKIPPED")

    # 4. Update dashboard
    print("\nUpdating dashboard HTML...")
    update_dashboard(
        date.today().isoformat(),
        snapshots,
        brand_volumes,
        traffic_updates
    )

    print("\nDone!")


if __name__ == "__main__":
    main()
