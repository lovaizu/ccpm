# Gaps

- S2: two runs going on at the same time in one repository, each in its own conversation, can
  cross. After `/rn:up`, and after a sign-off of an `/rn:on` run, rn takes the newest run from the
  runs' commits. A later turn of one conversation then reaches the other run once that run commits
  last. Lane gives rn's adapters no state of their own, and the README's walkthrough runs one run
  at a time, so no case covers it.
