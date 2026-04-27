from src.belief_base import BeliefBase
from src.parser import parse_formula
from src.resolution import logically_equivalent
from src.revision import expand, revise


def _formulas_set(base: BeliefBase) -> set:
    return set(base.formulas())


def _entailment_equivalent_bases(left: BeliefBase, right: BeliefBase) -> bool:
    candidates = _formulas_set(left) | _formulas_set(right)
    for formula in candidates:
        if left.entails(formula) != right.entails(formula):
            return False
    return True


def test_agm_success() -> None:
    base = BeliefBase()
    base.add(parse_formula("p"), priority=2)

    phi = parse_formula("q")
    revised = revise(base, phi)

    assert revised.entails(phi)


def test_agm_inclusion_belief_base_version() -> None:
    base = BeliefBase()
    base.add(parse_formula("p"), priority=5)
    base.add(parse_formula("p -> q"), priority=4)

    phi = parse_formula("~q")
    revised = revise(base, phi)
    old_formulas = _formulas_set(base)

    for formula in revised.formulas():
        assert formula in old_formulas or formula == phi


def test_agm_vacuity() -> None:
    base = BeliefBase()
    base.add(parse_formula("p"), priority=4)

    phi = parse_formula("q")
    assert not base.entails(parse_formula("~q"))

    revised = revise(base, phi, priority=100)
    expanded = expand(base, phi, priority=100)

    assert revised == expanded


def test_agm_consistency() -> None:
    base = BeliefBase()
    base.add(parse_formula("p -> q"), priority=2)
    base.add(parse_formula("p"), priority=2)

    phi = parse_formula("~q | r")
    revised = revise(base, phi)

    assert revised.is_consistent()


def test_agm_extensionality() -> None:
    base = BeliefBase()
    base.add(parse_formula("p -> q"), priority=5)
    base.add(parse_formula("p"), priority=5)

    phi = parse_formula("q")
    psi = parse_formula("~~q")
    assert logically_equivalent(phi, psi)

    revised_phi = revise(base, phi)
    revised_psi = revise(base, psi)

    assert _entailment_equivalent_bases(revised_phi, revised_psi)
