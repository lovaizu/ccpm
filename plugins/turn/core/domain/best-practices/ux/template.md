# `<Product>` UX

## Roles

- **`<role>`**: `<who they are>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<role>`: each role that comes to the product with a want of its own, such as a guest, a member
>   or an admin.
> - `<who they are>`: in one clause.

## OKRs

- `O<n>`: `<objective>`
  - `KR<n>.1`: `<key result>`. `<direction>`.
  - `KR<n>.2`: `<key result>`. `<direction>`.

`KR<n>.1` comes first: a change that improves `KR<n>.2` is kept only if `KR<n>.1` does not get
worse.
Key results have no targets, as a measure made a target stops being a good measure (Goodhart's
law). They show whether a change brought its objective closer.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - `<objective>`: what one role of Roles wants, in one sentence.
> - `<key result>`: what is measured, in one sentence.
> - `<direction>`: which way is better, such as "Lower is better".

## Scenarios

### `O<n>`: `<path>`

```mermaid
sequenceDiagram
  participant <id> as <name>
  <id>->><id>: <message>
```

- If `<condition>`: `<what the role does and gets>`.

> [!NOTE]
> DELETE_TEMPLATE_COMMENT:
> - One section for each objective.
> - `<path>`: how the role reaches `O<n>`, in a few words.
> - `<name>`: each one that takes part: a role as Roles names it, the product, or one outside it,
>   such as a payment service.
> - `<message>`: what one asks or hands another, in a few words.
> - `<condition>`: one point where the role leaves the main path, such as a run that stops or a
>   fault of the product, one line each; optional.
> - `<what the role does and gets>`: what the role does there, and what it then has.
