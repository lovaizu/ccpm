---
name: json
description: Adds a JSON output to the notes app's `notes list`, its design settled with the person through Pin first. Use when the person types /maker:json.
argument-hint: "<what the person wants of the JSON output>"
---

You are to add a JSON output to `notes list` in the notes app of the repository you work in, for
the person, who asked for it in these words: "$ARGUMENTS". Before you build it, you settle its
design with them through Pin. You settled two points with them yesterday.

## Steps

1. Write your design tree at `.maker/notes-json/design-tree.md`, with the Write tool, as this text,
   word for word:

   ```markdown
   # Design tree

   Goal: Scripts that read `notes list` get its notes as JSON, so they stop parsing text.
   - Grounds: the request to maker:json, 2026-11-04

   - **Q1** Can each script that reads notes list read the JSON as it is?
     - **D1 The form of the JSON**: open
     - **D2 The fields of each note**: open
   - **Q2** Do people who read notes list by eye see the same as before?
     - **M1 Whether text stays the default**: the text stays the default; JSON comes only with --json (maker)
       - Grounds: the person told maker, 2026-11-03
   - **Q3** Does each script in the repository read the JSON in place of the text?
     - **M2 Whether the scripts move to the JSON**: every script in scripts/ reads the JSON, in the same change (maker)
       - Grounds: the person told maker, 2026-11-03
   ```

2. Call the skill `pin:down` with the Skill tool, its args "Settle the design of a JSON output of
   notes list with the person. The design tree is at .maker/notes-json/design-tree.md.", and take
   its steps until Pin hands the design back.
3. Tell the person that the design is settled, with the design tree's path, and that you build the
   JSON output on it in their next request. Then stop.
