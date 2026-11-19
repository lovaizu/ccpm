# Lane's test gaps

This page is for whoever makes Lane's architecture and its cases. It names each place where Lane's
cases, in `dev/lane/tests/`, can't follow [the architecture](../architecture.md) or its skeleton in
`plugins/lane/`.

- S2: no record shows a Grep or a Glob that reaches a file never to read, so no case holds them.
  Each case waits for its record, made by `dev/tests/recorder/`.
