---
name: student-discount-radar
description: Looks up student discounts by brand (e.g. McDonald's, Amazon, AMC, Spotify) and by category across food, grocery, shopping, movie theatres, software, and AI tools using a bundled merchant dataset plus live web verification. Use when the student asks if a store has a student discount, searches a brand name for deals, or wants student savings on restaurants, groceries, shopping, movies, or software.
---

# Student Discount Radar

Bundled merchant index + Cubbie web verification. No API key.

If the student texts a brand like "McDonald's", look it up in the dataset first, then confirm
what is live on official / partner pages. Never invent coupon codes or guarantee a percent off.

## When to use

- "Does McDonald's have a student discount?"
- "Amazon student deal?"
- "AMC / Regal student tickets?"
- "Any student discount for Spotify / Adobe / GitHub?"
- "What grocery or food student discounts am I missing?"

Do not buy or check out for the student. Do not ask for passwords, cards, or keys in chat.

## Setup (first time only)

No packages required. Scripts use the Python standard library only.

## Steps

1. Remember country / campus city with Cubbie's **Memory** when the student names them
   (default country: United States). Ask one clarifying question only if the brand is ambiguous.

2. Run the local lookup from this Skill's folder (always do this for a named brand):

   ```bash
   python3 scripts/lookup.py --query "<brand or product>" --limit 5
   ```

   Examples: `--query "mcdonalds"`, `--query "amc"`, `--query "adobe"`.

   Browse a whole category:

   ```bash
   python3 scripts/lookup.py --category food_restaurants --limit 10
   python3 scripts/lookup.py --list-categories
   ```

   Categories: `food_restaurants`, `grocery`, `shopping`, `movies_entertainment`,
   `software_ai_cloud`, `travel`.

   Dry run without relying on the full file:

   ```bash
   python3 scripts/lookup.py --sample --query mcdonalds
   ```

3. **Verify live** with Cubbie's **Web** capability before promising a deal:
   - Open the match's `verify_urls` and the relevant `partner_hubs` (UNiDAYS, Student Beans,
     SheerID, GitHub Education, Amazon Student, etc.).
   - Read what the page says *today*: percent off, free item, ticket price, eligibility, country.
   - If the US brand is franchise-based (many restaurants), say the national policy may vary and
     suggest asking in-store with student ID when the dataset notes that.
   - Skip random coupon blogs and "working codes" posts.

4. Reply with at most three matches in the text thread:
   - Brand — what the verified page offers (or "no live official offer found")
   - How to unlock (UNiDAYS, Student Beans, .edu, SheerID, student ID in store)
   - Official link on its own line
   If the student asked "everything in grocery/food/movies/software", run category lookups, verify
   the top items, and put the long list in a PDF via Cubbie's **Documents** capability.

5. Offer next steps one at a time:
   - "Want me to open the claim page in the browser?"
   - "Mark this brand as already claimed?"
   - "Weekly new-deals check? Sunday 5 pm?"

6. Browser claim (only after yes): open the official URL with Cubbie's **Browser** capability.
   Hand the browser to the student for login, SheerID, payment, or 2FA. Never pay for them.

7. Recurring check-in (only after they pick a time): re-check 1–2 saved brands or categories and
   text only changes.

## Dataset

`assets/merchants.json` is a searchable index of **200+** merchants across food, grocery, shopping,
movie theatres, software/AI, and travel. It stores *where to look*, not forever-fixed coupon codes.
`references/categories.md` explains category coverage. Expand the JSON when you add brands; keep
`offer_hint` honest and code-free.

## Replies

Short plain-text lines. Lead with the brand they asked about. Links on their own line.
If lookup exit code 3 (no matches): say you have no index row yet, still search UNiDAYS + Student
Beans + the brand's education page on the web, then offer to remember the result.

## When something fails

| Situation | What to text |
| --- | --- |
| Exit code 2 / missing file | Skill files incomplete; reinstall from the GitHub link |
| Exit code 3 / no matches | No index hit — searching the web/partner hubs anyway |
| Web page disagrees with hint | Trust the live page; say the dataset tip was outdated |
| No official student offer | "No official student discount I can verify right now" + suggest asking in-store if relevant |
| Outside Cubbie | Run `python3 scripts/lookup.py --sample --query ...` locally; do not invent live prices |
