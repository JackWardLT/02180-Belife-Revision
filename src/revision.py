from __future__ import annotations

from itertools import combinations

from src.belief_base import Belief, BeliefBase
from src.formula import Formula
from src.resolution import is_satisfiable, negate

EXACT_ENUMERATION_LIMIT = 14


def expand(base: BeliefBase, phi: Formula, priority: int = 0) -> BeliefBase:
    """Return expansion of belief base by adding phi only."""

    expanded = base.copy()
    expanded.add(phi, priority=priority)
    return expanded


def contract(base: BeliefBase, phi: Formula) -> BeliefBase:
    """Contract belief base so phi is no longer entailed."""

    if not base.entails(phi):
        # Vacuity: if phi is not entailed, contraction leaves the base unchanged.
        return base

    entries = base.entries
    if len(entries) <= EXACT_ENUMERATION_LIMIT:
        return _contract_exact(entries, phi)
    # Greedy fallback used for performance, approximates partial meet contraction
    return _contract_greedy(entries, phi)


def revise(base: BeliefBase, phi: Formula, priority: int = 100) -> BeliefBase:
    """Revise a base using Levi identity: B * phi = (B ÷ ~phi) + phi."""

    if not is_satisfiable([phi]):
        raise ValueError("Cannot revise by an inconsistent formula")

    contracted = contract(base, negate(phi))
    return expand(contracted, phi, priority=priority)


def _contract_exact(entries: list[Belief], phi: Formula) -> BeliefBase:
    index_set = list(range(len(entries)))
    remainders: list[frozenset[int]] = []

    # Enumerate all subsets and keep those that do not entail phi.
    for subset_size in range(len(entries) + 1):
        for combo in combinations(index_set, subset_size):
            combo_set = frozenset(combo)
            formulas = [entries[i].formula for i in combo_set]
            if _entails(formulas, phi):
                continue
            remainders.append(combo_set)

    maximal_remainders = [
        r
        for r in remainders
        if not any(r < other for other in remainders)
    ]

    if not maximal_remainders:
        return BeliefBase([])

    scores = {
        remainder: sum(entries[i].priority for i in remainder)
        for remainder in maximal_remainders
    }
    best_score = max(scores.values())
    best_remainders = [r for r in maximal_remainders if scores[r] == best_score]

    # Selection function for prioritized partial meet: if multiple maximal-score
    # remainders remain, keep one deterministic representative to avoid
    # unnecessary information loss from intersecting many equally scored choices.
    selected = [_choose_deterministic_remainder(best_remainders, entries)]

    retained_indices = set.intersection(*(set(r) for r in selected)) if selected else set()
    retained_entries = [entries[i] for i in index_set if i in retained_indices]
    return BeliefBase(retained_entries)


def _choose_deterministic_remainder(
    remainders: list[frozenset[int]],
    entries: list[Belief],
) -> frozenset[int]:
    """Choose one preferred remainder among tied best-scoring candidates."""

    if len(remainders) == 1:
        return remainders[0]

    max_size = max(len(r) for r in remainders)
    size_filtered = [r for r in remainders if len(r) == max_size]

    def preference_key(remainder: frozenset[int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
        ordered_indices = tuple(sorted(remainder))
        ordered_priorities = tuple(-entries[i].priority for i in ordered_indices)
        return (ordered_priorities, ordered_indices)

    return min(size_filtered, key=preference_key)


def _contract_greedy(entries: list[Belief], phi: Formula) -> BeliefBase:
    remaining = list(entries)

    while _entails([b.formula for b in remaining], phi):
        removable_index = None

        for idx, belief in sorted(enumerate(remaining), key=lambda pair: (pair[1].priority, pair[0])):
            candidate = remaining[:idx] + remaining[idx + 1 :]
            if not _entails([b.formula for b in candidate], phi):
                removable_index = idx
                break

        if removable_index is None:
            removable_index = min(
                range(len(remaining)),
                key=lambda i: (remaining[i].priority, i),
            )

        remaining.pop(removable_index)

        if not remaining:
            break

    return BeliefBase(remaining)


def _entails(formulas: list[Formula], phi: Formula) -> bool:
    from src.resolution import entails

    return entails(formulas, phi)
