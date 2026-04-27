from __future__ import annotations

from itertools import combinations

from src.cnf import CNFClauses, Clause, Literal, cnf_to_clauses
from src.formula import Formula, Not


def negate(formula: Formula) -> Formula:
    """Return the syntactic negation of a formula."""

    if isinstance(formula, Not):
        return formula.child
    return Not(formula)


def resolve(ci: Clause, cj: Clause) -> set[Clause]:
    """Resolve two clauses and return all non-tautological resolvents."""

    resolvents: set[Clause] = set()

    for literal in ci:
        complementary = (literal[0], not literal[1])
        if complementary not in cj:
            continue

        merged = (set(ci) - {literal}) | (set(cj) - {complementary})
        if _is_tautological(merged):
            continue
        resolvents.add(frozenset(merged))

    return resolvents


def entails(beliefs: list[Formula], query: Formula) -> bool:
    """Return True if beliefs logically entail query via resolution refutation."""

    formulas = [*beliefs, negate(query)]
    clauses = _formulas_to_clauses(formulas)
    return _derives_empty_clause(clauses)


def is_satisfiable(formulas: list[Formula]) -> bool:
    """Check satisfiability of a formula set using resolution."""

    clauses = _formulas_to_clauses(formulas)
    return not _derives_empty_clause(clauses)


def is_consistent(formulas: list[Formula]) -> bool:
    """Alias for satisfiability in propositional logic."""

    return is_satisfiable(formulas)


def logically_equivalent(phi: Formula, psi: Formula) -> bool:
    """Check logical equivalence by bidirectional entailment."""

    return entails([phi], psi) and entails([psi], phi)


def _formulas_to_clauses(formulas: list[Formula]) -> CNFClauses:
    clauses: CNFClauses = set()
    for formula in formulas:
        clauses.update(cnf_to_clauses(formula))
    return clauses


def _derives_empty_clause(initial_clauses: CNFClauses) -> bool:
    if frozenset() in initial_clauses:
        return True

    clauses: set[Clause] = set(initial_clauses)

    while True:
        new_clauses: set[Clause] = set()
        for ci, cj in combinations(tuple(clauses), 2):
            resolvents = resolve(ci, cj)
            if frozenset() in resolvents:
                return True
            new_clauses |= (resolvents - clauses)

        if not new_clauses:
            return False

        clauses |= new_clauses


def _is_tautological(clause: set[Literal]) -> bool:
    for name, polarity in clause:
        if (name, not polarity) in clause:
            return True
    return False
