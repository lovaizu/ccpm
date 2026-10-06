# Claude Code plugin

This file has three readers. The generator reads it as the form to aim for when it builds a Claude Code plugin. The first user installs the plugin with `claude --plugin-dir`, runs the story its README tells from the user's first words to the result with `claude -p`, playing the user from what the README and the purpose say they know and want, and reports, for each question here, what it did and what happened. It does not judge. The conductor lays the report beside the aim and gives each question a Good or More. Once they have read it through, they can tell, from what happened when the plugin was used as its user would, whether the user gets what the README promises for what it costs them, and which parts of the plugin are not needed. The plugin's skills and agents are prompts, so they are also checked with the questions of `prompt.md`.

- Running the README's story to its end, what did you get, set beside each gain the README promises?

    What the user gets at the end of the whole path is why they would choose the plugin. Each part can do what it was built for while the whole still fails: a run cut into scenes passes every scene and never shows that the story does not reach its end, or reaches it with something other than what was promised.

- On that run, how long did you wait at each point, how many lines did you read to decide each time you were asked, and what were you asked each time?

    What the user spends is part of what they get: a plugin that brings the promised result after hours of waiting, or after a proposal too long to decide from, is one they stop using. The spending shows only across the whole path, since each scene is short, and it grows wherever a step was added for a fault instead of fixing its cause.

- Of the times you were asked, which were for something only you could decide, and which could the plugin have settled from what it had or could look up?

    A user called only for their own decisions can leave the work to the plugin. A question the request, the repository or the documentation already answers makes them watch over the work, and teaches them to answer without reading.

- Running the same story with what you would use instead, the version you have now or Claude Code without the plugin when there is none, what differed in what you got and what you spent?

    A plugin is worth installing only for what it adds over what the user already has. A run alone shows how the plugin behaves, not whether it is better; a change that makes every part more careful can leave the user worse off than before.

- While the plugin ran, what did it do to another conversation in the same repository, or to agents it did not start?

    A user works with several sessions side by side. A plugin that takes another session for its own, stops its tools or sends it on with the plugin's work breaks work the user never gave it, and the harm shows far from its cause.

- When you asked for the plugin's job in your own words, without naming its command, what started?

    A skill is chosen by its description. When the user's words for the job do not reach it, the user must learn the command first; when they reach it for other jobs, it starts where it was not wanted.

- Which of the plugin's files did the run read, run or follow, and which were never touched?

    A part no run touches is either not needed, and only adds what can break, or meant for a case the story never meets, which the conductor weighs. Instructions read on every call cost the user's wait and the model's attention each time, so what is read only for some cases is better kept apart and read when needed.
