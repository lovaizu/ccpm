Design points to fix, from the conductor's Mores in 01-report-design.md, waiting for writ.

- M1, writ/docs/design.md:82: a path counts as the first user's own saved output only when Claude
  Code itself recorded it so in the first user's own transcript: a tool result whose text begins with
  Claude Code's wrapper `<persisted-output>` and names the path after `Full output saved to: `, or
  whose structured `toolUseResult.persistedOutputPath` is that path. A path that only appears
  elsewhere in the record, typed in a tool call or printed by a command, does not count.
  - Why: M1 lets through only what is shown to be the first user's own; a path it printed or typed
    shows only that it saw the path, not that its call made the file.
  - Checked on this machine: Bash saved outputs carry the wrapper on 2.1.278, 2.1.282, 2.1.285 and
    2.1.291; `persistedOutputPath` is present on 2.1.278, 2.1.282 and 2.1.291 but absent on the
    2.1.285 records, so the wrapper is the form both rest on.
- M1, writ/docs/design.md:82: the path in the call is compared with the recorded one as the same
  file, after `~` is expanded and the path is normalized, so `..` or another spelling neither opens
  another file nor stops the own one.
- A1, writ/docs/verification.md:53: the let-through is tested by Read, Grep and Bash, as the scene
  allows.
