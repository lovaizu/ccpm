# Baseline

The shortfalls of plugins made before this best practice, Lane and rn, which its questions must
catch, as the meta's Q10 asks of a best practice made from real cases. Each names the question that
catches it.

| Shortfall | Where it shows | Question |
| --- | --- | --- |
| The code came first and its tests after, with no case of real use run before it, so the user had both thrown out. | The decision "The code made before" under Q26 of `plugins/rn` and of `plugins/lane` in `.rn/20261107-rn/design-tree.json` | Q1 |
| Six of rn's seven hooks have no `onFailure: "block"`, and each exits 0 where `python3` is older than 3.9, so a `SubagentStop` or `Stop` check that can't run lets a role end unchecked. | `plugins/rn/hooks/hooks.json` | Q5 |
| rn's `PreToolUse` and `PostToolUse` hooks match `*`, and its `UserPromptSubmit` and `Stop` hooks match everything, so each tool call, prompt, and stop of every session with rn enabled starts `python3`, even where rn never runs. | `plugins/rn/hooks/hooks.json` | Q6 |
| rn depends on Lane by its bare name, with no range of versions, and Lane has no release tag to resolve a range against, so each change of Lane reaches rn's users untried with rn. | `"dependencies": ["lane"]` in `plugins/rn/.claude-plugin/plugin.json`, and `git tag` | Q10 |
| rn's description differs between its manifest and its marketplace entry, and neither plugin's manifest has `homepage`, `repository`, or `license`, while installing copies only the plugin's folder and not the repository's `LICENSE`. | `plugins/rn/.claude-plugin/plugin.json`, `plugins/lane/.claude-plugin/plugin.json`, and `.claude-plugin/marketplace.json` | Q11 |
| Each line of Lane's changelog runs to hundreds of characters, one of them 1,020, so a user can't see at a glance what a release changes for them. | `plugins/lane/CHANGELOG.md`, line 20 | Q11 |
