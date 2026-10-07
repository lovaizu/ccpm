"""The scenes writ is tried in, as the design's quality section names them.

Each opening is the user's request; a stand-in answers what writ asks from it alone.
"""

SCENES = {
    "migration-plan": {
        "benefits": ["understands it in one reading", "hand it straight on",
                     "judge from the report", "asked instead of covered over"],
        "source": "fixture",
        "opening": "/writ:up Write a TypeScript migration plan for the team's engineers, at "
                   "docs/migration-plan.md. This app is moving from JavaScript to TypeScript. Once "
                   "they have read it, the team agrees on which directories to move first, and each "
                   "engineer volunteers for the parts they want; they do not start moving code right "
                   "after reading. No one owns any part yet. The order of directories, how the UI is "
                   "built, and whether cli/ is included are not decided; the team decides them after "
                   "reading.",
        "look": "the owners and the open choices are left visibly undecided, each with the reason, "
                "and the report alone decides approval",
        "target": None,
        "reader": "an engineer on the team, who reads the plan before the team meets to agree which "
                  "directories to move first and who takes which part",
    },
    "typing-guide": {
        "benefits": ["understands it in one reading", "hand it straight on",
                     "asked instead of covered over"],
        "source": "fixture",
        "opening": "/writ:up Fix docs/typing-guide.md. The readers are the engineers who move files "
                   "from JavaScript to TypeScript; they read it to write types that pass review "
                   "without being sent back. The move has not started and tsconfig.json does not "
                   "exist yet. Whether `any` is allowed is not decided, and nothing beyond what the "
                   "guide says has been decided.",
        "look": "`any` comes back as a question and no rule on it is written; the parts readers "
                "used before the fix are kept",
        "target": "docs/typing-guide.md",
        "reader": "an engineer on the team, who is about to move a JavaScript file to TypeScript and "
                  "add types that pass review",
    },
}
