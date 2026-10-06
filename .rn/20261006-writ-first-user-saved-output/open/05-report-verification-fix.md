# Check: writ/docs/verification.md

Target: writ/docs/verification.md
Receiver and purpose: whoever runs the checks again after a change to writ, who runs them and sees whether each criterion (A1, M1, M2 in .rn/20261006-writ-first-user-saved-output/steering.md) still holds.
Aim: a maintainer rerunning the machine checks is shown that every rule M1 rests on in writ/docs/design.md:82 holds, including that a path the first user only typed or printed into its own conversation record is stopped, and that a path written with `~` or `..` is compared as the same file (its own let through, another's stopped); the Goods of the last check are kept. The hook and tests are planned to be built after design sign-off (steering.md "Not yet specified"); the document describes what the tests will check.

## design.md: Reading the README as the product's user, what did you take as what the product does for you once the goal is achieved?

Report: (kept from 03-report-design-fix.md, not rechecked) From the work I understood this: the README does not change for this goal and says nothing about saved output, hooks, or `.claude/projects`. What it promises that this goal touches is at `writ/README.md:46` ("Before returning the document, writ has a first user use it ... reports what it took in and what it set out to do") and `writ/README.md:145` ("The first user actually gives the prompt to an AI and runs it ... It does not judge; it reports what happened"). As the user, I took it that the first user's report rests on what really happened in use; nothing in the README tells me that a long output would be hidden from it today, nor that it will be readable after. The user-facing gain of A1 (a report that quotes the whole output, without a detour) is visible only in the design document (`writ/docs/design.md:82`) and the verification document (`writ/docs/verification.md:28-42`), not in the README.

- Good: `writ/docs/verification.md:38-42` The writ user sees the gain of A1 in use: the first user's report quotes the whole long output, without running the work again another way.
  - Evidence (work): "report names the three failed entries, quoting the saved output, without the first user running"

## design.md: Taking each scene of the verification document as the user it stands for, what of why they would choose the product would its pass show, and which scene or input showed nothing another did not?

Report: **What I read**
- writ/docs/verification.md, the whole file.
- The steering file's criteria: A1, M1 and M2 (.rn/20261006-writ-first-user-saved-output/steering.md:23-31).
- The README's benefits (writ/README.md:3-15).
- writ/docs/design.md:80-82 and 454-458.

**Scene A1: who it stands for and what a pass would show**
- The one scene (writ/docs/verification.md:28) stands for a writ first user that runs the work and gets output too long to show.
- It passes when the first user "reads that saved file by Read, Grep or Bash on its path, writ's hook does not stop the read, and the report names the three failed entries, quoting the saved output, without the first user running the script again to see its output another way" (verification.md:38-41).
- From that I took that a pass would show A1: the first user sees the whole of what its own call returned, with no detour.
- I tied it to the README benefit "You check what you made by what happened when it was used as its user would use it" (README.md:14). That link is mine; the scene does not name a README benefit, and its heading repeats steering A1 word for word.

**Whether the input puts the user where the benefit matters.** I rebuilt the scene's input in a scratch directory. I wrote my own `print_log.py` from the description, because the document does not give its source.
- Output size: `628965` bytes. The three FAILED lines are lines 31207, 35880 and 39114.
- With plain `claude -p` on Claude Code 2.1.291, told to run the script with no pipes, the first tool result read:
  `<persisted-output>`
  `Output too large (614.2KB). Full output saved to: /Users/kiyo/.claude/projects/.../tool-results/bvevlzuy2.txt`
  The agent said it "showed me only the first 2KB". It then found the three entries by Grep on that saved path.
- So the input does make Claude Code save the output, and the failed entries are not in the part shown inline.

**Runs where the input showed nothing about A1**
- **Plain `claude -p`, told nothing about how to run it.** I gave it only the work, the receiver and the question. It read `print_log.py` first, then ran `python3 print_log.py | grep -v ': ok$'`. Nothing was saved. By verification.md:41-42 ("If the output was not saved ... the run showed nothing about A1; run it again"), that run would not count.
- **The real `writ:first-user` from this branch** (`claude -p --plugin-dir <worktree>/writ`, started through the main agent, given the four inputs from verification.md:17-18):
  - Its three tries were a redirect to a /tmp file plus `head`/`grep`, then `python3 ... | grep -n FAILED`, then `python3 print_log.py`. All three were blocked by the permission system: "This command requires approval".
  - It then answered from the source: "`print_log.py:1` holds the failure data: `fails = {31207: ...}`".
  - verification.md:7-12 sets no permission mode or allowed tools, and I found nothing there about this.
  - Because my `print_log.py` holds the reasons in its source, reading the source alone gave the right answer without running anything. verification.md:30-32 does not say whether the reasons may be visible in the source.
- **Overall:** in my runs, two of the three ways the agent chose to start (a pipe and a redirect) would leave nothing saved. Only the run where I said "no pipes" reached the saved file.

**Machine checks (verification.md:53-65)**
- **A1 (line 53):** "let through, by Read, by Grep and by Bash". This is the hook's let-through rule, the same read step the scene asks for at line 39. It does not involve a report or a detour.
- **M1 (lines 54-63).** Six items:
  - another agent's saved output, including through `~` or `..`;
  - the first user's own saved output through `~` or `..` (let through);
  - a conversation record;
  - a path beside its own saved output, including a folder;
  - a path only typed or printed;
  - a record that cannot be found or read.
  These match one by one the cases in design.md:82. Together they are the M1 criterion (steering:28-30).
- **M2 (line 64):** "Agents other than `writ:first-user` are not checked." A test of this kind already exists: `test_other_agents_reading_history_or_records_pass` (dev/writ/tests/test_pretooluse.py:110).
- **Coverage (line 65):** labelled "A1, M1, M2". It checks line coverage, not any one criterion.
- **Overlaps I found:**
  - The `~`/`..` let-through item at line 56 sits under M1 but is a let-through case, the same direction as the A1 item at line 53.
  - The A1 machine item (line 53) and scene step "writ's hook does not stop the read" (line 39) cover the same thing. The scene adds the report's content and the no-detour condition.
- **Status:** I did not run the tests. The doc says the hook and tests are not built yet (steering:66-69), and `writ/hooks/checks/` holds only `first_user_history.py` and `foreground_agents.py`.

- Good: `writ/docs/verification.md:54-61` The maintainer is shown every M1 rule of design.md:82 one by one, including that a path only typed or printed is stopped and that a path written with `~` or `..` is compared as the same file in both directions.
  - Evidence (report): "These match one by one the cases in design.md:82."
- Good: `writ/docs/verification.md:56` A maintainer sees that the first user's own saved output still opens when its path is spelled another way, so the M1 stops are not bought by blocking the first user's own read.
  - Evidence (work): "The first user's own saved output is let through when its path is written with `~` or `..`."
- Good: `writ/docs/verification.md:59-61` A maintainer sees that a path the first user only typed or printed does not open a file, so another agent's output found with a command stays closed.
  - Evidence (work): "in a call or a command printed it, not because Claude Code recorded it as saved output, is"
- Good: `writ/docs/verification.md:53` The machine check of the let-through covers every tool the scene allows, Grep included.
  - Evidence (work): "A1: The first user's own saved output is let through, by Read, by Grep and by Bash."
- Good: `writ/docs/verification.md:30-32` The scene's input does put the first user where A1 matters: the output is saved, and the failed entries lie past what is shown inline.
  - Evidence (report): "So the input does make Claude Code save the output, and the failed entries are not in the part shown inline."
- More: `writ/docs/verification.md:30-36` Left to choose how to run the script, the first user piped or redirected the output in two of three starts, so nothing was saved and the maintainer's run showed nothing about A1.
  - Evidence (report): "in my runs, two of the three ways the agent chose to start (a pipe and a redirect) would leave nothing saved"
  - Left because: outside the one point the caller handed over (.rn/20261006-writ-first-user-saved-output/open/04-notes-design.md), and the caller limited the change to that point; for the caller (rn) to decide.
- More: `writ/docs/verification.md:9-12` The maintainer is not told what permission to start the first user with; started as written, the real `writ:first-user` had every run of the script blocked and never reached a saved file.
  - Evidence (report): "verification.md:7-12 sets no permission mode or allowed tools, and I found nothing there about this."
  - Left because: outside the one point the caller handed over (.rn/20261006-writ-first-user-saved-output/open/04-notes-design.md), and the caller limited the change to that point; for the caller (rn) to decide.
- More: `writ/docs/verification.md:30-32` The maintainer writing `print_log.py` is not told whether the failure reasons may sit in its source; where they do, the first user answers from the source and the run shows nothing about A1.
  - Evidence (report): "verification.md:30-32 does not say whether the reasons may be visible in the source."
  - Left because: outside the one point the caller handed over (.rn/20261006-writ-first-user-saved-output/open/04-notes-design.md), and the caller limited the change to that point; for the caller (rn) to decide.
- More: `writ/docs/verification.md:65` The line is labelled with the three criteria, but what it shows is that every line is run, not that any criterion holds.
  - Evidence (report): "It checks line coverage, not any one criterion."
  - Left because: outside the one point the caller handed over (.rn/20261006-writ-first-user-saved-output/open/04-notes-design.md), and the caller limited the change to that point; for the caller (rn) to decide.
- More: `writ/docs/verification.md:41-42` The maintainer is not told how many times to rerun the scene when the first user pipes the output and nothing is saved.
  - Evidence (report): "that run would not count"
  - Left because: not among the points to fix, and the maintainer can still carry the scene through, since the scene says the run showed nothing and to run it again.
