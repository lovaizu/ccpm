# Check: writ/docs/verification.md

Target: writ/docs/verification.md
Receiver and purpose: whoever runs the checks again after a change to writ, who runs them and sees whether each criterion (A1, M1, M2 in .rn/20261006-writ-first-user-saved-output/steering.md) still holds.
Aim: a maintainer running scene A1 as written gets a run that shows A1: the first user runs `python3 print_log.py` with nothing added so Claude Code saves its output; the first user is not blocked from running it by a permission prompt; the failed entries and reasons cannot be learned from the script's source, only from its output; and the machine checks' coverage line claims no criterion, only that every line is run. The Goods of 05-report-verification-fix.md are kept. The hook that lets the first user read its own saved output and the A1 trial are not built yet (steering.md "Not yet specified"), so a stop by the current hook on the saved path is expected and is not what is checked.

## design.md: Reading the README as the product's user, what did you take as what the product does for you once the goal is achieved?

Report: (kept from 03-report-design-fix.md, not rechecked) From the work I understood this: the README does not change for this goal and says nothing about saved output, hooks, or `.claude/projects`. What it promises that this goal touches is at `writ/README.md:46` ("Before returning the document, writ has a first user use it ... reports what it took in and what it set out to do") and `writ/README.md:145` ("The first user actually gives the prompt to an AI and runs it ... It does not judge; it reports what happened"). As the user, I took it that the first user's report rests on what really happened in use; nothing in the README tells me that a long output would be hidden from it today, nor that it will be readable after. The user-facing gain of A1 (a report that quotes the whole output, without a detour) is visible only in the design document (`writ/docs/design.md:82`) and the verification document (`writ/docs/verification.md:28-42`), not in the README.

- Good: `writ/docs/verification.md:46-50` The writ user sees the gain of A1 in use: the first user's report quotes the whole long output, without running the work again another way.
  - Evidence (work): "report names the three failed entries, quoting the saved output, without the first user running"

## design.md: Taking each scene of the verification document as the user it stands for, what of why they would choose the product would its pass show, and which scene or input showed nothing another did not?

Report: (rechecked) **What I did**

I followed writ/docs/verification.md for scene A1:

1. **Repository.** I made a fresh git repository outside the ccpm repository, at `/private/tmp/claude-501/writ-a1-h8Nr88`.
2. **The script.** I wrote `print_log.py` as the scene describes at verification.md:34-38. It prints 40,000 lines, `entry <n>: ok` or `entry <n>: FAILED: <reason>`. A fixed seed (`random.Random(20261006)`) picks three failed entries from 30001-40000. Each reason is built at run time from two word lists plus a retry count.
3. **The answer.** I ran the script myself first, as the doc says the maintainer does ("the maintainer learns it by running the script"): entry 31333: FAILED: lock went missing after 5 retries; entry 34696: FAILED: cache went missing after 2 retries; entry 38107: FAILED: socket timed out after 5 retries. The output was 629,011 bytes.
4. **The essentials file.** I wrote `essentials.md` with the one question given at verification.md:39-41.
5. **The start line.** First I used the start line from verification.md:12, `claude -p --plugin-dir <writ> --permission-mode bypassPermissions` (Claude Code 2.1.291). My own environment did not let me run it: "Permission for this action was denied by the Claude Code auto mode classifier. Reason: [Create Unsafe Agents]". I then ran the same command with `--permission-mode auto`, the mode the existing `dev/writ/trials/run.py:39` uses. So the run below did not use the doc's permission mode.
6. **Starting the agent.** No A1 trial exists in `dev/writ/trials/` yet (it holds only `fixture`, `roles`, `run.py`, `scenes.py`). Following verification.md:20-22, I told the top-level session to start `writ:first-user` with the Agent tool. It handed over the four items: work, receiver and purpose, essentials file, language.

**What happened**

1. **Read the work.** It ran `ls -la && cat -n essentials.md && cat -n print_log.py`, which was allowed. It read the source and reported that the source does not give the answer: "What I don't know: the entry numbers of the 3 failures and their reason text. From the source alone, each reason has the form `<disk|socket|...> <timed out|was corrupted|...> after N retries` (`print_log.py:10`). I never saw the actual values in output."
2. **Ran the script.** It ran `python3 print_log.py`, which was allowed. Claude Code saved the output. The tool result read: "Output too large (614.3KB). Full output saved to: /Users/kiyo/.claude/projects/-private-tmp-claude-501-writ-a1-h8Nr88/4045b290-b4a6-4dbd-ba0c-e984faf748ee/tool-results/beifklvwi.txt". It was followed by a 2KB preview that ended around entry 150, with no FAILED line in it.
3. **Tried to read the saved file and was blocked.** Its command was a Bash call on that path (`wc -l`, `grep -n FAILED`, `tail -n 2`). writ's PreToolUse hook (`writ/hooks/pretooluse.py`) stopped it: "writ: the first user does not read how the work was made (git history or Claude Code conversation records); use the work as it is." It did not try Read or Grep on the path.
4. **Checked the working tree.** It ran `git status --short`, which was allowed.
5. **Delivered its report.** It did not run the script again in any other way. Its reason: "I did not re-run the script with a filter such as `| grep FAILED` or `| tail`, because the question says 'with nothing added to the command'. That left me no permitted way to see past the first 150 of the 40000 lines." Its report's answer: "I could not tell from the run which entries failed or what the log says about them. I stopped at that point." It named none of the three entries.

**Against the scene** (verification.md:46-50): the output was saved; the first user did try to read the saved file by Bash on its path; writ's hook stopped the read; the report named no failed entries; it did not run the script again. This run does not meet the "nothing about A1" rerun condition at verification.md:49-50.

**What I could not answer from this one run.** Only scene A1 exists in the doc (verification.md:30-50), so I could not compare scenes to find one that showed nothing another did not. I did not run the machine-check tests, because the hook they test is not built in this branch.

Earlier report, kept from 05-report-verification-fix.md for the Goods carried over:

**What I read**
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

- Good: `writ/docs/verification.md:39-44` Run as the scene's question says, the first user ran the script plainly and Claude Code saved its output, so the maintainer's run reaches the moment A1 is about, and the first user did not detour to a pipe after the stop.
  - Evidence (report): "It ran `python3 print_log.py`, which was allowed. Claude Code saved the output."
- Good: `writ/docs/verification.md:34-38` The first user read the script's source and still could not answer from it, so a correct report can only come from reading the output.
  - Evidence (report): "What I don't know: the entry numbers of the 3 failures and their reason text."
- Good: `writ/docs/verification.md:73` The maintainer reads the coverage line as what it shows, that every line is run, with no criterion claimed by it.
  - Evidence (work): "Every line of writ is run by the tests, as `coverage report` shows."
- Good: `writ/docs/verification.md:62-71` The maintainer is shown every M1 rule of design.md:82 one by one, including that a path only typed or printed is stopped and that a path written with `~` or `..` is compared as the same file in both directions.
  - Evidence (report): "These match one by one the cases in design.md:82."
- Good: `writ/docs/verification.md:64` A maintainer sees that the first user's own saved output still opens when its path is spelled another way, so the M1 stops are not bought by blocking the first user's own read.
  - Evidence (work): "The first user's own saved output is let through when its path is written with `~` or `..`."
- Good: `writ/docs/verification.md:67-69` A maintainer sees that a path the first user only typed or printed does not open a file, so another agent's output found with a command stays closed.
  - Evidence (work): "in a call or a command printed it, not because Claude Code recorded it as saved output, is"
- Good: `writ/docs/verification.md:61` The machine check of the let-through covers every tool the scene allows, Grep included.
  - Evidence (work): "A1: The first user's own saved output is let through, by Read, by Grep and by Bash."
- Good: `writ/docs/verification.md:34-38` The scene's input does put the first user where A1 matters: the output is saved, and the failed entries lie past what is shown inline.
  - Evidence (report): "It was followed by a 2KB preview that ended around entry 150, with no FAILED line in it."
- More: `writ/docs/verification.md:11-15` A maintainer starting the run from a Claude Code session in auto mode has the start line as written refused, so it falls back to another permission mode, and whether the written line lets the first user run the script without a prompt stays unshown.
  - Evidence (report): "My own environment did not let me run it"
- More: `writ/docs/verification.md:49-50` The maintainer is not told how many times to rerun the scene when the first user pipes the output and nothing is saved.
  - Evidence (report): "that run would not count"
  - Left because: not among the points to fix, and the maintainer can still carry the scene through, since the scene says the run showed nothing and to run it again.
