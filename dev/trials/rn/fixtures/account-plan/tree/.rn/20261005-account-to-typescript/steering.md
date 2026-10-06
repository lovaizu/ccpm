---
rn: 0.9.0
pr: PR_URL
status: running
artifact-language: English
conversation-language: Japanese
readme: README.md
design: docs/design.md
verification: docs/verification.md
---

# Goal

Show every user by a name of their own that reveals nothing personal, never "undefined", and move
`src/account` to TypeScript. Users who signed up with only an email address are shown as
"undefined undefined", and support keeps getting asked about it. `account` was left in JavaScript
because it had no incident; this is one, so it moves too, and a mistake of the kind in
`docs/incidents.md` made in it fails `npm run build`.

# Acceptance criteria

## Attractive quality

- A1: A user who signed up with only an email address is shown a name that tells them apart from
  every other user and shows nothing personal, no part of the address included, never "undefined",
  so support stops being asked about it.
- A2: Given only such a name, support finds the user's ID with one command run with the key, so a
  user who writes in giving that name is answered from their first message.

## Must-be quality

- M1: Users with a nickname, or with first and last names, are shown the same name as today.
- M2: A mistake of the kind in `docs/incidents.md` made in `account` fails `npm run build`.
- M3: A user with only a first name or only a last name is shown that name alone, never with
  "undefined".
- M4: No name reveals anything about the user, their ID included, to anyone without the key; the
  key is never in the repository.

# Assumptions

- Fact, decided by the user: the reason for the move is the "undefined undefined" name shown to
  users who signed up with only an email address, which brings repeated support questions.
- Fact, run with node on `src/account/account.js`: `displayName` gives "undefined undefined" for a
  user with no names, and "Kiyo undefined" for one with a first name only.
- Fact, decided by the user: none of the part before "@", the whole address, or one fixed word
  for everyone will do: the first two show the address, the last does not tell users apart.
- Assumption: other users may see the names, since the user does not know who sees them; so no
  personal information may be in them.
- Fact, decided by the user: an email-only user is named by a code made from their user ID with a
  secret key, such as "User 7F3K2Q": it tells users apart and reveals nothing. They accept keeping
  the key, and callers passing the ID to `displayName`. The ID itself would show how many users
  there are and who signed up first; a code from the address would change with the address.
- Assumption: a name that looks deliberate, such as "User 7F3K2Q", stops the support questions.
- Fact, read in `src/account/account.js` and `test/account.test.ts`: `displayName` reads only
  `nickname`, `firstName`, and `lastName` today; no ID is passed to it in this repository.
- Assumption: every caller has the user's ID where it calls `displayName`, and passes it as `id`, a
  number or text; the user does not know what their records call it, and a caller naming it
  otherwise adds it as `id`.
- Fact, decided by the user: the command that turns a name back into an ID is built in this work;
  without it, support could not act on the name and questions would come back.

# Rules

- Type mistakes are fixed by parsing or checking the value, never by casting with `as` or `any`
  (`README.md`, "Before shipping").
- `vendor/` is regenerated nightly; it is read, never edited (`README.md`, "vendor/").
- Production runs Node 20 and imports the built `dist/src/index.js`; `npm run build` and `npm test`
  must both pass (`docs/design.md`).

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified

- How the code is made from the ID and the key so that no two users share one, and how the command
  turns it back with the key alone, for IDs that are numbers or text.
- What the name reads as: its wording, such as "User", and its length.
- What a user with no names is shown when no `id` is passed.
- Where the key comes from on the server, and what happens when it is missing.
- What the command looks like to whoever runs it.
