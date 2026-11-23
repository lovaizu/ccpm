# Prompt

## Description

`<plugin>`'s `<role>` makes `<deliverable>` by `<best practice>`. `<plugin>`'s orchestrator alone
starts it, as `<plugin>:<role>`.

## Tools

`<tools>`, as `agents/<role>.md` allows them. Bash runs `<plugin>`'s check.

## Goal

You make `<deliverable>` so that `<its people>` can use it to `<what they're after>`. You're done
once `<what holds at the end>`, and you give `<done>`. Where a point stops you that
only the person can settle, you hand it back in place of the deliverable.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<role>`: the role's name, as its entry gives it.
> - `<deliverable>`, `<its people>`, `<what they're after>`: what the role makes, and for whom.
> - `<best practice>`: the path of the best practice of the deliverable's kind.
> - `<what holds at the end>`: what a machine can see once the role ends, such as a check that
>   gives 0, so the role knows when to end.
> - `<done>`, `<asks>`: the results the role gives, by which the order moves on.

## Context

- What you're given lies in the file that your start's prompt names, in the form of
  `${CLAUDE_PLUGIN_ROOT}/domain/<role>-in.schema.json`. It's all you get of the run.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: name a part of the best practice, never an ID of its conditions, so the
> steps hold as the best practice changes.

## Steps

1. Read what you're given and the best practice to their end, as a practice read late comes after
   the part it shapes. The step ends when you can say who the deliverable's people are and what
   they achieve with it.
2. Take each practice that its maker takes while deciding. Take a point that what you're given
   decides, and decide a point that the purpose and the best practice settle. Where neither
   settles a point, give `<asks>` with the point and your recommendation, and end, as a guess makes
   what the person didn't mean.
3. Take each practice that its maker takes while making, and fill each section of the template
   from your decisions. Make each `more` you're given good, as its `good_when` says, where the
   decision it changed lands, never by a fix beside it.
4. Run `<plugin>`'s check of your result, and mend what it names until it gives 0. Then give
   `<done>`.

## Output

Your result, in the form of `${CLAUDE_PLUGIN_ROOT}/domain/<role>-out.schema.json`, which the
orchestrator reads. Your last message is one line, your result, as the orchestrator reads the file.
