# Reader trial — round 1

**Body under test:** `writ/skills/up/SKILL.md` at `d2660dd`.
**Document read:** the step-9 render of `rn/README.md` (504 words), as recorded in `checks/12-dogfood.md`.
**Handed to the reader, and nothing else:** the produced document pasted in full, and the step-2
reader definition (WHO / WHAT / HOW). No outline, no draft, no `axes.md`, no history, no repository
access. The brief closed with "Do not use any tools. Do not read any files. Answer from this text
alone."
**Agent:** fresh-context subagent, 0 tool uses.

---

## Report, verbatim

1. I did not fully reach the purpose. I can tell what `rn` gives me — a plan I sign off on via PR, work done off-screen by "experts and reviewers," and a `dn → /clear → up` cycle that survives context loss. That last piece is exactly my problem, so I know I want this. What I cannot decide from this text alone: what actually happens when I run `/rn:on` on real work — is the "expert" a separate model, a subagent, a person? The doc never says. I also don't know what "reconciles it against the git log" does if the git log and the plan disagree, or what happens if I have uncommitted work when I hit `/clear` myself — the doc trusts me to run `/clear` "yourself" but doesn't say what's lost if I forget or do it too early. I'd install it, but I'd be feeling my way through the first session rather than knowing what to expect.

2. Headings alone: "rn — Right Now" / "You sign off once, on the plan" / "Then it runs, and the messy part stays off your screen" / "Every break is dn → clear → up" / "Install it and start" / "What stays yours". Read in sequence, they do carry a shape: name a goal, approve a plan, work happens invisibly, breaks are a three-step ritual, here's how to install, here's what's still on you. What they leave out: no heading signals *what kind of work* rn is for (bug fixes? features? is a "task" code-sized?), and no heading hints at failure modes or limits — every heading promises smoothness, none flags a boundary.

3. Where I stumbled:
- "the messy part stays off your screen" (section heading) vs. the diagram's own line "only when the call is yours → You weigh in" and the following sentence "When the assistant does stop for you..." — these two sit right next to each other and both are reassurances that trial-and-error is hidden, but then immediately concede you get pulled in sometimes. It's not contradictory exactly, but I re-read it once to check whether "messy part stays off your screen" was actually true, since the very next sentences are about when it doesn't.
- "The experts and reviewers are separate agents, so their trial and error never lands in your window." — asserted with no support. I don't know what "expert" or "reviewer" means here (subagents? separate model calls? a fixed pipeline?), so this reads as a claim I have to take on faith.
- "a plan worth reading is longer than a console comfortably shows" — this is presented as self-evidently true but it's actually the *reason* being given for a design choice (PR over console), stated as flat fact. I stumbled because it assumes I already agree plans are long, when for a "fix the bug in the payment screen" example, I'm not sure the plan needs to be long at all.
- The `/rn:gm` explanation: "`/rn:gm <what to change>` sends it back. Plain `/rn:gm` walks your PR review comments one at a time instead." Two different behaviors triggered by the presence/absence of an argument is a small thing to hold, and I had to reread it to be sure I had the mapping right — first read I expected `/rn:gm` alone to mean "reject the whole thing," not "start walking comments."
- "Those same two words answer every later sign-off, so there is never a moment where you have to work out how to reply." — this is a claim ("never a moment") stated with more confidence than the rest of the doc earns, especially right after telling me plain `/rn:gm` behaves differently depending on context — that's already a small "which mode am I in" moment for the reader.
- The closing section "What stays yours" restates content already given ("approving the plan," "weighing in," confirming at the end) — I had read all three already in section 2 and 3, so this read as a summary rather than new information, though it's short enough that it didn't cost much.

4. What I didn't need:
- The mermaid diagram, for me as a first-time reader deciding whether to install: it duplicates what the prose right above and below it already states (approve plan → run task → expert does it off-screen → sometimes you weigh in → confirm at end). It probably serves someone skimming visually or someone who wants the control-flow shape at a glance rather than reading prose — not me, since I read straight through and got the same information twice in a row.
- The console transcript example (`> /rn:up` ... `Resuming from #2`) is mostly reassurance/flavor rather than decision-relevant — it doesn't tell me anything about reconciliation logic I couldn't already infer from the prose sentence just above it ("finds the suspended session, reconciles it against the git log"). It serves someone who wants to see the UI/tone before installing, not someone deciding on capability.
- The final "What stays yours" section, as I noted, repeats material — it serves as a closing reassurance/memory aid for someone who already decided to install, not someone still deciding.
