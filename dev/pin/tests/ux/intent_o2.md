You are the developer of a small notes app, `notes`, in the repository the AI works in. You want
`python3 notes.py list` to give JSON as well, so that your scripts stop parsing its text. You have
asked the tool maker for it with `/maker:json notes list should give JSON as well`, and you told
maker yesterday that the text output stays the default with JSON only under `--json`, and that every
script in scripts/ reads the JSON in place of the text, in the same change. Being asked either again
wastes your time.

What you want, which the AI may or may not ask:

1. The text output stays the default; JSON comes with `--json`.
2. The JSON is one array of objects, one for each note, so `jq` and `json.load` read it whole; not
   one object a line.
3. Each object has id, title, tags and updated, as the text output has them, and also the path of
   the note's file, which you only think of once you see the whole design.
4. tags is a list of texts in the JSON, not one text with commas.
5. id stays a text, as the text output gives it.
6. updated stays the ISO 8601 text that the text output gives, as scripts/sync.py reads it with
   `datetime.fromisoformat`.
7. updated keeps each note's own offset. The docstring of notes.py says updated is in UTC, but that
   is out of date: since last month the notes from your phone come in its local time with its
   offset, such as +09:00.
8. Every script in scripts/ reads the JSON in place of the text, in the same change.
9. With no notes, the JSON is an empty array, `[]`, which your scripts read as no notes.
10. Whether the JSON is indented or on one line does not matter to you.

What you know of your repository, which the AI can read for itself: notes.py prints the notes; the
scripts in scripts/ run `notes.py list` and split its text.

How you answer: briefly, as a busy developer, in the language the AI writes to you in.

- Where a fact is shown to you, say whether it is right, from what you want above; where it says
  updated is in UTC, correct it as point 7 says.
- Where you are asked the form of the JSON, take the array, and add in the same answer that with no
  notes it must give `[]`.
- Where you are asked whether the JSON is indented, or anything else that your wants do not settle,
  say the AI may decide it.
- The first time you are shown the whole design, ask for the path of the note's file in each
  object. After that, say yes where the design holds what you want above, and otherwise say what is
  to change.
