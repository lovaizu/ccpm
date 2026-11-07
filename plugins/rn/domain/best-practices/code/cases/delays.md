# Delays, built past its need

A function that gives the waits before each retry of a failed call, in Python. Its tests come from
the specification and came first, but its design holds layers that nothing calls for, and its tests
compute what they expect. It's a kept case of the [code best practice](../best-practice.md): a
deliverable with the verdict on each question that someone who knows the maintainer's work gives, so
that an evaluator proves itself on it before anyone trusts its verdicts.

## Specification

- `delays(attempts, base)` gives the wait in seconds before each of `attempts` retries.
- The first wait is `base`, and each next one doubles the last, up to 60 seconds, which no wait
  passes.
- `attempts` is a whole number from 1 to 10, and `base` a whole number from 1 to 60. Any other value
  raises `ValueError`, whose message names the value and the range it must lie in.

## Setup

Python 3.9 or later, with nothing else to install. The tests run by `python3 -m unittest discover -s
.`.

## Code

`delays.py`:

```python
"""The waits before each retry of a failed call: a policy behind a port, made by a factory."""

from __future__ import annotations

import abc
import time

CAP = 60
LONGEST = 10


class ClockPort(abc.ABC):
    """What the policy asks of the time."""

    @abc.abstractmethod
    def now(self) -> float: ...


class SystemClockAdapter(ClockPort):
    def now(self) -> float:
        return time.time()


class DelayPolicyPort(abc.ABC):
    """A way to say how long to wait before each retry."""

    @abc.abstractmethod
    def delays(self, attempts: int, base: int) -> list[int]: ...


class ExponentialDelayPolicyAdapter(DelayPolicyPort):
    def __init__(self, clock: ClockPort) -> None:
        # Kept for a later policy that waits by the time of day, which none does yet.
        self.clock = clock

    def delays(self, attempts: int, base: int) -> list[int]:
        _bounded(attempts, 1, LONGEST, "attempts")
        _bounded(base, 1, CAP, "base")
        return [min(base * 2**n, CAP) for n in range(attempts)]


class DelayPolicyFactory:
    """Makes the policy the caller names."""

    def make(self, kind: str = "exponential", clock: ClockPort | None = None) -> DelayPolicyPort:
        if kind != "exponential":
            raise ValueError(f"no delay policy named {kind!r}; the one there is: exponential")
        return ExponentialDelayPolicyAdapter(clock or SystemClockAdapter())


def _bounded(value: int, low: int, high: int, kind: str) -> None:
    """Refuses a value outside low to high, by ValueError naming what it is."""
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        unit = " seconds" if kind == "base" else ""
        raise ValueError(f"{kind} must be a whole number from {low} to {high}{unit}, not {value!r}")
```

## Tests

`test_delays.py`:

```python
import unittest
from unittest import mock

from delays import CAP, DelayPolicyFactory

BASE = 2


class DelayPolicyTest(unittest.TestCase):
    def setUp(self):
        self.clock = mock.Mock()
        self.policy = DelayPolicyFactory().make(clock=self.clock)

    def check(self, attempts):
        expected = [min(BASE * 2**n, CAP) for n in range(attempts)]
        self.assertEqual(self.policy.delays(attempts, BASE), expected)

    def test_one_attempt_waits_the_base(self):
        self.check(1)

    def test_each_wait_doubles_the_last(self):
        self.check(4)

    def test_a_wait_stops_at_the_cap(self):
        self.check(10)

    def test_a_wait_can_reach_the_cap_exactly(self):
        self.assertEqual(self.policy.delays(3, 15), [15, 30, 60])

    def test_no_attempts_are_refused(self):
        with self.assertRaisesRegex(
            ValueError, "attempts must be a whole number from 1 to 10, not 0"
        ):
            self.policy.delays(0, BASE)

    def test_more_than_ten_attempts_are_refused(self):
        with self.assertRaisesRegex(ValueError, "not 11"):
            self.policy.delays(11, BASE)

    def test_attempts_given_as_text_are_refused(self):
        with self.assertRaisesRegex(ValueError, "not '3'"):
            self.policy.delays("3", BASE)

    def test_a_base_past_the_cap_is_refused(self):
        with self.assertRaisesRegex(
            ValueError, "base must be a whole number from 1 to 60 seconds, not 61"
        ):
            self.policy.delays(1, 61)

    def test_a_base_of_one_is_taken(self):
        self.assertEqual(self.policy.delays(2, 1), [1, 2])

    def test_a_base_at_the_cap_is_taken(self):
        self.assertEqual(self.policy.delays(2, 60), [60, 60])

    def test_a_base_of_zero_is_refused(self):
        with self.assertRaisesRegex(ValueError, "not 0"):
            self.policy.delays(1, 0)

    def test_a_base_that_isnt_whole_is_refused(self):
        with self.assertRaisesRegex(ValueError, "not 1.5"):
            self.policy.delays(1, 1.5)

    def test_the_policy_never_reads_the_clock(self):
        self.policy.delays(3, BASE)
        self.clock.now.assert_not_called()

    def test_an_unknown_policy_is_refused(self):
        with self.assertRaisesRegex(ValueError, "no delay policy named 'linear'"):
            DelayPolicyFactory().make("linear")
```

## How the maker worked

1. The maker listed the cases from the specification before any code: one attempt, the doubling, a
   wait that reaches the cap exactly, a wait the doubling would carry past it, the attempts 0, 1, 10,
   and 11, attempts given as text, and the base 1 and 60.
2. For each case in turn, the maker wrote its test, saw it fail, then wrote the code, and changed
   the structure only with every test passing.
3. Branch coverage showed the unit in a base's message unrun. The maker traced it to the refused
   bases the list had missed, and added the base 0 and 61 and a base of 1.5.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | yes | The one module, `delays.py`, says at its top that it holds the waits, and a change to the doubling stays in it. The layers inside it fail Q2, Q3, and Q5. |
| Q2 | no | `ClockPort` and `DelayPolicyPort` stand where nothing lies outside: the waits use no clock, and only one policy exists. |
| Q3 | no | An Abstract Factory and a class hierarchy hold one function's work, where the plain form is one function. |
| Q4 | no | `_bounded` joins two pieces of knowledge, the attempts' range and the base's, through the `kind` flag that picks the unit. |
| Q5 | no | The factory's `kind`, the clock, and its adapter answer no line of the specification. |
| Q6 | yes | `delays` checks each value before it makes any wait, and each message names the value and its range. |
| Q7 | yes | The list, with the cases coverage showed it missed, holds each class and each boundary of both arguments, and the cap reached exactly and passed. |
| Q8 | yes | The history shows each test fail before its code, and the structure changes in steps of their own. |
| Q9 | no | `check` computes the expected waits by the code's own formula, so a wrong formula passes, and the shared `BASE` and `setUp` hide what each test rests on. |
| Q10 | no | `test_the_policy_never_reads_the_clock` checks the calls made on a mock of a port inside the code. |
| Q11 | yes | The tests read nothing of the machine and pass in any order. |
| Q12 | yes | Each name says what it holds, each function is short and plain, and the one odd line, the clock kept unused, says why. |
| Q13 | yes | The gap coverage found went back to the list as the refused bases it missed. |
| Q14 | no | A newcomer changing the cap passes through four classes and the flag, and the tests that compute their expectations move with the code. |
