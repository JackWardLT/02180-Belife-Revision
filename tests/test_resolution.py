from src.parser import parse_formula
from src.resolution import entails, is_consistent, is_satisfiable, logically_equivalent


def test_entails_simple_chain() -> None:
    beliefs = [parse_formula("p -> q"), parse_formula("p")]
    assert entails(beliefs, parse_formula("q"))


def test_entails_with_biconditional_example() -> None:
    beliefs = [
        parse_formula("p <-> (q | r)"),
        parse_formula("~q"),
        parse_formula("~r"),
    ]
    assert entails(beliefs, parse_formula("~p"))


def test_inconsistent_base_detection() -> None:
    formulas = [parse_formula("p"), parse_formula("q"), parse_formula("p -> ~q")]
    assert not is_consistent(formulas)
    assert not is_satisfiable(formulas)


def test_logical_equivalence() -> None:
    phi = parse_formula("p -> q")
    psi = parse_formula("~p | q")
    assert logically_equivalent(phi, psi)
