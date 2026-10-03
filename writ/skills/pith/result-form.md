# Result file form

The result file is read by the user, by a caller such as rn, and by later versions of writ, so its form is the same in every version. Write the content in the user's language; the labels below stay as written. `scripts/check_result.py` checks a file against this form before pith returns.

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

- `{NN}` shows the order the files arrived in.

    The user opens `open/` and reads what waits for a decision in the order it came.

## What must always hold

- The top names the target, its receiver and purpose, and the aim.

    A later reader knows what each Good and More was compared with, without going back to the conversation.

- Each question has its own section, headed by the essentials file's name and the question copied word for word, with the first user's report and at least one Good or More under it.

    The file name lets the user read the question in its essentials file. With the same characters, the script can match every question against the essentials file and find one left without an answer.

- Every Good and More has a location as `path:line` and evidence quoted from the report or the work.

    The location lets the user look at that place instead of the whole work. The evidence lets the user check the judgment instead of trusting it. Both are in a fixed form, so the script can check that the location exists and the quoted text is really there.

- A Good says what the receiver gains, a More says the struggle, and a left More says why it was left.

    What the receiver gains shows what must not be lost when the work is fixed. The struggle lets the user decide by its effect on the receiver whether to accept a left More. The reason shows the More was left by a decision, not missed.
