# The learnings stage of /rn:up

Step 11 of `/rn:up`, from the finished work approved to the pull request marked ready, taken as
`orchestrator.md` says.

11. Find what this piece of work fell short in, put each learning to the user and mark the pull
    request ready, so what it taught makes later work better where the user chooses.
    - In: the finished work approved, the stage learnings.
    - Run `rn.py history`, which prints `{"feedback": [{"commit", "signoff", "message", "answer":
      {"commit", "message"} or null}, ...], "remade": [{"commit", "work", "call", "message"}, ...],
      "replaced": [{"commit", "work", "was", "now", "message"}, ...]}`, from the session's branch:
      each feedback the user sent back with the proposal that answered it, each work made again and
      each decision an answer replaced, each with its commit and message. Read what led to each in
      the history, with `git show <commit>` and `git log --format='%h %B' <commit>` as far back as
      the move it rests on.
    - Where a cause you doubt is in no commit, such as how a point was asked or what a message to
      the user held, check it with `rn.py search "<words>"`, which prints `{"found":
      [{"conversation", "time", "said"}, ...]}`, each part the user or you said or did that holds
      the words, in the session's conversations; a cause neither shows is no learning.
    - Write the learnings: step 3 on work `learnings`, giving nothing more, the part holding a
      learning for each place the work fell short, none where nothing did; as the step that comes
      after, this step on putting the first learning to the user.
    - Run `rn.py learnings`, which prints `{"learnings": {"L<n>": "<the learning>", ...}}`, the
      learnings in `<session>/learnings.md`.
    - Put each learning to the user, one per message, in the form "Learnings to decide" of
      `messages.md`, with where it is recommended to go. Keep each answer before the next: one
      taken for a checklist with `rn.py decide checklist-<kind>`, one taken for an issue with
      `rn.py decide issue-<n> --title Learning --says <the learning as rn.py learnings gave it>`,
      `<n>` counting the issues of the session from 1; then every answer with `rn.py state`, Next
      this step on the learning after it, Open each issue not yet sent, the message holding the
      answer.
    - For each issue: have it made, step 3 on work `issue-<n>`, giving nothing more, which turn
      makes at `<session>/issue-<n>.md`; read it whole, show it to the user whole, put into the
      conversation language, adding nothing and leaving nothing out, and ask whether to send it; on
      their yes alone, run `gh issue create --repo lovaizu/ccpm --title "$(sed -n '1s/^# //p'
      <session>/issue-<n>.md)" --body "$(tail -n +3 <session>/issue-<n>.md)"`, which prints the
      issue's URL; keep it with `rn.py state`, Next this step, Open without it, the message holding
      the URL, and tell them `Issue sent: <url>`.
    - For each kind with a learning taken for a checklist: have it made, step 3 on work
      `checklist-<kind>`, giving nothing more.
    - Run `rn.py state --stage finished --message <m>`, which marks the pull request ready, sets
      Next and keeps the session finished.
    - Tell the user `The pull request is ready to merge: <the steering's pr>`, and that the merge is
      theirs; end.
    - Out: the pull request ready, every learning answered and kept.
