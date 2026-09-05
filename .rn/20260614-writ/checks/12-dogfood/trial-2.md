# Reader trial — round 2

**Body under test:** `writ/skills/up/SKILL.md` at `d2660dd`.
**Document read:** the round-1 fixes applied (476 words), as recorded in `checks/12-dogfood.md`.
**Handed to the reader, and nothing else:** the produced document pasted in full, and the step-2
reader definition (WHO / WHAT / HOW). No outline, no draft, no `axes.md`, no history, no repository
access. The brief closed with "Do not use any tools. Do not read any files. Answer from this text
alone."
**Agent:** fresh-context subagent, 0 tool uses.

---

## Report, verbatim

**1. Did I reach the purpose?**
Partly. The very first paragraph already answers my actual question — what happens when my context fills up: "`dn` → `/clear` → `up` picks the session back up from git instead of from your memory." Combined with "Install it and start," I have enough to act: install the two `/plugin` commands, run `/rn:on <goal>`, and know the break sequence. What I *can't* decide from this reading: what actually happens if I reject work, since "The same two commands answer every later sign-off — the plan, the approach when it needs its own look, and the result at the end" introduces "the approach" as a third sign-off point that's never defined anywhere else in the document. I also can't tell whether this requires me to already have a GitHub repo with PR access — "draft PR" is used as if I already know the mechanics are GitHub-based, but that's never stated outright. So: yes on the core pain point, no on the edges of what I'm actually agreeing to run.

**2. Do the headings alone carry the argument?**
Reading only: "You sign off once, on the plan" → "Then it runs, and pulls you in only when the call is yours" → "Every break is dn → clear → up" → "Install it and start" → "The one move it cannot make for you." That's a real arc — approve once, it works autonomously, breaks are handled by a named sequence, here's how to get it, here's the one manual step. It's coherent on its own. What it leaves out: my actual trigger for caring (context loss) never appears in a heading — "break" is the closest proxy but doesn't name the problem. It also gives no hint that `/rn:ty`/`/rn:gm` exist or what they do, and nothing in the headings signals the PR-centric mechanism (drafts, review comments) that the body leans on heavily.

**3. Where did I stumble?**
- "with your feedback after it, that is what changes; on its own, it goes to your review comments on the PR and works through them one at a time." — I had to re-read this twice to resolve what "it," "that," and "on its own" each refer to (feedback typed after the command vs. the bare command).
- "The same two commands answer every later sign-off — the plan, the approach when it needs its own look, and the result at the end." — "the approach when it needs its own look" has no antecedent anywhere in the document. A claim with nothing behind it.
- The dn/clear/up fact is stated three separate times: in paragraph 1 ("`dn` → `/clear` → `up` picks the session back up from git instead of from your memory"), again in its own section ("`/rn:dn` commits what is finished, pushes it, and leaves a note for next time... `/rn:up` finds the suspended session, reconciles it against the git log, and starts the task you had not reached"), and a third time in the closing section ("rn commits and pushes at a break and leaves itself a note, but `/clear` is yours to run — which is why the break is three steps and not one"). Reading straight through, the third occurrence reads as already-said.
- The mermaid block itself: read as plain text in a straight-through pass, it's a dump of flowchart syntax (`G([Your goal]) --> P([You approve the plan...`) — if this doesn't render, it's noise I have to skip over mid-document, breaking the read.
- "its message opens with a three-line map — ✅ done, 👉 now, ⬜ ahead — so you answer from that without opening the plan." — asserted with no example; I have to take it on faith.
- `/rn:gm` and `/rn:ty` are never explained as words (unlike `/rn:on`, `/rn:dn`, `/rn:up` which are transparent). I'm left guessing what "gm" stands for.

**4. What content did I not need?**
- The mermaid diagram's internal detail ("Expert does it," "reviewers try to break it," "cleared, added to the same PR") — serves someone who wants to understand the implementation/architecture, not someone deciding whether to install. I didn't need the mechanism, just the promise that noise stays out of my view (which the prose sentence right after already gives me in one line).
- The three-line map detail (✅ 👉 ⬜) — serves me *after* I'm already a user and need a quick-reference reminder mid-session, not me right now evaluating whether to start.
- "the approach when it needs its own look" clause — serves an existing user who has already hit a mid-task approval prompt and wants to know it's the same command; for a first-time reader it's an unresolved dangling reference that adds nothing actionable.
- The third repetition of dn/clear/up in the closing section — serves nobody in a straight-through read; it might serve a skimmer who jumps straight to the last section without reading the top, but that's not this reader.
