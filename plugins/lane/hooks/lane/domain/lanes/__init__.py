"""Each type of rule that Lane lays, by the name a proposal gives it. Each type alone makes its
sentence and its check, so the step a role reads and the call the guard stops never differ."""

from __future__ import annotations

from types import ModuleType

from domain.lanes import run_only

TYPES: dict[str, ModuleType] = {"run_only": run_only}
