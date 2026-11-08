# `<plugin>`

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: the plugin's README is a deliverable of its own, of the kind readme.
> Make it from the plugin's product vision with the readme best practice, before the plugin's
> architecture.
>
> Write the plugin's other files in this order, as each takes what the files before it name:
>
> 1. `.claude-plugin/plugin.json`, as the parts and the proposal name the plugin and Lane.
> 2. Each role's two schemas, `domain/role-in.schema.json` and `domain/role-out.schema.json`, and
>    then its part, `domain/role.md`, which names them. Then the skill's part, `domain/command.md`.
> 3. The entries, `agents/role.md` and `skills/command/SKILL.md`, each naming its part.
> 4. The scripts the parts run, `scripts/command.py`.
> 5. The proposal and its adapters, `.lane/yyyymmdd-plugin/`, once the steps, the entries, and the
>    scripts its lanes take exist. Run `lay.py print` on it, read what it prints, and then run
>    `lay.py write`.
> 6. `hooks/hooks.json`, which `lay.py write` writes. Add to it by hand only a hook that no lane
>    holds.
> 7. `CHANGELOG.md`, at each release.
