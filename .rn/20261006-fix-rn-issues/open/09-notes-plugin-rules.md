# Plugin rules, rewritten from zero

Agreed with the user one point at a time; the rules are written from these points, not patched.

## Purpose of the rules

A plugin that achieves its purpose comes out simple, never heavy, and is made and checked with little
effort.

- How a plugin is made and how it is checked are decided together, since a way of making cannot be
  judged better without a check that shows it.
- The way of making is not assumed (one shared flow with domain parts is only one candidate, beside a
  short self-contained prompt per plugin and the official plugins' shape). It is chosen after the
  form of the check is decided, by comparing the candidates with that check.

## What the check shows

- What the user got: whether the user actually gets each gain the plugin's README promises.
- What the user spent for it: how long they waited, how much they read to decide, and how many times
  they were called. Every part can work while the whole keeps the user waiting for hours, as rn 0.9.0
  did; looking only at what was got misses it.

## How the check is run

- Day to day, a change is judged by scenes: each starts from the state just before the moment the user
  gets a gain and ends at the first result that shows it, so it runs in minutes.
- At each milestone, the README's whole story is run once, the only run that shows what the user
  spent; rn 0.9.0, checked by scenes alone, kept the user waiting 2 h 43 min unseen.
- The story, its starting state and the version compared against (the one in use) are fixed first
  and not changed on the way: the rebuild's comparison never finished because its subject changed
  four times.

## Open

- Who plays the user, and in what kind of session.
