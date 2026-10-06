# First user report: the Design sign-off proposal

Viewpoint: `rn/0.9.0/references/essentials/conductor.md`, "Proposal".

What I read and used: the proposal `open/01-notes-proposal.md`; `steering.md`; `writ/docs/design.md:76-82`;
`writ/docs/verification.md` (whole); today's `writ/hooks/hooks.json`, `writ/hooks/checks/first_user_history.py`,
`writ/agents/first-user.md:28-42`; the listing of `dev/writ/trials/`; the PR's state and head
(`gh pr view 42`: OPEN, draft, head `c26de1d`, the same as the local HEAD). I built the A1 scene as
`verification.md:36-46` describes, outside the repository, and ran it against today's writ (details
under question 3).

What I did not look at: commit messages, git history or diffs, the PR's conversation, earlier reports,
the rest of `design.md`, and `dev/writ/tests/`. The repository is unchanged but for this file.

## Deciding as the user whether the work has come close enough, what did you learn of how far it now gives each thing you would choose it for, and of what came closer since the last proposal?

From the work I understood this. The proposal's "Toward what you would choose it for" has one line, for
A1 (`01-notes-proposal.md`, the line beginning "- A1: on paper, fully"): the design lets the first user
read its own saved output by any reading tool, nothing is built yet, and the A1 scene reproduces #36
today, so after the build it will show the result. It names only A1; M1 and M2 appear only as Goods
further down. From it I learned that A1 is designed but not yet usable, and that whether it holds is
deferred to the build (the More A1 says the same).

On "what came closer since the last proposal": the proposal says "(first proposal of the design)" and
"Changed since the last approval: none". I read "none" as meaning nothing changed in the goal or
criteria since the Plan sign-off, but the line does not say what "changed" refers to, while the design
itself is what is new at this sign-off; I could not tell from the proposal which of the two it meant.

## Deciding yes or no as the user, what beyond the proposal did you need?

From the work I understood this. The proposal's first paragraph says what approval leads to (plan and
build the hook, its unittest cases, the A1 trial, a line in the first user's definition, the CHANGELOG
entry) and why (it closes #36 without opening Claude Code's records, and the scene already reproduces
#36). That was enough to know the move.

What I went outside it for:
- To trust the Goods I had to open `design.md:82` and `verification.md`; the proposal gives the places
  but not a record of the run in "run against today's writ, the first user tried to read the saved file
  and was stopped" (Good A1 under "How you will see it works"). No path to that run's record or report
  is given, so I ran the scene myself to see it.
- The #36 stop happened on a Bash call. `design.md:82` says "The path in the call is compared with the
  recorded one" and "The hook stops a call that names any other path there ... whatever the tool", but
  neither the design nor the proposal says how a path is picked out of a Bash command string. In my run
  the first user's stopped command was
  `F=/Users/kiyo/.claude/projects/.../tool-results/bx9ao7a7u.txt; wc -l $F; grep -n FAILED $F; ...; cd /private/tmp/.../a1run && git status --short`
  (one path under `.claude/projects` assigned to a variable, plus another path outside it). I could not
  tell from the design whether such a command would be let through.

## Using the work where each Good was found, what happened that differs from the Good?

Doing as written, this happened.

The places:
- Good A1 (read by Read, Grep or Bash): `design.md:82` says "the first user then reads its own output as
  it reads anything else"; `verification.md:63` reads "The first user's own saved output is let
  through, by Read, by Grep and by Bash." Matches.
- Good M1 (only a path Claude Code recorded opens): `design.md:82` ("A path that appears in the record
  only in other ways, typed in a tool call or printed by a command, does not count ... with `find`") and
  `verification.md:69-71`. Matches.
- Good M1 (`~` and `..`): `design.md:82` ("after `~` is expanded and both are normalized") and
  `verification.md:64-66`. Matches.
- Good M2: `design.md:80` ("the hooks stop these only when it is `writ:first-user`") and
  `verification.md:74`. Matches.
- Good A1 (the scene starts the first user as a subagent): `verification.md:19-23` and `:36-46`. Matches.
- Good M1 (every M1 rule has its own machine check, `verification.md:64-73`): the lines name checks for
  another agent's output (`:64-65`), a conversation record (`:67`), a path beside it including a folder
  (`:68`), a typed or printed path (`:69-71`), and an unreadable record (`:72-73`). Each M1 rule I found
  in `design.md:82` has one of these lines.
- "Taken away: ... the one new stop ... applies only to paths that are stopped today anyway": today's
  check stops any string argument matching `/\.claude/projects(?:/|$|[\s"'`;|&)])`
  (`writ/hooks/checks/first_user_history.py:12`, `:47-48`), and the new stop in `design.md:82` is on
  paths "under `.claude/projects`". I found nothing that differs.

Running the A1 scene against today's writ (the Good "run against today's writ, the first user tried to
read the saved file and was stopped, as in #36"): I built `print_log.py` (40,000 lines, three
`FAILED` entries after 30,000 from a fixed seed) and `essentials.md` with the question from
`verification.md:41-43` in a fresh git repository under the scratchpad, and ran, on Claude Code 2.1.291,
`claude -p --plugin-dir <worktree>/writ --permission-mode auto "<start writ:first-user with the Agent tool, handing it the work, receiver and purpose, essentials file, English>"`.
- In the first user's record `<session>/subagents/agent-a7030657b236afa09.jsonl`, line 16 ran
  `python3 print_log.py`; line 17's tool result began `<persisted-output>` and read
  "Output too large (614.2KB). Full output saved to: /Users/kiyo/.claude/projects/.../tool-results/bx9ao7a7u.txt".
- Line 22 was the Bash call reading that file; line 23 was writ's stop, "writ: the first user does not
  read how the work was made ...".
- The first user's report said it "could not find out which entries failed", and that it did not add
  `| grep FAILED` to the command because the question said "with nothing added to the command".
- This is the same as the Good: the first user tried to read the saved file and was stopped.

Two more things I saw in that record, which bear on `design.md:82` and the More A1:
- In this run too, the first user's own record quoted the saved path in the `<persisted-output>`
  wrapper (line 17) before the read was attempted (line 22), now with `writ:first-user` itself rather
  than a general-purpose subagent.
- The record holds no `persistedOutputPath` on that result: `toolUseResult` appears only once in the
  whole file, and not on line 17. `design.md:82` already says the wrapper is the form relied on.

## Deciding yes or no as the user, which parts of the proposal did you use and which did you read past?

From the work I understood this.

Used:
- the first paragraph (what approval leads to and why);
- the A1 line under "Toward what you would choose it for";
- "Taken away";
- each Good and the More with its place, under "What the first user may read" and "How you will see it
  works".

Read past:
- the "Goal:" and "Judged by:" block, which repeats `steering.md`'s Goal and criteria word for word,
  as the user agreed them at the Plan sign-off;
- the status header lines (`✅ #1`, `👉 #2`, the Draft PR link), except for the instruction
  `/rn:ty` / `/rn:gm`;
- "Changed since the last approval: none", which I could not place (see question 1).

## Conductor's Good and More

- Good A1: every Good's place holds, and the A1 scene run against today's writ reproduced #36 (first user's record line 17 saved, line 23 stopped).
- More A1: writ/docs/design.md:82 does not say how a path is picked out of a Bash command, while the call stopped in #36 put the path in a shell variable beside another path.
- More A1: writ/docs/design.md:82 still says the rule rests on one trial with a general-purpose subagent; three runs with `writ:first-user` itself on 2.1.291 now show the wrapper quoting the path before the read.
- More: the proposal's "Changed since the last approval: none" cannot be placed, and the run behind the scene's Good is not pointed to.
