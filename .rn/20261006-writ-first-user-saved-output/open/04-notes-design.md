Design point to fix, from More 1 left in 03-report-design-fix.md, waiting for writ.

- M1, writ/docs/verification.md machine checks: add, tagged M1, that a path the first user only
  typed or printed into its record is stopped, and that a path written with `~` or `..` is compared
  as the same file: its own let through, another's stopped.
  - Why: design.md:82 now rests M1 on these two rules, and a rule no test checks can break unseen.
