---
name: start
description: Starts the sleeper subagent in the background and returns at once.
disable-model-invocation: true
---
Install nothing, and send nothing to any outside service.

1. Start the subagent rec:sleeper by the Agent tool with run_in_background set to true, the
   description `Sleep then echo`, and the prompt: `Run the Bash command python3 -c "import time;
   time.sleep(30)" in the foreground. Then run the Bash command echo after-sleep. Then reply with
   the word slept.`
2. Don't wait for it. Reply with the word started.
