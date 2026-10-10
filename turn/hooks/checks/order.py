"""The first user uses what was made before anything else, and the learner learns from each use
before anything else; a turn ends done only after both."""


def check(done, now):
    """What must come before `now` (maker, made, first-user, learner or done), given the calls
    `done` made so far in this turn."""
    unused = unlearned = used = False
    for what in done:
        if what == "made":
            unused = True
        elif what == "first-user":
            unused, unlearned, used = False, True, True
        elif what == "learner":
            unlearned = False
    if now == "learner":
        return [] if unlearned else ["nothing to learn from yet: have turn:first-user use the work first"]
    if unlearned:
        return ["have turn:learner learn from the last use first"]
    if now in ("maker", "done") and unused:
        return ["have turn:first-user use what was made first"]
    if now == "done" and not used:
        return ["the work has not been used: have turn:first-user use it first"]
    return []
