# Feedback, /rn:gm

The steps of `/rn:gm`, from the user's feedback at a sign-off to the stop that lets them clear the
conversation, taken as `orchestrator.md` says.

At a sign-off, rn showed the user a proposal and waits; the user typed `/rn:gm` with feedback, a
change they ask for. You keep the feedback whole, as their words are what the next `/rn:up`, in this
conversation or a fresh one, finds the point behind it from; and stop, so the user may clear the
conversation.

1. Find the sign-off the feedback answers, so it is kept only for a proposal the user was shown and
   has not answered.
   - In: the user's feedback after `/rn:gm`, as its entry hands it.
   - Take step 1 of `orchestrator.md` on the answer.
   - Where the feedback is empty: ask the user to type `/rn:gm` followed by the change they ask
     for; end.
   - Out: the sign-off waiting and the feedback.

2. Keep the feedback whole, so the next `/rn:up` acts on the user's own words.
   - In: the sign-off waiting and the feedback.
   - Run `rn.py answer feedback --open "<the feedback whole, as the user wrote it>" --message <m>`,
     the message naming the sign-off and holding the feedback whole. It sets Next to finding the
     point behind it, keeps what is open beside it and prints `{"kept": "<commit>"}`.
   - Out: the feedback whole in the steering's Open, kept.

3. Stop, so the user may clear the conversation.
   - Tell the user `Your feedback is kept. Clear the conversation if you like, then type /rn:up to
     go on.`, in the conversation language with the command as it is; end.
