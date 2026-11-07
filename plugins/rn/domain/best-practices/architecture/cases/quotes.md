# Quotes, a pass on some questions

A design of a web service that quotes the price of a home insurance policy. Its structure is sound,
and the rest is thin. It's a kept case of the [architecture best practice](../best-practice.md):
a deliverable with the verdict on each question that someone who knows the developer's work gives,
so that an evaluator proves itself on it before anyone trusts its verdicts.

## The deliverable

````markdown
# `quotes` architecture

This document says how the parts of quotes give [its product vision](product-vision.md). The
pricing core holds every rule of a quote. The API and the adapters around it only carry data in
and out.

## Drivers

### Use cases

- **`U1`**: the customer wants to enter their home's details and get a quote, or the reason none
  can be given. It carries the README's first step.

### Quality scenarios

quotes must be fast, secure, and scalable.

## Structure

```text
customer (person) -> quotes (software system) -> flood map service (software system)
quotes -> sales team's tools (software system), by quote events
quotes API (service) -> pricing core, flood map adapter (components); quotes database; quote events
```

Legend: an arrow points from the element that acts.

- **quotes API**, a service in Kotlin: takes a request for a quote and answers it. Its files lie in
  `api/`.
- **pricing core**, a component of the quotes API in Kotlin: the price of a home's cover. Its files
  lie in `core/pricing/`.
- **flood map adapter**, a component of the quotes API in Kotlin: how the flood map service's reply
  reads. Its files lie in `api/floodmap/`.
- **quotes database**, a database in PostgreSQL: each quote given.
- **quote events**, a Kafka topic: each quote given, for the sales team's tools.

## Dependencies

The pricing core depends on nothing outside Kotlin's standard library. The API and the adapters
depend on it, and on no other adapter. Konsist checks the rule in CI.

| Port | Owned by | What the core needs | Adapters |
| --- | --- | --- | --- |
| FloodRisk | pricing core | the flood risk of an address | flood map adapter, and the tests' map |

## Interfaces

The API sends a quote event to the topic for each quote.

## Runtime

### `U1`: a quote given

```text
customer -> quotes API: the home's details
quotes API -> pricing core: price the home
pricing core -> flood map adapter: the flood risk of the address
pricing core -> quotes API: the price
quotes API -> quotes database: saves the quote
quotes API -> quote events: the quote event
quotes API -> customer: the quote
```

## Deployment

quotes runs in the cloud.

## Decisions

- We use Kafka.
- We use PostgreSQL.

## Tests

Each feature has an end-to-end test in a browser, against staging. Unit tests cover the pricing
core where time allows.
````

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | no | The qualities are three adjectives, with no stimulus, no environment, and no measure, so they give a structure nothing to meet. |
| Q2 | yes | Each element is a container or a component of one, with its type, its technology, its one responsibility, and its files. |
| Q3 | yes | The rule points every dependency to the pricing core, its one port has a real adapter and a test's, and a tool checks it in CI. |
| Q4 | no | The quote event's form, its owner, and its contract go unnamed, so the sales team's tools and the API each guess them. The flood map service's contract goes unnamed too. |
| Q5 | no | `U1` draws only the quote given. The answer with a reason and no quote, which the use case names, and a flood map service that doesn't answer have no path. |
| Q6 | no | "In the cloud" names no environment, nothing it gives, no outside service, and no way to start the product. |
| Q7 | no | The opening gives the idea, but each decision gives no context, no option it beat, and no consequence. |
| Q8 | yes | No line says how a component works inside. |
| Q9 | no | End-to-end tests hold every case, the slowest level, and the unit level runs only where time allows. No double has a source or a check. |
| Q10 | no | No test runs a path of `U1` across the real joins, and the one test list there is, a test for each feature, comes from the features, not the runtime view. |
| Q11 | no | A new developer can't set the product up, test the event's form, or tell which outside services it needs. |
