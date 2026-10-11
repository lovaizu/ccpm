---
name: note
description: Writes NOTE.md, the note a visitor reads to find when to come. Use on /note:note.
---

# note:note

1. If the last `.note/task-<k>.json` has a `next` that starts with `stopped:`, go to step 3 with it as `in`. Otherwise write the task's CCS to the next free `.note/task-<k>.json` (start at 1):

   ```json
   {
     "focal_entities": [{"deliverable": "NOTE.md"}, {"receiver": "A visitor who has only the note"}],
     "goal_orientation": [{"acceptance": "A visitor finds the opening hours in the note alone"},
       {"use": "Read the note to find when to come"}],
     "retrieved_artifacts": [{"viewpoint": "${CLAUDE_PLUGIN_ROOT}/viewpoints/note.md"}],
     "constraints": [{"language": "English"}],
     "episodic_trace": [], "semantic_gist": [], "relational_map": [], "predictive_cue": [], "uncertainty_signal": []
   }
   ```

2. Go to step 3 with that file as `in`.

3. Call the `turn:up` skill with these two lines as its arguments, `<k+1>` being the next free number:

   ```
   in: .note/task-<k>.json
   out: .note/task-<k+1>.json
   ```

4. Read `jq -r '.predictive_cue[].next' .note/task-<k+1>.json` and act on it:
   - `done`: say NOTE.md is ready, and finish.
   - `ask the user`: ask the user each `jq -r '.uncertainty_signal[].gap'` in the conversation, and finish your reply there. With the answers, write the returned CCS with `{"answer": "<question> — <answer>"}` added at the end of `constraints` to the next free file, and go to step 3 with it as `in`.
   - `to the caller: <reason>`: tell the user the reason and finish.
   - `stopped: <where from>`: say where it stopped, and finish. On `/note:note` again, it carries on from there.
