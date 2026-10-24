#!/usr/bin/env python3
"""Search the bundled student-discount merchant index.

Prints short JSON for Cubbie. Does not invent live coupon codes — Cubbie must
verify verify_urls / partner hubs on the web before telling the student an offer is active.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets" / "merchants.json"
SAMPLE = ROOT / "assets" / "sample_merchants.json"


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
    args = p.parse_args()

    data = load_data(sample=args.sample)

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

    matches = search(data, args.query, args.category, max(1, min(args.limit, 25)))
    result = {
        "query": args.query,
        "category": args.category,
        "match_count": len(matches),
        "disclaimer": data.get("disclaimer"),
        "partner_hubs": data.get("partner_hubs", {}),
        "matches": matches,
        "next_step": "Verify each match on verify_urls and partner hubs with live web search before telling the student a discount is available. Never invent coupon codes.",
    }
    text = json.dumps(result, indent=2)
    # Cubbie reads the first 8,000 characters of command output
    if len(text) > 7800:
        text = text[:7800] + "\n… truncated …\n"
    print(text)
    if not matches:
        sys.exit(3)


if __name__ == "__main__":
    main()
