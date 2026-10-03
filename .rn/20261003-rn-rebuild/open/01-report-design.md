# First user report: the design (README, design document, verification document)

Read at commit `91c525bd4a0d1e4b66831e0e9e850de9ca5541d1`: `rn/README.md`, `rn/docs/design.md`,
`rn/docs/verification.md`. Also looked at: the practice repository `lovaizu/rn-try` (its README,
`src/cart/cart.ts`, the branch list, the pull request list, and the front matter of the
`steering.md` on `main`, `island-delivery-fee`, `rn/free-shipping-j`, `rn/lower-overseas-shipping`,
and `rn/reject-over-100-percent-coupons`), and `rn/.claude-plugin/plugin.json` and the top of
`rn/CHANGELOG.md`. Not looked at: commit messages, git log, anything under this repository's `.rn/`
other than writing this file, `rn/skills/` and `rn/references/` other than
`rn/references/essentials/design.md`. `rn/agents/` and `rn/hooks/` do not exist at this commit.
Whether `omitClaudeMd` is a field Claude Code accepts in an agent definition, and what `agent_type`
a hook receives, I did not check against the Claude Code documentation.

## 1. Following the README's use step by step against the design document, which step did the design give no way to take?

Steps 1 (Start), 3 (Work out the design), 4 (Build and check), 6 (Finish), and Install: doing as
written, for each step I found the section that takes it (design: "Hearing what the user really
wants", "The pull request", "The design and the verification document", "Each result is used once
and settled by the conductor", "It installs from the marketplace with writ"). Two steps ran into the
hook checks:

- README "2. Approve or give feedback — `/rn:ty` and `/rn:gm`": "`/rn:gm <feedback>` asks for
  changes ... Either one stops there." Doing as written: design "Feedback at a sign-off" puts the
  feedback whole into a `feedback` item in `open/`, and the plan or design is worked out again
  after it. Design "It calls the user only for decisions that are theirs" says giving feedback
  stops, and "Who does what" calls the commit where `rn` stops for the user the stop commit. Hook
  check 6 (design "Hooks check rn's rules as it goes") requires a stop commit to leave `open/`
  holding only design points waiting for `writ`, and its decision line to end `waiting for #N …`.
  At the stop after `/rn:gm`, the `feedback` item is still in `open/` (it is settled only by the
  rework that follows "go on"), so the stop commit after `/rn:gm` is one check 6 stops. I found no
  place that says the stop after `/rn:gm` is not a stop commit, or what its decision line ends with.

- README "5. Pause and resume — `/rn:dn`, `/rn:up`": the console shows `/rn:dn` ending with
  "👉 #4 move src/checkout ── stopped here; next: /rn:up". Doing as written: design "open/ and the
  record in commit messages" says `/rn:dn` commits an unfinished task's edits beside its notes, and
  the diagram in "Everything decided is pushed" has the conductor write "what /rn:dn leaves" into
  `open/` as notes. That commit is where `rn` stops for the user, so it is a stop commit, and hook
  check 6 again requires `open/` to hold only design points waiting for `writ` and the decision line
  to end `waiting for #N …`. The `/rn:dn` notes, and any report of the unfinished task not yet
  settled, are still in `open/`, and the README's line says "stopped here; next: /rn:up", not
  "waiting for". I found no way given for `/rn:dn` to stop that check 6 lets through, and no form
  given for `/rn:dn`'s decision line, which `/rn:up` reads by `●`, `──`, `→`, and `waiting for`
  (design "open/ and the record in commit messages").

- README "2." plain `/rn:gm`: "takes your review comments on the pull request as feedback". Design
  "Feedback at a sign-off" says "the review comments they wrote on the pull request for that
  sign-off". From the work I understood that only comments for the current sign-off are taken, but I
  found no place that says how comments for this sign-off are told apart from earlier ones on the
  same pull request.

## 2. Tracing each acceptance criterion through the design document, which criterion did no feature make hold?

From the work I understood this: the diagram in design "The features that give them" ties every
criterion A1–A4 and M1–M7 to at least one feature, and each feature section opens with "Gives …"
matching the diagram. Following each into its section:

- A1 (features 1 and 3), A2 (features 2 and 3), A3 (feature 4), A4 (feature 5), M1 ("The pull
  request"), M2 (decision line, hook checks 4 and 8), M3 (hook check 5 and the settled-report
  form), M7 ("It installs from the marketplace with writ"): each has a section that says how it
  holds.
- M4: "`steering.md`, `open/`, and the verification document keep the form every command reads them
  by". The design gives the form of `steering.md` ("steering.md holds the goal and the plan in one
  place", hook check 1) and the file names in `open/` (hook check 2). For the verification document
  I found what it holds (design "The design and the verification document") but not the form a
  command reads it by, and hook check 3 checks only that every acceptance criterion has a check in
  it. The form of an `open/` file's content (beyond its name) is also not given; the settled-report
  example in "open/ and the record in commit messages" shows the commit message, not the file.
- M5: "A sign-off is passed only by the user's approval". Hook check 7: "A sign-off is marked `[x]`
  ... only in a commit approving it." Only the conductor commits (policy "Only the conductor uses
  git"), and I found no place that says how a hook tells that a commit approves a sign-off, or that
  the user, not the conductor, gave that approval.
- M6: features 3 and 6. Design "Keeping the first user apart, by how it is defined" states the hooks
  hold only for Claude Code's file tools and that reads through the shell (such as `git log`) are not
  stopped; what holds the rest is that the first user is given no path to the maker's account. From
  the work I understood M6 is held for the shell by what the first user is handed, not by a check.

## 3. Building the `open/` and report flow as a generator would, what did you have to decide that is the user's to decide?

Doing as written, tracing who writes, who reads, and when an item leaves `open/` (design "open/ and
the record in commit messages", "Each result is used once and settled by the conductor", the diagram
in "Everything decided is pushed", hook checks 2, 5, 6, 10, 11):

- Writes: a first user writes a `report` to the file the conductor names; `writ` writes a `report`
  on how the documents read; the user's `/rn:gm` feedback becomes a `feedback` item (the diagram
  shows the user writing it; I took the conductor as the one who writes the file, since the user
  only types the command); the conductor writes `notes` (design points agreed, and what `/rn:dn`
  leaves).
- Reads: the conductor reads the short result and the file; the user reads the committed report on
  the pull request; `/rn:up` reads `open/`; `writ` reads design-point notes.
- Leaves: in the commit that settles it, copied whole into that commit's message.

What I had to decide, finding nothing that decides it:

- When a task's first report leaves `open/`. The example "rn: settle the report on #3 move src/cart"
  carries one report and a More "→ fixed: typed the quantity as number", with the decision
  "purpose fulfilled → #4". So the first report stays in `open/` through the fix and the fresh first
  user's check of that viewpoint. Whether that later one-viewpoint report is its own file (design:
  "one for each use it asks for, such as task #3's result, or one viewpoint of it after a fix") or
  the same file written anew ("Asking for the same use again writes the same file anew"), and
  whether it is copied into the same settle commit, I had to choose.
- "the conductor takes the earlier one, already in git, out of the file first": the earlier report
  is then removed from `open/` without being settled, and hook check 5 asks that a settled item's
  text be whole in the commit message. I had to choose whether that removal is a settling (and its
  text goes into that commit's message) or not (and its text is in no commit message, only in the
  earlier commit that added it).
- How the `{NN}` number is chosen once items have left: whether it keeps counting for the session or
  starts again from what is in `open/`.
- Which file is the first user's "own report file" for hook check 10. The conductor names the path
  in its call; the design says a hook tells agents apart by `agent_type`, and I found nothing that
  gives the hook the named path. I had to choose between "any `NN-report-*.md` in `open/`" and some
  way of passing the path.
- The language of a `feedback` item and of its settle commit. Design "Feedback at a sign-off": the
  feedback "is kept whole", "measured by the user's own words". Design "steering.md holds the goal
  and the plan in one place": `artifact-language` is for "everything written to the repository, the
  record and commits included". With `conversation-language: Japanese` and `artifact-language:
  English` (the design's own example), the user's words cannot be both whole and in English. Which
  language the record keeps is a choice the user made at the start; the two rules give different
  answers.
- Whether the report the conductor "commits ... as it arrives" sits in `open/` at a sign-off stop.
  "every report and feedback is settled before the user approves" says no; I took it that all
  reports from the design's use are settled before the Design sign-off stop commit.

## 4. Taking each scene of the verification document as the one who must pass it, how could you pass it with a product that misses its criterion?

From the work I understood this, scene by scene (`rn/docs/verification.md`, "Golden-path scenes"
and "Machine checks"):

- A1, first scene: the scene names no goal and no reason. As the one who must pass, I choose the
  rough goal and what the stand-in knows, and also name "what each difference prevents". A product
  that rewrites the first words without reaching the stand-in's reason still passes if the
  differences I name are ones I can explain.
- A1, second scene: the feedback and the "deeper mismatch" are not given. I choose both after the
  plan exists, so I can choose a mismatch the next plan already fixes.
- A1, third scene: "with criteria that name only percent coupons over 100%". Run from `/rn:on`, the
  hearing (A1's first scene) may already write negative coupons into the criteria, and then the case
  is named by the letter and the scene no longer tests it. The scene does not say how the session
  reaches the Deliverable sign-off with those narrow criteria. "handles that case" is not given a
  result; A2's second scene says either refusing the order or full price can be the user's answer, so
  any behavior other than raising the total passes. In `lovaizu/rn-try`, `src/cart/cart.ts`
  `applyCoupon` does raise the total for `{ percent: -10 }` (`total * (1 - coupon.percent / 100)`)
  and for `{ amount: -300 }` (`Math.max(0, total - coupon.amount)`), as the scene says.
- A2, first scene: it passes when every call is a sign-off or a question only the user can decide.
  A product that decides the user's questions itself and calls only at sign-offs passes this scene.
  Only the second scene's one question (refuse or full price) checks that a user's decision reaches
  the user.
- A3: "every Good and More holds at its place". A proposal that leaves out a real shortfall, with
  every listed Good and More holding, passes as long as the yes/no comes out right; the scene does
  not ask whether a More is missing.
- A4, first scene: "starts from the same task, does not redo finished ones". A product that
  restarts the interrupted task from nothing, dropping the edits `/rn:dn` committed, passes;
  "from where it stopped" inside the task is not checked.
- A4, second scene: "the stand-in decides from what it gives as from the first proposal". A
  stand-in that says yes both times passes regardless of what `/rn:up` gives.
- A4, third scene: "`/rn:up` on a session paused under `rn` 0.8.0". In `lovaizu/rn-try` I found no
  session marked 0.8.0: the five `steering.md` files I read on `main` and four branches all have
  `rn: 0.9.0` (the version `rn/.claude-plugin/plugin.json` has now), while their front matter
  differs from the design's (one has `ux:`, none has `verification`, `artifact-language`, or
  `conversation-language`). The design ("steering.md holds the goal and the plan in one place")
  says the `rn` field tells an older session. As the one who must pass, I would have to make the
  0.8.0 session myself, and the sessions already there, marked 0.9.0 in an older form, are not
  covered by the scene.
- Machine checks, M1 row: "The practice repository's default branch holds no commit a run made".
  `main` of `lovaizu/rn-try` already holds `.rn/20260929-typescript-migration/steering.md` with
  `status: finished`, from an earlier session merged into it. The row gives no way to tell a commit
  a run made from one the user merged, so it passes or fails by how I choose to tell them apart.
- Machine checks, M6 row: it checks reads only through Claude Code's file tools, as it says; a first
  user that reads `git log` through the shell passes it.
- Machine checks, M4 row: hook checks 1 to 3 check the form of `steering.md` and the names in
  `open/`; a verification document whose form a command cannot read passes as long as each
  criterion ID appears in it.
