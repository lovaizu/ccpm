# fw

The common base under plugins such as writ and rn. You do not call it yourself; it comes installed
with them.

What it does for you while one of them works:

- You are asked only what is yours to decide, one point at a time, and approve the plan once.
- Before anything is made, the plugin agrees with its AI roles what each will do; a separate AI that
  knows nothing of your talk then uses the result as its receiver would, and what it stumbles on is
  fixed and checked again before you see it.
- The plugin learns from each round. What it learns about the way of working it follows for the rest
  of the session, and at the end it asks whether to send that to the plugin's makers as an issue;
  nothing is sent unless you say yes.
- The work is recorded in your repository, so after you clear the conversation, or the next day, it
  goes on from where it stopped without your explaining again.
- It acts only on its own roles and record; your other sessions and files outside the repository are
  left alone.

Requires Python 3.9 or later.

For developers: see [dev/fw/README.md](../dev/fw/README.md).
