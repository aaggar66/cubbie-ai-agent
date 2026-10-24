#!/usr/bin/env python3
"""School-first perks: normalize a school's domain, give search queries for its
official pages, and cache perks Cubbie verified there (under HOME).

The script never browses. Cubbie runs the searches, opens the official pages,
and saves only what a page on the school's own domain says.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

NAME = "student-saver"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "assets" / "sample_school.json"

# Where schools usually publish what students already get, by category.
CATEGORY_TERMS = {
    "software_ai": ["free software students", "AI tools students", "Microsoft 365 students", "Adobe students"],
    "food_dining": ["dining hours", "meal plan", "dining dollars bonus", "late night dining"],
    "transit": ["transit pass students", "shuttle", "bike share students"],
    "events_athletics": ["student tickets", "free student events", "arts box office students"],
    "tech_hardware": ["bookstore computers student pricing", "laptop discount students"],
    "health_fitness": ["recreation center students", "student health services free"],
    "perks_general": ["student discounts", "student perks", "included in tuition and fees"],
}

DOMAIN_RE = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$")


def normalize_domain(raw: str) -> str:
    """Accept a domain, URL or email (asu.edu, https://www.asu.edu/x, a@asu.edu,
    canvas.asu.edu) and return the school's base domain (asu.edu)."""
    s = (raw or "").strip().lower()
    if "@" in s:
        s = s.rsplit("@", 1)[1]
    s = re.sub(r"^[a-z]+://", "", s).split("/", 1)[0].split(":", 1)[0]
    parts = [p for p in s.split(".") if p]
    # Keep the registrable part for common academic suffixes: x.edu, x.ac.uk, x.edu.au
    if len(parts) >= 3 and parts[-2] in {"ac", "edu"} and len(parts[-1]) == 2:
        parts = parts[-3:]
    elif len(parts) >= 2:
        parts = parts[-2:]
    domain = ".".join(parts)
    if not DOMAIN_RE.match(domain):
        print(f"error: '{raw}' does not look like a school domain (for example asu.edu)", file=sys.stderr)
        sys.exit(2)
    return domain


def cache_path(domain: str) -> Path:
    return Path.home() / ".config" / NAME / "schools" / f"{domain}.json"


def load_cache(domain: str, sample: bool) -> dict:
    if sample:
        with SAMPLE.open(encoding="utf-8") as f:
            data = json.load(f)
        data["domain"] = domain
        return data
    path = cache_path(domain)
    if not path.is_file():
        return {"domain": domain, "perks": []}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def matching_perks(cache: dict, query: str | None, category: str | None) -> list[dict]:
    perks = cache.get("perks", [])
    if category:
        perks = [p for p in perks if p.get("category") == category]
    if query:
        tokens = [t for t in re.split(r"\W+", query.lower()) if len(t) > 1]
        perks = [
            p for p in perks
            if any(t in " ".join([p.get("name", ""), p.get("summary", ""), p.get("category", "")]).lower() for t in tokens)
        ]
    return perks


def search_queries(domain: str, query: str | None, category: str | None) -> list[str]:
    if query:
        return [f"site:{domain} {query} students", f"site:{domain} {query} free for students"]
    cats = [category] if category else list(CATEGORY_TERMS)
    return [f"site:{domain} {term}" for c in cats for term in CATEGORY_TERMS.get(c, [])[:2]]


def cmd_show(args) -> None:
    domain = normalize_domain(args.domain)
    cache = load_cache(domain, args.sample)
    out = {
        "domain": domain,
        "perks": matching_perks(cache, args.query, args.category),
        "search_queries": search_queries(domain, args.query, args.category),
        "next_step": "Open the school's own pages from these searches. Count a perk only if a page on "
                     f"{domain} (or a page it links to) says students get it, then save it with `add`.",
    }
    print(json.dumps(out, indent=2))


def cmd_add(args) -> None:
    domain = normalize_domain(args.domain)
    if normalize_domain(args.url) != domain and not args.linked_from_school:
        print(f"error: the source must be on {domain}, or pass --linked-from-school if the school's page links to it",
              file=sys.stderr)
        sys.exit(4)
    perk = {
        "name": args.name,
        "category": args.category,
        "summary": args.summary,
        "cost": args.cost,
        "how_to_claim": args.how_to_claim,
        "url": args.url,
        "checked": args.checked or date.today().isoformat(),
    }
    if args.sample:
        print(json.dumps({"ok": True, "sample": True, "perk": perk}, indent=2))
        return
    cache = load_cache(domain, sample=False)
    cache["perks"] = [p for p in cache.get("perks", []) if p.get("name", "").lower() != args.name.lower()]
    cache["perks"].append(perk)
    path = cache_path(domain)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)
        f.write("\n")
    print(json.dumps({"ok": True, "domain": domain, "perk": perk, "count": len(cache["perks"])}, indent=2))


def cmd_domain(args) -> None:
    print(json.dumps({"domain": normalize_domain(args.value)}))


def main() -> None:
    p = argparse.ArgumentParser(description="School-first perks for StudentSaver")
    p.add_argument("--sample", action="store_true", help="Use assets/sample_school.json and write nothing")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("domain", help="Turn an email, URL or Canvas address into the school domain")
    s.add_argument("value")
    s.set_defaults(fn=cmd_domain)

    s = sub.add_parser("show", help="Saved perks for the school plus official-site search queries")
    s.add_argument("--domain", required=True)
    s.add_argument("--query", "-q")
    s.add_argument("--category", "-c", choices=sorted(CATEGORY_TERMS))
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("add", help="Save a perk verified on the school's own site")
    s.add_argument("--domain", required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--category", required=True, choices=sorted(CATEGORY_TERMS))
    s.add_argument("--summary", required=True)
    s.add_argument("--url", required=True)
    s.add_argument("--cost", default="free")
    s.add_argument("--how-to-claim", default="")
    s.add_argument("--checked", help="YYYY-MM-DD, the student's local date")
    s.add_argument("--linked-from-school", action="store_true")
    s.set_defaults(fn=cmd_add)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
