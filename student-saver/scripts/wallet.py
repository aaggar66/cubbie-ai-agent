#!/usr/bin/env python3
"""Student Wallet + savings log + deal watches (persisted under HOME).

Never stores card numbers, CVVs, passwords, or API keys — only nicknames
like "Chase Freedom Unlimited" and program names.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

NAME = "student-saver"


def config_dir(sample: bool) -> Path:
    if sample:
        # Do not touch real student state in --sample mode
        base = Path(os.environ.get("TMPDIR") or "/tmp") / f"{NAME}-sample"
    else:
        base = Path.home() / ".config" / NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def path_wallet(sample: bool) -> Path:
    return config_dir(sample) / "wallet.json"


def path_savings(sample: bool) -> Path:
    return config_dir(sample) / "savings.json"


def path_watches(sample: bool) -> Path:
    return config_dir(sample) / "watches.json"


def path_offers(sample: bool) -> Path:
    return config_dir(sample) / "offers.json"


def parse_day(value: str, flag: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        print(f"error: {flag} must be a date like 2026-10-24", file=sys.stderr)
        sys.exit(2)


def read_json(path: Path, default):
    if not path.is_file():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def empty_wallet() -> dict:
    return {
        "university": None,
        "school_domain": None,  # e.g. asu.edu, from the school email or Canvas address
        "campus": None,
        "level": None,  # undergraduate | graduate | phd
        "country": "US",
        "programs": [],  # UNiDAYS, Student Beans, Prime Student, GitHub Student, ...
        "cards": [],  # nicknames only
        "memberships": [],
        "preferences": [],
        "updated_at": None,
    }


def cmd_show(args) -> None:
    w = read_json(path_wallet(args.sample), empty_wallet())
    print(json.dumps({"wallet": w, "path": str(path_wallet(args.sample))}, indent=2))


def cmd_set(args) -> None:
    w = read_json(path_wallet(args.sample), empty_wallet())
    if args.university is not None:
        w["university"] = args.university
    if args.school_domain is not None:
        from school import normalize_domain  # same scripts/ folder

        w["school_domain"] = normalize_domain(args.school_domain)
    if args.campus is not None:
        w["campus"] = args.campus
    if args.level is not None:
        w["level"] = args.level
    if args.country is not None:
        w["country"] = args.country
    if args.program:
        for p in args.program:
            if p not in w["programs"]:
                w["programs"].append(p)
    if args.card:
        for c in args.card:
            # Refuse anything that looks like a PAN
            digits = "".join(ch for ch in c if ch.isdigit())
            if len(digits) >= 12:
                print("error: do not store card numbers — use a nickname only", file=sys.stderr)
                sys.exit(4)
            if c not in w["cards"]:
                w["cards"].append(c)
    if args.membership:
        for m in args.membership:
            if m not in w["memberships"]:
                w["memberships"].append(m)
    if args.preference:
        for p in args.preference:
            if p not in w["preferences"]:
                w["preferences"].append(p)
    w["updated_at"] = datetime.now(timezone.utc).isoformat()
    write_json(path_wallet(args.sample), w)
    print(json.dumps({"ok": True, "wallet": w}, indent=2))


def cmd_clear(args) -> None:
    write_json(path_wallet(args.sample), empty_wallet())
    print(json.dumps({"ok": True, "wallet": empty_wallet()}, indent=2))


def cmd_log_saving(args) -> None:
    log = read_json(path_savings(args.sample), {"entries": [], "total_saved": 0.0})
    entry = {
        "at": datetime.now(timezone.utc).isoformat(),
        "merchant": args.merchant,
        "category": args.category or "other",
        "retail": args.retail,
        "effective": args.effective,
        "saved": round(args.retail - args.effective, 2),
        "note": args.note or "",
    }
    log["entries"].append(entry)
    log["total_saved"] = round(sum(e["saved"] for e in log["entries"]), 2)
    write_json(path_savings(args.sample), log)
    print(json.dumps({"ok": True, "entry": entry, "total_saved": log["total_saved"]}, indent=2))


def cmd_summary(args) -> None:
    log = read_json(path_savings(args.sample), {"entries": [], "total_saved": 0.0})
    by_cat: dict[str, float] = {}
    for e in log["entries"]:
        by_cat[e.get("category") or "other"] = by_cat.get(e.get("category") or "other", 0.0) + e["saved"]
    print(
        json.dumps(
            {
                "total_saved": log.get("total_saved", 0.0),
                "purchase_count": len(log.get("entries", [])),
                "by_category": {k: round(v, 2) for k, v in sorted(by_cat.items())},
                "recent": log.get("entries", [])[-5:],
            },
            indent=2,
        )
    )


def cmd_watch_add(args) -> None:
    watches = read_json(path_watches(args.sample), {"items": []})
    item = {
        "id": f"w{len(watches['items']) + 1}",
        "product": args.product,
        "merchant": args.merchant or "",
        "target_effective": args.target,
        "current_effective": args.current,
        "status": "watching",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    watches["items"].append(item)
    write_json(path_watches(args.sample), watches)
    print(json.dumps({"ok": True, "watch": item, "count": len(watches["items"])}, indent=2))


def cmd_watch_list(args) -> None:
    watches = read_json(path_watches(args.sample), {"items": []})
    print(json.dumps(watches, indent=2))


def cmd_watch_hit(args) -> None:
    watches = read_json(path_watches(args.sample), {"items": []})
    found = None
    for item in watches["items"]:
        if item["id"] == args.id or item["product"].lower() == args.id.lower():
            item["status"] = "target_hit"
            item["current_effective"] = args.current
            item["hit_at"] = datetime.now(timezone.utc).isoformat()
            found = item
            break
    if not found:
        print("error: watch not found", file=sys.stderr)
        sys.exit(3)
    write_json(path_watches(args.sample), watches)
    print(json.dumps({"ok": True, "watch": found}, indent=2))


def offer_view(item: dict, today: date) -> dict:
    """Add days_left, status and the reminder dates still ahead of today."""
    v = dict(item)
    ends = date.fromisoformat(item["ends"])
    days_left = (ends - today).days
    v["days_left"] = days_left
    if days_left < 0:
        v["status"] = "ended"
    elif days_left <= max(item.get("remind_days") or [0]):
        v["status"] = "ending_soon"
    else:
        v["status"] = "active"
    v["upcoming_reminders"] = sorted(
        (ends - timedelta(days=d)).isoformat()
        for d in set(item.get("remind_days") or [])
        if ends - timedelta(days=d) >= today
    )
    return v


def cmd_offer_add(args) -> None:
    ends = parse_day(args.ends, "--ends")
    started = parse_day(args.started, "--started") if args.started else None
    if started and ends < started:
        print("error: --ends is before --started", file=sys.stderr)
        sys.exit(2)
    if any(d < 0 for d in args.remind_days):
        print("error: --remind-days must be 0 or more", file=sys.stderr)
        sys.exit(2)
    offers = read_json(path_offers(args.sample), {"items": []})
    # Same service + offer name replaces the old entry (e.g. after re-verifying)
    offers["items"] = [
        o for o in offers["items"]
        if not (o["service"].lower() == args.service.lower() and o["offer"].lower() == args.offer.lower())
    ]
    next_id = max([int(o["id"][1:]) for o in offers["items"] if o["id"][1:].isdigit()] + [0]) + 1
    item = {
        "id": f"o{next_id}",
        "service": args.service,
        "offer": args.offer,
        "started": started.isoformat() if started else None,
        "ends": ends.isoformat(),
        "price_after": args.price_after,
        "auto_renews": args.auto_renews,
        "url": args.url,
        "remind_days": sorted(set(args.remind_days), reverse=True),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    offers["items"].append(item)
    write_json(path_offers(args.sample), offers)
    today = parse_day(args.today, "--today") if args.today else date.today()
    print(json.dumps({"ok": True, "offer": offer_view(item, today)}, indent=2))


def cmd_offer_list(args) -> None:
    offers = read_json(path_offers(args.sample), {"items": []})
    today = parse_day(args.today, "--today") if args.today else date.today()
    views = sorted((offer_view(o, today) for o in offers["items"]), key=lambda v: v["ends"])
    print(json.dumps({"today": today.isoformat(), "count": len(views), "offers": views}, indent=2))


def cmd_offer_remove(args) -> None:
    offers = read_json(path_offers(args.sample), {"items": []})
    keep = [o for o in offers["items"] if o["id"] != args.id and o["service"].lower() != args.id.lower()]
    if len(keep) == len(offers["items"]):
        print("error: offer not found", file=sys.stderr)
        sys.exit(3)
    removed = len(offers["items"]) - len(keep)
    offers["items"] = keep
    write_json(path_offers(args.sample), offers)
    print(json.dumps({"ok": True, "removed": removed}, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description="StudentSaver wallet / savings / watches")
    p.add_argument(
        "--sample",
        action="store_true",
        help="Use throwaway sample state under TMPDIR (never real HOME wallet)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("show", help="Show Student Wallet")
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("set", help="Update Student Wallet fields")
    s.add_argument("--university")
    s.add_argument("--school-domain", help="asu.edu, or the student's school email / Canvas address")
    s.add_argument("--campus")
    s.add_argument("--level", choices=["undergraduate", "graduate", "phd"])
    s.add_argument("--country")
    s.add_argument("--program", action="append", default=[])
    s.add_argument("--card", action="append", default=[])
    s.add_argument("--membership", action="append", default=[])
    s.add_argument("--preference", action="append", default=[])
    s.set_defaults(fn=cmd_set)

    s = sub.add_parser("clear", help="Reset wallet")
    s.set_defaults(fn=cmd_clear)

    s = sub.add_parser("log-saving", help="Record a completed optimized purchase")
    s.add_argument("--merchant", required=True)
    s.add_argument("--retail", type=float, required=True)
    s.add_argument("--effective", type=float, required=True)
    s.add_argument("--category", default="other")
    s.add_argument("--note", default="")
    s.set_defaults(fn=cmd_log_saving)

    s = sub.add_parser("summary", help="Savings totals for the dashboard text/PDF")
    s.set_defaults(fn=cmd_summary)

    s = sub.add_parser("watch-add", help="Watch a product until target effective price")
    s.add_argument("--product", required=True)
    s.add_argument("--merchant", default="")
    s.add_argument("--target", type=float, required=True)
    s.add_argument("--current", type=float, required=True)
    s.set_defaults(fn=cmd_watch_add)

    s = sub.add_parser("watch-list", help="List active watches")
    s.set_defaults(fn=cmd_watch_list)

    s = sub.add_parser("watch-hit", help="Mark a watch as target hit")
    s.add_argument("--id", required=True)
    s.add_argument("--current", type=float, required=True)
    s.set_defaults(fn=cmd_watch_hit)

    s = sub.add_parser("offer-add", help="Track a claimed free or student offer until it ends or renews")
    s.add_argument("--service", required=True, help="e.g. Kiro")
    s.add_argument("--offer", required=True, help="e.g. Student plan, 1,000 credits/month")
    s.add_argument("--ends", required=True, help="YYYY-MM-DD the free/discounted period ends, renews or needs re-verification")
    s.add_argument("--started", help="YYYY-MM-DD")
    s.add_argument("--price-after", default="unknown", help='e.g. "$20/month"')
    s.add_argument("--auto-renews", choices=["yes", "no", "unknown"], default="unknown")
    s.add_argument("--url", default="", help="Official page to cancel, renew or re-verify")
    s.add_argument("--remind-days", type=int, action="append", default=None,
                   help="Days before --ends to remind; repeat (default 7 and 1)")
    s.add_argument("--today", help="YYYY-MM-DD, the student's local date")
    s.set_defaults(fn=cmd_offer_add)

    s = sub.add_parser("offer-list", help="Tracked offers, soonest end first, with reminder dates")
    s.add_argument("--today", help="YYYY-MM-DD, the student's local date")
    s.set_defaults(fn=cmd_offer_list)

    s = sub.add_parser("offer-remove", help="Stop tracking an offer (by id or service)")
    s.add_argument("--id", required=True)
    s.set_defaults(fn=cmd_offer_remove)

    args = p.parse_args()
    if getattr(args, "remind_days", "unset") is None:
        args.remind_days = [7, 1]
    args.fn(args)


if __name__ == "__main__":
    main()
