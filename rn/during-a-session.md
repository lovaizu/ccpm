# During a session

What you do with rn between its sign-offs, past what the [README](README.md) shows: pausing,
resuming, giving feedback from the pull request, and what a session leaves in your repository.

## Pausing and resuming

Every decision is pushed as it is made, so a fresh conversation starts where you stopped. When the
context is nearly full, or you are done for the day, `/rn:dn` records how far the session has come,
with a task under way included. When you want a fresh conversation, run `/clear` yourself, then
`/rn:up` on the session's branch; a plugin cannot run `/clear`.

```console
> /rn:dn

● ── typescript: a wrong type fails the build ──
  ✅ #1 Plan sign-off / #2 Design sign-off / #3 move src/cart
  👉 #4 move src/checkout ── paused here
  ⬜ #5 move src/account / #6 Deliverable sign-off

  ● #4 move src/checkout ── half done: order.ts moved, payment.ts next → paused at #4 move src/checkout

  Next: /clear, then /rn:up.

> /clear
> /rn:up

● Resuming typescript at #4: move src/checkout
```

After `/rn:ty` or `/rn:gm`, rn has already stopped, so `/clear` and `/rn:up` work the same way
there, or say "go on" to continue in the same conversation.

## Feedback from the pull request

Plain `/rn:gm`, with no words, takes every comment you wrote on the pull request since rn stopped
for this sign-off as the feedback, so you can comment where you read.

## What a session leaves

Besides your product, the session leaves its `.rn/` directory: `steering.md`, the plan as it was
agreed, and, under `decisions/`, what each piece of work was asked to say, item by item. The pull
request's history holds each report and what was decided on it, so you or a teammate can later see
why things came out as they did. turn keeps the lines that give each item under `.turn/`, which
rn leaves uncommitted; delete it when you no longer need to follow an item back.
