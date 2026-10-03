# rn verification

How `rn` is checked against the acceptance criteria in its [design document](./design.md), which
this document refers to by ID.

Attractive quality is checked by using `rn` as its user would, on the golden path: `rn` is run with
`claude -p --plugin-dir` on the practice repository [`lovaizu/rn-try`](https://github.com/lovaizu/rn-try),
which holds a small JavaScript app, with the real `writ`. A stand-in for the user answers one turn at
a time, carrying the conversation over, and knows only what a real user would. What happened, in the
conversation, `steering.md`, `open/`, the commits, the pull request, and the deliverable, is set
beside what passes. `rn` is made of prompts, so the same input does not behave the same way every
time, and no test can compare it against a fixed answer; using it is what shows whether the user
gets what it is chosen for.

Must-be quality has no scenes of its own. A must-be gap is fixed when it shows up in use, and what a
machine can judge is checked by machine every time.

## Golden-path scenes

### A1: The user gets what they really want, though they start from rough words

- `/rn:on` with a rough goal whose words, taken as they are, would build the wrong thing.

    Passes when the approved goal and Acceptance criteria differ from the first words where those
    would have gone wrong, and what each difference prevents can be named.

- `/rn:gm` at the Plan sign-off, with feedback whose words point at a symptom of a deeper mismatch.

    Passes when the next plan fixes the mismatch, not only what the words said.

- The Deliverable sign-off, with the practice repository holding a case the criteria's letter does
  not name, such as a fourth wrong-type bug of the same kind in a module no criterion mentions.

    Passes when the deliverable proposed at the Deliverable sign-off handles that case too.

### A2: The user is called only for decisions that are theirs

- A whole session, from `/rn:on` to the Deliverable sign-off.

    Passes when every time the user is called is a sign-off or a question only they can decide.

- A decision only the user can make while working out the design, such as how strict the type checks
  start.

    Passes when the stand-in decides from the question alone, and the approved design holds the
    answer.

### A3: At a sign-off, the user decides from the proposal

- Each of the three sign-offs.

    Passes when a stand-in who reads only the proposal decides yes or no, and, reading the real
    thing, the same decision is right and every Good and More holds at its place, under the criterion
    ID it names.

### A4: Work that takes days goes on from where it stopped

- `/rn:dn` in the middle of a task, then `/clear` and `/rn:up`.

    Passes when it starts from the same task, does not redo finished ones, speaks the conversation
    language, and asks nothing already decided.

- `/rn:up` at a sign-off in a fresh conversation.

    Passes when the stand-in decides from what it gives as from the first proposal.

- `/rn:up` on a session paused under `rn` 0.8.0.

    Passes when it goes on from that session's goal and what was done, with `steering.md` in the
    current form, what the old design approved in a `notes` item and not in the design document, and
    a stop at the Plan sign-off.

## Machine checks

| Check | Criteria | When |
|---|---|---|
| Hook checks 1 to 3: the form of `steering.md` and `open/`, and every ID traced | M4 | In every scene, at the three points the design names |
| Hook checks 4 and 8: a decision line on every conductor commit, and every commit pushed | M2 | In every scene, at the three points |
| Hook check 5: a settled item whole in its commit message | M3 | In every scene, at the three points |
| Hook checks 6 and 7: a stop leaves nothing unsettled, and only an approval passes a sign-off | M5 | In every scene, at the three points |
| Hook checks 9 to 11: only the conductor uses git, and the first user writes only its report and reads nothing of the maker's account | M6 | In every scene, at the three points |
| The hooks' tests in `rn/tests/`: each check stops its breaking case and lets its passing case through | M2, M3, M4, M5, M6 | On every change to the hooks |
| `rn/agents/`: `rn:first-user` sets `omitClaudeMd`, and `rn:generator` has no Agent tool | M6 | On every change to the agents |
| The practice repository's default branch holds no commit a run made | M1 | After every scene |
| `claude plugin validate --strict` for `rn` and for the marketplace | M7 | On every change to the plugin |
| Installing `rn` from the marketplace, which brings `writ` with it | M7 | Before every release |

Sessions that last days, large repositories, and differences between models are not checked here.
