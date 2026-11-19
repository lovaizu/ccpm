# Lane's test gaps

This page is for whoever makes Lane's architecture and its cases. It names each place where Lane's
cases, in `dev/lane/tests/`, can't follow [the architecture](../architecture.md) or its skeleton in
`plugins/lane/`. Every integration case also waits for the double of Claude Code, as
[the skeleton's gaps](../skeleton-gaps.md) say.

- S9 and Route: a command that a route of a running run waits for and a command that starts its
  own skill's run are both a route `after: {"command": ...}` of `lane/rules.json`, and both reach
  the guard as a UserPromptExpansion, which `guard.answer` hands to `skill_called` as a skill's
  call while `command_typed` takes it as a `typed` move. No part decides which one a command is,
  so `test_a_typed_command_that_a_route_waits_for_puts_its_starts_in_place` and
  `test_another_skills_command_typed_while_a_subagent_runs_starts_its_run_beside` can't both
  hold.
- S9 and Run: a subagent stopped by TaskStop has its start due again, as
  [Claude Code's states](../claude-code-states.md#what-the-guard-answers-in-each-single-behavior)
  say, but `guard.result_reached` changes nothing, and `record.Entry` has no kind for a start that
  ended with no result. `routes.due` still counts that start as made, so no part gives it due at
  the main conversation's later Stop, as
  `test_a_subagent_stopped_by_task_stop_is_due_again` checks.
- S4 and rule types: neither the architecture nor `lanes/commands.py` says when a Bash call's
  command is one that a rule of commands names: the whole line, its first words, or each command
  of a pipeline. The AI writes `git -C <repo> log --oneline` for `git log`, as
  `claude-code-2.1.322.jsonl` shows, so the cases run only the command as the rule names it.
- S2: no record shows a Grep, a Glob, or a Bash command that reaches a file never to read, so no
  case holds them, and `lanes/reads_none.py` judges a Grep and a Glob but no Bash command.
  Each case waits for its record, made by `dev/tests/recorder/`.
