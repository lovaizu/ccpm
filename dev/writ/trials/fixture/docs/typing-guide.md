# Typing rules

Follow these rules when adding types to a file that has been moved to TypeScript. Reviews check that code follows them.

## Compiler settings

- Set `"strict": true` in `tsconfig.json`. Do not loosen it per file.
- Do not merge a file that fails the type check. `// @ts-ignore` and `// @ts-expect-error` may be used only in test code, with the reason written in a comment.

## Where types go

- Put the types for API requests and responses in `src/types/api.ts`, and import them from both `src/api/` and `src/ui/`. Do not write the same shape separately on each side.
- A type used in only one file goes in that file.
- Define types with `type`, not `interface`.

## Functions

- For exported functions, always write the types of the parameters and the return value.
- For functions that are not exported, the return type may be left to inference. Write the parameter types.
- Write the return type of an `async` function as `Promise<...>`.

## null and undefined

- Use `null` for a missing value. Response fields too return `null` when there is no value, rather than leaving the field out.
- Only optional parameters take `?` and accept `undefined`.
- Do not use `!` (the non-null assertion). Handle the missing case with an `if`.

## Values from outside

- Check the contents of `req.body` and `req.query` before giving them a type. Put the checking functions in `src/api/validate.ts`.
- When using a library without types, declare just the functions you use in `src/types/vendor.d.ts`.
- The result of `res.json()` from `fetch` may be cast with `as` to a type in `src/types/api.ts`. Do not use `as` anywhere else.

## Files in the middle of the move

- When TypeScript code imports a file that is still JavaScript, do not put a `.d.ts` next to that file; move that file first.
- Move at most one directory per PR. Put the rename (`.js` to `.ts`) and the rewrite of the contents in separate commits.
