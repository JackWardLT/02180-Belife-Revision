from __future__ import annotations

import argparse

from src.belief_base import BeliefBase
from src.formula import formula_to_str
from src.parser import parse_formula
from src.revision import revise


def build_parser() -> argparse.ArgumentParser:
    """Create command-line parser for belief revision."""

    parser = argparse.ArgumentParser(description="Propositional belief revision CLI")
    parser.add_argument(
        "--belief",
        action="append",
        default=[],
        help="Belief in format 'formula:priority' (priority optional)",
    )
    parser.add_argument("--revise", required=True, help="Formula used for revision")
    return parser


def parse_belief_argument(raw: str) -> tuple[str, int]:
    """Parse one --belief argument value."""

    if ":" not in raw:
        return raw.strip(), 0

    formula_text, priority_text = raw.rsplit(":", 1)
    formula_text = formula_text.strip()
    try:
        priority = int(priority_text.strip())
    except ValueError as exc:
        raise ValueError(f"Invalid priority in belief argument: {raw!r}") from exc

    if not formula_text:
        raise ValueError("Belief formula cannot be empty")

    return formula_text, priority


def main() -> None:
    """Run belief revision from command line arguments."""

    args = build_parser().parse_args()

    base = BeliefBase()
    for raw_belief in args.belief:
        formula_text, priority = parse_belief_argument(raw_belief)
        base.add(parse_formula(formula_text), priority=priority, source="cli")

    revision_formula = parse_formula(args.revise)
    revised = revise(base, revision_formula)

    print("Original belief base:")
    print(_format_base(base))
    print(f"Revision formula: {formula_to_str(revision_formula)}")
    print()
    print("Final belief base after revision:")
    print(_format_base(revised))


def _format_base(base: BeliefBase) -> str:
    if len(base) == 0:
        return "{ }"

    formulas = [formula_to_str(entry.formula) for entry in base.entries]
    return "{ " + ", ".join(formulas) + " }"


if __name__ == "__main__":
    main()
