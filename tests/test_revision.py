from src.belief_base import BeliefBase
from src.parser import parse_formula
from src.revision import contract, expand, revise


def test_expand_is_simple_addition() -> None:
    base = BeliefBase()
    base.add(parse_formula("p"), priority=2)
    base.add(parse_formula("~p"), priority=1)

    expanded = expand(base, parse_formula("q"), priority=3)

    assert len(expanded.entries) == 3
    assert expanded.entails(parse_formula("p"))
    assert expanded.entails(parse_formula("~p"))


def test_revision_by_negated_belief() -> None:
    base = BeliefBase()
    base.add(parse_formula("p"), priority=5)
    base.add(parse_formula("q"), priority=2)

    revised = revise(base, parse_formula("~q"), priority=10)

    assert revised.entails(parse_formula("~q"))
    assert not revised.entails(parse_formula("q"))


def test_contraction_by_entailed_formula_uses_entailment() -> None:
    base = BeliefBase()
    base.add(parse_formula("p"), priority=1)
    base.add(parse_formula("p & q"), priority=2)
    base.add(parse_formula("p | q"), priority=3)
    base.add(parse_formula("p <-> q"), priority=4)

    contracted = contract(base, parse_formula("p"))
    assert not contracted.entails(parse_formula("p"))


def test_revision_keeps_maximal_subset_in_tie_case() -> None:
    base = BeliefBase()
    base.add(parse_formula("p"), priority=5)
    base.add(parse_formula("p -> q"), priority=5)

    revised = revise(base, parse_formula("~q"), priority=100)

    assert revised.entails(parse_formula("~q"))
    old_formula_count = sum(1 for f in revised.formulas() if f in base.formulas())
    assert old_formula_count == 1


def test_revision_not_overly_destructive_for_multiple_derivations() -> None:
    base = BeliefBase()
    base.add(parse_formula("p"), priority=5)
    base.add(parse_formula("q"), priority=5)
    base.add(parse_formula("p -> r"), priority=5)
    base.add(parse_formula("q -> r"), priority=5)

    revised = revise(base, parse_formula("~r"), priority=100)

    assert revised.entails(parse_formula("~r"))
    old_formula_count = sum(1 for f in revised.formulas() if f in base.formulas())
    assert old_formula_count == 2
