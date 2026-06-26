# PR Feedback Workflow

The light loop to process PR review feedback. A **coordinator** dispatches one **execution subagent**
per review thread, sequentially, and reviews each result before the next. Verification is a single
coordinator pass — not the QA-expert / multi-round chain of [`task-workflow.md`](./task-workflow.md).

`/rn:gm` with no argument enters this loop (the feedback source is the PR's review comments).
`/rn:gm <text>` instead acts on `<text>` directly and does **not** enter this loop.

## Roles

- **Coordinator** — the main agent in the conversation. Identifies the PR, collects the threads, builds
  the queue, dispatches one execution subagent per thread in sequence, reviews each result before
  dispatching the next, and re-instructs on a problem. Never resolves a thread.
- **Execution subagent** — subagent (Agent tool, no conversation history). Handles exactly one thread,
  with exactly one of two outcomes (address-and-reply, or reply-with-a-question). Never resolves a thread.

## Phase: Identify the PR

1. **Find the session's PR** for the current branch:

   ```bash
   gh pr view --json number,url
   ```

   Record `number` (the PR number) and `url`. Capture `owner`/`repo` from the remote:

   ```bash
   gh repo view --json owner,name -q '.owner.login + " " + .name'
   ```

## Phase: Collect threads

1. **Fetch all review threads** via GraphQL:

   ```bash
   gh api graphql -f owner='{owner}' -f repo='{repo}' -F pr={number} -f query='
   query($owner:String!,$repo:String!,$pr:Int!){
     repository(owner:$owner,name:$repo){
       pullRequest(number:$pr){
         reviewThreads(first:100){
           nodes{
             isResolved
             comments(first:100){
               nodes{ databaseId author{login} body path line }
             }
           }
         }
       }
     }
   }'
   ```

2. **Build the queue.** Keep a thread **only** when both hold:
   - `isResolved == false`, AND
   - the **last** comment's `author.login` equals the **first** comment's `author.login` (the reviewer
     has the last word — the assistant has not replied, or the reviewer replied after the assistant).

   Drop every other thread (resolved, or the assistant has the last word). For each kept thread record:
   the **first** comment's `databaseId` (the reply target), its `path` and `line`, and the full comment
   bodies (the discussion to act on).

## Phase: Dispatch (sequential, one thread at a time)

Process the queue **one thread at a time**. Never dispatch two threads in parallel — the coordinator
reviews each subagent's result before dispatching the next.

For each thread, dispatch one execution subagent with a work-order containing:

1. **Thread** — the `path`, `line`, the full comment bodies, and the first comment's `databaseId`.
2. **Task** — produce exactly one of the two outcomes below.
3. **Outcome (a) — address it:**
   1. Make the change.
   2. Stage the touched paths **explicitly**: `git add <path>…`. Never `git add -A` or `git add .`.
   3. Commit with a plain conventional message (`feat:` / `fix:` / `docs:` / … matching the change).
      The message must **not** contain `complete task #`.
   4. Push to the session PR. Never force-push.
   5. Get the commit's permalink: `gh browse <sha> -n` (prints the URL; `-n` = no browser).
   6. **Reply to the thread** with a short summary of what was done plus the commit link, in-reply-to
      the thread's first comment:

      ```bash
      gh api repos/{owner}/{repo}/pulls/{number}/comments/{first_comment_databaseId}/replies \
        -f body='Done: <short summary>. <commit-url>'
      ```

4. **Outcome (b) — needs a decision / is unclear:** make **no** code change. Reply to the thread with
   the question, in-reply-to the thread's first comment:

   ```bash
   gh api repos/{owner}/{repo}/pulls/{number}/comments/{first_comment_databaseId}/replies \
     -f body='<the question>'
   ```

5. **Return** — a compact summary: which outcome, what changed (files), the commit SHA and that it was
   pushed (outcome a), or the question asked (outcome b).

6. **Never resolve the thread.** Resolution is the author's act on GitHub (see Phase: Resolve-by-author).

## Phase: Coordinator review (between items)

After each subagent returns, before dispatching the next thread:

1. **Check the result.** Confirm the subagent produced one of the two outcomes for the right thread:
   outcome (a) — the change matches the thread, it is committed and pushed, and the reply carries the
   commit link; outcome (b) — a reply with a question and no code change.
2. **OK → dispatch the next thread.** Continue the queue.
3. **Problem → re-instruct the same subagent on the same thread.** Do not advance until it is right.

When the queue is empty, the loop is done.

## Phase: Resolve-by-author

- The loop **never** resolves a thread. Neither the coordinator nor the subagent calls
  `resolveReviewThread` or marks anything resolved.
- Resolution is the **author's** act on GitHub: the reviewer who opened the thread resolves it after
  reading the reply.
- The loop treats GitHub's unresolved state as its **queue**. Re-running the loop re-collects threads
  with the `isResolved == false` + last-comment-is-author filter, so it naturally picks up the author's
  follow-up replies and skips the threads the author has resolved.

## Verification

One coordinator pass per item (Phase: Coordinator review) is the whole of verification. No QA expert,
no language or software-engineering experts, no multi-round iteration cap.
