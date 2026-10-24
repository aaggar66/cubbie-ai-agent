#!/usr/bin/env python3
"""Effective-price optimizer with simple stackability rules.

Inputs are percentages or fixed dollar amounts Cubbie already verified on the web.
This script does math only — it does not invent discounts.
"""

from __future__ import annotations

import argparse
import json
import sys


def money(x: float) -> float:
    return round(x + 1e-9, 2)


def apply_percent(price: float, pct: float) -> float:
    return money(price * (pct / 100.0))


def evaluate(
    retail: float,
    student_pct: float,
    coupon_pct: float,
    coupon_fixed: float,
    card_pct: float,
    portal_pct: float,
    student_coupon_stack: bool,
) -> dict:
    """Return ranked valid strategies.

    Model (hackathon-simple, documented in SKILL.md):
    - Student % and coupon %/fixed apply to retail (order: larger percent-off first if both).
    - Card % and portal % apply to the post-discount price (cashback-style).
    - Default: student discount does NOT stack with coupon unless --student-coupon-stack.
    - Card + portal always allowed with either student or coupon path.
    """
    if retail <= 0:
        print("error: retail must be > 0", file=sys.stderr)
        sys.exit(2)

    strategies = []

    def add(name: str, use_student: bool, use_coupon: bool) -> None:
        if use_student and use_coupon and not student_coupon_stack:
            return
        price = retail
        lines = [{"label": "Retail", "amount": money(retail)}]
        # Apply product discounts to retail
        disc_bits = []
        if use_student and student_pct > 0:
            d = apply_percent(retail, student_pct)
            disc_bits.append(("Student discount", d))
        if use_coupon:
            if coupon_pct > 0:
                disc_bits.append(("Coupon %", apply_percent(retail, coupon_pct)))
            if coupon_fixed > 0:
                disc_bits.append(("Coupon $", money(coupon_fixed)))
        # Apply larger discount first for display; subtract sequentially from retail base
        # (conservative: both come off original retail, then clamp)
        product_off = money(sum(a for _, a in disc_bits))
        if product_off > retail:
            product_off = money(retail)
        for label, amt in disc_bits:
            lines.append({"label": label, "amount": -money(amt)})
        after = money(retail - product_off)

        card_amt = apply_percent(after, card_pct) if card_pct > 0 else 0.0
        portal_amt = apply_percent(after, portal_pct) if portal_pct > 0 else 0.0
        if card_amt:
            lines.append({"label": "Card rewards", "amount": -money(card_amt)})
        if portal_amt:
            lines.append({"label": "Portal cashback", "amount": -money(portal_amt)})

        effective = money(after - card_amt - portal_amt)
        if effective < 0:
            effective = 0.0
        saved = money(retail - effective)
        strategies.append(
            {
                "name": name,
                "use_student": use_student,
                "use_coupon": use_coupon,
                "lines": lines,
                "effective": effective,
                "saved": saved,
                "save_pct": money((saved / retail) * 100) if retail else 0.0,
            }
        )

    add("Student + card/portal", True, False)
    add("Coupon + card/portal", False, True)
    add("Student + coupon + card/portal", True, True)
    add("Card/portal only", False, False)

    # Drop empty-ish duplicates
    uniq = []
    seen = set()
    for s in strategies:
        key = (s["effective"], s["use_student"], s["use_coupon"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(s)

    uniq.sort(key=lambda s: (s["effective"], -s["saved"]))
    best = uniq[0] if uniq else None
    return {
        "retail": money(retail),
        "rules": {
            "student_coupon_stack": student_coupon_stack,
            "card_and_portal_on": "post-discount price",
        },
        "strategies": uniq,
        "best": best,
        "note": "Cubbie must have verified each %/$ on official pages before passing them here.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Optimize effective purchase price")
    p.add_argument("--retail", type=float, default=None)
    p.add_argument("--student-pct", type=float, default=0.0)
    p.add_argument("--coupon-pct", type=float, default=0.0)
    p.add_argument("--coupon-fixed", type=float, default=0.0)
    p.add_argument("--card-pct", type=float, default=0.0)
    p.add_argument("--portal-pct", type=float, default=0.0)
    p.add_argument(
        "--student-coupon-stack",
        action="store_true",
        help="Allow student % and coupon to both apply (only if merchant terms say so)",
    )
    p.add_argument(
        "--sample",
        action="store_true",
        help="Run a built-in demo calculation",
    )
    args = p.parse_args()

    if args.sample:
        result = evaluate(
            retail=199.0,
            student_pct=10.0,
            coupon_pct=15.0,
            coupon_fixed=0.0,
            card_pct=5.0,
            portal_pct=3.0,
            student_coupon_stack=False,
        )
        result["sample"] = True
    else:
        if args.retail is None:
            print("error: --retail is required (or pass --sample)", file=sys.stderr)
            sys.exit(2)
        result = evaluate(
            retail=args.retail,
            student_pct=args.student_pct,
            coupon_pct=args.coupon_pct,
            coupon_fixed=args.coupon_fixed,
            card_pct=args.card_pct,
            portal_pct=args.portal_pct,
            student_coupon_stack=args.student_coupon_stack,
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
