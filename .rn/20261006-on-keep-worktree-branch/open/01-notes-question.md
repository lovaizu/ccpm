Serves: goal

What I understand so far: you start a Claude Code worktree for a piece of work, such as
`.claude/worktrees/fix-branch` with its branch `worktree-fix-branch`, and run `/rn:on` there. Today
`/rn:on` always makes a new branch with a name of its own, so the session's branch and pull request
no longer match the worktree you made, and you spend turns asking why and putting it back.

When you run `/rn:on` in a worktree you started, what should the session do for you, and why does
that matter to you?
