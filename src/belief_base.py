from __future__ import annotations

from dataclasses import dataclass

from src.formula import Formula
from src.resolution import entails, is_consistent


@dataclass(frozen=True)
class Belief:
    """One belief entry with optional source metadata and priority."""

    formula: Formula
    priority: int = 0
    source: str | None = None


class BeliefBase:
    """Priority-aware belief base storing explicit formulas only."""

    def __init__(self, entries: list[Belief] | None = None) -> None:
        self._entries: list[Belief] = list(entries) if entries is not None else []

    @property
    def entries(self) -> list[Belief]:
        """Return a shallow copy of belief entries."""

        return list(self._entries)

    def add(self, formula: Formula, priority: int = 0, source: str | None = None) -> None:
        """Add a belief to the base."""

        self._entries.append(Belief(formula=formula, priority=priority, source=source))

    def remove(self, formula: Formula) -> None:
        """Remove all occurrences of a formula from the base."""

        self._entries = [entry for entry in self._entries if entry.formula != formula]

    def formulas(self) -> list[Formula]:
        """Return stored formulas in insertion order."""

        return [entry.formula for entry in self._entries]

    def entails(self, query: Formula) -> bool:
        """Check whether current base entails query."""

        return entails(self.formulas(), query)

    def is_consistent(self) -> bool:
        """Check whether current base is logically consistent."""

        return is_consistent(self.formulas())

    def copy(self) -> BeliefBase:
        """Return a copy of the belief base."""

        return BeliefBase(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BeliefBase):
            return False
        return self._entries == other._entries

    def __str__(self) -> str:
        if not self._entries:
            return "BeliefBase([])"

        lines = ["BeliefBase(["]
        for entry in self._entries:
            source = f", source={entry.source!r}" if entry.source is not None else ""
            lines.append(
                f"  formula={entry.formula}, priority={entry.priority}{source}"
            )
        lines.append("])")
        return "\n".join(lines)
