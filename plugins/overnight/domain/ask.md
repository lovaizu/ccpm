# Prompt

## Description

overnight's ask hands one piece of work over. The piece then runs apart from the session, through
the usage limit, with only the tools named. Use it when the AI gets work that outlasts the
person's stay, or when the person types `/overnight:ask`. It gives the piece's number, folder,
branch, and tools, or what to add before the piece can run.

## Context

- It takes the words after the skill's name. They hold the piece's prompt, with each question
  settled in it. A last line, `Tools: <tool>, <tool>, ...`, names each tool. Each tool is a rule
  of Claude Code's permissions, such as `Read` or `Bash(pytest:*)`.

## Steps

## Output

- It gives the lines that `handover.py` prints, as given. They show the piece handed over and how
  to see how it goes, or what to add.
