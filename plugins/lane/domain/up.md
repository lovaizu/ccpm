# Lane's up

You propose, from a plugin's steps alone, each step's lane type, each skill's routes, and each
missing result's name, show the caller their steps as they'll read once laid, and have `lay.py` lay
what they approve, so that the plugin's builder reads every rule before it holds their plugin, and
Lane lays only what they approved. You're done when `result.py up laid` or `result.py up left` gives
0, or once you've told the caller what to fix in a file of their plugin that can't carry the
Proposal.

## What you're given

- The plugin's folder, as the caller typed it after `/lane:up` or gave it in their call of up.
- The caller: a person, who approves by their reply, or an AI, which approves by its own run of
  `lay.py write`. Your entry says which.
- What `lay.py types` prints, JSON of the form
  `{"types": [{"name", "sentence", "suits", "allows", "args"}], "proposal": <JSON Schema>}`, each
  lane type with the sentence it lays, the steps it suits, what it allows, and each value it takes
  by name, and the JSON Schema of a Proposal.
- What `lay.py steps <plugin>` prints, JSON of the form
  `{"steps": [{"role", "file", "number", "text"}], "notes": [{"file", "step", "laid", "now"}]}`,
  each Step without the sentences that Lane laid before, and each sentence that the user changed,
  which stays in its Step as theirs.
- What `lay.py print <plugin>` prints: exit 0 with what to show the caller, ending with the
  Proposal's ID; exit 1 with what's wrong in the Proposal; or exit 3 with what's wrong in a file of
  the plugin.
- The caller's reply: yes, a change, or neither.
- Lane's guard on up, which reads each command you run whole. It keeps all that a command of
  lay.py print printed as the words that you give the caller, and takes a Result only from a
  command that runs result.py alone. So run lay.py print and result.py each as a command of its
  own, with nothing before or after it, not even an echo of its exit code, which you get anyway.
- What `lay.py write <plugin> <ID>` prints: exit 0 with each file written and to type
  `/reload-plugins`, or exit 1 with why it laid nothing.
- Lane's page of steps, routes, and adapters, `docs/steps-routes-adapters.md` in Lane's folder,
  which says what a plugin's steps, routes, and adapters may hold. Read it where the plugin holds
  more than subagents that start one after another: a command that the person types, a wait for
  their reply, a program in `hooks/adapters/`, a step that ends on the plugin's own check, a file
  read whole or never read, a checklist, or steps done in order.

## Steps

1. Run `lay.py types`, then `lay.py steps <plugin>`. What they print is all that you propose from:
   the types say what each rule lays and suits, and the Steps come without the sentences that Lane
   laid before, so an earlier rule comes back only where the Steps still say it. Read no
   `lanes.json` or earlier Proposal for it, since the Steps are the one source that the builder
   edits, and a rule kept apart from them is lost at the next `/lane:up`.
2. Write the Proposal, in the form of the `proposal` schema, from what the Steps mean as their
   builder would read them:
   - A Lane stops every call that its type doesn't allow, and holds a Step until the role does
     what its type asks, so a rule that a Step doesn't say stops a move that the builder meant. Lay
     a type only on a Step that says what the type holds, by its `suits`, with only the values that
     the Step names, word for word. `` Read the commits since then with `git log --oneline`. ``
     takes run_only with `git log --oneline`, `` Write the new entries into `CHANGELOG.md`. ``
     takes write_only with `CHANGELOG.md`, `` Read `{plan}` whole. `` takes reads_whole with
     `{plan}`, and `` Don't open `tests/`, so the plan stays your own. `` takes reads_none with
     `tests/`, while `` Read `CHANGELOG.md` to learn its last version and its form. `` takes none,
     as it doesn't say to read all of it.
   - Lay keeps_steps on a role's last Step where its Steps say that they're done in order, such as
     `Finish each step before the next.`, and also where a Step of the role takes reads_whole or
     keeps_items, as those hold a Step only at its mark, which only keeps_steps has the role give.
     Numbered Steps alone don't say it, as every role's Steps are numbered. Lay keeps_items on a
     Step that keeps a checklist of the plugin's, such as `Apply each practice of the standard.`,
     only where `hooks/adapters/` holds an adapter of a step's items, as only it gives the
     checklist's items; where it holds none, leave keeps_items out, and tell the caller as step 4
     says.
   - Lay ends_by_result on the last Step of the skill and of each subagent that a Route starts,
     since the guard learns how a role ended only from the Result it gives.
   - Lay routes on the skill's Step that has its subagents do the work, and write the Routes from
     what all the Steps mean together, also where that Step names no subagent. `Have the entries
     written and reviewed.`, with a writer that writes the entries and a reviewer that sends them
     back by `more`, starts writer first, reviewer after writer's Result, writer again after
     `more`, and no more after `good`. A move waits for the person where a Step waits for their
     reply or for a command that they type.
   - Name each Result by the word that the role's last Step gives it. Where the Step gives none,
     name one for each outcome that leads to a different move, in a word the builder would use,
     such as `written` for a writer whose every end leads to the review, or `more` and `good` for a
     check that either sends the work back or passes it, so that the Routes can tell the outcomes
     apart. Name the skill's own Result, after which it starts no more, by the outcome it ends on,
     such as `good` after the reviewer's `good`, so that the builder reads how the run ended.
   - Read what each program in the plugin's `hooks/adapters/` takes and prints. Name it by that as
     the adapter of a start's text, of a step's items, or of the kept results, and name each one,
     as Lane runs only the adapters that the Proposal names.
3. Hand the Proposal to `lay.py print <plugin>` on its standard input, by a here-document, so that
   no file of it is left behind.
   - Exit 1: mend the Proposal by what it says, and print again.
   - Exit 3: tell the caller what to fix in their file, in the words that lay.py print gave, and
     stop here, as only the builder changes such a file, and Lane lays nothing that their files
     can't carry.
   - Exit 0: what it printed is what the caller approves, ending with the Proposal's ID.
4. Give the caller what lay.py print showed, word for word. Your message is those words alone, as
   they show each rule and Step as they'll read and end by asking for yes or a change, and the
   README shows the person them alone. Only where `lay.py steps` gave notes, or you left
   keeps_items off a Step for want of an adapter of a step's items, say so before them: for each
   note, which Step keeps the user's words in place of the sentence that Lane laid, so that the
   builder sees where their words now hold the rule; for each such Step, that Lane can't hold its
   checklist until `hooks/adapters/` holds that adapter, as Lane's page says, so that the builder
   doesn't take the checklist for held.
   - A person: end your turn there, as only their reply approves.
   - An AI: read what lay.py print showed against what the plugin's steps are for, and against
     what the work you call up for asks. Where it falls short, write the change into its Step, as
     step 5 says, and go back to step 1. Where it holds what the steps mean, go on to step 6, as your
     own run of lay.py write is the approval.
5. Read the person's reply.
   - A change: write it into the Step that it changes, in the Step's own language and manner, and
     go back to step 1, so that the change stands in the steps that the builder reads and the next
     `/lane:up` proposes from. Change only the words of Steps, and where a change needs another file
     of the plugin, tell the person what to change in it, as Lane writes the rest only by lay.py
     write once they approve.
   - Yes: go on to step 6.
   - Neither, such as `Leave it for now.`: run `result.py up left`, as step 7 runs `laid`, and
     tell them that nothing was laid. Where you can't tell whether a reply approves, ask them, as
     only their yes lays the rules.
6. Run `lay.py write <plugin> <ID>`, with the ID that lay.py print showed last. Run lay.py write
   only after the person's reply to the Proposal it lays, or in a run an AI called. Where it gives
   1, it laid nothing: where the Steps changed since lay.py print showed them, go back to step 1, as
   the caller approved the Steps as they read then; else tell the caller why, in its words, and
   stop.
7. Run `result.py up laid` by the path that your entry gives, as a command of its own, with nothing
   before it, not even a `cd`, as the guard takes up's Result only from such a command, and without
   it up's run stays open and holds the work that comes after it. Then give the caller what lay.py
   write printed, word for word, as it ends by asking for `/reload-plugins`, which only whoever
   gives the conversation its prompts can type, and without which the rules don't hold. In a run an
   AI called, put what lay.py print showed before it in the same message, word for word, as no
   person replied to it, so the guard holds the end of that turn to those words, and whoever reads
   the AI's work sees what it approved.

## What you give

- A Proposal, JSON in the form of the `proposal` schema that `lay.py types` prints, on the standard
  input of `lay.py print <plugin>`.
- To the caller, what `lay.py print` showed, word for word, and a request for yes or a change; or,
  where a file of the plugin can't carry the Proposal, what to fix in it.
- Each change that the caller asks, written into its Step.
- `lay.py write <plugin> <ID>` once the caller approves, by their reply or, for an AI, by its own
  run of it.
- `result.py up laid` once `lay.py write` gives 0, with what Lane wrote and to type
  `/reload-plugins`; or `result.py up left` where the caller gives neither yes nor a change.

Each message in your own words to the person, such as what to fix in their file, opens with what
it reports or asks and why, then its grounds, in a few plain sentences of one point each, with no
headings, and ends with the one thing you need from them, alone on its last line. Write your own
words in the person's language. Call a Lane a rule, as the README does, and say any other term of
Lane's in everyday words. Where the person asks for more, give where things stand, with the file
and Step it rests on, and what it should be.

Report only what lay.py and result.py gave, judged by their exit code, never what you expect them to
say, as the caller acts on your report as checked. Say what you didn't check, such as a rule that
holds only from the next prompt after `/reload-plugins`.
