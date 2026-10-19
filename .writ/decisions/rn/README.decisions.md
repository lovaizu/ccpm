# What rn's README says

What the UX (`dev/rn/ux.md`) does not settle for the README. Whom rn is for, what they gain, the
scenes and the benefits are the UX's.

## readme

### The example
- The situation: the user's app is written in JavaScript and they want it moved to TypeScript, work
  that takes days. They type `/rn:up move this app to TypeScript` in their repository.
- Behind their words, which rn's first points bring out: three of last quarter's production bugs
  were a value of the wrong type, undefined where a number was expected, and they want such a
  mistake caught before it ships. So the goal is that such a mistake fails the build; every file
  ending in .ts is not enough, since a file moved with loose types would still let it through.
- The example shows rn's messages in the form the UX's first scene gives, as console output.

### Installing
- In Claude Code, add the marketplace once with `/plugin marketplace add lovaizu/ccpm`, then
  install rn with `/plugin install rn@ccpm`. This also installs turn, the plugin rn has make each
  piece of work and read it in its receiver's place.

### Requirements, each with why
- Claude Code: rn runs inside it.
- A git repository with its remote on GitHub: rn puts the plan and the work on a pull request.
- The GitHub CLI `gh`, logged in with push access: rn opens and updates the pull request with it.
- Python 3.9 or later as `python3`, and jq: rn's and turn's scripts run on them.

### Documentation
- The changelog (`CHANGELOG.md`): what changed in each version.
- For those who build rn: `../dev/rn/README.md`.

### Terms of use
- MIT License (`../LICENSE`).
