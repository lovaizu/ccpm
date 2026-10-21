# lane's UX

The UX is read by whoever builds or changes lane. It is remade on dev/architecture.md, as agreed at
62f0861, and on lane/README.decisions.md; what the agreed dev/lane/ux.md (6069bd1) says holds unless
a line here changes it.

## ux

### B-1: The users and their goals
- G1: The builder, whoever builds a Claude Code plugin whose work an AI does in several steps, wants
  every run of it to go the course they set, its steps that alone are not sure to hold kept by hooks,
  without writing a flow or a check.
- lane is called by an AI, the builder's Claude or a plugin's step, which puts lane's questions to
  the builder and sends back the answers (dev/architecture.md, Where the orchestrator runs).

### B-2: Key results, B-4: why each, B-7: order
- KR1.1: The defects the builder meets using lane as it is: the flow letting through a move that
  breaks the plugin's rules or refusing one they allow; a hook that does not notice a drift from its
  sentence in the forms the steps tell, or tells the AI of a call the sentence allows; a flow
  definition, step, setting or copy lane writes that must be changed or worked around; fewer is
  better, and none once the goal is reached. Each defect is work the builder does in lane's place.
- Judged against the version in use on the same plugins, with no target value.

### B-5: The scenes
1. The builder asks Claude to lay lanes on their plugin; Claude starts `lane:up`.
2. `lane:up` reads the plugin's skills and agents, and sends Claude, one at a time, each point the
   files do not settle and each fact found that the proposal rests on; Claude puts each to the
   builder and sends the answer back.
3. `lane:up` proposes the flow, its phases, the steps of each type of work and the approvals, and
   the lanes, each under the action it keeps, with the step as it would read and its hooks; the
   builder says OK or what to change.
4. On the OK, it writes the flow definition, the steps and the hooks, and puts lane's code in the
   plugin: a link in a plugin of the ccpm marketplace, a copy with its version elsewhere.
5. Run again where an older copy is, `lane:up` brings the copy, the flow definition's form and the
   hooks to its own version.
6. In a run, the flow refuses a move that breaks the plugin's rules, and a hook stops a call that
   drifts from a lane; the AI reads the sentence, prefixed by the plugin's name, and goes on as its
   steps say.
6a. At an approval, the orchestrator asks with Claude Code's AskUserQuestion; lane's hook
   refuses a call whose answers an AI filled in, records the option the caller chose, and the flow
   goes on only on that record (the user, 2026-10-21: D, after reading how cc-sdd, AI-DLC, Kiro,
   Spec Kit, BMAD, OpenSpec and superpowers keep an approval; only AI-DLC holds it in code, by a
   UserPromptSubmit hook, which also fires on a background subagent's report).
7. A run stopped anywhere goes on from its last move in a new conversation.
8. On a machine without Python 3.9 or later, the flow stops the run at its first move and the hooks
   stop the calls they watch, each asking for Python to be installed (R31).

### B-6: The benefits
- The builder answers and approves instead of writing a flow or checks; holding the course,
  noticing a drift and telling the sentence are lane's, and already tested.
- Every run goes the same course, its approvals counted only from the caller's own answer.
- Hooks are laid only where a step alone is not sure to hold, so they stay few.
