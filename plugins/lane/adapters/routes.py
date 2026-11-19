"""Lane's route adapter: which roles a plugin's fixed order makes due now, from the routes of its
lane/rules.json and the run as it stands."""

from __future__ import annotations

import json
import os
import sys

# The form of the rules and of what an order takes and gives lie in hooks/lane/, found from this
# file's real path, wherever Lane lies, so they're imported only once the path holds it.
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "hooks", "lane")
)

from adapters import OrderRun, StartDue
from rules import Route, read_rules


def starts_due(routes: list[Route], run: OrderRun) -> list[StartDue]:
    """The starts due of the run by the routes.

    Takes: the plugin's routes, and the run as its order sees it.
    Gives: each role that the route after the run's latest result or command makes due, as many
    times at once as the route names it, less each start of it made since; the command that called
    the run, given again, leaves the starts due as they stand, as S10 draws; none where no route
    goes after the latest result or command, or each start it makes due is made, so that the run
    ends once no start of it runs.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("routes.starts_due")


def main() -> int:
    """Reads what Lane gives an order on standard input, in the form of
    starts_due.in.schema.json, and prints the starts due by the routes of the plugin's
    lane/rules.json, in the form of starts_due.out.schema.json."""
    given = json.load(sys.stdin)
    rules = read_rules(given["plugin_root"])
    routes = rules.get("routes", []) if rules else []
    print(json.dumps({"starts": starts_due(routes, given["run"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
