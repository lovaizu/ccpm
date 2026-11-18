"""The states of writer's Start in write's Run that the state transition cases share, each as the
run record's lines that bring it about, with the walkthrough's Routes and a resume of writer after
reviewer's `more`."""

from __future__ import annotations

import lane_data as d
from form import Move
from run_record import Called, Ended, Gave, Started, Tied

ROUTES = (
    d.route(d.After("first"), Move("start", role="writer")),
    d.route(d.After("result", role="writer", result="written"), Move("start", role="reviewer")),
    d.route(d.After("result", role="reviewer", result="more"), Move("resume", role="writer")),
    d.route(d.After("result", role="reviewer", result="good"), Move("no_more", result="good")),
)
TEXT = "Carry out your steps"
CALLED = Called("r1", "write", "")
WRITER = Started("r1", "writer", TEXT, {}, "toolu_w", False)
TIED = Tied("r1", "toolu_w", "a01")
GAVE = Gave("r1", "writer", "written", "a01")
END_FIRST = Ended("r1", "a01", False, "toolu_w")
# A resume that no Route opens, as the guard adds it with its tie at the SendMessage's PreToolUse.
RESUME = (
    Started("r1", "writer", "Go on", {}, "toolu_w2", True, False),
    Tied("r1", "toolu_w2", "a01"),
)

UNTIED = (CALLED, WRITER)
RUNNING = (*UNTIED, TIED)
GAVE_RUNNING = (*RUNNING, GAVE)
ENDED_BARE = (*RUNNING, END_FIRST)
ENDED_GAVE = (*GAVE_RUNNING, END_FIRST)
RESUMED_BEFORE_END = (*GAVE_RUNNING, *RESUME)
RESUMED_AFTER_END = (*ENDED_GAVE, *RESUME)
# A resume that reviewer's `more` opens, after writer's first pass and reviewer's ended.
RESUMED_OPENED = (
    *ENDED_GAVE,
    Started("r1", "reviewer", TEXT, {}, "toolu_r", False),
    Tied("r1", "toolu_r", "a02"),
    Gave("r1", "reviewer", "more", "a02"),
    Ended("r1", "a02", False, "toolu_r"),
    Started("r1", "writer", "Go on", {}, "toolu_w2", True),
    Tied("r1", "toolu_w2", "a01"),
)
