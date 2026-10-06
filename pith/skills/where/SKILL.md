---
name: where
description: This skill should be used when writ, rn or another plugin's conductor needs the location of pith's own files, such as its essentials files, style rules and lint, to hand them to an agent. It returns pith's directory.
user-invocable: false
---

pith's files are under `${CLAUDE_PLUGIN_ROOT}`: the essentials files in `references/essentials/`, the style rules in `references/style.md`, the lint in `references/lint/`, and the result file's form in `references/result-form.md`, checked by `python3 scripts/check_result.py <result file>`. Use these paths as they are.
