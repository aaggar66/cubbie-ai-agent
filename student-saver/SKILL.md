---
name: student-saver
description: "Student savings agent that starts from what the student's own school gives them free, then brand discounts, price stacking, deal watches and semester totals. Use when the student asks what their school gives them, says optimize my purchase, asks if a store or app has a student discount (McDonald's, Amazon, AMC, Adobe, ChatGPT), wants card vs coupon help, a deal watch, savings dashboard, or missed Spotify/Adobe student plans."
---

# StudentSaver (Cubbie Skill)

Autonomous-feeling savings agent for students — **not** a coupon dump.

Pitch: given what this student is eligible for, find the cheapest *legitimate* way to buy, watch until a target hits, and track real savings.

No API keys. Never store card numbers. Never invent coupon codes. Never pay or check out for the student.

## When to use

- "Does McDonald's have a student discount?"
- "Optimize my purchase — AirPods under $180"
- "I have Chase Freedom and Prime Student — what's best at Best Buy?"
- "Watch this deal 24/7 until it's under $170"
- "How much have I saved this semester?" / savings dashboard
- "Am I missing student plans for Spotify or Adobe?"
- "What does my school give me for free?"

## Setup

Scripts use the Python standard library only. State is saved under
`~/.config/student-saver/` (wallet, savings log, watches, school perks). `--sample` never writes there.

## Your school first

Every Cubbie user is a student, so every answer starts from what their own school already gives them.
A perk the school provides (often already paid for in tuition and fees) beats any brand discount.

### 1. Find the school without asking

Check `python3 scripts/wallet.py show` first. If `school_domain` is empty, work it out from what Cubbie
already knows, in this order, and stop at the first that works:

1. What Cubbie already remembers about the student (school, campus, level).
2. The student's connected Canvas: the school's name and its Canvas address (for example `canvas.asu.edu`).
3. The student's school email address from their connected email (for example `name@asu.edu`).

Turn what you found into the school's domain and save it:

```bash
python3 scripts/school.py domain "canvas.asu.edu"
python3 scripts/wallet.py set --university "Arizona State University" --school-domain asu.edu
```

Only if none of these work, ask once: "Which school are you at?" Add campus and level
(undergraduate, graduate, PhD) to the wallet when Cubbie learns them; many offers differ by level.
Never ask for the student ID number or the school password.

### 2. Explore the school's own offers

Before any brand lookup, run:

```bash
python3 scripts/school.py show --domain <school_domain> --query "<what they want>"
python3 scripts/school.py show --domain <school_domain> --category food_dining
python3 scripts/school.py show --domain <school_domain>          # everything, for "what do I get free?"
```

It prints perks already verified for this school plus searches limited to the school's own site.
If `references/schools/<school_domain>.md` exists (for example `references/schools/asu.edu.md`), read it
too: it lists official pages to start from.

Run the searches with Cubbie's **Web** capability and open the school's pages. A perk counts only if a page
on the school's domain (or a vendor page the school links to) says its students get it. Save each one so
the next question is instant:

```bash
python3 scripts/school.py add --domain asu.edu --name "ChatGPT Edu" --category software_ai \
  --summary "ChatGPT Edu for every ASU student at no cost" --cost free \
  --how-to-claim "Sign in with ASU account" --url "https://ai.asu.edu/chatgpt-edu" --checked 2026-10-24
```

Pass `--checked` as the student's local date. Recheck a saved perk on its page if it is older than one
semester, before you rely on it.

### 3. Then brands

Only after the school check, continue with the brand lookup below. If the school already gives the student
what they asked for, or an equal tool, lead with that.

## Student Wallet

On first use (or when asked), build a lightweight wallet. Ask one question at a time.
Remember with Cubbie's **Memory** capability AND persist with the script:

```bash
python3 scripts/wallet.py show
python3 scripts/wallet.py set --university "Arizona State University" --school-domain asu.edu \
  --level graduate --country US \
  --program "UNiDAYS" --program "Prime Student" --program "GitHub Student" \
  --card "Chase Freedom Unlimited" --card "Discover Student" \
  --membership "Costco" --preference "online"
```

Rules:

- Cards are **nicknames only** (no PANs, CVV, expiry).
- Programs: UNiDAYS, Student Beans, Prime Student, GitHub Student, Spotify Student, etc.
- If `show` is empty, offer defaults the student can accept with "yes".

## Brand / category lookup

When they name a store or ask "student discount at X":

```bash
python3 scripts/lookup.py --query "<brand>" --limit 5
python3 scripts/lookup.py --category food_restaurants --limit 10
python3 scripts/lookup.py --list-categories
```

Then **verify live** with Cubbie's **Web** capability on `verify_urls` / partner hubs
(UNiDAYS, Student Beans, SheerID, official edu pages). Trust the live page over `offer_hint`.

Dataset: `assets/merchants.json` (200+ food, grocery, shopping, movies, software merchants).

## Optimize My Purchase (signature flow)

1. Read wallet (`wallet.py show`), and check the school first (`school.py show --query "<product>"`).
   If the school gives it free, say so and stop unless the student still wants to buy.
2. Look up merchant(s) (`lookup.py`). Verify current student %, coupons, card rates on the web.
3. Run the stackability optimizer with **only verified numbers**:

```bash
python3 scripts/optimize.py --retail 199 --student-pct 10 --coupon-pct 15 \
  --card-pct 5 --portal-pct 3
```

Add `--student-coupon-stack` only when the merchant terms explicitly allow both.

Sample / dry run:

```bash
python3 scripts/optimize.py --sample
```

4. Text the **best** strategy in a few short lines: retail → discounts → effective price → which card nickname → official links on their own lines.
5. Ask: "Log this saving?" / "Watch until a target?"

Log a completed plan the student confirms they will use:

```bash
python3 scripts/wallet.py log-saving --merchant "Nike" --retail 120 --effective 93.10 --category shopping
```

## Deal Watch (scheduled, not a literal always-on server)

Cubbie's **Reminders / scheduled check-ins** are the 24/7 agent. After optimize:

1. Ask target (e.g. under $170) and how often to check (default: every morning 9 am, or every 6 hours if they insist).
2. Save the watch:

```bash
python3 scripts/wallet.py watch-add --product "AirPods Pro" --merchant "Amazon" --target 170 --current 183
```

3. Create the check-in only after the student says yes. Each run should:
   - Re-verify offers on the web for that product/merchant
   - Re-run `optimize.py` with fresh numbers
   - If new effective ≤ target: mark hit and text them

```bash
python3 scripts/wallet.py watch-list
python3 scripts/wallet.py watch-hit --id "AirPods Pro" --current 158
```

Do **not** spam for tiny changes. Notify when target hits or effective price improves by ≥ $10 / ≥ 5%.

## Savings Leak Detector

Proactively (or when asked "what am I missing?"): first what the student's school provides
(`school.py show --domain <school_domain>`), then the wallet programs + common subscriptions
(Spotify, Adobe, Amazon, DoorDash, GitHub, YouTube, Microsoft 365), check official student pages
with **Web**. List only verified gaps: current vs student plan, estimated yearly save.
Never claim a plan exists without a live official page.

## Savings dashboard (in-thread + PDF)

```bash
python3 scripts/wallet.py summary
```

Text a short total + top categories. If they want a visual dashboard, make a one-page PDF with
Cubbie's **Documents** capability (semester total, by category, active watches from `watch-list`).
A full website dashboard is optional stretch — Track 1 must work entirely inside Cubbie.

## Replies

Plain text, few lines, lead with effective price or yes/no on the brand.
Links on their own line. One question at a time.
Never invent codes. Never guarantee approval of SheerID / .edu verify.

## When something fails

| Case | Reply |
| --- | --- |
| Lookup exit 3 | No index row — still search UNiDAYS/Student Beans/official site |
| School unknown (no memory, Canvas or school email) | Ask once: "Which school are you at?" |
| `school.py` exit 2 | Not a school domain; ask for the school's name and find its website |
| `school.py add` exit 4 | Source isn't the school's site; find the school's own page or don't save it |
| School search finds nothing | Say "Didn't find this on <school> pages" and move on to brand offers |
| Optimize missing inputs | Ask for retail price or verify % first |
| Wallet card looks like a number | Refuse; ask for nickname only |
| No live official offer | Say so; suggest ask in-store with student ID if relevant |
| Watch not improved | Silent or one-line "still watching — best is $X" |
