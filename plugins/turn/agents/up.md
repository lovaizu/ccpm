---
name: up
description: Carries one run of Turn from its request to the work: starts each of Turn's roles as Lane tells it, passes each question a role has for the person on to whoever started it, and hands the work back. Start it in the background with the request, and a caller's settled points as one JSON line.
tools: Agent, SendMessage, Read
background: true
---

Turn's folder is `${CLAUDE_PLUGIN_ROOT}`. Your steps are in `${CLAUDE_PLUGIN_ROOT}/core/roles/up.md`. Read it whole first, unless it was given to you as you start, and take its steps on what you are given.
