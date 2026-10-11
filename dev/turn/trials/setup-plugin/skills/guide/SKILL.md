---
name: guide
description: Writes SETUP.md, the guide a new team member follows on their first day to get the app running. Use on /setup:guide.
---

# setup:guide

1. Write the task's CCS to the next free `.setup/task-<k>.json` (start at 1), unless the user's answer is being added (step 3):

   ```json
   {
     "focal_entities": [{"deliverable": "SETUP.md"},
       {"receiver": "A new team member on their first day, starting the app from the guide alone"}],
     "goal_orientation": [{"acceptance": "A new team member starts the app by following the guide, without asking anyone"},
       {"use": "Run the steps from the top in a freshly cloned repository"}],
     "retrieved_artifacts": [{"viewpoint": "${CLAUDE_PLUGIN_ROOT}/viewpoints/setup.md"}],
     "constraints": [{"language": "English"}],
     "episodic_trace": [], "semantic_gist": [], "relational_map": [], "predictive_cue": [], "uncertainty_signal": []
   }
   ```

2. Call the `turn:up` skill with these two lines as its arguments, `<k+1>` being the next free number:

   ```
   in: .setup/task-<k>.json
   out: .setup/task-<k+1>.json
   ```

3. Read `jq -r '.predictive_cue[].next' .setup/task-<k+1>.json` and act on it:
   - `done`: say SETUP.md is ready, and finish.
   - `ask the user`: ask the user each `jq -r '.uncertainty_signal[].gap'`. With the answers, write the returned CCS with `{"answer": "<question> — <answer>"}` added at the end of `constraints` to the next free file, and go to step 2 with it as `in`.
   - `to the caller: <reason>`: tell the user the reason and finish.
   - `stopped: <where from>`: go to step 2 with the returned CCS as `in`.
