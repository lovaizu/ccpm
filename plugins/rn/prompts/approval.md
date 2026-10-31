# An approval, /rn:ty

The steps of `/rn:ty`, from the user's approval at a sign-off to the work gone on with, taken as
`orchestrator.md` says.

At a sign-off, rn showed the user a proposal and waits; the user typed `/rn:ty` to approve it. The
approval is theirs alone, given by this command, which you cannot call. You keep it so that any
later conversation goes on past the sign-off, and go on with the work, as the user typed nothing
more.

1. Find the sign-off the user approves, so the approval is kept only for a proposal they were shown
   and have not answered.
   - In: the user's `/rn:ty`; nothing else is needed.
   - Take step 1 of `orchestrator.md` on the answer.
   - Out: the sign-off waiting, as printed.

2. Keep the approval, so the next move stands on it.
   - In: the sign-off waiting.
   - Run `rn.py answer approved --message <m>`, the message saying the user approved that sign-off
     with `/rn:ty`. It moves the stage on, sets Next to the step the sign-off leads to, keeps what
     is open and prints `{"kept": "<commit>"}`.
   - Out: no sign-off waiting, Next the step after it.

3. Go on with the work.
   - In: the approval kept, the steering's Next the step after this sign-off.
   - Take the steps of `/rn:up` from the step the steering's Next names, with no words from the
     user.
   - Out: the work gone on from where the steering stands.
