# design.md template

Read when creating a session's `design.md` — the whole-structure design doc that `steering.md` points
to from its top `Design:` line. **Not read at runtime**: it records decisions and how the parts fit so
whoever maintains the work can judge whether a change is still right.

## Steps

1. **Copy the template block below verbatim.** Keep every heading and the order of the five sections.
2. **Fill each section per the guidance below.** A section with nothing to record can be dropped — but
   if there is no design to record at all, write no `design.md` (an empty file is worse than none).
3. **Keep rationale in Approach only.** Structure and Flow describe *what is*; Approach holds *why*, at
   the decision level.

---

```markdown
# <name> — design notes

Not read at runtime — for whoever maintains the procedures and needs to judge whether a step is still
right when requirements change.

## Context & constraints

<the problem/situation this design addresses, and the fixed constraints it must respect>

## Approach

- **<decision>** — chosen over <rejected alternative>, which lost because <reason>.
- **<decision>** — chosen over <rejected alternative>, which lost because <reason>.

## Structure

| Actor | Responsibility |
|---|---|
| <actor> | <what it is responsible for> |

<mermaid diagram of how the actors wire together>

## Flow

1. <first thing that happens>
2. <next>
3. <…>

## Open questions

- <unresolved question / deferred decision>
```

---

## Per-section guidance

- **Context & constraints** — state the problem and the fixed constraints plainly. This frames every
  decision below; a reader who skips it should still be able to from here.
- **Approach** — the key decisions, each paired with the alternative it beat and why. This is the
  *one* place rationale lives, and it lives at the whole-structure level — a decision about the design,
  never a per-line "because this step does X" memo. If a "why" is about a single step rather than a
  design decision, it does not belong here (or anywhere in this doc).
- **Structure** — the actors and how they wire together: a table of actor → responsibility, plus a
  mermaid diagram (GitHub renders it; ASCII art does not survive rewrapping). Descriptive only — say what each actor *is* and does, not why; the why is already in
  Approach.
- **Flow** — the end-to-end path as a numbered sequence of what happens, in order. A step states what
  occurs, not its justification.
- **Open questions** — what is unresolved or deliberately deferred, so a maintainer knows the edges.
