── split-pith: make pith the one place to check work, with writ and rn on it ──
👉 #1 Plan sign-off ── read it on the PR: /rn:ty to approve, /rn:gm <feedback> to ask for changes
⬜ #2 Design sign-off

Draft PR: https://github.com/lovaizu/ccpm/pull/40

Next, once approved: work out the design with you, starting from what the plan leaves open (how writ
and rn reach pith, who writes the result file and its form, which of rn's parts move to pith), and
first try, on a throwaway pair of plugins, whether a plugin can call a dependency's skill and start
its agents, since the whole design rests on it.

Goal: Make pith the one place where work is checked by having it used (the first user, the comparison
with the aim, the result file's form), while each caller keeps the viewpoints for its own kinds of
work, split out of writ into a plugin of its own (issue #35), with writ and rn both checking through
it. Today the same skeleton (a first user who does not know how the work was made, viewpoint files,
Good and More against the aim) lives in writ as pith and again inside rn, and the two grow apart; with
one home, an improvement to how work is checked is made once and reaches both, and anyone can check
any work by use without installing a plugin for writing documents.
Judged by:
- A1: Installing pith alone, without writ, gives `/pith:up`, which checks any work (a document, a
  prompt, code, tests) by a first user's use, first writing the viewpoints for a kind of work that has
  none, such as code or tests.
- A2: writ and rn both check their work through pith, so a change to how work is checked is made in
  pith once and reaches both.
- M1: `/writ:up`'s golden paths (writing a new document, fixing an existing one) give no less than
  before.
- M2: An rn session's golden path (plan, design, tasks, deliverable, each checked before its sign-off)
  gives no less than before.
- M3: Whoever calls `/writ:pith` today finds the same check as `/pith:up`, installed with writ.
- M4: No copy of pith's parts remains in writ or rn, and each part they share has exactly one home.
- M5: Each plugin keeps `.claude/rules/plugin.md`: tests that run every line in CI, trials, a README
  stating Python 3.9 or later, a CHANGELOG entry, both `claude plugin validate --strict` runs passing,
  and a listing in `.claude-plugin/marketplace.json` and the root `README.md`.

Toward what you would choose it for:
- A1: planned only; nothing is built yet (first proposal)
- A2: planned only; nothing is built yet (first proposal)

Taken away: `/writ:pith`, replaced by `/pith:up` (M3).

### Why you want it
- Good goal: the reason (two copies growing apart; checking without writ) is read as meant, at steering.md:14-20

### What you gain
- Good A1: checking any work without installing writ, at steering.md:26-28
- Good A2: one change to checking reaches both writ and rn, at steering.md:29-30
- More A1, A2: their gains are worded by me from our conversation, not in your own words; approving
  the plan approves them as written, at steering.md:26-31
- More A2: whether a plugin can call a dependency's skill and start its agents is not yet known; the
  docs name it but do not show how (Assumption, steering.md:53-54); the design starts by trying it

### What this session also does
- Good goal: issue #37 (pith run about three times per `/writ:up`) is closed by applying the plugin
  rules to every check through pith, at steering.md:67-70
