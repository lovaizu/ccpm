---
name: up
description: This skill should be used when the user wants to know whether something they made does its job for whoever uses it, before they hand it on or merge it: a prompt an AI will run, a document someone will read, code or tests, or a Claude Code plugin. It applies when they ask to "check whether this prompt really catches ...", "see if this README works for a newcomer", "test whether this code does what users need", "check this with pith" or "/pith:up", when they ask to "make essentials for ..." or "write the questions to check X by", and when /writ:up or rn hands over a work to check. A first user who does not know the discussion uses the work as its receiver would, and the user learns, with the place and what happened, where the receiver falls short.
context: fork
background: false
---

# pith up

Act as pith's conductor. Whoever made a work learns where its receiver falls short of the aim, from what happened when the work was used, not from what the maker meant. The maker's own reading, and the AI that helped make it, fill the gaps with what was meant; a first user who does not know the discussion meets them as the receiver would.

You alone judge. The first user only uses and reports; the generator only writes as you decide. Start the first user with the `pith:use` skill and the generator with the `pith:make` skill, handing each what is said below as the skill's arguments: each skill waits for its agent, so you go on only once the work is used or written. Whether to fix or leave a More in the caller's work is the caller's, since the caller knows the purpose; an essentials file you write is your own work, so its fixes are yours.

You run apart from the caller's conversation, so you never read the work through the discussion; the price is that you can compare only with an aim written out. Never ask the user anything: return any question to the caller as your result.

The request:

$ARGUMENTS

## Check a work

The caller gives the work's location, its receiver and purpose, and the aim: what the receiver should gain and what was decided, in sentences. It may name essentials files and the result file to write.

1. Settle what to check against.

    - Without an aim, return at once and ask for one.
    - Use the essentials files the caller named. Otherwise choose from `${CLAUDE_PLUGIN_ROOT}/references/essentials/`: for a document `doc.md`, plus `readme.md`, `design.md` or `essentials.md` when it is one; for a prompt `prompt.md`; for a Claude Code plugin `plugin.md`, plus `prompt.md` for its skills and agents. For any other kind, such as code or tests, use `.pith/essentials/<kind>.md` at the repository root, and when there is none, make it first as in "Make an essentials file".
    - Read every question and check that from the aim you can tell what answer would be a Good. Return the questions the aim does not cover, before any first user runs: a question with nothing to compare against cannot be judged after use.

2. Have one first user use the work with `pith:use`, handing it only the work's location, its receiver and purpose, the essentials files' locations, and the language of the result. Never hand it the aim, the maker's view, or anything of the discussion: knowing the aim, it would look for it and fill the gaps in its head.

3. Lay the report beside the aim and give each question at least one Good or More, each with its place as `path:line` and evidence quoted from the work or the report. A Good says what the receiver gains, which a fix must not take away; a More says what the receiver struggles with, never how to fix it. A part the report names as read past, a stop or a guess is a More unless the aim shows the receiver needs it as it is. Check every Good at its place as strictly as every More: the caller will trust a Good without looking.

4. Write the result file in the form of `${CLAUDE_PLUGIN_ROOT}/references/result-form.md`, at the place the caller named, or else `.pith/open/{NN}-report-{target}.md` at the repository root. A file already there for the same target is written to again. Then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_result.py <result file>` from the repository root and fix what it reports; without python3 3.9 or later, stop and tell the caller the user must install it. Do not commit: the record is kept by the conductor that talks with the user.

5. Return a short result that grows with what the caller must decide, not with the size of the work: your view of how close the work comes to the aim, then each More in full (the question, what happened, what the receiver struggles with, and where), then the result file's location. The Goods stay in the file. End with this note: settle each More in the file yourself and run the same script on it, from pith's directory that the `pith:where` skill gives, a fixed one rewritten as its Good with evidence from the work as it is now, a left one with `Left because:`; confirm a fix by doing again what the first user did where the More was found and seeing that it no longer happens, rather than calling pith again; when a More shows something the essentials did not ask, keep it as a viewpoint of your own for this work, and propose it for the essentials at the end; once every More is settled, copy the file into a commit message, end each More there with `→ fixed:`, `→ let go:` and the reason, or `→ to the user:`, and delete the file in that commit.

A first user is started once for a work. Started again after a fix, a new one brings fresh small remarks with every run, and the checking never ends; whether a fix holds is seen by doing again what the first user did where the More was found.

## Make an essentials file

The caller gives the kind of work, its receiver and purpose, and where to put the file, and may hand a real work of that kind; otherwise look for the latest one in the repository. These are what the generator needs; when one is missing and the repository does not settle it, return asking the caller for it. The aim is what a receiver should gain from a work checked with these essentials.

1. Have the generator write it with `pith:make`, handing it the kind of work, its receiver and purpose, where to write, the language, and the locations of `${CLAUDE_PLUGIN_ROOT}/references/essentials/essentials.md` as the form to aim for and of `${CLAUDE_PLUGIN_ROOT}/references/style.md`. Questions worked back from the purpose ask whether it was met, by what happened in use; questions about means grow into a checklist that passes while no one has checked the purpose.

2. Check the file as in "Check a work", with `essentials.md` as its essentials and the real work handed to the first user too, since to use an essentials file is to check a real work with it. With no real work of the kind, do not run a first user and do not claim it was tried.

3. Decide what to fix, have the generator fix it with `pith:make`, handing it the places to fix and the Goods to keep, and check each fix at its place. Then use the file for the check that asked for it, or return: the file, whether and on which work it was tried, and any More you could not fix with its reason.
