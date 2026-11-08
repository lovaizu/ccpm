# Triage, sure of one queue

A system prompt that a shop's program sends with each support ticket, so that a model names the
queue of the team that answers it. The program around it holds what must hold. The prompt
contradicts itself on tickets of two topics, gives its queues no reason for their split, and its
examples and evals all lean to one queue. It's
a kept case of the [prompt best practice](../best-practice.md): a prompt with the verdict on each
question that someone who knows the work of the AI that runs it gives, so that an evaluator proves
itself on it before anyone trusts its verdicts. A question whose practice excludes a prompt of this
kind has the verdict n/a.

## Where it runs

The shop's program calls the model once for each new ticket. It sends the system prompt below and
the ticket as the user's message, and offers it one tool, `record_triage`, whose `queue` field takes
only `billing`, `shipping`, `account`, `technical`, or `unsure`, beside `quote` and `reason`. The
program checks each reply against the tool's schema, asks once more where it fails, and sends the
ticket to a person where it fails again. It routes the ticket and sets its deadline by the queue.
Its tests feed the check a reply with an unknown queue, one with no quote, and one that holds, and
see the first two refused and the third let through.

## Prompt

```text
You sort support tickets for Larkspur, a shop that sells garden tools online, into the queue of the
team that answers them, so that a customer reaches the right person on the first try. Read the
ticket, then record its queue with the record_triage tool, once.

The queues:
- billing: charges, refunds, invoices, and ways to pay.
- shipping: where an order is, damage on the way, and labels for returns.
- account: signing in, passwords, a changed email address, and closing an account.
- technical: the website or the app failing, such as a page that won't load or a basket that
  empties itself.
- unsure: a ticket you can't place in one of the others. A person reads these, as a wrong queue
  costs the customer a day while the ticket waits to be moved.

Always pick exactly one queue.

If a ticket is about two topics, list both queues.

In quote, give the sentence of the ticket your queue rests on, so that the team sees why. In reason,
say in a few words why that sentence belongs to that queue.

<examples>
<example>
Ticket: I was charged twice for order 4471.
record_triage: queue billing, quote "I was charged twice for order 4471.", reason a double charge
</example>
<example>
Ticket: My refund for the broken shears hasn't arrived after two weeks.
record_triage: queue billing, quote "My refund for the broken shears hasn't arrived", reason a refund
</example>
<example>
Ticket: The invoice shows my old address.
record_triage: queue billing, quote "The invoice shows my old address.", reason an invoice
</example>
</examples>
```

The evals hold 40 tickets from March, each with the queue a team lead gave it, graded by exact match
of the queue. None of them is `unsure`, and none is about two topics.

## How it ran held back

60 tickets from June, kept apart from the making, ran five times each. Tickets about a charge for
shipping went to `billing` in most runs. On tickets about two topics, some runs recorded one queue
and some tried to record two, which the schema refused, so the program asked again and then sent
each such ticket to a person.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | yes | The prompt says the queue serves a customer reaching the right person, and the task ends at one call of the tool. |
| Q2 | yes | It names the shop, each queue and what it holds, and the tool to call. |
| Q3 | no | The queues split by topic with no reason for the split, so a charge for shipping, which no queue's words settle, gets no ground to judge from. |
| Q4 | no | All three examples are billing tickets of one shape, so the model takes "a charge" for billing whatever the topic. |
| Q5 | yes | One call with one action has no order to keep, and the prompt gives no step. |
| Q6 | yes | The program routes the ticket and sets its deadline, and the model only names the queue. |
| Q7 | yes | The call offers one tool, the one the task needs. |
| Q8 | yes | The program checks each reply against the schema, and its tests show the check refusing a break and letting a good reply through. |
| Q9 | yes | A ticket the model can't place goes to a person through `unsure`. |
| Q10 | yes | The tool's schema fixes the form the program reads. |
| Q11 | n/a | A program reads the reply, and no person decides from it. |
| Q12 | yes | Each queue comes with the ticket's own sentence that it rests on. |
| Q13 | n/a | The program sends the prompt by itself, and no host chooses it. |
| Q14 | no | "Always pick exactly one queue" and "list both queues" pull apart on every ticket of two topics. |
| Q15 | yes | Each line bears on the label. |
| Q16 | no | The evals hold no `unsure` ticket and none of two topics, so they can't show the prompt failing where it fails. |
| Q17 | no | On the held-back tickets, charges for shipping went to the wrong team, and tickets of two topics got different replies from run to run. |
