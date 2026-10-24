# Cubbie StudentSaver (Hackathon · Track 1)

**Pitch:** Cubbie becomes an autonomous student savings agent — Student Wallet, brand discount lookup, stackable effective-price optimizer, scheduled deal watch, savings leak checks, and a semester savings summary.

Not “Honey for students.” The question is: *given what I’m eligible for, what’s the cheapest legitimate way to buy — and tell me when my target hits?*

## Install on Cubbie

Public GitHub repo: https://github.com/aaggar66/cubbie-ai-agent

Text Cubbie:

```text
https://github.com/aaggar66/cubbie-ai-agent/tree/main/student-saver
```

Reply **yes**, then try:

- `Build my student wallet — ASU, Prime Student, Chase Freedom`
- `Does McDonald's have a student discount?`
- `Optimize my purchase: $199 headphones, 10% student, 15% coupon, 5% card — don't stack student+coupon`
- `Watch AirPods until effective price is under $170`
- `How much have I saved?`

## What's in the Skill

```text
student-saver/
  SKILL.md
  assets/merchants.json      # 200+ brands (food, grocery, shopping, movies, software)
  scripts/lookup.py          # brand / category search
  scripts/optimize.py        # stackability + effective price
  scripts/wallet.py          # wallet, savings log, deal watches
```

## Also in this repo

- `student-discount-radar/` — earlier brand-lookup-only Skill
- `internship-radar/` — internship shortlist Skill

## Local checks

```bash
python3 student-saver/scripts/lookup.py --sample --query mcdonalds
python3 student-saver/scripts/optimize.py --sample
HOME=$(mktemp -d) python3 student-saver/scripts/wallet.py --sample set --university "Demo U" --card "Chase Freedom"
python3 path/to/cubbie-hackathon-kit/skills/cubbie-skill-creator/scripts/validate_cubbie_skill.py student-saver
```

Cubbie: https://cubbie.ai · Hackathon: https://hackathon.cubbie.ai
