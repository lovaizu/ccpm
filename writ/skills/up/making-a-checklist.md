# Making a checklist

A checklist is made as a job of its own, started inside the job for the document, which is open
again once it ends. Its reader is whoever writes or judges documents of that kind.

1. Run `up.py start ${CLAUDE_SESSION_ID}`, and go through the steps of the skill for a document of
   the kind `checklist`, at `.writ/checklists/<kind>.md`, where `<kind>` names the kind in a word or
   two joined by hyphens, such as `release-notes`.
2. For a kind writ has a checklist for, the checklist holds only what it adds to writ's: settle
   that it opens with front matter naming it `<kind>-addition`, and that its opening says which of
   writ's checklists it adds to.
3. When the job ends, it hands back to the job for the document: continue that job's steps where
   you left them.
