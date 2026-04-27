import pytest

from src.formula import And, Iff, Implies, Not, Or, Var
from src.parser import parse_formula


def test_parse_variable() -> None:
    assert parse_formula("p") == Var("p")


def test_parse_precedence() -> None:
    parsed = parse_formula("~p & q | r")
    assert parsed == Or(And(Not(Var("p")), Var("q")), Var("r"))


def test_parse_implication_and_iff_right_associative() -> None:
    parsed_imp = parse_formula("p -> q -> r")
    assert parsed_imp == Implies(Var("p"), Implies(Var("q"), Var("r")))

    parsed_iff = parse_formula("p <-> q <-> r")
    assert parsed_iff == Iff(Var("p"), Iff(Var("q"), Var("r")))


def test_parse_parentheses() -> None:
    parsed = parse_formula("p <-> (q | r)")
    assert parsed == Iff(Var("p"), Or(Var("q"), Var("r")))


def test_parse_nested_negation() -> None:
    parsed = parse_formula("~(p & q)")
    assert parsed == Not(And(Var("p"), Var("q")))


@pytest.mark.parametrize("text", ["", "(", "p &", "-> p", "p )) q", "p <->"])
def test_parse_invalid_syntax(text: str) -> None:
    with pytest.raises(ValueError):
        parse_formula(text)
