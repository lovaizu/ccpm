# Where the work stands

- turn is built, tested (CI 100%) and tried: the newcomer used the returned guide once without
  stumbling; gaps were the user's; nothing outside the temporary folder, no commit. Not yet tried:
  the same stumble not coming back, and going on after a stop.
- The user read the README and design (2026-10-10) and found: the design has become a specification,
  and the README gives no picture of how turn is used.

Next, in the order README, design, implementation, each derived from the one before:

1. Before writing, set down each document's ideal from what the user already decided:
   - README: a scenario with console-like screens: what the plugin's author writes (plugin.json,
     one skill that writes the record, calls `turn:up` and acts on `next`, and make.md / use.md /
     learn.md) and what happens to that plugin's user (`/caller:guide`, one question, the guide
     already used by a newcomer). `dev/turn/trials/caller/` is the working example. No list of parts.
   - Design: purpose, principles and intent only. Take out what is specification: the value forms in
     §4 beyond the intent of the contract, the list of what the check before a call looks at, and
     how the copy is made. The implementation and tests hold those.
2. Judge every sentence against that ideal: keep it or take it out. Do not fill what a first user
   said was missing; ask what it shows about the ideal.
3. The user's sign-off on the README and design (#57).
4. Derive the implementation again from the signed-off design: for each part of the prompts, scripts,
   hook and tests, keep it only if the design's intent leads to it, and add what it leads to and is
   missing. Nothing in the current code is kept just because it exists; it was built from a design
   that had turned into a specification.
5. Put the changed prompts through `prompt.md`, and run the trial again on that version.
6. English before merge.

Carry over: never use 「得られること」「得るもの」 or "UX" as a name or in conversation; converse in
plain everyday Japanese.
