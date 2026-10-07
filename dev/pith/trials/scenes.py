"""The scenes pith is tried in, run with pith alone by writ's trial runner, which pith shares with
writ along with its fixture: `python3 dev/pith/trials/run.py <command> <scene> <workdir>`."""

PR_REVIEW_AIM = (
    "The receiver is a Claude running in CI; for each PR it reads the diff with this prompt and writes "
    "a comment. The aim: never miss an API change that would break src/ui/api-client.js, and comment "
    "on nothing else. When a break looks intentional (for example, the UI fix is planned for a later "
    "PR), still comment: pointing it out is cheap, and whether it is fine to merge is the PR author's "
    "call, not the reviewer's. When it cannot tell for sure whether a call breaks, comment anyway and "
    "say plainly that it is unsure and why; a false alarm costs less than a miss. For the fix, it may "
    "suggest the obvious change to api-client.js, but when there is more than one reasonable way "
    "(update the UI, or keep the old API working), list the options briefly and leave the choice to "
    "the PR author."
)

SCENES = {
    "pr-review-hole": {
        "benefits": ["check by what happened in use"],
        "source": "fixture",
        "opening": "/pith:up check .github/prompts/pr-review.md. " + PR_REVIEW_AIM,
        "look": "a More points at the missing check on response fields, with what happened in use as "
                "its evidence",
        "target": None,
        "reader": None,
    },
    "pr-review-sound": {
        "benefits": ["check by what happened in use"],
        "source": "fixture",
        "opening": "/pith:up check .github/prompts/pr-review.good.md. " + PR_REVIEW_AIM,
        "look": "the question the other scene's More answers comes back Good",
        "target": None,
        "reader": None,
    },
    "export": {
        "benefits": ["write essentials worked back from the purpose"],
        "source": "fixture",
        "opening": "/pith:up Check cli/src/export.js. Engineers run `taskctl export` to put tasks into "
                   "a file they share. The aim is that the file holds exactly the tasks asked for, and a "
                   "wrong option stops with a message.",
        "look": "pith writes .pith/essentials/code.md, every question is answered from what happened "
                "when the code was called, and a More shows a mistyped --since taken without a word",
        "target": None,
        "reader": None,
    },
}
