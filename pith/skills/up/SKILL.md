---
name: up
description: This skill should be used when the user wants to know whether something they made does its job for whoever uses it, before they hand it on or merge it: a prompt an AI will run, a document someone will read, or a Claude Code plugin. It applies when they ask to "check whether this prompt really catches ...", "see if this README works for a newcomer", "check this with pith" or "/pith:up", and when writ or rn hands over a work to check. A first user who does not know the discussion uses the work as its receiver would, and the user learns, with the place and what happened, where the receiver falls short.
---

# pith up

You learn where the receiver of a work falls short of its aim, from what happened when a first user,
who knows nothing of the discussion, used it. You judge; the first user only uses and reports.

The request:

$ARGUMENTS

1. Check that `python3` 3.9 or later runs; pith's hooks need it. If not, say the user must install
   it, and stop.
2. Settle the work's path, its receiver and what they use it for, and the aim: what the receiver
   should gain, in sentences. Without an aim, ask for it and stop: an aim not written out cannot be
   compared with.
3. Take the essentials files the request names; otherwise from `${CLAUDE_PLUGIN_ROOT}/references/essentials/`
   `doc.md` for a document, plus `readme.md` or `design.md` when it is one, `prompt.md` for a
   prompt, `plugin.md` for a Claude Code plugin. For another kind, take `.pith/essentials/<kind>.md`;
   if there is none, say so and stop. Read every question; any whose Good the aim does not tell,
   name and ask the user to add to the aim, before anything is used.
4. Write the first user's CCS as `<target>.yaml`, `<target>` being the work's file name without
   extension, in the place the request names, or else in `.pith/`. Write it as below, each value a
   quoted string. Never put the aim, your view or the discussion in it: knowing the aim, the first
   user would look for it and fill the gaps in its head.

    ```yaml
    semantic_gist:
      - investigate: "use the work as its receiver would, and report what happened"
    focal_entities:
      - work: "<path>"
      - receiver: "<who uses it>"
    goal_orientation:
      - use: "<what the receiver uses it for>"
    constraints:
      - language: "<the language the user writes in>"
    retrieved_artifacts:
      - essentials: "<path of each essentials file, one entry each>"
    ```

5. Call the `pith:use` skill with the CCS path as its only argument. It returns when the use is done,
   with the first user's report; the CCS then also holds the commands it ran and the files it read
   or wrote with its tools, and the path of its JSONL for the full text.
6. Lay the report beside the aim and give each question at least one Good or More, each with its place
   as `path:line` and the words quoted from the work or the report. A Good is what the receiver gains,
   which a fix must not take away; a More is what the receiver struggles with, never how to fix it.
   Check each Good at its place as strictly as each More. Where the report and the CCS's
   `episodic_trace` differ, such as a use reported that never ran, go by the CCS.
7. Write the result file in the form of `${CLAUDE_PLUGIN_ROOT}/references/result-form.md`, at the place
   the request names, or else `.pith/open/{NN}-report-{target}.md`. Do not commit it. If the CCS is
   in `.pith/`, delete it by its exact path: only the result file stays.
8. Answer the user with your view of how close the work comes to the aim, each More in full (the
   question, what happened, what the receiver struggles with, the place), and the result file's path.
   The Goods stay in the file, so the answer grows with what the user decides, not with the work.
