# `<plugin>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: the plugin's README is a deliverable of its own, of the kind readme.
> Make it from the plugin's product vision with the readme best practice, before the plugin's
> architecture.
>
> The plugin's code and prompt deliverables make their files first, and each passes by its own
> best practice before the plugin deliverable starts. In the plan, the plugin deliverable names each
> of them among its preconditions, as Q1 says. Write the files in this order, as each takes what the
> files before it name:
>
> 1. By the code deliverable: each role's two schemas, `domain/role-in.schema.json` and
>    `domain/role-out.schema.json`, and the scripts that a role or the person runs,
>    `scripts/command.py`.
> 2. By the prompt deliverable: each role's part, `domain/role.md`, which names its schemas, and the
>    skill's part, `domain/command.md`. Then the entries, `agents/role.md` and
>    `skills/command/SKILL.md`, each naming its part. A plugin with no prompts, such as Lane, has
>    no prompt deliverable and holds none of these files.
>
> Once they pass, the plugin deliverable makes the rest:
>
> 3. `.claude-plugin/plugin.json`, with the name that the plugin's commands carry, and each plugin
>    it takes a part from, such as Lane for its guard.
> 4. `CHANGELOG.md`, with each change under `[Unreleased]`, and a heading for its version at each
>    release.
> 5. `docs/page.md`, a page for each need that the users have beyond the README, once the files it
>    covers exist. Leave it out where the README holds all they need.
> 6. The proposal and its adapters, `.lane/yyyymmdd-plugin/`, once the steps, the entries, and the
>    scripts its lanes take exist. Run `lay.py print` on it, read what it prints, and then run
>    `lay.py write`.
> 7. `hooks/hooks.json`, which `lay.py write` writes last. Add to it by hand only a hook that no
>    lane holds.
>
> A plugin with no roles, such as Lane, leaves out the agents, each role's part and its two
> schemas, the proposal, and `hooks/hooks.json`, as it has no role for a guard to hold. It skips
> steps 6 and 7. Where it has a skill, the skill does the work itself, as the notes of
> `domain/command.md` say.
