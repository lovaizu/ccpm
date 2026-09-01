# Reader trial — round 3 (the cap)

**Body under test:** `writ/skills/up/SKILL.md` at `d2660dd`.
**Document read:** the round-2 fixes applied (409 words), as recorded in `checks/12-dogfood.md`. This
is the delivered document — no edit was made after this trial, so the run ends on a reading.
**Handed to the reader, and nothing else:** the produced document pasted in full, and the step-2
reader definition (WHO / WHAT / HOW). No outline, no draft, no `axes.md`, no history, no repository
access. The brief closed with "Do not use any tools. Do not read any files. Answer from this text
alone."
**Agent:** fresh-context subagent, 0 tool uses.

---

## Report, verbatim

**1. Did you reach the purpose?**

Partly. I can decide the core question — "will this stop me from losing work when my context fills up" — because the opening line answers it directly: "when your context fills up, `dn` → `/clear` → `up` picks the session back up from git instead of from your memory." That mechanism is restated with the exact commands in the "Every break is dn → clear → up" section, so I trust it's real and not just a tagline.

What I cannot decide: whether it fits *my* work. The only example is code ("fix the bug in the payment screen"), and the mechanism assumes a PR/git repo — nothing tells me if this only works on coding repos or works for any goal. I also don't know what it costs to run (multiple subagents + reviewers per task sounds like several model calls per task — is that metered, slow, expensive?) or what "reviewers whose job is to break it" actually are. So: yes on the headline promise, no on fit-for-my-case and cost.

**2. Do the headings alone carry the argument?**

Headings, in order: "rn — Right Now" / "You sign off once, on the plan" / "Then it runs, and pulls you in only when the call is yours" / "Every break is dn → clear → up" / "Install it and start" / "The one move it cannot make for you."

Read alone, they tell a clean sequence: approve a plan once → it runs mostly unattended → here's how you pause and resume → here's how to install → here's the one thing you still have to do yourself. That's a coherent shape. What they leave out: the word "context" or "losing work" never appears in a heading — the actual pain point this reader has is only visible once you read the body of heading 3. The headings also never say the plan lives on a *pull request*, or that a *subagent* does the work — I'd need the body for that.

**3. Where did you stumble**

- First sentence uses bare, unprefixed commands — "`dn` → `/clear` → `up`" — but every later mention uses the full form, "`/rn:dn`" and "`/rn:up`". On first read I couldn't tell if `dn`/`up` were shorthand for something else or literal commands; I had to reach the "Install it and start" section to confirm they're `/rn:dn` / `/rn:up`.
- "reviewers whose job is to break it" — no elaboration anywhere on what a reviewer is (another subagent? a static check? a human?). A claim with nothing behind it.
- "Only what they clear lands on the PR" — "they" only resolves to "reviewers" a sentence later; I had to reread to bind the pronoun.
- "You get asked for something when the call is genuinely yours" — "something" is never made concrete. No example of what kind of decision triggers this.
- "The plan lands on the PR rather than in the console because it is too long to read there comfortably." — asserted as fact ("too long") with no basis given — I have no plan length in front of me to judge that.
- The dn→clear→up idea is stated three separate times in close succession: the opener, the section heading "Every break is dn → clear → up," and the closer "which is why the break is three steps and not one." Same content, three phrasings — read as padding/machine-written repetition rather than new information each time.
- The title "rn — Right Now" is never explained or connected to anything in the body — I never learned why it's called that.

**4. What content did you not need**

- "The plan lands on the PR rather than in the console because it is too long to read there comfortably." — this is a design-rationale aside; it serves someone auditing rn's design choices, not me deciding whether to install it. I just needed to know *where* the plan appears, not *why*.
- The full final section, "The one move it cannot make for you," restates the dn/clear/up mechanic a third time before adding the one new fact ("a plugin has no way to [clear context] on your behalf"). That one clause is useful; the restatement around it is not — it serves a reader validating the tool's internal consistency, not the reader deciding to install.
- The detail on `/rn:gm`'s two input modes ("type your changes after the command... or send `/rn:gm` bare and it goes to the review comments...") is operator-level, day-2 documentation. It serves someone already mid-session using the tool, not someone still on the fence about installing it — I could decide to install without knowing this yet.
