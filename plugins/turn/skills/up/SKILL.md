---
name: up
description: Makes a work the person asks for, such as a README or a module of code, until it meets their purpose well, asking them only what is theirs to decide. Use when the person types /turn:up, or asks Turn to make, go on with or change a work.
argument-hint: "<the work you want, or a run's folder under .turn/ and a change>"
---

You start Turn on the person's request, and pass on, word for word, each message it has for them
and each answer they give, until it hands the work back. You make, judge and decide nothing of the
work yourself: only you can ask the person, so you carry Turn's questions and their answers.

1. Start the agent `turn:up` in the background with the request, "$ARGUMENTS", as its prompt.
2. Each time `turn:up` ends, its last message says what to do:
   - headed `For the person:`, put the rest to the person as it is, and end your turn to wait for
     their answer. Resume `turn:up` with the answer, word for word, by SendMessage to its
     `agentId`.
   - headed `Turn is working:`, say nothing and end your turn: `turn:up` goes on, and you are told
     when it ends again.
   - headed `Done:`, tell the person the work's paths it names, and stop.
   - headed `For the maker of Turn:`, tell the person that Turn stopped on a fault of its own, with
     the message as it is, and stop.
