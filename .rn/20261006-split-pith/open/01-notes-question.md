Serves: goal

Issue #35 named rn as pith's first caller outside writ. That no longer holds as written: rn 0.9.0
already depends on writ (`rn/.claude-plugin/plugin.json`), so it reaches pith anyway, and it checks its
work with its own first user (`rn/agents/first-user.md`), not with pith. Today the split would serve
people who want to check a prompt, code, or tests by having it used, without installing writ; it
gives rn nothing unless rn is changed later, in a session of its own.

What do you want the split to do for you, or for those who use these plugins, now that rn is in that
state?

Your answer decides whether the plan keeps rn in the goal and in A2, and whether the result file's
form must be settled in this session or can wait until a caller outside writ appears.
