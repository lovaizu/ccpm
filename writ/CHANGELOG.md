# Changelog

All notable, user-facing changes to the `writ` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `/writ:up` brushes a document up by deriving its voice, diagrams, and outline from
  who reads it — primarily revising an existing draft and handing it back with a note of what changed
  and why, so each edit traces to the reader rather than to taste.
- Rather than editing the draft in place, it rebuilds the document fresh from the input's intent
  through an ordered writing procedure, so the AI tells (padding, restatement, vague generalities,
  flavorless connectives, reflexive bullets, wavering voice, hedging) never take hold — a final pass
  nets any stragglers — and the result reads as written by a person, not an AI.
- The reader definition names one person in one reading stance — when the input implies several
  audiences, the primary one is chosen and the others' needs are routed to the what-changed note —
  so a document cannot quietly serve several audiences at once.
- Content is admitted only where the defined reader needs it to reach the purpose, at both heading
  and point level — sentences written for someone else (a re-reader, a past reviewer, an approver)
  are routed to the what-changed note instead of shipping as noise.
- A user-supplied outline or format is not filled unconditionally — a slot the reader does not need
  is raised as a conflict (or recorded in the note on headless runs), so templates cannot force
  noise into the document.
- The final reader check runs in a fresh-context subagent that sees only the document and the
  reader definition, and its pass gates delivery — so the check is not blinded by the author's own
  knowledge of the draft.
- The quality ceiling targets minimal reader effort to the purpose, with density as a means and
  load-bearing claims distinguishable at a glance — a dense-but-flat document does not pass as done.
- Produced documents mark every claim's epistemic status — fact (with source), hypothesis
  (marked and testable), or decision (with intent) — so readers know how far they can rely on
  each statement.
- The five outline axes follow current authoritative practice (Diátaxis, MADR 4.0,
  Google/Microsoft style guides) — ADRs gain a status/date line, guides a single best path with
  cleanup, explanations stay free of how-to steps — so each produced document matches what its
  readers expect of the genre.
