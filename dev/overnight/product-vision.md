# Product vision of overnight

## Roles

- arranging AI\
  The AI that queues the user's `claude -p` tasks overnight at their instruction, and takes the
  results in.
- calling plugin's AI\
  The AI of another plugin that runs `claude -p` unattended, and has overnight resume its stopped
  tasks.

## Objectives and key results

- O1: the arranging AI gets the user's `claude -p` work done by morning, outside the daytime usage
  window.
  - KR1.1: the share of the queued tasks that are given up or still running in the morning. Lower
    is better.
  - KR1.2: the commands the arranging AI runs to start the queue and take the results in. Fewer is
    better.
- O2: the calling plugin's AI gets each unattended `claude -p` task to its full result, past every
  usage limit.
  - KR2.1: the share of its tasks stopped by a usage limit that lack their full result, such as
    one never resumed. Lower is better.
  - KR2.2: the lines the calling plugin's AI writes to have its tasks waited out and resumed. Fewer
    is better.

KR1.1 and KR2.1 come first: keep a change that improves a key result only if none before it
gets worse.
Key results have no targets, as a measure made a target stops being a good measure, by Goodhart's
law. They show whether a change brought its objective closer.

## Concept

overnight carries each `claude -p` task, queued or handed over, to its end past every usage limit
while nobody answers.

- A session that survives the stop, for O2\
  A stopped task resumes in the same conversation, even after its caller has gone.
- The stop read from the reply, for O2\
  Only a reply that says the task hit the limit makes it wait, and any other reply ends it.
- Wait, then resume, for O2\
  A stopped task resumes two minutes after the limit resets, its new reply added to the earlier one.
- A queue with a start time, for O1\
  Tasks run three at a time from the start time, and each waits out the limit alone.
- Nobody to answer a prompt, for O1\
  Each task may do all it needs from the start, and write only in its own directory.
- Running on after Claude Code closes, for O1\
  The queue keeps running after the user closes the conversation that started it.
- A log to read in the morning, for O1\
  One timed line for each start, wait, finish, and give-up shows how each task ended.
- Given up after seven stops, for O1\
  overnight gives up and logs a task the limit stopped seven times, so it can't hold up the night.
- Results taken in from the main session, for O1\
  In the morning, the arranging AI reports how each task ended and brings the results into the
  main session.
