from __future__ import annotations

from src.formula import And, Formula, Iff, Implies, Not, Or, Var

Literal = tuple[str, bool]
Clause = frozenset[Literal]
CNFClauses = set[Clause]


def eliminate_iff(formula: Formula) -> Formula:
    """Eliminate biconditionals from a formula."""

    if isinstance(formula, Var):
        return formula
    if isinstance(formula, Not):
        return Not(eliminate_iff(formula.child))
    if isinstance(formula, And):
        return And(eliminate_iff(formula.left), eliminate_iff(formula.right))
    if isinstance(formula, Or):
        return Or(eliminate_iff(formula.left), eliminate_iff(formula.right))
    if isinstance(formula, Implies):
        return Implies(eliminate_iff(formula.left), eliminate_iff(formula.right))
    if isinstance(formula, Iff):
        left = eliminate_iff(formula.left)
        right = eliminate_iff(formula.right)
        return And(Implies(left, right), Implies(right, left))
    raise TypeError(f"Unsupported formula type: {type(formula)!r}")


def eliminate_implies(formula: Formula) -> Formula:
    """Eliminate implications from a formula."""

    if isinstance(formula, Var):
        return formula
    if isinstance(formula, Not):
        return Not(eliminate_implies(formula.child))
    if isinstance(formula, And):
        return And(eliminate_implies(formula.left), eliminate_implies(formula.right))
    if isinstance(formula, Or):
        return Or(eliminate_implies(formula.left), eliminate_implies(formula.right))
    if isinstance(formula, Implies):
        return Or(Not(eliminate_implies(formula.left)), eliminate_implies(formula.right))
    raise TypeError("Iff should be removed before eliminating implications")


def move_not_inwards(formula: Formula) -> Formula:
    """Push negations inwards using De Morgan laws."""

    if isinstance(formula, Var):
        return formula
    if isinstance(formula, And):
        return And(move_not_inwards(formula.left), move_not_inwards(formula.right))
    if isinstance(formula, Or):
        return Or(move_not_inwards(formula.left), move_not_inwards(formula.right))
    if isinstance(formula, Not):
        child = formula.child
        if isinstance(child, Var):
            return formula
        if isinstance(child, Not):
            return move_not_inwards(child.child)
        if isinstance(child, And):
            return Or(
                move_not_inwards(Not(child.left)),
                move_not_inwards(Not(child.right)),
            )
        if isinstance(child, Or):
            return And(
                move_not_inwards(Not(child.left)),
                move_not_inwards(Not(child.right)),
            )
        raise TypeError("Formula should contain only And/Or/Not/Var at this stage")
    raise TypeError("Formula should contain only And/Or/Not/Var at this stage")


def distribute_or_over_and(formula: Formula) -> Formula:
    """Distribute disjunction over conjunction to produce CNF shape."""

    if isinstance(formula, (Var, Not)):
        return formula
    if isinstance(formula, And):
        return And(
            distribute_or_over_and(formula.left),
            distribute_or_over_and(formula.right),
        )
    if isinstance(formula, Or):
        left = distribute_or_over_and(formula.left)
        right = distribute_or_over_and(formula.right)

        if isinstance(left, And):
            return And(
                distribute_or_over_and(Or(left.left, right)),
                distribute_or_over_and(Or(left.right, right)),
            )
        if isinstance(right, And):
            return And(
                distribute_or_over_and(Or(left, right.left)),
                distribute_or_over_and(Or(left, right.right)),
            )
        return Or(left, right)
    raise TypeError("Formula should contain only And/Or/Not/Var at this stage")


def to_cnf(formula: Formula) -> Formula:
    """Convert any supported formula to conjunctive normal form."""

    no_iff = eliminate_iff(formula)
    no_imp = eliminate_implies(no_iff)
    nnf = move_not_inwards(no_imp)
    return distribute_or_over_and(nnf)


def cnf_to_clauses(formula: Formula) -> CNFClauses:
    """Convert a CNF AST formula into a set of clauses."""

    cnf_formula = to_cnf(formula)
    clauses: CNFClauses = set()

    for conjunct in _flatten_and(cnf_formula):
        literals = _extract_clause_literals(conjunct)
        if _is_tautological_clause(literals):
            continue
        clauses.add(frozenset(literals))

    return clauses


def _flatten_and(formula: Formula) -> list[Formula]:
    if isinstance(formula, And):
        return _flatten_and(formula.left) + _flatten_and(formula.right)
    return [formula]


def _extract_clause_literals(formula: Formula) -> set[Literal]:
    if isinstance(formula, Or):
        left = _extract_clause_literals(formula.left)
        right = _extract_clause_literals(formula.right)
        return left | right

    if isinstance(formula, Var):
        return {(formula.name, True)}

    if isinstance(formula, Not) and isinstance(formula.child, Var):
        return {(formula.child.name, False)}

    raise ValueError("Formula is not in CNF clause-literal form")


def _is_tautological_clause(literals: set[Literal]) -> bool:
    for name, polarity in literals:
        if (name, not polarity) in literals:
            return True
    return False
