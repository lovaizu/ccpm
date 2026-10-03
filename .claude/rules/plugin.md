# Plugin rules (ccpm)

How a plugin in this marketplace is built, checked, registered and released, in that order.

Source: facts confirmed in the official docs (plugins-reference / plugin-marketplaces / skills / hooks /
sub-agents at code.claude.com/docs) and the official plugins (plugin-dev, hookify, security-guidance,
code-modernization).

## 1. Build

### Hooks and check scripts

- **Follow the official hook best practice** (plugin-dev's `hook-development`).
- **Put each check in its own named file, and one entry file per hook event**, as the official
  `hookify` does (e.g. `pretooluse.py`). This also holds for a script a plugin runs to check its own
  output.
  - Rationale: each check can then be read, fixed and tested on its own.
- **Write them in Python 3 with the standard library only, running on 3.9.**
  - Rationale: with many checks, bash is weak to maintain and test. python3 comes with git in the Mac
    developer tools, so wherever git is there, python3 is too; on Linux and Windows it is no less
    common than jq. TypeScript is not used, since Node.js may not be on the user's machine.
- **When python3 is missing, stop and tell the user to install it; never skip the check.**
  - Rationale: a skipped check goes unnoticed, so no one learns the rule is not being kept.
- **State in the plugin's README that Python 3.9 or later is needed.**
- **Write the tests with the standard `unittest`, in the plugin's own `tests/`** (e.g. `rn/tests/`),
  as the official `security-guidance` and `code-modernization` plugins do. **Feed in the JSON a hook
  would receive, and check both a case it stops and a case it lets through.**
  - Rationale: a check that never stops anything looks the same as one that works.

### Roles

- **Build a plugin that makes and checks work from three roles: the conductor, the generator and the
  first user** (always these words).
  - The **conductor** alone judges and decides what comes next: it hands work to the generator, has the
    first user use the result, sets what the first user reports beside the aim, gives each a Good or a
    More, and decides what to fix or leave.
  - The **generator** makes or fixes the work as the conductor decides.
  - The **first user** uses the work as its user would and reports what happened, without judging it.
  - Rationale: judgment kept in the one role that knows the aim weighs every remark against it; a
    first user that judges, or a generator that grades its own work, fills the gaps with what it meant.
  - A plugin that only checks work someone else made leaves out the generator. A plugin that makes
    nothing for anyone to use, such as a hook that only guards a rule or a connector to another tool,
    needs none of the three.
- **Keep the first user from what it must not see by how the role is defined:** start it as a
  separate subagent that does not carry over the conversation, set `omitClaudeMd`, hand it only the
  work and its purpose, and take the tool that calls other agents away from the generator, so the
  generator cannot call the first user.
  - Rationale: the first user is there to use the work as its user would, without
    knowing how it was made. A subagent can be called by anyone, from the conversation, a user, a
    forked skill or another subagent, so watching every way it can be called with hooks grows tangled;
    a plugin's settings cannot restrict it either. A definition holds however it is called.
- **Leave to hooks only the mechanical rules a definition cannot hold**, such as a file's form, a
  name, matching IDs, a commit's form, or a push left undone.

### Results

- **Write the whole result to a file in `open/`, and return to the caller only a short result and the
  file's location.** The short result opens with the conductor's view, gives every essential one line
  (Good or More, and where), and sets out in full only what the user must decide, such as a More that
  was left.
  - Rationale: a whole result in the conversation is too long to be read, crowds the caller's context,
    and is lost when the conversation is summarized.
- **Name it `{dir}/open/{NN}-{kind}-{target}.md`, commit it, and push it.** `{dir}` is the plugin's own
  directory (e.g. `.writ/`), or the place the caller names (rn names its session,
  `.rn/{date}-{slug}/`). `{NN}` is the order it arrived in; `{kind}` is `report` (what the first user
  reported, with its Good and More), `feedback` (what the user said) or `notes` (points agreed and
  waiting); `{target}` names the work. Using the same target again overwrites the same file.
  - Rationale: pushed, the result survives the conversation and can be read on the pull request; one
    file per target holds only what applies to the work as it is now.
- **Clear a file once everything in it is settled: copy its whole text into the commit message, and
  delete the file in that commit.** A More is settled when it is fixed, let go with its reason, or
  decided by the user; end each More in the message with what became of it (`→ fixed:`,
  `→ let go:` with the reason, or `→ to the user:`). A plugin may add its own marks, such as rn's
  decision line.
  - Rationale: `open/` then holds only what still needs action, so a file left there is the sign that
    something does; the record stays in git history, and the working tree ends with nothing but the
    work.

## 2. Check

### Validation: use it as its user would

- **Check the attractive quality by validation: use the plugin as its user would, on the golden path,
  and compare what happened with what it aims for.**
  - Rationale: the attractive quality is why the user chooses the plugin, so the checking effort goes
    there first.
- **Spend no checking effort on what the user takes for granted: do not cover edge cases or
  alternative flows up front, and do not have a first user check a fix of it again. Fix it when it
  shows up in use; the conductor confirms the fix.**
  - Rationale: such a failure is easy to see and should be quick to fix, so checking it costs more
    than it saves. Covering it up front grows a list of checks that all pass while no one has checked
    the attractive quality, and rechecking it, as rn found, draws mostly more of the same remarks.
- **After an attractive-quality More is fixed, have a new first user check that point again.**
  - Rationale: whether the user now gets what the work is for shows only when someone who does not know
    the discussion uses it again.
- **Check by script, every time, whatever a script can decide.**
  - Rationale: it costs nothing to run and gives the same answer every time.

### Structure check

- **Pass both `claude plugin validate <plugin-path> --strict` and `claude plugin validate
  <marketplace-root> --strict`.**
  - Rationale: a malformed manifest fails for every user at install, before any behavior is reached.

## 3. Register

- **Add every plugin to `.claude-plugin/marketplace.json`** — one entry under `plugins` with `name`,
  `description`, `source` (e.g. `./rn`), and `category`. This is what Claude Code reads to install it.
- **List every plugin in the root `README.md`** with a link to its own README (e.g.
  `[rn](./rn/README.md)`) and a one-line description. This is the human entry point.
- **Change the two together** when a plugin is added, renamed, or removed.
  - Rationale: a plugin counts as shipped only once both the machine and a human reader can reach it.

## 4. Release

### Version number

- **Write `version` in exactly one place: `plugin.json`, and always set it** (semver, e.g. `0.1.0`).
  - Rationale: when both are set, `plugin.json` wins over the marketplace entry, so a second copy is
    meaningless; `claude plugin validate --strict` fails when it is unset. Users receive an update only
    when it is bumped.
- **Bump only on an explicit release instruction**, not on merge to `main`. Until then, user-facing
  changes wait under CHANGELOG's `## [Unreleased]`.
- **Decide the increment by the largest change, from the user's side:** major for a breaking change
  (on `0.x`, minor instead), minor for a new or changed user-visible behavior, patch for no behavior
  change.

### CHANGELOG

- **Keep `CHANGELOG.md` in the plugin root**, in [Keep a Changelog](https://keepachangelog.com)
  format: `## [Unreleased]` on top while changes are pending, then one `## [x.y.z] - YYYY-MM-DD` per
  release, grouped under `Added` / `Changed` / `Fixed` / `Removed` as they apply.
- **Write an entry for every change a user would notice**, as one line: `<what changed> — <why it
  helps the user>`. Typos, refactors, internal docs and formatting get none.
- **On a release, rename `## [Unreleased]` to the version and date, and leave no empty
  `## [Unreleased]` behind**; it is re-created when the next user-facing change lands.

### Who does what

1. **Assistant** — bumps `version` in `plugin.json`, finalizes `CHANGELOG.md`, commits, and pushes.
2. **Assistant** — asks the user to merge the pull request to `main`; never merges it itself and never
   uses `--admin`.
   - Rationale: `main` is protected, and only the user can clear its required review.
3. **User** — merges, and says so.
4. **Assistant** — tags `main` and publishes the GitHub Release.

### Tags and GitHub Releases

- **Tag each release on `main`** as `<plugin>--v<version>` (e.g. `rn--v0.2.0`), created with
  `claude plugin tag --push` from the plugin directory.
  - Rationale: this is Claude Code's own form: a plugin that depends on another with a version range
    resolves it against these tags, and the prefix lets each plugin version independently. The
    command also validates the plugin and refuses a tag that already exists.
- **Publish a GitHub Release** for that tag, with the CHANGELOG's matching section as the notes.
- **Read release timing from tags and Releases, not from merge commits.**
