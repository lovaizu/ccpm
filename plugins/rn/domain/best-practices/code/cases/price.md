# Price, a pass on every question

A command that prices an order, in Python. It's a kept case of the [code best
practice](../best-practice.md): a deliverable with the verdict on each question that someone who
knows the maintainer's work gives, so that an evaluator proves itself on it before anyone trusts its
verdicts.

## Specification

- `price <total> [--member]` prints the price of an order of `<total>` cents and exits 0.
- A total is a whole number of cents from 0 to 1,000,000.
- An order of 10,000 cents or more gets 10% off. A member gets 5% off any order. A member's large
  order gets both, 15% off.
- The price rounds down to whole cents.
- Any other arguments print what to fix on standard error, and the command exits 2.

## Setup

Python 3.9 or later, with nothing else to install. The tests run by `python3 -m unittest discover -s
.`.

## Code

`pricing.py`:

```python
"""What an order costs after its discounts: the one place that holds the discount rules."""

# An order of this many cents or more is a large order.
LARGE_ORDER = 10_000
# The percent off a large order, and off any order of a member's.
LARGE_OFF = 10
MEMBER_OFF = 5


def price(total: int, member: bool) -> int:
    """The price, in whole cents rounded down, of an order of `total` cents, after each discount
    that applies. Expects a total of 0 or more, which the command's edge checks."""
    off = (LARGE_OFF if total >= LARGE_ORDER else 0) + (MEMBER_OFF if member else 0)
    return total * (100 - off) // 100
```

`price.py`:

```python
"""The price command: reads its arguments into an order, or refuses them with what to fix."""

import re
import sys

import pricing

LARGEST = 1_000_000
USAGE = f"usage: price <total in cents, 0 to {LARGEST}> [--member]"


class Refused(Exception):
    """Arguments the command can't take, with the message that says what to fix."""


def order(args: list[str]) -> tuple[int, bool]:
    """The total and the membership the arguments give. Refuses, by Refused, any others."""
    if len(args) not in (1, 2) or args[1:] not in ([], ["--member"]):
        raise Refused(USAGE)
    if not re.fullmatch(r"[0-9]+", args[0]) or int(args[0]) > LARGEST:
        raise Refused(f"the total {args[0]!r} is no whole number of cents from 0 to {LARGEST}")
    return int(args[0]), args[1:] == ["--member"]


def main(args: list[str]) -> int:
    """Prints the order's price and gives 0, or prints what to fix and gives 2."""
    try:
        total, member = order(args)
    except Refused as why:
        print(f"price: {why}", file=sys.stderr)
        return 2
    print(pricing.price(total, member))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

## Tests

`test_pricing.py`:

```python
import unittest

from pricing import price


class Price(unittest.TestCase):
    def test_an_order_just_below_a_large_one_pays_in_full(self):
        # Given: 9,999 cents, one below a large order, of no member
        # When: it's priced
        # Then: no discount applies
        self.assertEqual(price(9_999, member=False), 9_999)

    def test_a_large_order_gets_ten_percent_off(self):
        self.assertEqual(price(10_000, member=False), 9_000)

    def test_a_member_gets_five_percent_off_a_small_order(self):
        self.assertEqual(price(2_000, member=True), 1_900)

    def test_a_member_s_large_order_gets_both_discounts(self):
        self.assertEqual(price(10_000, member=True), 8_500)

    def test_the_price_rounds_down_to_whole_cents(self):
        # Given: 999 cents of a member's, which 5% off makes 949.05
        # Then: the part of a cent is dropped
        self.assertEqual(price(999, member=True), 949)

    def test_an_empty_order_costs_nothing(self):
        self.assertEqual(price(0, member=True), 0)
```

`test_price.py`:

```python
import contextlib
import io
import unittest

from price import Refused, main, order


class Order(unittest.TestCase):
    def test_a_total_and_the_member_flag_make_a_member_s_order(self):
        self.assertEqual(order(["10000", "--member"]), (10_000, True))

    def test_the_largest_total_is_taken(self):
        self.assertEqual(order(["1000000"]), (1_000_000, False))

    def test_a_total_past_the_largest_is_refused_with_what_is_taken(self):
        with self.assertRaisesRegex(Refused, r"'1000001' is no whole number of cents from 0 to"):
            order(["1000001"])

    def test_a_negative_total_is_refused(self):
        with self.assertRaisesRegex(Refused, r"'-1'"):
            order(["-1"])

    def test_a_total_with_a_fraction_of_a_cent_is_refused(self):
        with self.assertRaisesRegex(Refused, r"'12.5'"):
            order(["12.5"])

    def test_a_flag_other_than_member_is_refused_with_the_usage(self):
        with self.assertRaisesRegex(Refused, r"^usage: price"):
            order(["100", "--vip"])

    def test_no_arguments_are_refused_with_the_usage(self):
        with self.assertRaisesRegex(Refused, r"^usage: price"):
            order([])


class Main(unittest.TestCase):
    def test_an_order_prints_its_price_and_gives_0(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["10000", "--member"])
        self.assertEqual((code, out.getvalue()), (0, "8500\n"))

    def test_a_refusal_prints_what_to_fix_and_gives_2(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = main(["-1"])
        self.assertEqual(code, 2)
        self.assertIn("price: the total '-1' is no whole number", err.getvalue())
```

## How the maker worked

1. The maker listed the cases from the specification before any code. The classes of a total: taken,
   past the largest, negative, and no whole number. The boundaries: 9,999 and 10,000 for a large
   order, and 1,000,001 past the largest. The decision table of large order and member:
   0%, 5%, 10%, and 15% off. The rounding, and the arguments other than `--member`.
2. For each case in turn, the maker wrote its test, ran the tests and saw it fail, then wrote the
   code that made it pass. The history holds a commit for each, with the failing run before it.
3. Mutation testing then found that `> LARGEST` could become `>= LARGEST` unseen. The maker traced
   it to the boundary the list had missed, the largest total taken, and added that case and its
   test.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | yes | `pricing.py` hides the discount rules, and `price.py` hides how the command reads its arguments. Each says so at its top. |
| Q2 | yes | The core, `pricing.py`, imports nothing. The command's edge alone reads the arguments and prints. No port stands where nothing lies outside. |
| Q3 | yes | No problem here calls for a pattern, and the code uses none. |
| Q4 | yes | Each discount, the large order's line, and the largest total each live in one named constant. |
| Q5 | yes | Each branch and argument answers a line of the specification. |
| Q6 | yes | `order` checks every argument before `price` runs, and each refusal names the value and what the command takes. |
| Q7 | yes | The list, with the boundary mutation testing showed it missed, holds each class, each boundary, and each column of the decision table, with expected values worked from the specification. |
| Q8 | yes | The history shows each test fail before its code, and the structure changes in commits of their own. |
| Q9 | yes | Each test names one behavior and shows its inputs and its expected result in its body. |
| Q10 | yes | The tests call `price` and `order` and `main` as their callers do, with no doubles, as nothing lies outside the process. |
| Q11 | yes | The tests read nothing of the machine, share no state, and pass in any order. |
| Q12 | yes | Each function says in one sentence what it does, and each name says what it holds. |
| Q13 | yes | The one gap mutation testing found went back to the list as the boundary it missed. |
| Q14 | yes | A change to a discount is one constant in `pricing.py`, and the test named for that discount shows whether every other one still holds. |
