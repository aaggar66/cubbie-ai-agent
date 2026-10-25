#!/usr/bin/env python3
"""Search the bundled student-discount merchant index.

Prints short JSON for Cubbie. Does not invent live coupon codes — Cubbie must
verify verify_urls / partner hubs on the web before telling the student an offer is active.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets" / "merchants.json"
SAMPLE = ROOT / "assets" / "sample_merchants.json"
VERIFIED = ROOT / "assets" / "verified_offers.json"

# Brand offers change often: a verified entry older than this is marked recheck.
VERIFIED_MAX_AGE_DAYS = 30


def load_verified() -> list[dict]:
    if not VERIFIED.is_file():
        return []
    with VERIFIED.open(encoding="utf-8") as f:
        return json.load(f).get("offers", [])


def _has_words(haystack: str, needle: str) -> bool:
    return bool(needle) and re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", haystack) is not None


def verified_score(query: str, offer: dict) -> int:
    """Whole-word matching only, so 'mac' doesn't match 'machine learning'."""
    q = query.lower().strip()
    names = [offer.get("brand", "").lower(), *[a.lower() for a in offer.get("aliases", [])]]
    if q in names:
        return 100
    if any(_has_words(q, n) for n in names):  # "is spotify cheaper" contains "spotify"
        return 90
    if any(_has_words(n, q) for n in names):  # "copilot" inside "github copilot"
        return 80
    return 0


def verified_matches(query: str, today: date, limit: int) -> list[dict]:
    """Offers checked on official pages, best match first, with freshness."""
    ranked = []
    for offer in load_verified():
        s = verified_score(query, offer)
        if s:
            ranked.append((s, offer))
    ranked.sort(key=lambda t: (-t[0], t[1].get("brand", "").lower()))
    out = []
    for _, offer in ranked[:limit]:
        o = {k: v for k, v in offer.items() if k != "aliases"}
        try:
            age = (today - date.fromisoformat(o.get("checked", ""))).days
        except (TypeError, ValueError):
            age = None
        o["days_since_check"] = age
        o["freshness"] = "fresh" if age is not None and 0 <= age <= VERIFIED_MAX_AGE_DAYS else "recheck"
        out.append(o)
    return out


def load_data(sample: bool) -> dict:
    path = SAMPLE if sample else DATA
    if not path.is_file():
        print(f"error: missing data file {path}", file=sys.stderr)
        sys.exit(2)
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def norm(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum() or ch.isspace()).strip()


def score_merchant(query: str, merchant: dict) -> int:
    q = norm(query)
    if not q:
        return 0
    name = norm(merchant.get("name", ""))
    aliases = [norm(a) for a in merchant.get("aliases", [])]
    hay = [name, *aliases]
    if q in hay or any(q == h for h in hay):
        return 100
    if any(q in h or h in q for h in hay if h):
        return 80
    # token overlap
    q_tokens = set(q.split())
    best = 0
    for h in hay:
        h_tokens = set(h.split())
        if not q_tokens or not h_tokens:
            continue
        overlap = len(q_tokens & h_tokens)
        if overlap:
            best = max(best, 40 + 10 * overlap)
    return best


def search(data: dict, query: str | None, category: str | None, limit: int) -> list[dict]:
    merchants = data.get("merchants", [])
    if category:
        cat = category.strip().lower()
        merchants = [m for m in merchants if m.get("category", "").lower() == cat]

    if query:
        ranked = []
        for m in merchants:
            s = score_merchant(query, m)
            if s > 0:
                ranked.append((s, m))
        ranked.sort(key=lambda t: (-t[0], t[1].get("name", "").lower()))
        return [m for _, m in ranked[:limit]]

    # category-only or browse: alphabetical slice
    merchants = sorted(merchants, key=lambda m: m.get("name", "").lower())
    return merchants[:limit]


def main() -> None:
    p = argparse.ArgumentParser(description="Look up student-discount merchants")
    p.add_argument("--query", "-q", help="Merchant or product name, e.g. mcdonalds")
    p.add_argument(
        "--category",
        "-c",
        help="food_restaurants|grocery|shopping|movies_entertainment|software_ai_cloud|travel",
    )
    p.add_argument("--limit", "-n", type=int, default=5)
    p.add_argument(
        "--sample",
        action="store_true",
        help="Use assets/sample_merchants.json (no network; for dry runs)",
    )
    p.add_argument("--list-categories", action="store_true")
    p.add_argument("--today", help="YYYY-MM-DD, the student's local date (for verified-offer freshness)")
    args = p.parse_args()

    data = load_data(sample=args.sample)
    if args.today:
        try:
            today = date.fromisoformat(args.today)
        except ValueError:
            print("error: --today must be a date like 2026-10-24", file=sys.stderr)
            sys.exit(2)
    else:
        today = date.today()

    if args.list_categories:
        out = {
            "categories": data.get("categories", []),
            "partner_hubs": data.get("partner_hubs", {}),
            "merchant_count": len(data.get("merchants", [])),
        }
        print(json.dumps(out, indent=2))
        return

    if not args.query and not args.category:
        print(
            "error: pass --query (e.g. mcdonalds) and/or --category",
            file=sys.stderr,
        )
        sys.exit(2)

    limit = max(1, min(args.limit, 25))
    matches = search(data, args.query, args.category, limit)
    verified = verified_matches(args.query, today, 3) if args.query else []
    result = {
        "query": args.query,
        "category": args.category,
        "today": today.isoformat(),
        "verified_offers": verified,
        "match_count": len(matches),
        "disclaimer": data.get("disclaimer"),
        "partner_hubs": data.get("partner_hubs", {}),
        "matches": matches,
        "next_step": "verified_offers were read on official pages on their checked date: reopen source_url if "
                     "freshness is recheck, and never present an unverified or not_available entry as a live offer. "
                     "matches only say where to look: verify each on verify_urls and partner hubs before telling "
                     "the student a discount is available. Never invent coupon codes.",
    }
    text = json.dumps(result, indent=2)
    # Cubbie reads the first 8,000 characters of command output
    if len(text) > 7800:
        text = text[:7800] + "\n… truncated …\n"
    print(text)
    if not matches and not verified:
        sys.exit(3)


if __name__ == "__main__":
    main()
