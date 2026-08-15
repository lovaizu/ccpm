# Changelog

All notable, user-facing changes to the `aiya` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- First working version of `aiya`: hand over one rough purpose with `/aiya:on` and a conductor carries it end to end — pinning the purpose down through interview and research, settling the approach, building independent pieces in parallel with fresh-eyes verification and automatic redo — while you answer just six checkpoints with `/aiya:ty` (approve) or `/aiya:gm` (send back), and pause and resume any time with `/aiya:dn` and `/aiya:up`.
- Runs on GitHub, GitLab, or with no git at all — the platform is detected at start and only two things vary: `/aiya:gm` with no argument (comment pickup) needs a PR/MR, and surviving machine loss needs a remote.
