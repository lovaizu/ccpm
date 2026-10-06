# Result file form

Write the content in the user's language; the labels below stay as written. `scripts/check_result.py` checks a file against this form before pith returns.

```
# Check: <target path>

Target: <path>
Receiver and purpose: <text>
Aim: <text>

## <essentials file name>: <question word for word>

Report: <the first user's report for this question; may span lines>

- Good: `<path>:<line>` <what the receiver gains>
  - Evidence (work): "<quote from the work>"
- More: `<path>:<line>` <the struggle>
  - Evidence (report): "<quote from the report above>"
  - Left because: <reason, once a More is left>
```

`<line>` is one line or a range `a-b`. Paths are relative to the repository root.

## File name

`{dir}/open/{NN}-report-{target}.md`. `{NN}` is two digits, one more than the highest number already in `open/`. A recheck rewrites the same file and replaces only the sections of the questions it rechecked.
