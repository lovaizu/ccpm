# Plugin authoring rules (ccpm)

Source: based on facts confirmed in the official docs (plugins-reference / plugin-marketplaces / skills at code.claude.com/docs).

## Language

- **Artifacts default to English** unless instructed otherwise — code, docs, READMEs, rule files, commit messages, and the like. Rationale: English reaches the widest audience, and it is a language AI models are heavily trained on.
- **Communication matches the other party's language** — PR descriptions, review comments, and console exchanges follow whatever language the person is using. Rationale: lower the communication cost for the people involved.

## Version number

- **Write `version` in exactly one place: `plugin.json`.** Do not put `version` in `marketplace.json`.
  - Resolution order is `plugin.json` → marketplace entry → git commit SHA. **When both are set, `plugin.json` wins**, so a `version` in the marketplace entry is redundant and meaningless.
  - The top-level `version` in the marketplace is "manifest metadata" and is not used to detect updates for users.
- **Always set `version` in `plugin.json`** (semver, e.g. `0.1.0`).
  - `claude plugin validate --strict` warns and then fails when `version` is unset.
- **What it means (from the user's side):** pinning a version means users receive an update **only when you bump it**. Raise the version with each release.
  - Omitting it makes every commit a new release (the commit-SHA strategy, suited to active development), but to pass `--strict` this repo's policy is to keep `version` in `plugin.json`.

## Validation gate

- Structural validation must pass both `claude plugin validate <plugin-path> --strict` and `claude plugin validate <marketplace-root> --strict`.
- Confirm behavior headlessly: `claude -p "/<plugin>:<skill>" --plugin-dir <plugin-path>` (skill namespace = plugin name).
