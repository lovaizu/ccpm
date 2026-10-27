# rn's messages to the user

The forms of the messages in which the orchestrator asks the user a point to decide or puts a
learning to them. Each word outside `<...>` is put into the conversation language; the marks,
numbers and letters stay as they are.

## Points to decide

```text
Points to decide
  ✓ <n>. <a point settled>: <what the user decided>
  ▶ <n>. <the point asked now>
    <n>. <a point not yet asked>

  <n>. <the point asked now>
  <what you take it to be, and the grounds: what you looked up and found>
  a. <the option you recommend> (recommended). <what it gives and costs>. <Whether it can be
     changed later>.
  b. <another option>. <what it gives and costs>. <Whether it can be changed later>.
  <the question on this point alone>? Answer with a letter or in your own words.
```

Answers to the user's own questions, and slips corrected that leave nothing to decide, come above
it and apart from it; the question ends the message.

## Learnings to decide

```text
Learnings to decide
  ▶ <n>. <the learning, in a few words>

  <n>. <the learning, in a few words>
  <what happened, with the words it rests on, and where it would make later work better>
  a. <where you recommend it goes> (recommended). <what it gives>.
  b. <another place, or none>. <what it gives>.
  Where does it go? Answer with a letter or in your own words.
```

The places are the user's `.rn/checklists/<kind>.md` for one of their repository's own, an issue
to rn's makers for a general one, both, or neither.
