# Check: writ, by its design's qualities (#6, round 1)

Target: writ (English), run with `claude -p --plugin-dir writ` in a sample repository, one copy per scene
Receiver and purpose: a Claude Code user; they get the six benefits the README promises
Aim: each benefit passes in its scene by what happened to the user and the reader (design, quality section)

## Benefits

- Good: understands it in one reading. Scene A (migration plan): a reader who did not know the discussion took it they should agree the order and the three open choices at the meeting and volunteer for a part, which is the user's purpose; no mark blocked it. Scene B: the reader took it that nothing can move until the team settles the open points, which is what writ told the user.
- More: understands it in one reading. Scene A's plan is 189 lines; the reader read past the rule that setup goes with the first part, said about 7 times, and the repeated "not from a build or a trial" notes. writ's own check reported parts read past as a More and left it.
- Good: hand it straight on, scene A. The user would change some things (repeated caveats, code referred to by line number, part sizes scattered), but none blocks the team's discussion.
- More: hand it straight on, scene B. Line 77 adds "the rename-only commit need not pass the type check, but the PR as merged must", a rule the team never decided and the user was never asked; the report said nothing was filled in by guess.
- More: judge from the report. In both scenes each question's line carries only line numbers, so the user could not tell what each Good or More was about and read the whole document; in scene B the decision changed after reading (line 77). The left Mores do not say which question they answer.
- Good: asked instead of covered over. Scene B: `any` was raised before the document was returned and written as the user decided. Scene A: owners and the three open choices were left visibly undecided, with the reason.
- More: asked instead of covered over, scene B. The user answered 10 rounds, 9 of them "not decided"; new undecided team points came after each check, one at a time; writ proposed to stop only at the end, and 6 more came back in the final report. The user said they tired of it.
- Good: check by what happened in use, scene C. The prompt with the hole got a More at line 12 (checks read as request-side only); the good prompt's matching question came back Good; other Mores came from 18 and 21 actual runs (comments outside the aim, a recommended option the author should choose). The hole itself did not bite in the runs (3 of 3 caught the rename), so that More rests on the first user's reading.
- Good: write essentials worked back from the purpose, scene D. Five questions; a team member answered them by reading 1.4 and running the CLI, and decided from the answers to wait and upgrade later.

## Taken for granted

- Good: only the target and `open/` files changed in every scene; every result file passed the form check.
- let go: a run took 20–30 minutes; the user said the wait did not bother them.
- let go: each recheck commits the result file again (5 commits in scene A); the record is the one the design asks for.
