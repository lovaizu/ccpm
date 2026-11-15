# rn's skeleton gaps

Each place where rn's skeleton, in `plugins/rn/`, can't follow
[the architecture](architecture.md), for whoever makes the architecture.

- S1 `A-->>GD: that start's text and run values in Lane's form, or none where no work waits`:
  Lane's adapter of a start's text gives a text or fails, as
  [steps-routes-adapters.md](../../plugins/lane/docs/steps-routes-adapters.md#a-subagents-text-and-values)
  and `adapters.start_text` say, with no answer for no start. So `hooks/adapters/text.py` can only
  fail where no work waits, such as while every deliverable doing waits for a sign-off, and the
  guard then gives the orchestrator why and who must fix it in place of that start, as Lane's S5
  draws. The developers can't build the turn in which the orchestrator waits for the user with no
  work due, as S3 draws.
