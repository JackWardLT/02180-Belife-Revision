# Propositional Belief Revision Engine



A Python 3.11+ implementation of a propositional belief revision agent.

## Authors
- Isabella Blinkenberg Madsen – s236178
- Lars Thorvik – s253735
- Román Olalla García – s254615
- Ruta Miglava – s253817

## Features

- Symbolic propositional formulas represented as immutable AST dataclasses.
- Recursive descent parsing with precedence and parentheses.
- CNF conversion pipeline implemented from scratch.
- Resolution-based entailment and satisfiability checks.
- Priority-aware belief base with metadata.
- Expansion, contraction, and revision via Levi identity:

  B * phi = (B ÷ ~phi) + phi

- Tests for parser, CNF, resolution, revision behavior, and AGM-style postulates.

## Project Layout

- src/formula.py
- src/parser.py
- src/cnf.py
- src/resolution.py
- src/belief_base.py
- src/revision.py
- src/cli.py
- tests/test_parser.py
- tests/test_cnf.py
- tests/test_resolution.py
- tests/test_revision.py
- tests/test_agm_postulates.py

## Formula Syntax

Supported syntax:

- Variables: p, q, r, A, B, rain, prepared, lucky
- Negation: ~
- Conjunction: &
- Disjunction: |
- Implication: ->
- Biconditional: <->
- Parentheses: ( and )

Examples:

- p
- ~p
- p & q
- p -> q
- p <-> (q | r)
- ~(p & q)

Precedence used by the parser:

1. ~
2. &
3. |
4. ->
5. <->

Implication and biconditional are parsed right-associatively.

## Design Choices

### Belief Base vs Belief Set

The implementation uses a finite explicit belief base (stored formulas) rather than a logically closed belief set.

This makes operations computationally manageable and transparent for assignments. Entailment is computed on demand by resolution.

### Resolution-Based Entailment

To test whether KB entails phi:

1. Build KB with ~phi.
2. Convert formulas to CNF clauses.
3. Saturate the clause set by pairwise resolution.
4. If empty clause is derived, entailment holds.

No external SAT or theorem proving libraries are used.

### Contraction: Prioritized Partial Meet

For small bases, contraction computes inclusion-maximal remainders that do not entail the target formula.

- Score each remainder by sum of retained priorities.
- Select highest-scoring remainder(s).
- Return the intersection of selected remainders.

Lower-priority beliefs are more likely to be removed.

For larger bases, a greedy fallback removes low-priority formulas until entailment is broken.

### Expansion

Expansion is simple addition. It does not enforce consistency.

### Revision with Levi Identity

Revision is implemented as:

1. Contract by ~phi.
2. Expand by phi.

If phi itself is inconsistent, revision raises ValueError.

## Installation and Test

Create and activate a Python 3.11+ environment, then install pytest:

```powershell
python -m pip install pytest
```

Run tests:

```powershell
pytest -q
```

## CLI Usage

Example:

```powershell
python -m src.cli --belief "p:5" --belief "p -> q:4" --belief "q:1" --revise "~q"
```

Output includes:

- Original belief base
- Revision operation
- Resulting revised belief base

## AGM-Style Tests Included

The suite checks:

1. Success
2. Inclusion (belief-base interpretation)
3. Vacuity
4. Consistency
5. Extensionality
