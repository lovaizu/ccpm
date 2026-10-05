"""The scenes writ is tried in, one or two per benefit, as the design's quality section names them.

`source` is "fixture" (the sample app in fixture/) or "repo" (this repository at HEAD).
`user` is what the user knows and has decided; the user plays from it alone.
`target` is the document a reader reads afterwards, and `reader` who reads it and why.
"""

MIGRATION_USER = """\
You lead a team whose app (this repository) is written in JavaScript and is moving to TypeScript.
You want a migration plan for the team's engineers.
- Once they have read it, the team agrees on which directories to move first, and each engineer
  volunteers for the parts they want to take on. They do not start moving code right after reading.
- No one owns any part yet; the team decides that after reading.
- You have not decided the order of directories, how the UI is built, or whether cli/ is included.
  These are for the team to decide after reading.
- Any place writ proposes under docs/ is fine. English.
"""

TYPING_USER = """\
You keep docs/typing-guide.md, the rules your team's engineers follow when they add types to code
moved from JavaScript to TypeScript. The move has not started and tsconfig.json does not exist yet;
you want the rules settled first.
- The readers are the engineers who move the files. They read it to write types that pass review
  without being sent back. Whether reviewers also count as readers has not been discussed.
- If asked about `any`, you decide now: `any` is allowed only in declarations for untyped libraries
  in src/types/vendor.d.ts, nowhere else, tests included. Elsewhere take the value as `unknown` and
  narrow it before use.
- Nothing else beyond what the guide already says has been discussed by the team.
- The place stays docs/typing-guide.md.
"""

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
    "migration-plan": {
        "benefits": ["understands it in one reading", "hand it straight on",
                     "judge from the report", "asked instead of covered over"],
        "source": "fixture",
        "opening": "/writ:up Write a TypeScript migration plan for the team's engineers",
        "user": MIGRATION_USER,
        "target": None,
        "reader": "an engineer on the team, who reads the plan before the team meets to agree which "
                  "directories to move first and who takes which part",
    },
    "typing-guide": {
        "benefits": ["understands it in one reading", "hand it straight on",
                     "asked instead of covered over"],
        "source": "fixture",
        "opening": "/writ:up docs/typing-guide.md",
        "user": TYPING_USER,
        "target": "docs/typing-guide.md",
        "reader": "an engineer on the team, who is about to move a JavaScript file to TypeScript and "
                  "add types that pass review",
    },
    "pr-review-hole": {
        "benefits": ["check by what happened in use"],
        "source": "fixture",
        "opening": "/writ:pith check .github/prompts/pr-review.md. " + PR_REVIEW_AIM,
        "user": "You wrote the prompt and want it checked. You have nothing to add to the aim.",
        "target": None,
        "reader": None,
    },
    "pr-review-sound": {
        "benefits": ["check by what happened in use"],
        "source": "fixture",
        "opening": "/writ:pith check .github/prompts/pr-review.good.md. " + PR_REVIEW_AIM,
        "user": "You wrote the prompt and want it checked. You have nothing to add to the aim.",
        "target": None,
        "reader": None,
    },
    "release-notes": {
        "benefits": ["write essentials worked back from the purpose"],
        "source": "fixture",
        "opening": "/writ:pith Write essentials for our CLI's release notes. Put them at "
                   "docs/essentials/release-notes.md. The readers are the developers in the company "
                   "who use this CLI, reading to decide whether to upgrade now.",
        "user": "Your team builds the internal CLI in cli/. There is no set way to check its release "
                "notes; docs/releases/ holds the real ones.",
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
        "user": None,
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
        "user": None,
        "target": "writ/docs/design.md",
        "reader": "whoever is about to change writ's prompts, agents or hooks without breaking a "
                  "decision in its design",
    },
}
