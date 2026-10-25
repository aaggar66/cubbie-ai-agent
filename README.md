# StudentSaver: a Cubbie Skill (Cubbie Hackathon, Track 1)

StudentSaver helps a student pay less for things they're about to buy. It checks what their own school
already provides first, then official student offers from brands, then works out the cheapest way to pay.
It also tracks offers the student claimed and reminds them before one ends.

It runs on [Cubbie](https://cubbie.ai), the AI assistant in students' iMessage, using Cubbie's own abilities
(web, memory, reminders, documents). The scripts use only the Python standard library and need no API keys.

Status: the folder passes the Cubbie Hackathon Kit's validator and the scripts were tested locally.
End-to-end testing on a live Cubbie account is still pending.

## Install on Cubbie

Text Cubbie this link and reply "yes" when it asks to fetch it:

```text
https://github.com/aaggar66/cubbie-ai-agent/tree/main/student-saver
```

Then try, each as a new message:

- `What does ASU give me for free?`
- `Any coupons for food near campus?`
- `I'm about to pay for an AI coding IDE, can I get it free as a student?`
- `Does McDonald's have a student discount?`
- `Optimize my purchase: $199 headphones, 10% student, 15% coupon, 5% card`
- `Watch AirPods until the effective price is under $170`
- `I just claimed a student plan, remind me before it ends`
- `How much have I saved?`

## How it works

1. **First reply.** Right after install, Cubbie finds the student's school and texts up to three perks it
   confirmed on the school's own pages, then asks one question. No setup interview first.
2. **Find the school.** Cubbie uses what it already has (its memory of the student, their connected Canvas,
   or their school email address) and turns it into the school's domain, such as `asu.edu`. It asks the
   student only if none of these are available.
3. **School first.** Cubbie searches the school's own website. A perk counts only if a page on that domain,
   or a page it links to, says students get it. Verified perks are saved with their source link and the date
   checked. A saved perk older than 120 days (about one semester) is marked `recheck`, and Cubbie reopens its
   page before mentioning it.
4. **Brand offers.** `lookup.py` first returns any of 30 offers the team checked on official brand pages
   (see below), then rows from a 222-brand index that only says where to look. Cubbie confirms anything
   not verified and fresh on the live official page before telling the student.
5. **Local coupons.** For ASU, University of Arizona, NAU and Texas A&M, Cubbie also reads that school's
   Student Insider coupons page and shows each coupon's own terms and expiry, labelled as third-party.
6. **Cheapest way to pay.** With numbers Cubbie has verified, a script compares paying with the student
   discount, a coupon, card rewards and cashback.
7. **Follow-up, with the student's yes.** It can watch a product's price on a schedule the student picks,
   track a claimed offer's end date and set reminders before it, and keep a running savings total.

## What's in the Skill

```text
student-saver/
  SKILL.md                         instructions Cubbie follows
  scripts/school.py                school domain, official-site searches, verified school perks
  scripts/lookup.py                search the brand index by name or category
  scripts/optimize.py              effective-price math and stacking rules
  scripts/wallet.py                wallet, savings log, price watches, tracked offers
  assets/merchants.json            brand index (222 entries)
  assets/verified_offers.json      30 US student offers checked on official pages (2026-10-24)
  assets/sample_merchants.json     sample data for --sample runs
  assets/sample_school.json        sample data for --sample runs
  references/categories.md         where to look for deals, by category
  references/schools/asu.edu.md    official ASU pages to start from
```

### Verified offers

`assets/verified_offers.json` holds 30 US student offers, each read on the brand's own website or its
official help or terms pages on 2026-10-24, with the source URL. Facts a page didn't state are left `null`.

| Status | Count | Brands |
| --- | --- | --- |
| `verified` | 23 | GitHub Student Developer Pack, GitHub Copilot, JetBrains, Notion, Figma, Autodesk, Google AI Pro, Kiro, Spotify, Apple Music, Peacock, Paramount+, DoorDash, Uber One, Headspace, Apple Education Store, Samsung, Microsoft Store, Lenovo, Under Armour, J.Crew, Amtrak, Levi's |
| `not_available` | 1 | Cursor (the official page says new student sign-ups stopped on June 25, 2026) |
| `unverified` | 6 | Adobe, YouTube Premium, Amazon Prime Student, Grubhub, Nike, Adidas (official pages wouldn't load or didn't state the offer) |

`lookup.py` marks a verified offer `recheck` once it is more than 30 days old. Unverified entries are never
presented as facts.

### Local coupons

[Student Insider](https://www.studentinsider.com) is a third-party local coupon guide paid for by its
advertisers. On 2026-10-24 its homepage listed four service areas: ASU, University of Arizona, NAU and Texas
A&M. `school.py` returns that school's Coupons page, and each coupon on it states its own code, conditions
and expiry date. The Skill labels these as Student Insider coupons, not school perks, and doesn't suggest
bar, cannabis or vape listings unless the student asks for them.

### Brand index

`assets/merchants.json` has 222 entries: 71 food and restaurants, 55 shopping, 36 grocery, 36 software, AI
and cloud, 14 movies and entertainment, and 10 travel. Each entry lists where to check for a student offer
(UNiDAYS, Student Beans, SheerID, the brand's own pages) and a hint. It contains no prices, percentages or
coupon codes. The country and partner tags have not been verified entry by entry, which is why Cubbie must
confirm every offer live.

### School pages

`references/schools/asu.edu.md` lists official ASU pages for software and AI, dining, transit, events and
tech purchases, gathered from asu.edu search results on 2026-10-24. Every other school is explored live
through `school.py`. Cubbie is told to open each page and confirm before relying on it.

### Price math (`optimize.py`)

- The student discount and coupon are both taken off the retail price.
- Card rewards and portal cashback are taken off the price after discounts.
- The student discount and a coupon are not combined unless `--student-coupon-stack` is passed, which
  `SKILL.md` allows only when the store's terms say both apply.
- The sample (`--sample`: $199, 10% student, 15% coupon, 5% card, 3% portal) gives $155.62 with the coupon
  path.

## Saved data

Each student's data stays on their own Cubbie drive under `~/.config/student-saver/`:

| File | Holds |
| --- | --- |
| `wallet.json` | school, school domain, campus, level, country, program names, card nicknames, memberships |
| `schools/<domain>.json` | perks verified on that school's site, with source link and date checked |
| `savings.json` | savings the student confirmed |
| `watches.json` | price watches |
| `offers.json` | tracked offers with end dates, price after and reminder days |

`--sample` runs write to a separate temporary folder and never touch this data.

## Rules the Skill follows

- No coupon codes, prices or eligibility rules from memory; only what an official page says.
- No card numbers. `wallet.py` refuses any card entry with 12 or more digits.
- No student ID numbers, passwords or keys asked for in chat.
- Cubbie never pays, signs up, cancels or renews anything for the student. Reminders and check-ins are
  created only after the student agrees.

## Limits

- Price watches and offer reminders run only as Cubbie scheduled check-ins and reminders. Nothing runs
  continuously, and there are no live price feeds or store APIs.
- Results depend on pages Cubbie can open. A page that blocks reading, or loads its content with scripts,
  can make a check fail or need Cubbie's browser.
- School detection depends on what the student has shared with Cubbie. ASU is the only school with a bundled
  page list. Local coupons cover only the four Student Insider schools.
- The 30 verified offers are US offers checked on one date; they go stale, which is why `lookup.py` flags
  them after 30 days.
- `school.py` and `wallet.py` take the student's local date as `--today`, because the sandbox clock may be in
  another time zone. Reminder dates are calendar days, not times.

## Local checks

From the repository root:

```bash
python3 student-saver/scripts/school.py --sample show --domain asu.edu --today 2026-10-24
python3 student-saver/scripts/lookup.py --sample --query mcdonalds
python3 student-saver/scripts/lookup.py --query spotify --today 2026-10-24
python3 student-saver/scripts/optimize.py --sample
python3 student-saver/scripts/wallet.py --sample offer-add --service Demo --offer "Student plan" --ends 2027-10-24 --today 2026-10-24
HOME=$(mktemp -d) python3 student-saver/scripts/wallet.py set --university "Demo U" --school-domain demo.edu
uv run path/to/cubbie-hackathon-kit/skills/cubbie-skill-creator/scripts/validate_cubbie_skill.py student-saver
```

Cubbie: https://cubbie.ai · Hackathon: https://hackathon.cubbie.ai
