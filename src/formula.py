from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True)
class Var:
    """A propositional variable."""

    name: str


@dataclass(frozen=True)
class Not:
    """Negation of a formula."""

    child: Formula


@dataclass(frozen=True)
class And:
    """Conjunction of two formulas."""

    left: Formula
    right: Formula


@dataclass(frozen=True)
class Or:
    """Disjunction of two formulas."""

    left: Formula
    right: Formula


@dataclass(frozen=True)
class Implies:
    """Material implication."""

    left: Formula
    right: Formula


@dataclass(frozen=True)
class Iff:
    """Biconditional."""

    left: Formula
    right: Formula


Formula: TypeAlias = Var | Not | And | Or | Implies | Iff


_PRECEDENCE = {
    Iff: 1,
    Implies: 2,
    Or: 3,
    And: 4,
    Not: 5,
    Var: 6,
}


def formula_to_str(formula: Formula) -> str:
    """Render a formula with minimal parentheses."""

    def _render(node: Formula, parent_prec: int) -> str:
        prec = _PRECEDENCE[type(node)]

        if isinstance(node, Var):
            text = node.name
        elif isinstance(node, Not):
            child_text = _render(node.child, prec)
            text = f"~{child_text}"
        elif isinstance(node, And):
            left = _render(node.left, prec)
            right = _render(node.right, prec + 1)
            text = f"{left} & {right}"
        elif isinstance(node, Or):
            left = _render(node.left, prec)
            right = _render(node.right, prec + 1)
            text = f"{left} | {right}"
        elif isinstance(node, Implies):
            left = _render(node.left, prec + 1)
            right = _render(node.right, prec)
            text = f"{left} -> {right}"
        elif isinstance(node, Iff):
            left = _render(node.left, prec + 1)
            right = _render(node.right, prec)
            text = f"{left} <-> {right}"
        else:
            raise TypeError(f"Unsupported formula type: {type(node)!r}")

        if prec < parent_prec:
            return f"({text})"
        return text

    return _render(formula, 0)
