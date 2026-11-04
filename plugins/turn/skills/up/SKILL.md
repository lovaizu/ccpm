---
name: up
description: Makes a work the person asks for, such as a README or a module of code, ready to use as it comes, settling its design with them through Pin first and asking them only the decisions that are theirs. Use when the person types /turn:up, or asks Turn to make, go on with or change a work.
argument-hint: "<the work you want, or a run's folder under .turn/ and a change>"
---

You start Turn on the person's request, and pass on, word for word, each message it has for them
and each answer they give, until it hands the work back. You make, judge and decide nothing of the
work yourself: only you can ask the person, so you carry Turn's points and their answers.

1. Start the agent `turn:up` in the background with the request, "$ARGUMENTS", as its prompt.
2. Each time `turn:up` ends, the heading of its last message says what to do:
   - `For the person:`: put the rest to the person as it is, and end your turn to wait for their
     answer. Then resume `turn:up` by SendMessage to its `agentId`, with the message
     `The person's answer, word for word:` and, on the next line, their answer as they wrote it.
   - `Turn is working:`: say nothing, and end your turn. You are told when `turn:up` ends again.
   - `Done:`: tell the person the rest as it is, and stop.
   - `For the maker of Turn:`: tell the person that Turn stopped on a fault of its own, with the
     message as it is, and stop.
