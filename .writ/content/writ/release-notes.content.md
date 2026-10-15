# What .writ/checklists/release-notes.md says

## checklist

### B-1: User and purpose
- Release notes are a plugin's `CHANGELOG.md`, read by someone who uses the plugin and sees that a
  new version is out.
- From them they can tell what changed for them in each version and why it helps them, and so
  decide whether and when to update.

### B-2: Every part of the purpose checked
- What changed for them: one line for every change a user would notice, under the version it came
  in; typos, refactors, internal documents and formatting get none.
- Why it helps: each line says `<what changed> — <why it helps the user>`.
- Each version: one `## [x.y.z] - YYYY-MM-DD` heading per release, the newest first, with its lines
  grouped under `Added`, `Changed`, `Fixed` and `Removed` as they apply.
- A change not yet released waits under `## [Unreleased]`; on a release that heading becomes the
  version and date, and no empty `## [Unreleased]` is left behind.
- The form is Keep a Changelog (https://keepachangelog.com), which users of other projects already
  read.
