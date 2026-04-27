from src.cnf import cnf_to_clauses, to_cnf
from src.formula import And, Not, Or, Var
from src.parser import parse_formula


def test_to_cnf_eliminates_implies() -> None:
    formula = parse_formula("p -> q")
    cnf = to_cnf(formula)
    assert cnf == Or(Not(Var("p")), Var("q"))


def test_to_cnf_de_morgan() -> None:
    formula = parse_formula("~(p & q)")
    cnf = to_cnf(formula)
    assert cnf == Or(Not(Var("p")), Not(Var("q")))


def test_to_cnf_distribution() -> None:
    formula = parse_formula("p | (q & r)")
    cnf = to_cnf(formula)
    assert cnf == And(Or(Var("p"), Var("q")), Or(Var("p"), Var("r")))


def test_cnf_to_clauses_removes_tautologies() -> None:
    formula = parse_formula("(p | ~p) & q")
    clauses = cnf_to_clauses(formula)
    assert clauses == {frozenset({("q", True)})}


def test_cnf_to_clauses_deduplicates_literals() -> None:
    formula = parse_formula("p | p | q")
    clauses = cnf_to_clauses(formula)
    assert clauses == {frozenset({("p", True), ("q", True)})}
