# lane UX

lane lays a lane where a step alone is not sure to hold: a sentence of the step with a hook that
notices a drift from it and tells the AI the sentence again. Build and change every part of lane so
that it does what its README and lanes say, with no defect.

## Users and goals

- G1: The builder, whoever writes the steps of an agent, wants the steps that are not sure to hold
  kept by hooks, without writing a check.

## Key results

- KR1.1: The defects the builder meets using lane as it is: a hook that does not notice a drift from
  its sentence in the forms the steps tell, tells the AI of a call the sentence allows, or a step,
  setting or copy lane writes that must be changed or worked around; fewer is better, and none once
  the goal is reached.

  Each defect is work the builder does in lane's place, and one they miss is a hook that does not
  keep the AI to its step.

## Scenes

- The builder writes an agent's steps, and types `/lane:up`.
- lane asks, one point at a time, what it needs: which steps to lay lanes on, offering the agents
  just written, then what the files do not settle, such as which files a step alone writes; the
  builder answers each.
- lane proposes the lanes to lay where a step alone is not sure to hold, each under the action it
  keeps, with the step as it would read and the hooks that keep it; the builder says OK or what to
  change.
- On the OK, lane writes the steps and the hooks, and puts its code where the steps are, once for
  all of them: a link in a plugin of the ccpm marketplace, a copy with its version anywhere else.
- Run again where an older copy is, `/lane:up` brings the copy and the hooks to its own version.
- In a run, the AI makes a call that drifts from a lane; Claude Code does not run it, and the AI
  reads the lane's sentence, prefixed by the name of the plugin, or of the agent.
- On a machine without Python 3.9 or later, the hooks stop the calls they watch and ask for Python
  to be installed.

## Benefits

- The builder answers and approves instead of writing checks; noticing a drift and telling the
  sentence are lane's, and already tested.
- Hooks are laid only where a step alone is not sure to hold, so they stay few.
