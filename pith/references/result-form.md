# Result file form

Write the content in the user's language; the labels below stay as written. Whoever writes the file, pith or the caller settling it, checks it against this form with `scripts/check_result.py <result file>`, run from the repository root.

```
# Check: <target path>

Target: <path>
Receiver and purpose: <text>
Essentials: <path of each essentials file, separated by spaces>
Aim: <text>

## <essentials file name>: <question word for word>

Report: <the first user's report for this question; may span lines>

- Good: `<path>:<line>` <what the receiver gains>
  - Evidence (work): "<quote from the work>"
- More: `<path>:<line>` <the struggle>
  - Evidence (report): "<quote from the report above>"
  - Left because: <reason, once a More is left>
```

`<line>` is one line or a range `a-b`. Paths are relative to the repository root, or absolute.

## File name

`{dir}/open/{NN}-report-{target}.md`. `{NN}` is two digits, one more than the highest number already in `open/`. Checking the same target again writes the same file.

## Settling and clearing

The caller settles each More: a fixed one is rewritten as the Good it now is, with evidence from the work as it is now; a left one gets `Left because:`. A fix is confirmed by doing again what the first user did where the More was found and seeing that it no longer happens, not by another check: a new first user brings fresh small remarks with every run. Once every More is settled, the conductor that talks with the user copies the file whole into a commit message, ends each More there with `→ fixed:`, `→ let go:` and the reason, or `→ to the user:`, and deletes the file in that commit, so `open/` holds only what still needs action and the record stays in git.
