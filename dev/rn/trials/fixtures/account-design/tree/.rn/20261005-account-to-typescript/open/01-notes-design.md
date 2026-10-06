The design points agreed with the user, waiting for `writ`.

- The code is the first 10 characters, in Crockford base32, of HMAC-SHA256 over the user's ID as
  text, keyed with the secret key. 50 bits keep two users from sharing a code at any number of
  users the shop will have; the same ID always gives the same code.
- The name reads `User ` and the code, such as "User 7F3K2Q9M1A".
- `displayName` called for a user with no names and no `id` throws an error saying the `id` is
  missing, so a caller that forgot it fails in its tests instead of showing a name shared by everyone.
- The key comes from the environment variable `ACCOUNT_NAME_KEY` on the server. When it is missing,
  the server refuses to start and says which variable is missing, so no name is ever made without it.
- The command is `npm run whois -- "User 7F3K2Q9M1A"`. It reads the user IDs, one per line, from its
  standard input, takes the key from `ACCOUNT_NAME_KEY`, and prints the ID whose code matches, or
  says none does. A code is not turned back into an ID by the key alone, so the IDs are fed to it.
- How the user sees it works: for each form an absent name takes, the name shown is "User" and a
  code, different for different users; and `whois` given that name and the IDs prints the user's ID.
