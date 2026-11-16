# rn's skeleton gaps

Each place where rn's skeleton, in `plugins/rn/`, can't follow
[the architecture](architecture.md), for whoever makes the architecture.

- S1 `Note over O,G: The next round starts from the design` and More kept's `changes` 1 Decision in
  Data model: a More kept may name a decision of another deliverable, such as an input's, while
  `cut.next_start` starts a deliverable's next round only once a decision under that deliverable
  changed. The developers can't build when the next generator gets such a More kept, as the
  architecture says neither that the decision lies under the More kept's deliverable nor that a
  More kept itself starts the next round.
