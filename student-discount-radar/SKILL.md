---
name: student-discount-radar
description: Finds current student discounts and free tiers for shopping, food, groceries, Amazon, travel, AI tools, software, cloud, and campus life. Use when the student asks about student discounts, .edu deals, GitHub Student Pack, AI or API credits, Amazon Prime Student, grocery or food coupons, free software, or whether they are missing savings.
---

# Student Discount Radar

This Skill uses Cubbie's built-in capabilities. It has no scripts and needs no API key.

It helps a student claim **real, currently available** student savings across everyday life and tools — not a stale list of fake promo codes.

## When to use

- "What student discounts am I missing?"
- "Any AI / ChatGPT / Claude / Cursor / API credits for students?"
- "Amazon Prime Student, grocery, or food deals?"
- "GitHub Student Pack / JetBrains / Adobe / Microsoft 365?"
- "Student discounts near campus for shopping or restaurants"

Do not invent coupon codes, prices, or eligibility. Do not buy or check out for the student.
Do not ask for passwords, payment cards, or keys in the chat.

## Categories to cover

When the student asks broadly ("everything", "what am I missing"), work through the checklist in
`references/categories.md` (shopping, food, grocery, Amazon, travel, AI/models, software, cloud/dev,
campus, finance). When they name one area, search that area first, then offer one related category.

## Steps

1. Learn context (one question at a time; suggest a default they can accept with "yes"):
   - Country / campus city (default: United States if unclear)
   - School email domain if useful (e.g. `.edu`) — optional
   - Already claimed? (GitHub Student Pack, Prime Student, etc.)
   Remember answers with Cubbie's **Memory** capability.

2. Search with Cubbie's **Web** capability for **official** student offers only:
   - Prefer vendor education pages, GitHub Education, UNiDAYS / Student Beans / SheerID partner pages,
     university bookstore or student-affairs discount pages, and well-known student programs.
   - Read the page you cite. Note: what is free or % off, who qualifies, verify method (.edu, SheerID,
     Student Pack), and expiry if shown.
   - Skip forum "working codes", random coupon blogs, and anything that asks to DM a code.

3. Build a shortlist (at most five in the text thread). For each deal, one or two lines:
   - Name — what you get
   - Who qualifies + how to verify
   - Official link on its own line
   Lead with highest-value / easiest claims first (often: GitHub Student Pack, Prime Student, Google/Microsoft
   education, major AI student plans, local grocery/food if they asked).
   If more than five are worth keeping, make a one-page PDF checklist with Cubbie's **Documents** capability,
   send it, and text only the top three plus "full list in the PDF".

4. For AI / API / token discounts specifically:
   - Search current student, education, startup, or research credit programs for major model and cloud providers.
   - Say clearly if an offer is "student", "educator", "research", or "startup" — do not blur them.
   - If usage billing is involved, offer a simple monthly budget reminder after they claim a plan.

5. Offer next actions, one at a time:
   - "Want the official claim link for the top one?"
   - "Mark these as already claimed so I don't repeat them?"
   - "Weekly check for new student deals? Sunday 5 pm?"

6. Claiming / buying (only with the student's yes):
   - Open the official page with Cubbie's **Browser** capability if they want help walking through signup.
   - For payment, 2FA, or identity verify (SheerID, campus login), hand the browser to the student.
   - Never enter card details or passwords for them. Never pay.

7. Recurring check-in (only after they pick a time):
   Create a scheduled check-in that re-searches 1–2 categories they care about and texts only **new or ending-soon**
   offers, skipping anything Memory says they already claimed.

## Replies

Keep each reply to a few short lines, plain text, no Markdown headings or tables.
Lead with the best deal. Put every official link on its own line.
Ask one question at a time. Suggest a default they can accept with "yes".
If a deal cannot be verified on an official page, say so and omit it.

## When something fails

- Nothing found for a category: say so in one line; offer a nearby category or a different country.
- Page will not load: skip that vendor; continue with verified ones.
- Eligibility unclear: say "verify on their site" and link the official page; do not promise approval.
- Outside Cubbie (no Web): give the category checklist from `references/categories.md` so the student can search
  themselves; do not invent live offers.
