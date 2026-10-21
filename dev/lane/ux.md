# lane UX

lane is a library of ready checks that a builder links into their plugin and sets beside each step,
so the plugin's AI, drifting from the step, is told its way. Build and change every part of lane so
that it does what its README and checks say, with no defect.

## Users and goals

- G1: The builder, whoever builds a plugin in the ccpm marketplace whose AI works through steps,
  wants to pair each step with its hook by setting one of lane's checks as it is.

## Key results

- KR1.1: The defects the builder meets setting lane's checks as they are: a check that does not
  notice the drift it is for in the forms the steps tell, stops a call the step allows, or must be
  changed or worked around to serve a step it is said to fit; fewer is better, and none once the goal
  is reached.

  Each defect is work the builder does in lane's place, and one they miss is a hook that does not
  keep the plugin's AI to its step.

## Scenes

- The builder writes a step, and links lane into their plugin.
- They choose, from lane's checks, the one that fits the step, and add it to their plugin's
  `hooks/hooks.json` with the agent it watches and what it says.
- In a run, the watched agent makes a call that drifts from the step; Claude Code does not run it,
  and the agent reads what the check says, prefixed by the plugin's name.
- On a machine without Python 3.9 or later, the check stops the calls it watches and asks for Python
  to be installed.
- Where no check fits a step, the builder adds one to lane, and every plugin can set it.

## Benefits

- The builder writes the step and one line of hook settings; noticing the drift, stopping the call
  and telling the step's way are lane's, and already tested.
