# Language rules (ccpm)

Which language to write in, depending on whether it is an artifact or a live exchange.

## Artifacts

- **Default to English** unless instructed otherwise — code, docs, READMEs, rule files, commit messages, and PR titles and descriptions.
- Rationale: English reaches the widest audience, and it is a language AI models are heavily trained on. These outputs persist and get browsed later, so the audience is broad rather than one specific person.

### Exception: a plugin whose users are limited to one language

- **When a plugin's users are limited to a single non-English audience (e.g. Japan), the artifacts that *user* reads are written in that language** — the plugin's own `README.md` and the fill-in templates / deliverables a user produces with it. Everything else stays English: the AI-instruction prompts (`SKILL.md`), code, the plugin and marketplace metadata and its `description`, `CHANGELOG.md`, the root `README.md` listing, and commit / PR text.
  - Rationale: the default's premise — a broad, unknown audience — does not hold here. If the tool only makes sense for, say, Japanese client proposals, the person reading its README and filling its templates reads Japanese; English would raise their cost for no added reach. The AI-facing prompt and the machine / market-facing metadata keep their broad audience, so they stay English.
- **Decide a plugin's audience before creating it.** Whether its users are language-limited is not something to infer mid-build — **confirm it with the user first, and state it explicitly in that plugin's steering** (as a decision entry), so the language split is fixed up front instead of re-litigated file by file.

## Communication

- **Match the other party's language** — review comments and console exchanges follow whatever language the person is using.
- Rationale: lower the communication cost for the specific person you are talking to.
