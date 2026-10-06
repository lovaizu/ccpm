# Check: rn/README.md

Target: rn/README.md
Receiver and purpose: a developer using Claude Code who meets rn for the first time; they decide whether to use rn on a goal in their own repository, and install it and start a session.
Aim: From the opening the reader takes in what they gain: they get what they really want though they start from rough words; their time goes only to the decisions that are theirs, without watching over the work; at each of the three sign-offs they decide from a short proposal without re-reading the work; work that takes days goes on in a fresh conversation from where it stopped without explaining again; and other Claude Code sessions they run in the same repository keep working beside an rn session. The reader takes these as reasons to choose rn over prompting Claude Code by hand. They take in the flow as plan, design, build, each ending in a sign-off they approve or give feedback on, and that their default branch changes only when they merge. They learn only the names they need to start: the commands /rn:on, /rn:ty, /rn:gm, /rn:dn, /rn:up, and that approval can also be given in plain words. A proposal at a sign-off shows where the session is, how close each thing they would choose the work for has come, only the points they must decide, and the next move with why; the goal, criteria and the full checks are on the pull request. The reader can install rn from this README alone, with the prerequisites (Claude Code, a GitHub remote, gh logged in with push access, Python 3.9 or later) and why each is needed, and run /rn:on. When they start rn on a branch of their own that has no commits yet, rn works on that branch. They can tell what is fact from example. Decided by the user: no agent checks a question, the plan or a proposal before the user reads it; the user is its first reader.

## doc.md: Once you finished reading, what did you take it you should decide and do?

Report: What I would do: check that I have a GitHub remote, `gh` logged in with push access, and Python 3.9 or later (rn/README.md:13-17). Then run `/plugin marketplace add lovaizu/ccpm` and `/plugin install rn@ccpm` (:25-26), and in my repo type `/rn:on <rough goal>` (:85).

What I took the session to be:
- rn asks me one point at a time until we agree a plan, `steering.md`, kept on a draft PR. I approve with `/rn:ty` or ask for changes with `/rn:gm`.
- Then the same for a design document plus a verification document.
- Then it builds on its own. Before each result reaches me, a separate agent "that knows nothing of how it was made" uses it (:194-195).
- Then I approve the deliverable, the PR is marked ready, and I merge.
- `/rn:dn`, then `/clear`, then `/rn:up` pauses and resumes.

What I took I should decide: whether rn's three opening promises (:6-9) are worth it for a multi-day change. Also that rn will push to GitHub and open a draft PR from my first words: "From your first words, `rn` keeps the plan, `steering.md`, on a draft pull request" (:99), and "Every decision is pushed as it is made" (:210). And that rn will write into my own README and design docs: "What you settle goes into your README, design document, and verification document" (:181–182), and writ is installed so rn can "write your README and design document" (:29-30).

- Good: `rn/README.md:13-27` The reader comes away knowing the three things to do: check the prerequisites, run the two install commands, and run `/rn:on` with a rough goal.
  - Evidence (report): "Then run `/plugin marketplace add lovaizu/ccpm` and `/plugin install rn@ccpm` (:25-26), and in my repo type `/rn:on <rough goal>` (:85)."
- Good: `rn/README.md:36-37` The reader takes in that the default branch changes only when they merge.
  - Evidence (report): "Then I approve the deliverable, the PR is marked ready, and I merge."
- More: `rn/README.md:158-163` The reader takes `/rn:ty` as the only way to approve; that approval can also be given in plain words does not reach them.
  - Evidence (report): "I approve with `/rn:ty` or ask for changes with `/rn:gm`."
  - Evidence (work): "`/rn:ty` approves."
- More: `rn/README.md:3-9` The reader weighs only three promises; that other Claude Code sessions in the same repository keep working beside an rn session is not among what they decide on.
  - Evidence (report): "whether rn's three opening promises (:6-9) are worth it for a multi-day change"

## doc.md: Which parts did you use to decide or act, which did you skip without using, and where did you find yourself reading again what you had already read?

Report: Used:
- :3-9 to decide.
- :13-17 and :21-27 to act.
- :74-85 for the first command.
- :158-171 for approving.
- :208-231 for pausing.

Skimmed or skipped:
- Most of the sign-off example at :120-147. I stopped at "### Is the goal what you really want...", "Good A1:", "More: none" and "...", and could not use those lines.
- :254-258 (How it is built). It is aimed at someone studying rn, not me.

Read again:
- :149-156, the paragraph explaining the sign-off message. I read it twice, going back and forth to :120-147 to match "how close the work has come to each thing you would choose it for" with the block headed "Toward what you would choose it for:" (:136).
- :68-70, the diagram legend, which I reread against the diagram (see the figure question below).
- :176-179 and :235-238, which both explain the verification document. The second ("it was used as you would use it, in each scene of the verification document") repeats the first and adds the word "scene".

- Good: `rn/README.md:3-9` The opening is what the reader uses to decide, and the install and start parts are what they use to act.
  - Evidence (report): ":3-9 to decide."
- More: `rn/README.md:130-144` In the sign-off example the reader skips the goal-and-criteria list and the per-question Good/More grounds and cannot use them; the aim puts the goal, criteria and full checks on the pull request, with only the points to decide in the proposal.
  - Evidence (report): "I stopped at "### Is the goal what you really want...", "Good A1:", "More: none" and "...", and could not use those lines."
  - Evidence (work): "Then it gives its grounds: each question the plan must answer, with what is good and what falls short, and where."
- More: `rn/README.md:149-156` The reader reads the explanation of the sign-off message twice, going back and forth to the example to match its parts.
  - Evidence (report): "I read it twice, going back and forth to :120-147"
- More: `rn/README.md:235-238` The verification document is explained twice; the second time repeats the first and adds a new word.
  - Evidence (report): "repeats the first and adds the word "scene""
- More: `rn/README.md:254-258` The reader skips "How it is built" as meant for someone studying rn.
  - Evidence (report): "It is aimed at someone studying rn, not me."

## doc.md: In trying to decide or act, what was not in the document, so that you could only guess or ask someone?

Report: - **Permissions.** :194 says "You don't babysit it", but nothing says whether rn needs a permission mode in Claude Code that skips approval prompts, or whether I will be prompted for every edit, `gh` call and push. I could only guess.
- **Cost and duration.** Nothing on token use, how long a session takes, or which model it needs.
- **When `/rn:dn` is needed.** :163 says after `/rn:ty` or `/rn:gm` "You can clear the conversation at that point and lose nothing", with no `/rn:dn`. :212 says to use `/rn:dn` when context is full or at day's end. :210 says every decision is pushed already. I could not tell what I would lose if I ran `/clear` without `/rn:dn`.
- **What the command names stand for.** No expansion is given for `ty`, `gm`, `dn`, `up`. I guessed thank you / give me / down / up.
- **Branch and README details.** Nothing on which branch name rn uses, what happens if my repo has no README or no `docs/`, or where the design and verification documents are placed in my repo.
- **The `.rn/` directory.** :249 says it is left behind. Nothing says whether it should be committed or merged into the default branch.
- **What if I don't use GitHub.** Not said, except that GitHub is required (:14).
- **Uninstalling or stopping a session.** Not covered.

- Good: `rn/README.md:13-17` Each prerequisite comes with why it is needed, so the reader does not have to guess why GitHub, `gh` and Python are required.
  - Evidence (work): "since `rn` puts everything you review on a pull request"
- More: `rn/README.md:194` The reader cannot tell whether "you don't babysit it" means Claude Code's approval prompts stop, or they will be asked for every edit and push.
  - Evidence (report): "nothing says whether rn needs a permission mode in Claude Code that skips approval prompts, or whether I will be prompted for every edit, `gh` call and push. I could only guess."
- More: `rn/README.md:11-17` The reader finds nothing on cost, duration or the model needed.
  - Evidence (report): "Nothing on token use, how long a session takes, or which model it needs."
- More: `rn/README.md:162-163` The reader cannot tell when `/rn:dn` is needed, since clearing after a sign-off is said to lose nothing without it.
  - Evidence (report): "I could not tell what I would lose if I ran `/clear` without `/rn:dn`."
  - Evidence (work): "You can clear the conversation at that point and lose nothing"
- More: `rn/README.md:36-37` The reader finds nothing on which branch rn works on; the README says rn uses its own branch, while the aim has rn work on the reader's own branch when it has no commits yet.
  - Evidence (report): "Nothing on which branch name rn uses"
  - Evidence (work): "It works on its own branch and a draft pull request"
- More: `rn/README.md:181-182` The reader cannot tell what happens when their repository has no README or `docs/`, or where the design and verification documents go.
  - Evidence (report): "what happens if my repo has no README or no `docs/`, or where the design and verification documents are placed in my repo"
- More: `rn/README.md:249-252` The reader cannot tell whether `.rn/` is meant to be merged into the default branch.
  - Evidence (report): "Nothing says whether it should be committed or merged into the default branch."
- More: `rn/README.md:158-160` The reader guesses what the command names stand for.
  - Evidence (report): "I guessed thank you / give me / down / up."
- More: `rn/README.md:14` The reader finds nothing on using rn without GitHub beyond that it is required.
  - Evidence (report): "Not said, except that GitHub is required (:14)."
- More: `rn/README.md:19-27` The reader finds nothing on uninstalling rn or stopping a session.
  - Evidence (report): "Uninstalling or stopping a session.** Not covered."

## doc.md: Reading through, where did you stop, go back or look ahead, and what did you not understand there?

Report: - **:29-30**, "which `rn` has write your README and design document". I stopped here, because at that point I did not know rn writes my README. That became clear only at :181.
- **:34-37 and :68-70**, the legend. "Dotted lines", "dashed box" and "bold box" are three different styles. I went back to the mermaid source to match them (`-.->`, `stroke-dasharray`, `stroke-width: 3px`).
- **:107-113**, "Attractive quality" / "Must-be quality". I did not recognise these terms. :101 ("what would make you choose the result, and what you take for granted") is the only gloss, and I had to map which is which.
- **:117-118**, "the plan shows them as not yet specified". I looked ahead to :121-123, where the map shows only #1 and #2. Then at :219-221 tasks #3-#5 and "#6 Deliverable sign-off" appear. I went back to check where the Design sign-off sits in that numbering.
- **:141-143**, "Good A1" / "More: none". I did not understand what "Good" and "More" mean or who assigns them.
- **:146** and **:156**, "The last line is what `rn` records of where it stopped". I went back to :146 to find which line that is.
- **:162**, "Either one stops there." I did not know whether "stops" meant rn halts the session or just this step. :170 ("Say "go on", or /clear and then /rn:up.") answered it.
- **:237**, "each scene of the verification document". "Scene" is new here. :178 had said "how it will be used as you would use it".

- Good: `rn/README.md:74-97` The reader reads the start step and its example through without stopping.
  - Evidence (work): "Knowing why you want it is what shows where your first words would go wrong"
- More: `rn/README.md:29-30` The reader stops, since rn writing their README is said before they know it does.
  - Evidence (report): "I stopped here, because at that point I did not know rn writes my README. That became clear only at :181."
- More: `rn/README.md:68-70` The reader goes back to the diagram source to match three line and box styles to the legend.
  - Evidence (report): "I went back to the mermaid source to match them"
- More: `rn/README.md:107-113` The reader does not recognise "Attractive quality" and "Must-be quality" and has to map them.
  - Evidence (report): "I did not recognise these terms."
- More: `rn/README.md:117-123` The reader goes back to work out where the tasks and the Design sign-off sit in the numbering.
  - Evidence (report): "I went back to check where the Design sign-off sits in that numbering."
- More: `rn/README.md:141-143` The reader does not understand "Good" and "More" or who gives them.
  - Evidence (report): "I did not understand what "Good" and "More" mean or who assigns them."
- More: `rn/README.md:155-156` The reader goes back to find which line "the last line" is.
  - Evidence (report): "I went back to :146 to find which line that is."
- More: `rn/README.md:162` The reader cannot tell what "stops" means until the example below.
  - Evidence (report): "I did not know whether "stops" meant rn halts the session or just this step."
- More: `rn/README.md:237` "Scene" appears for the first time and stops the reader.
  - Evidence (report): ""Scene" is new here."

## doc.md: When you looked for a part to read again by its heading, under which heading did you find it, and under which did you not?

Report: Found:
- Prerequisites under "What you need" (:11).
- Install commands under "Install" (:19).
- How to resume under "5. Pause and resume — `/rn:dn`, `/rn:up`" (:208).
- Approving under "2. Approve or give feedback — `/rn:ty` and `/rn:gm`" (:158).

Not found:
- A list of all five commands in one place. They sit in the headings of steps 1, 2 and 5.
- Anything on permissions, cost or limits, under any heading.
- What the sign-off message means. That is under "1. Start — `/rn:on`" (:149-156), where I did not expect it, not under a heading of its own or under "2. Approve".

- Good: `rn/README.md:11-19` The reader finds the prerequisites and the install commands under the headings they look for.
  - Evidence (report): "Prerequisites under "What you need" (:11)."
- Good: `rn/README.md:158` The reader finds approving and resuming under the headings named for their commands.
  - Evidence (report): "Approving under "2. Approve or give feedback — `/rn:ty` and `/rn:gm`" (:158)."
- More: `rn/README.md:149-156` The reader does not find what the sign-off message means where they look for it; it sits under "1. Start".
  - Evidence (report): "where I did not expect it, not under a heading of its own or under "2. Approve""
- More: `rn/README.md:74` The reader finds no one place listing all five commands.
  - Evidence (report): "A list of all five commands in one place. They sit in the headings of steps 1, 2 and 5."

## doc.md: Where, while reading, did you have to piece together in your head who does what, what passes, and in what order?

Report: - **Two loops back from the deliverable.** From Deliverable sign-off, feedback goes either to Make or to "Work out the design" (:59-60). The text at :240 says only "`/rn:gm` has it fixed". I had to work out myself that rn, not I, picks which loop, and that I may be asked again at Design.
- **The checking step.** The order "agent uses it → reports to rn → rn compares with purpose → one-line decision" (:194-203) I built up sentence by sentence.
- **Session state.** What lives where (the PR, `steering.md`, `.rn/`, my README and docs) I assembled across :99, :181, :210 and :249.

- Good: `rn/README.md:39-66` The reader takes the whole flow from the diagram: plan, design and build, each ending in a sign-off.
  - Evidence (work): "Plan -->|approve| DesignTalk"
- More: `rn/README.md:59-60` The reader has to work out who picks which way feedback on the deliverable goes back.
  - Evidence (report): "I had to work out myself that rn, not I, picks which loop, and that I may be asked again at Design."
- More: `rn/README.md:194-203` The reader builds up the order of the checking step sentence by sentence.
  - Evidence (report): "I built up sentence by sentence."
- More: `rn/README.md:249` The reader assembles what lives where from four places.
  - Evidence (report): "I assembled across :99, :181, :210 and :249."

## doc.md: How certain did you take each statement you relied on to decide or act?

Report: I took these as fact, as stated flatly without any check or limit given:
- "what you get is what you meant" (:77)
- "lose nothing" (:163)
- "a result passes because it does its job, not because its maker says so" (:196)
- "starts where you stopped, without explaining anything again" (:210-211)

I also took the prerequisites (:13-17) and install commands (:25-26) as fact. The marketplace file and plugin.json do match them.

The TypeScript example (:72-246) I took as an illustration, not a recorded run. Nothing says which it is.

- Good: `rn/README.md:13-26` The reader takes the prerequisites and install commands as fact, and they match the repository.
  - Evidence (report): "The marketplace file and plugin.json do match them."
- Good: `rn/README.md:72` The reader takes the TypeScript example as an illustration.
  - Evidence (work): "Say your app is written in JavaScript"
- More: `rn/README.md:72` The reader is left unsure whether the example is an illustration or a recorded run.
  - Evidence (report): "Nothing says which it is."
- More: `rn/README.md:77` The reader takes the promises as fact, with nothing to show how far they hold.
  - Evidence (report): "I took these as fact, as stated flatly without any check or limit given:"

## readme.md: Having read the opening, what did you take it you would get from this product?

Report: From :3-9:
- I state a goal roughly and only make decisions.
- I get what I actually want without writing a careful prompt.
- I don't watch the work or re-read all of it to approve it.
- Multi-day work continues the next day or in a new conversation.

The opening line I took in: "All you do is decide." (:3-4)

- Good: `rn/README.md:6-9` From the opening the reader takes in what they gain: what they really want from rough words, time only on their own decisions without watching or re-reading, and multi-day work going on in a fresh conversation.
  - Evidence (report): "I get what I actually want without writing a careful prompt."
- More: `rn/README.md:6-9` The reader does not take in that other Claude Code sessions in the same repository keep working beside an rn session.
  - Evidence (report): "Multi-day work continues the next day or in a new conversation."

## readme.md: What did you take in as the reason to choose this product over what you would use instead?

Report: The alternative I had in mind was plain Claude Code prompting.

Reasons I took in:
- **(a) It finds out why I want a change.** It asks why I want the change and catches a wrong goal. In the example, "Every file ending in .ts is not enough" (:92-93, :96-97).
- **(b) An independent agent checks results.** Results are checked by an agent that did not make them, and judged against the purpose (:194-196). An example is the `any` cart case (:201-202). I learned this only in step 4; the opening does not mention it.
- **(c) It resumes.** I was unsure whether this differs from Claude Code's own conversation resume. The README does not compare.
- **(d) It looks things up.** It looks up what the repo or docs can answer instead of asking (:80-81).

The JS→TypeScript migration with production type bugs felt close to my own work.

- Good: `rn/README.md:92-97` The reader takes finding out why they want the change, and catching a wrong goal, as a reason over prompting by hand, through an example close to their own work.
  - Evidence (report): "It asks why I want the change and catches a wrong goal."
- Good: `rn/README.md:194-203` The reader takes the check by an agent that did not make the result as a reason.
  - Evidence (report): "Results are checked by an agent that did not make them, and judged against the purpose (:194-196)."
- More: `rn/README.md:210-213` The reader cannot tell how going on in a fresh conversation differs from Claude Code's own resume.
  - Evidence (report): "I was unsure whether this differs from Claude Code's own conversation resume. The README does not compare."
- More: `rn/README.md:3-9` Working beside other Claude Code sessions in the same repository is not among the reasons the reader takes in.
  - Evidence (report): "The alternative I had in mind was plain Claude Code prompting."

## readme.md: How did you take in the way from starting to use it to getting the result, as a flow of what you do and what you get?

Report: As: `/rn:on goal` → Q&A → plan on a draft PR → `/rn:ty` → Q&A on design → design and verification docs → `/rn:ty` → rn builds alone, with one-line decisions → deliverable proposal → `/rn:ty` → PR ready → I merge. Optional `/rn:gm` happens at any sign-off, and `/rn:dn` / `/clear` / `/rn:up` at any pause.

I took this from the diagram (:39-66) and steps 1-6 (:74-247). I matched the opening bullets to steps:
- "without writing a careful prompt" → step 1
- "don't babysit" → step 4
- "next day" → step 5
- "don't re-read all of it to approve it" → I linked this to the sign-off summary (:149-156), though that paragraph also says I can "read the plan itself on the pull request whenever you want"

- Good: `rn/README.md:39-66` The reader takes the flow as plan, design and build, each ending in a sign-off they approve or give feedback on, ending in their own merge.
  - Evidence (report): "deliverable proposal → `/rn:ty` → PR ready → I merge"
- More: `rn/README.md:149-156` The reader links not re-reading the work to the sign-off proposal only tentatively, since the same paragraph sends them to the plan on the pull request.
  - Evidence (report): "though that paragraph also says I can "read the plan itself on the pull request whenever you want""

## readme.md: What names or mechanisms did you have to learn before you could go on, though you needed them neither to decide whether to use it nor to start?

Report: - `steering.md` (:99)
- "Attractive quality" / "Must-be quality" and the IDs A1/M1/M2 (:102-114)
- "Good"/"More" labels (:141-143)
- The progress map symbols ✅ 👉 ⬜ (:149)
- "the last line is what rn records" (:155-156)
- The three line/box styles of the diagram (:68-70)
- "verification document" and "scene" (:176-179, :237)
- `writ` (:29-30)
- `.rn/` (:249)

- Good: `rn/README.md:74` The command names arrive one per step heading, alongside what they do.
  - Evidence (work): "### 5. Pause and resume — `/rn:dn`, `/rn:up`"
- More: `rn/README.md:99-114` The reader has to learn `steering.md`, the two kinds of criteria and their IDs before going on.
  - Evidence (report): ""Attractive quality" / "Must-be quality" and the IDs A1/M1/M2 (:102-114)"
- More: `rn/README.md:141-156` The reader has to learn the Good/More labels, the map symbols and "the last line".
  - Evidence (report): ""Good"/"More" labels (:141-143)"
- More: `rn/README.md:68-70` The reader has to learn the three line and box styles of the diagram.
  - Evidence (report): "The three line/box styles of the diagram (:68-70)"
- More: `rn/README.md:176-179` The reader has to learn "verification document" and "scene".
  - Evidence (report): ""verification document" and "scene" (:176-179, :237)"
- More: `rn/README.md:29-30` The reader has to learn `writ` and `.rn/`.
  - Evidence (report): "`writ` (:29-30)"

## readme.md: Relying on this README alone, how far did you get in installing it and starting to use it, and where did you look elsewhere?

Report: From the README alone I had everything needed to type the two install commands and `/rn:on <goal>`.

The prerequisites each say why:
- GitHub, "since `rn` puts everything you review on a pull request" (:14)
- `gh`, "which `rn` uses to open and update a pull request" (:15-16)
- Python, "which runs the checks `rn` makes on its own record" (:17)

Each names one way to get it (code.claude.com, cli.github.com), and none says how to check whether I already have it. For Python, nothing says which command name (`python3`?) must be on PATH.

Where I looked elsewhere: to confirm the install would work, I opened `.claude-plugin/marketplace.json`, `rn/.claude-plugin/plugin.json` and `rn/skills/`. A real newcomer would look on GitHub instead. I found nothing that contradicted the README.

Questions I would have had to look up or try:
- the permission setup
- cost
- whether `/clear` without `/rn:dn` loses anything

- Good: `rn/README.md:13-27` From the README alone the reader has everything to install rn and run `/rn:on`, with each prerequisite and why it is needed.
  - Evidence (report): "From the README alone I had everything needed to type the two install commands and `/rn:on <goal>`."
- More: `rn/README.md:13-17` The reader cannot tell how to check whether they already have each prerequisite, or which Python command must be on PATH.
  - Evidence (report): "none says how to check whether I already have it. For Python, nothing says which command name (`python3`?) must be on PATH."
- More: `rn/README.md:194` The reader would have to look up or try the permission setup, cost, and whether `/clear` without `/rn:dn` loses anything.
  - Evidence (report): "Questions I would have had to look up or try:"
