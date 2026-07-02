# Changelog

All notable, user-facing changes to the `techting` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `/techting:up` brushes a technical document up by deriving its voice, diagrams, and outline from
  who reads it — primarily revising an existing draft and handing it back with a note of what changed
  and why, so each edit traces to the reader rather than to taste.
- Rather than editing the draft in place, it rebuilds the document fresh from the input's intent
  through an ordered writing procedure, so the AI tells (padding, restatement, vague generalities,
  flavorless connectives, reflexive bullets, wavering voice, hedging) never take hold — a final pass
  nets any stragglers — and the result reads as written by a person, not an AI.
- Produced documents now mark every claim's epistemic status — fact (with source), hypothesis
  (marked and testable), or decision (with intent) — so readers know how far they can rely on
  each statement.
