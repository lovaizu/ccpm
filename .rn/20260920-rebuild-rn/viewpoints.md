# Viewpoints: prompt authoring

An agent built from a prompt — a skill, a reference, a subagent's brief — generates and evaluates.
It does its best work when generation is handed the purpose and evaluation is handed the viewpoints
that decide whether the result does its job; steps alone get exactly what is written and nothing
the writer did not foresee. These are the viewpoints for judging such a prompt.

## Viewpoints

1. **Does the purpose lead?** Every part that asks for work says what outcome it serves, for whom,
   and why — so an agent meeting a case the text did not foresee still acts toward the outcome. NG
   when a part is a recipe whose aim a reader would have to guess.

2. **Is evaluation handed what decides the job?** Wherever a result is judged — by the agent itself
   or by another — it is judged on the few viewpoints that say whether the result serves its purpose,
   not on whether steps ran or a checklist was filled. NG when the judgment could pass work that
   fails its purpose, or fail work that serves it.

3. **Are steps kept to the work's rules?** Steps appear only where the work must go one fixed way —
   where output lands, what must happen (a commit, a file a later step reads, a format a machine
   parses) — and each still says why. NG when steps stand in for judgment the purpose should carry,
   or when a rule the work depends on is left as a bare "do not" with nothing that carries it out.

## Judging

1. Read the files you are given in full, as they stand now; a change can break a part it did not
   touch.
2. For each viewpoint, answer OK or NG. Quote the lines that decide it as `path:line`; for an NG,
   name the concrete case where an agent following this text would go wrong.
3. Leave out wording, line length and formatting unless they change what the agent does — they are
   not what these viewpoints judge.
4. Whether a purpose names the real need cannot be read off the text; it shows only when the prompt
   runs on a real case. Where your verdict depends on that, say so instead of guessing.
5. Return the verdict as your final message; write no files.
