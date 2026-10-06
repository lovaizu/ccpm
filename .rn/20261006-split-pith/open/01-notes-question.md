Serves: A2

Should this session also fix issue #37, so that one check through pith starts a first user only where
use can show something new?

Today one `/writ:up` call runs pith about three times (#37: 43 pith runs for 13 calls; three documents
for rn took 2 h 43 min). The third run checks nothing: it only brings the result file to its final
state, because only pith may write that file. Who writes the result file and its form are already
open points this session must decide for pith's design (Not yet specified), and #37's fix is one
answer to them: the caller's conductor settles the file directly, and its form is held by
`check_result.py` and a hook.

1. Include #37 (proposed). The result file's owner and form are decided once, for writ and rn
   together, and rn moves onto a pith that does not spend an agent on bookkeeping. It adds a criterion
   (one first user for the first check, and one per fixed attractive More, nothing else) and a little
   more work on writ's side.
2. Leave #37 for later. This session stays smaller, but the result file's owner is decided now and
   then changed again for #37, and rn first moves onto the heavier pith.
