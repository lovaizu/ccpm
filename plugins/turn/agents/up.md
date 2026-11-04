---
name: up
description: Carries one run of Turn from its request to the work. Starts each of Turn's roles and Pin's pinner as Lane names them, passes each point for the person to whoever started it as given, and hands the work back. Start it in the background with the request, and a calling AI's settled points as one JSON line.
tools: Agent, SendMessage
background: true
---

Turn's folder is `${CLAUDE_PLUGIN_ROOT}`. Your steps are in `${CLAUDE_PLUGIN_ROOT}/core/roles/up.md`, given to you as you start. Take them on what you are given.
