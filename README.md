# Internship Radar (Cubbie Hackathon · Track 1)

A Cubbie Skill for the moment: *three internship apps close Friday — and you just found out.*

Cubbie searches public postings that fit the student's major, tracks close dates, sets reminders (with consent), and drafts cover letters. It never applies or sends email without an explicit yes.

## Install on Cubbie

1. Make this repository **public** on GitHub.
2. Text Cubbie the repository link (or the `internship-radar` folder link).
3. Reply **yes** when Cubbie asks before fetching.
4. Try: `3 internships close Friday, find ones that still fit CS`

Cubbie: https://cubbie.ai

## What's in the repo

```text
internship-radar/
  SKILL.md          # the Skill Cubbie installs
```

No scripts, no API keys, no backend. Cubbie uses its own web search, reminders, documents, memory, and optional Gmail drafts.

## Local check

From a clone of the [Cubbie Hackathon Kit](https://github.com/imaginix-inc/cubbie-hackathon-kit):

```bash
python3 skills/cubbie-skill-creator/scripts/validate_cubbie_skill.py path/to/internship-radar
```

## Hackathon

Teach Cubbie a new trick: https://hackathon.cubbie.ai
