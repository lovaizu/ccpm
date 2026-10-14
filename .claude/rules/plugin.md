# Plugin rules (ccpm)

How a plugin in this marketplace is built, step by step in the order the work is done. Each step
names the checklists in `writ/checklists/` to open while doing it; a checklist says what
the work must be, and this file says how the work goes.

When a step's work needs something its checklist does not ask, add the question to that checklist,
whichever plugin is being built, and make the work again against it.

- Rationale: what is made with the checklist open is made right as it is made; a gap left in a
  checklist is met again by every plugin made with it.

Source: facts confirmed in the official docs (plugins-reference / plugin-marketplaces, prompting
best practices / skill authoring best practices) and the official plugins.

## Steps

### 1. Write the README

**Write `<plugin>/README.md` with `doc.md` and `readme.md` open, and have the user agree to it
before anything else is made.**

- Rationale: everything after is built to what the README promises the user; built first, it would
  stand on a measure no one has settled.

### 2. Write the design

**Write `dev/<plugin>/design.md` with `doc.md` and `design.md` open, and have the user agree to it.**
Beside it, put `dev/<plugin>/README.md`, which links the design and says how to run the tests and
trials once they exist; `dev/README.md` lists each plugin's folder and links these rules, and the
root `README.md` leads users to each plugin's README and builders to `dev/`. Put no README deeper.

- Rationale: installing copies the plugin's folder, so what only builders need stays in `dev/`;
  GitHub shows a folder's README when it is opened, so a visitor finds the way by opening folders,
  and a README further down repeats its parent's and drifts from it.

### 3. Have the README and the design read once

**Have a first user who does not know the discussion read the README and the design once, as their
readers would, and settle each finding by fixing the decision or principle it comes from.**

- Rationale: a reading after every fix turns each finding into a patch, and the documents drift
  from their aim while every reading passes.

### 4. List the units

**List the units to build. A unit is the smallest slice through which the user meets one or more of
the qualities in the design's Goals, from start to end. The first unit carries one attractive
quality by the thinnest path.** Keep each unit to the simplest mechanism that serves it, and add no
special path for a case an existing check already stops.

- Rationale: a unit run end to end shows early whether the plugin keeps its promise, and the first
  shows soonest whether the user would choose it at all; every special path is one more thing for
  users to learn and builders to keep right.

### 5. Build each unit

**For each unit, in order, do a to e.**

a. **Write its tests in `dev/<plugin>/tests/` with `unittest`, run them and see them fail.** Feed
   in what the code would receive, and check a case it stops as well as one it lets through. Name
   each test by what must happen, as one sentence, and mark its body `# Given: <the situation>`,
   `# When: <what is done>`, `# Then: <what must be so>`, each in plain words, not in terms of the
   code.
   - Rationale: a test written after the code is fitted to what the code does, not to what it must
     do; a test never seen failing may check nothing; a check that never stops anything looks the
     same as one that works; a Then whose code checks less than its words say stands out.

b. **Write the code until the tests pass.** What runs on users' machines is Python 3, 3.9 or later,
   with the standard library only, and the README says so; a script that only calls an existing
   tool may be sh. What the plugin's agents read and write as data is JSON; where they need only a
   part, they read and change it with `jq`, and where the purpose needs it read whole, they read it
   whole. When a tool the plugin runs on, such as python3 or jq, is missing, the plugin stops and
   says how to install it. The tests run every line the plugin runs; delete a line no test has a
   reason to run, and mark `# pragma: no cover`, with its reason beside it, only where whether a
   line runs depends on an environment the tests cannot make. CI counts the lines on every push
   and fails on any not run.
   - Rationale: what the plugin makes can be wrong, so it is held by tests, and python3 is wherever
     git is while Node.js may not be; an agent changes only the part it needs with a tool it
     already knows, and a judgment made on a part where the whole was needed cannot be told from
     one made on the whole; a skipped check goes unnoticed.

c. **Write each prompt, a skill or an agent, with `doc.md` and `prompt.md` open, and run it to see
   that the AI does what its Role and Steps say.**
   - Rationale: a prompt is known by what the AI does with it; a trial on unchecked prompts finds
     the prompts' slips, not whether the plugin keeps its promises.

d. **Write the hooks that check the process the prompts' steps set:** a step begun before the
   steps ahead of it are done, a step left out, an input not read or an output not written where
   its step says. Each stop says which step went wrong and what that step needs. Put each check in
   its own named file, with one entry file per hook event, as the official `hookify` does.
   - Rationale: the steps say what must happen and the hooks see whether it did, so a slip is
     caught as it is made, not found later in a result that looks right; each check is read, fixed
     and tested on its own.

e. **Try the unit as its user**, with the code that runs it kept in `dev/<plugin>/trials/`, out of
   the line count, on the models the plugin's agents name and never a smaller one. Judge it from
   the JSONL of every conversation and agent it started, by the design's Verification. A trial that
   needs a real GitHub repository runs in the private `lovaizu/rn-try`, one at a time.
   - Rationale: CI cannot start Claude Code, so each run is its own check, and a smaller model's
     slips are not the plugin's; the outcome shows that something went wrong, the records show
     where; pull requests and pushes a run makes stay out of every repository people use, and two
     runs at once would mix in it.

**Change a prompt or a document after a trial only for a cause confirmed in the records and traced
to what the README and the design say it should be.**

- Rationale: what an AI does varies from run to run; a line added for one run's slip meets a
  different slip in the next, and the additions never settle.

### 6. Check the whole

**Try the plugin as its user from start to end, and check every quality in the design's
Verification.** Settle what it finds at the unit its cause lies in, then check the whole again.

- Rationale: each unit was checked on its own; what lies between units, and qualities that show only
  over the whole, such as the time a whole run takes, show only here.

### 7. Check the structure

**Pass both `claude plugin validate <plugin-path> --strict` and `claude plugin validate
<marketplace-root> --strict`.**

- Rationale: a malformed manifest fails for every user at install, before any behavior is reached.

### 8. Release

**Release only on an explicit instruction from the user**, not on merge to `main`. Until then,
user-facing changes wait under CHANGELOG's `## [Unreleased]`.

- Rationale: users receive an update only when the version is bumped, so the user decides when it
  reaches them.

On the first release, and whenever a plugin is renamed or removed, **register it**: add one entry
under `plugins` in `.claude-plugin/marketplace.json` with `name`, `description`, `source` (e.g.
`./rn`) and `category`, and list it in the root `README.md` with a link to its README and a one-line
description. Change the two together.

- Rationale: Claude Code installs from the marketplace entry and people find the plugin from the
  root README; a plugin counts as shipped only once both can reach it.

**Write `version` in exactly one place, `plugin.json`, and always set it** (semver, e.g. `0.1.0`).
Decide the increment by the largest change from the user's side: major for a breaking change (on
`0.x`, minor instead), minor for a new or changed user-visible behavior, patch for no behavior
change.

- Rationale: when both are set, `plugin.json` wins over the marketplace entry, so a second copy is
  meaningless; `claude plugin validate --strict` fails when it is unset.

**Keep `CHANGELOG.md` in the plugin root** in [Keep a Changelog](https://keepachangelog.com)
format: one `## [x.y.z] - YYYY-MM-DD` per release, grouped under `Added` / `Changed` / `Fixed` /
`Removed` as they apply, with one line for every change a user would notice, written as `<what
changed> — <why it helps the user>`. Typos, refactors, internal docs and formatting get none. On a
release, rename `## [Unreleased]` to the version and date, and leave no empty `## [Unreleased]`
behind; it is made again when the next user-facing change lands.

- Rationale: the user reads what changed for them and why, in the same place for every plugin.

Who does what:

1. The assistant bumps `version` in `plugin.json`, finalizes `CHANGELOG.md`, makes the final check
   in `final-check.md`, commits and pushes.
2. The assistant asks the user to merge the pull request to `main`; it never merges it itself and
   never uses `--admin`.
   - Rationale: `main` is protected, and only the user can clear its required review.
3. The user merges, and says so.
4. The assistant tags `main` as `<plugin>--v<version>` (e.g. `rn--v0.2.0`) with `claude plugin tag
   --push` from the plugin directory, and publishes a GitHub Release for that tag with the
   CHANGELOG's matching section as the notes.
   - Rationale: this is Claude Code's own form: a plugin that depends on another with a version
     range resolves it against these tags, and the prefix lets each plugin version independently;
     the command also validates the plugin and refuses a tag that already exists. Release timing is
     read from tags and Releases, not from merge commits.
