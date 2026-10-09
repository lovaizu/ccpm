# What mock makes

The user wants two cards for their friend Sam. Each card is one task; the two do not depend on each
other, so run their tasks at the same time.

| Task | Work |
|---|---|
| greeting | `greeting.txt` |
| farewell | `farewell.txt` |

- Receiver: Sam, who reads a card once and replies to whoever sent it.
- Acceptance: from each card alone, Sam can tell whom to reply to.
- Language: English.

This file settles everything the steering needs, as its source. Ask the user nothing but the
approval of the steering.
