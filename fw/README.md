# fw

The common base for plugins in this marketplace that have AI make something for their user. A plugin
built on fw writes only its domain parts; fw holds the task flow, the four roles, the record and the
checks, so they are fixed and tested once for every plugin.

Requires Python 3.9 or later; fw's hooks run on it.

## What a plugin built on fw writes

- An entry skill that calls the `fw:flow` skill with four lines:

    ```
    record: .<plugin>
    domain: ${CLAUDE_PLUGIN_ROOT}/fw
    issues: <owner>/<repository> where the session's process learnings may be sent
    request: $ARGUMENTS
    ```

- A domain folder, `<plugin>/fw/`, holding for each role (`make`, `use`, `learn`) its instructions
  (`<role>.md`) and the CCS entries it needs before it starts (`<role>.json`, a list of
  `{"component", "type", "from"}`), and, when the conductor needs it, `conductor.md`: what the plugin
  makes and how to fill and judge it.
- `"dependencies": ["fw"]` in its `plugin.json`.

## What fw does in the user's session

- The conductor agrees with the user what they want, one point at a time, then runs each task: the
  maker makes the work, a first user who knows nothing of the discussion uses it once, the learner
  learns from the turn, and the conductor judges, has differences fixed and the stumbled places
  rechecked. Each role agrees with the conductor what it will do before it works.
- The record in `<record>/` (the steering and one CCS per role in each task's folder) is committed,
  so the work goes on from the same state after the conversation is cleared.
- The hooks stop a role from starting, or being told go, without what that step needs, and say what
  is missing; they act only on fw's own roles and their CCS.
- At the end, the conductor asks whether to send the process rules learned in the session to the
  plugin as an issue, and sends them only on yes.
