Design points to fix, from the Mores left in 05-report-verification-fix.md, waiting for writ.

- A1, writ/docs/verification.md scene: the essentials question has the first user run
  `python3 print_log.py` as written, with nothing added, the way its receiver runs it, so the output
  is saved and the run shows A1.
  - Why: in 2 of 3 runs the first user piped or redirected the output, nothing was saved, and the
    run showed nothing about A1.
- A1, writ/docs/verification.md "Where a run starts": the first user is started with a permission
  mode that lets it run the script without approval.
  - Why: started as written, the first user was blocked from running the script and answered from
    the source.
- A1, writ/docs/verification.md scene: the failed entries and their reasons are made when the script
  runs, not written as text in its source, so they can be learned only from the output.
  - Why: read from the source, the answer shows nothing about A1.
- writ/docs/verification.md machine checks: the coverage line names no criterion; it shows only that
  every line of writ is run.
  - Why: a full run does not show any criterion holds.
