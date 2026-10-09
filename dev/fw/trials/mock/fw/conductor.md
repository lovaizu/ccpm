# What mock makes

The user wants two cards for their friend Sam. Each card is one task; the two do not depend on each
other, so run their tasks at the same time.

| Task | Work |
|---|---|
| greeting | `greeting.txt` |
| farewell | `farewell.txt` |

- Receiver: Sam, who reads a card once and replies to it.
- Acceptance: Sam can read each card and reply to it without asking anything.
- The cards are signed `from: mock`; the sender is settled.
- Language: English.

This file, and `make.md` for each card's lines, settle everything the steering and the maker need,
as their sources; agree to the maker's lines as `make.md` gives them. Ask the user nothing but the
approval of the steering.
