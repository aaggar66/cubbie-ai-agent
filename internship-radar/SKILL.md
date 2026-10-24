---
name: internship-radar
description: Finds internship and early-career postings that fit the student's major, tracks close dates, and drafts cover letters. Use when the student mentions internships, job applications closing soon, Handshake or LinkedIn postings, cover letters, or says they just found out several apps are due this week.
---

# Internship Radar

This Skill uses Cubbie's built-in capabilities. It has no scripts and needs no API key.

## When to use

- "3 internships close Friday and I just found out"
- "Find me software internships that still take apps"
- "Draft a cover letter for this posting"
- "Remind me before these application deadlines"

Do not use it to submit applications, send emails, or apply on the student's behalf without an explicit yes.
Do not invent postings, deadlines, or company facts.

## Steps

1. Learn what to search for (ask one question at a time; suggest a default they can accept with "yes"):
   - Major or target roles (e.g. "software engineering intern?")
   - Location preference (remote, city, or "anywhere?")
   - How soon deadlines matter (default: closing in the next 14 days)
   Remember the answers with Cubbie's **Memory** capability for later searches.

2. Search with Cubbie's **Web** capability for current internship or early-career postings that match.
   Prefer well-known student job boards and company career pages (Handshake listings that are public, LinkedIn,
   Indeed, Greenhouse, Lever, university career pages). Read the posting pages you cite.
   Collect for each match: role title, company, location or remote, application close date (or "rolling"),
   and the application URL.

3. Drop anything that is clearly closed, senior-only, or unrelated to the student's target.
   If fewer than three solid matches appear, widen the search once (nearby roles or a longer deadline window)
   and say you widened it.

4. Text a short shortlist (at most five). For each item, one or two lines:
   - Role @ Company — closes DATE or rolling
   - Link on its own line
   Lead with the soonest deadline. If more than five are worth keeping, make a one-page PDF with Cubbie's
   **Documents** capability, send it, and text only the top three plus "full list in the PDF".

5. Offer next actions, one at a time:
   - "Want reminders 48h and 24h before each close date?"
   - "Want a cover-letter draft for one of these?"
   - "Want a nightly check-in that rechecks closings? 9 pm?"

6. Reminders (only after the student says yes):
   Create reminders with Cubbie's **Reminders** capability for each chosen posting: 48 hours and 24 hours
   before the close time in the student's time zone. Drop times that have already passed.
   If something closes in under 24 hours, say so immediately instead of only scheduling.
   Each reminder names the role, company, close time, and the application link.

7. Cover letter draft (only when the student picks a posting):
   - Read the posting page again with **Web**.
   - Draft a short cover letter (plain text in the thread, or a PDF via **Documents** if they ask).
   - Ground every claim in what the student told you or what is on the posting; never invent experience.
   - If they want it in Gmail: draft (do not send) with Cubbie's **Google / Gmail** capability.
     If Google is not connected, ask them to connect it or paste the draft into their own mail app.
   - Never send an email or submit an application until the student clearly says yes to that exact action.

8. Recurring check-in (only after the student picks a time):
   Create a scheduled check-in that re-runs a short search for closings in the next 7 days that match the
   remembered major and location, then texts only what is new or closing within 48 hours.

## Replies

Keep each reply to a few short lines, plain text, no Markdown headings or tables.
Lead with the soonest deadline. Put every application link on its own line.
Ask one question at a time. Suggest a default the student can accept with "yes".

## When something fails

- No matching postings: say so in one line, ask whether to widen role, location, or deadline window.
- A posting page will not load: skip it, note that one listing was unavailable, continue with the rest.
- Close date is missing: label it "rolling / date unclear" and do not invent a deadline; still offer a reminder
  on a date the student chooses.
- Google not connected when they want a Gmail draft: offer the draft in the thread instead, and how to connect Google.
- Outside Cubbie (no Web or Reminders): list the search plan and the reminder times so the student can set them
  themselves; do not invent live posting results.
