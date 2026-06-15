# cmux drive primitives (LIVE-confirmed)

The three primitives a loop watcher needs to drive a Claude Code surface: interrupt
(ESC), type-and-submit a slash command, and read the screen. Each is confirmed with a
LIVE run against a throwaway workspace (`surface:21`, cwd `/tmp`) created for this spike,
running real interactive Claude Code on Claude Max (no `-p`, no SDK).

cmux binary: `/Applications/cmux.app/Contents/Resources/bin/cmux` (on PATH as `cmux`).

## Surface targeting (the form every command uses)

All three verbs default to `$CMUX_SURFACE_ID` / `$CMUX_WORKSPACE_ID`. **Always pass an
explicit `--surface <id>`** — a bare command silently hits the caller's own surface.
Ref forms accepted: `surface:<n>` (index ref) or the UUID. List them with
`cmux tree --id-format both`. Examples below use `surface:21`.

```
cmux send       --surface <id> <text>
cmux send-key   --surface <id> <key>
cmux read-screen --surface <id>
```

## (a) Send ESC that stops an in-progress Claude Code response

ESC key name is **`escape`** (lowercase). The observed interrupt below is itself the
proof the name is valid and effective: an unrecognized key would not have stopped
generation.

```
cmux send-key --surface <id> escape
```

**Observed (surface:21):** a 600-word essay was actively streaming (context climbing
0%→10%, `● high · /effort` indicator showing active generation). One `send-key … escape`
stopped it mid-sentence. `read-screen` after showed the response cut off at
`In 1873, Sholes sold his design to the Remington company, a firm` followed by the
interrupt marker:

```
  ⎿  Interrupted · What should Claude do instead?
```

and the `/effort` active-generation indicator disappeared from the footer. This is the
canonical "stopped" signal a watcher can detect.

## (b) Type a slash command and submit it

Two calls: `send` types the text into the prompt, `send-key … enter` submits it.

```
cmux send     --surface <id> '/help'
cmux send-key --surface <id> enter
```

**Observed (surface:21):** `/help` landed in the prompt and ran — `read-screen` showed the
help panel header `Help  General   Commands   Custom commands`. Generic text+submit was
also proven in Stage A:

```
cmux send     --surface <id> 'echo hello-cmux-7f3'
cmux send-key --surface <id> enter
```

`read-screen` then showed:

```
❯ echo hello-cmux-7f3
hello-cmux-7f3
```

so `send <text>` + `send-key enter` reliably types and submits, for both a shell command
and a Claude Code slash command.

## (c) Read a surface's screen

```
cmux read-screen --surface <id>
```

**Observed (surface:21):** returns the rendered pane text (TUI box-drawing included). It is
the read used to confirm every result above — the shell prompt `❯`, the `hello-cmux-7f3`
output, the streaming essay, and the `⎿  Interrupted` marker were all read this way.
(`capture-pane` was not needed; `read-screen` returned the full pane content.)

## Fragility notes for the watcher (later task)

- **PTY-attach gotcha.** A freshly created HIDDEN workspace/surface does not spawn a PTY;
  `send`/`read-screen` return `invalid_params: Surface is not a terminal`. Create with
  `--focus true` so it is frontmost, then WAIT real wall-clock time for the PTY to come
  up. Confirm a shell prompt (`❯`) is visible via `read-screen` BEFORE typing. Foreground
  `sleep` is blocked in the harness — poll across separate calls or use a background loop.
- **Always pass `--surface`.** Omitting it defaults to the caller's own surface and would
  interrupt the orchestrator. Never run a bare `send`/`send-key`/`read-screen`.
- **`surface-health` without `--surface` is unreliable** — observed it reporting a
  different surface (`surface:16`) than requested. Prefer `read-screen --surface <id>`
  (looking for the shell prompt) as the readiness probe, not `surface-health`.
- **send/submit is two calls, not atomic.** `send` then `send-key enter` are separate;
  there is a small race window. In practice both landed reliably in this spike, but a
  watcher should read-screen to confirm the submit took rather than assume it.
  - A single-call form exists: `cmux send --help` documents that `\n` and `\r` in the
    text send Enter (e.g. `cmux send --surface <id> 'echo hi\n'`). This was confirmed for
    **shell** input only; it was **not** tested against the Claude Code TUI prompt, where a
    literal newline may insert a line rather than submit. So the verified two-call
    `send` + `send-key enter` remains the default for driving the CC prompt.
- **Detecting "still generating" vs "stopped":** while generating, the footer shows the
  `● high · /effort` active indicator and context % climbs; after ESC the indicator is
  gone and `⎿  Interrupted` appears. Read-screen polling on these markers is how the
  watcher knows when a response is in-progress vs interrupted/done.
