# Prompt

## Description

overnight's status shows how each piece handed over went. It gives each piece's state, branch,
waits, and last words. It gives too the share of pieces that the usage limit, a wait for an
answer, or the session closing stopped. Use it in any later session, such as when the person asks
how the night went. Use it too when the person types `/overnight:status`.

## Context

- It takes nothing: it shows each piece recorded in the repository that the session works in.

## Steps

## Output

- It gives the lines that `pieces.py report` prints, as given: a table of each piece and the share
  stopped, or `No pieces yet`.
