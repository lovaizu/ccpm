# Product vision of overnight

## Roles

- task owner\
  One who has the AI they instruct run `claude -p` tasks overnight, and takes their results in the
  morning.
- plugin developer\
  One who has the AI running their plugin wait out the usage limit, without writing that wait
  themselves.

## Objectives and key results

- O1: the task owner goes on in the morning with the result of each task left for the night.
  - KR1.1: the share of the night's tasks whose result the task owner lacks the next morning.
    Lower is better.
  - KR1.2: the task owner's own time on the night's tasks, from listing them to taking in their
    results. Shorter is better.
- O2: the plugin developer has each run of their plugin go on past the usage limit to its end.
  - KR2.1: the share of the plugin's runs that hit the usage limit and don't go on to their end.
    Lower is better.
  - KR2.2: the plugin developer's own time to make their plugin wait out the usage limit and
    resume. Shorter is better.

KR1.1 and KR2.1 comes first: keep a change that improves a key result only if none before it gets
worse.
Key results have no targets, as a measure made a target stops being a good measure, by Goodhart's
law. They show whether a change brought its objective closer.

## Concept

overnight lets each task go on to its end, even on a night that nobody watches, without losing it
partway.

- Resumed where it stopped, for O1\
  A task that stops goes on from where it stopped in the same task, so its work is kept.
- Waits out the usage limit, for O1 and O2\
  A task or a plugin's run waits out the usage limit, then resumes and goes on to its end.
- Read from the log alone, for O1\
  In the morning, the log alone tells the task owner which tasks finished and which were given up.
