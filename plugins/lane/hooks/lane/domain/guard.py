"""What the guard does on each hook event: which line it adds to the run record, which check it asks
of the lane types or the adapter, and what it answers, by Lane's rules that only the main
conversation starts the roles, that a Run moves only on a Result from result.py, and that the guard
checks only within a Run."""

from __future__ import annotations

from events import Answer, Event


def handle(event: Event, root: str) -> Answer:
    """The guard's answer to one hook event of the plugin.

    Takes: the event, and the plugin's folder, whose hooks/lanes.json holds the Lanes, the Routes,
    and the adapters.
    Gives, and adds to the run record, by what the event is:
    - a skill's call (S1, S3, S5, S7): adds the call of a new Run, by a person or an AI, or picks
      the Run up from the record or the Kept results, and answers the first start due or where the
      run picks up; for another plugin's skill that a move names, adds it so that the Run stands
      aside;
    - a prompt typed (S2, S5): adds it to each Run of the conversation, so that the moves of a
      Route after a typed command are due;
    - a start or resume (S5, S6): checks it by `lanes.check_start` with the Lanes of the role that
      makes it, and adds the Start where it's due, lets a resume that the Routes open none for
      through, and stops any other with the moves due, or a subagent's start of a role with the
      sentence of the Lane on its last Step;
    - the PostToolUse of a start (S5): adds the tie of the Start to its agent_id;
    - the PostToolUse of result.py that gave 0 (S2, S5, S6): adds the Result, for the subagent's
      Start where it has an agent_id;
    - the PostToolUse of lay.py print (S1): adds what it showed, with the Proposal's ID;
    - any other call (S2, S5, S6): checks it by each Lane of each Run that holds it, and lets it
      through or stops it with the Lane's sentence and what the role may do;
    - a subagent's end (S6): checks it by each Lane of the role, and stops it with a broken Lane's
      sentence, that of the Lane on its last Step where it gave no Result since its Start;
    - a subagent's end reaching the main conversation (S5): adds the end, and answers the Result and
      the moves of its Route, or, ended with no Result, its start due again;
    - the main conversation's end of its turn (S2, S5): stops it with the moves due where a move is
      due and no subagent of the Run runs, unless the move waits for the person; else checks it by
      each Lane of each Run's skill;
    - an event outside every Run: lets it through and adds nothing.
    Changes: the run record, by the lines above, and whatever an adapter or a command of the
    plugin's changes.
    Refuses: nothing; where lanes.json, the run record, an adapter, or a Lane can't be read or
    run, it stops the event with why and who must fix it, except an adapter that fails at the
    skill's call, whose start it gives with why while it lets the call run.
    Carries: each `CC->>G` arrow of S1 to S7, and each `G-->>` answer.
    """
    raise NotImplementedError("guard.handle")
