# Evaluate a prompt

Evaluate a prompt — a skill, a reference, a subagent's brief — by whether an agent following it
reaches the purpose the prompt exists for, including in cases its writer did not foresee. Your
verdict is read by whoever asked for it, to choose the next move: rewrite the prompt, run it on a
real case, or take it to the human. It serves that choice when it says whether the prompt reaches
its purpose and which faults decide that.

## Structure

- **Are generation and evaluation split?** The result is evaluated by an agent other than the
  generator, without the generator's conversation. The generator's own check is never the final
  verdict.
- **Is the evaluator kept clear of the generator's pull?** It is handed the purpose, the viewpoints
  and the result — not the generator's account or excuses, and not an earlier round's verdict.
- **Does a role between them decide the next move by the purpose?** After each verdict, someone
  decides — by whether it serves the purpose, not by a count — to run again, change the viewpoints,
  return to the human, or stop.

## Generation

- **Is it handed the essential purpose?** It gets the purpose, not a recipe, and the purpose reaches
  past the surface of the request to why the result is needed.
- **Does it check its own result against that purpose?** Before returning, it checks whether the
  purpose is reached, not whether every step was done.

## Evaluation

- **Is it handed the essential viewpoints?** A few viewpoints drawn from the purpose, not a
  checklist of steps run or formats matched.
- **Does it evaluate whether the purpose is achieved?** It evaluates the result, not the work done —
  where it can, by running the result on a real case rather than reading its text. It neither passes
  work that misses the purpose nor fails work that reaches it over details.

## Work steps

- **Are only context-dependent work rules written as steps?** Steps carry what the agent could not
  know from the purpose: where output lands, the repository's conventions, the shape a later step or
  a machine reads. What the agent could judge from the purpose is not written as a step.
- **Are they steps, not rules or prohibitions?** Each is a step in the flow of the work, not a
  "must" or "never" set beside it — a rule beside the flow gets weighed against the flow, then
  dropped or applied where it does not fit; a step happens where it belongs.

## Evaluating

1. Read the files you are given in full, as they stand now.
2. State the purpose of the prompt you are evaluating, taken from the files themselves. Whoever asked
   you often wrote the prompt, so a purpose their request states is a claim to test against the
   files, not the yardstick. The questions above are answered against the purpose you state.
3. For each question above, answer OK or NG. Quote the deciding lines as `path:line`; for an NG,
   name the concrete case where an agent following the text goes wrong. A part the question asks
   about may live in a file you were not given — say where it would have to live, and answer NG
   only when it belongs in these files and is not there.
4. Where a verdict depends on running the prompt, name the real case that would settle it.
5. Return as your final message: first, whether the prompt reaches its purpose and the NGs that
   decide it; then the rest.
