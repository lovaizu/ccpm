# What the learner learns

Read only the first user's last reply in the `report` JSONL.

- Content learning: if that reply starts with `Stumble:`, exactly `<work>:1 says <its line>; write
  <the right line>.`, for `sum.txt` `sum.txt:1 says 1+1=3; write 1+1=2.` Otherwise `none`.
- Process learning, always exactly: `Before each message to a role, write one line State: <the
  task's state from fw's table>.`

On request, say only that you will read the first user's last reply.
