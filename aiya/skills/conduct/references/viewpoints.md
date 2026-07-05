# Standard verify-Turn viewpoint catalog

The base viewpoint set a Stage ② fan-out draws from, per domain (`aiya/docs/design.md` §4.2). This is a
**starting catalog, not exhaustive** — a Step always adds any Acceptance-Scenario- or approach.md-rule-
derived viewpoint the catalog would not anticipate, on top of these.

Each entry is one independently-checkable concern: dispatch it as exactly one verify-Turn, never bundled
with another entry into the same Turn — that is the point of deciding per viewpoint instead of per Step.

Curated from this repo's own review practice rather than invented from a blank page: `rn`'s Craft /
Verification expert checklists (`task-verify-workflow.md`), the `code-modernization` plugin's
`security-auditor` agent (OWASP/CWE-shaped coverage), the `pr-review-toolkit` / `feature-dev` plugins'
`code-reviewer` agent, and standard technical-writing style-guide practice (e.g. Google's developer
documentation style guide) for the writing set.

## Coding

Correctness and quality (from `task-verify-workflow.md`'s Craft/Verification checklists and the
`code-reviewer` agent):

- Naming clarity and consistency with the codebase's existing conventions.
- Error handling: failure paths handled, no silently swallowed errors.
- Null / boundary handling: empty, max, and type-conversion cases.
- Thread-safety / concurrency safety, where the artifact touches shared state.
- No duplication — logic that already exists elsewhere is reused, not re-implemented.
- Resource lifecycle: no leaked handles, connections, or memory.
- Test coverage: tests are meaningful, in Given/When/Then shape, and cover the change's edge cases
  (boundary, error, empty, max, type conversion) — not just the happy path.

Security (from the `security-auditor` agent's OWASP/CWE-shaped coverage — adapt to what the Step's
artifact actually is; skip items that don't apply, e.g. web-only items for a batch job):

- Injection (SQL, NoSQL, OS command, template) — every user-controlled input traced to its sink.
- Authentication / access control — missing checks, IDOR, privilege escalation, unguarded admin paths.
- Sensitive data exposure — secrets in source, PII in logs, weak crypto.
- Insecure deserialization — untrusted data into an unsafe parser.
- Input validation at trust boundaries (API params, form fields, batch records).
- Known-vulnerable dependencies (manifest versions with disclosed CVEs).
- Security misconfiguration — debug mode left on, verbose errors, default/hardcoded credentials.

## Writing

From `task-verify-workflow.md`'s writing Craft/Verification checklist plus standard technical-writing
style-guide practice:

- Prose clarity and grammatical correctness — no ambiguous referent, no unresolved pronoun.
- Consistency with the document's existing voice and terminology — no synonym drift for the same
  concept.
- Active voice, imperative mood, one idea per sentence, for procedural content.
- Structure carries the argument — headings alone, read top to bottom, convey the point; no
  content-free heading.
- Every claim or reference fact-checked against its cited source — no unverified assertion stated as
  fact.
- Completeness — no material claim or requirement from the goal left unaddressed.

## Visual (diagrams, figures)

From `task-verify-workflow.md`'s dry-run Verification checklist:

- The diagram traced step by step against the behavior it claims to describe — every step and branch
  covered, none skipped.
- Notation and legend are clear and consistent with the document's existing conventions.
- Every label and arrow direction matches the relationship actually described in the surrounding prose.
- No orphan node or edge — everything drawn is referenced by the text, and everything the text
  describes is drawn.
