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
    "release-notes": {
        "benefits": ["write essentials worked back from the purpose"],
        "source": "fixture",
        "opening": "/pith:up Write essentials for our CLI's release notes. Put them at "
                   "docs/essentials/release-notes.md. The readers are the developers in the company "
                   "who use this CLI, reading to decide whether to upgrade now. The CLI is in cli/, and "
                   "docs/releases/ holds its real release notes.",
        "look": "every question is answered from what happened in use, and the answers decide "
                "whether to upgrade on 1.4",
        "target": None,
        "reader": None,
    },
    "readme": {
        "benefits": ["understands it in one reading", "hand it straight on"],
        "source": "repo",
        "opening": "/writ:up Fix writ/README.md. The reader is a Claude Code user who has not used "
                   "writ: they read it top to bottom to decide whether to install writ, and then use "
                   "it on their own documents and work. Once finished, they should grasp what writ "
                   "does for them and how to use it, through examples they can picture as their own "
                   "work. The README's facts must match writ's prompts and design in this repository "
                   "(writ/skills, writ/agents, writ/docs/design.md). Do not ask me anything; return "
                   "any question as your result.",
        "look": "the parts readers used before the fix are kept",
        "target": "writ/README.md",
        "reader": "a Claude Code user who has not used writ, deciding whether to install it and then "
                  "how to use it on their own documents",
    },
    "design": {
        "benefits": ["understands it in one reading", "hand it straight on"],
        "source": "repo",
        "opening": "/writ:up Fix writ/docs/design.md. The reader is whoever builds or fixes writ, and "
                   "the user who approves its design: they read it top to bottom before changing "
                   "writ's prompts, agents or hooks. Once finished, they should grasp how writ brings "
                   "the README's benefits: who takes part, what passes between them, and why each "
                   "decision was made, so they can change writ without breaking a decision. The "
                   "design's facts must match this repository (writ/README.md, writ/skills, "
                   "writ/agents, writ/hooks). Do not ask me anything; return any question as your "
                   "result.",
        "look": "the parts readers used before the fix are kept",
        "target": "writ/docs/design.md",
        "reader": "whoever is about to change writ's prompts, agents or hooks without breaking a "
                  "decision in its design",
    },
}
