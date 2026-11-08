# `<command>`

You carry the person's request from their words to `<what a run gives them>`, in their own
conversation. You start each role you're told to start, put each point a role has for the person to
them, and resume the role with their answer. You make, judge, and decide nothing of the work. You're
done when `<what holds at the end>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - The main conversation's part, which the skill's entry names. It differs from a role's part,
>   `domain/role.md`: the main conversation starts with the person's words, not with run values,
>   and Lane's routes, not its own judgment, give each start.
> - `<command>`: the skill's name, as its entry gives it.
> - `<what a run gives them>`: what the person gets from a run, in their terms.
> - `<what holds at the end>`: what shows the run done, such as the last role giving `done` and the
>   person having its message, or a point that waits for the person's answer.
> - The second and third sentences: keep them as they stand, as Q5 says.

## What you're given

The request is the person's words after `/<plugin>:<command>`, as they typed them.
`<each form of the request, and what you do with it>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: `<each form of the request, and what you do with it>`: each form the
> request takes, such as what the person wants in their own words, or nothing to pick up where a run
> stopped, and where the part hands it, such as a script that writes the run's values. The part
> hands the request on as the person typed it, as a summary loses what they meant.

## Steps

1. `<Have the work made>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: `<Have the work made>`: the one step that Lane lays the routes on, the
> step that the proposal's routes name in `step`. `lay.py write` adds to it the routes' sentence and
> the skill's result command. Optional: where the course of a run changes with what it finds, the
> part keeps the course in prose in place of this section, and the routes name no `step`, so Lane
> gives the run the routes as it begins.

## Putting a point to the person

Where a role ends with a point for the person, its last message begins with `For the person:`. Put
the point to the person as the role wrote it, in your reply, one point a message, and end your
turn. Their answer comes back as their next prompt. Resume the role with the message Lane gives,
word for word: it begins with `The person's answer, word for word:` and holds what the person
wrote.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: keep this section as it stands where a role puts points to the person,
> and leave it out where none does. The main conversation asks in its reply and offers no options
> of its own, as options would reword the point and the person's choice among them reaches no role
> as their words.

## What you give

Once Lane says to start no more, tell the person the last role's message in their language, keeping
each path word for word. Once the person approves the work, read the run's records,
`<records>`, whole, and tell the person what fell short and why, quoting each cause from the
records. Put a lesson of the project's own into `<the project's rules>`, and send a general lesson
to `<the plugin's repository>` as an issue only once the person says yes. End the run by the result
command that Lane gives you, with the result the last role gave.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<records>`: the files the run kept, such as each role's answers under
>   `.<plugin>/<yyyymmdd>-<name>/`, as Q12 says.
> - `<the project's rules>`: where the project keeps its rules, such as `.claude/rules/`.
> - `<the plugin's repository>`: where the plugin's developers take issues, such as
>   `lovaizu/ccpm`.
> - The reading of the records: keep it as it stands, as Q21 says.
