# Notes for Report


## Belief Base vs Belief Set

A key design decision is the use of a **belief base** rather than a belief set.

A belief set is deductively closed, meaning it contains all logical consequences of its formulas. While theoretically appealing, this leads to issues such as logical omniscience and becomes computationally infeasible.

A belief base, on the other hand:

- Is **not closed under logical consequence**
- Stores only explicitly given formulas
- Computes consequences dynamically when needed

This approach is more computationally manageable and aligns better with practical AI systems. Logical entailment is handled on demand rather than precomputed.

---

## Logical Entailment (Resolution)

Entailment is implemented using **resolution**, which is a sound and complete method for propositional logic.

To check whether:

```

KB ⊨ φ

```

The following procedure is used:

1. Compute:
```

KB ∧ ¬φ

```
2. Convert the result into **Conjunctive Normal Form (CNF)**
3. Apply resolution repeatedly
4. If the empty clause is derived → entailment holds

Important points:

- CNF is required because resolution operates on clauses
- The method guarantees correctness (soundness and completeness)

---

## Contraction

Contraction is one of the most critical parts of the implementation.

### Goal

Remove a formula `φ` from the belief base while making **minimal changes**.

### Remainders

A remainder is defined as:

- A subset of the belief base
- That does **not** entail `φ`
- And is **maximal** (no belief can be added back without reintroducing `φ`)

### Partial Meet Contraction

The theoretical process:

1. Compute all remainders
2. Select a subset of them (selection function)
3. Take their intersection

### Implementation Detail (Priority-Based Selection)

The implementation extends the standard approach:

- Each belief is assigned a **priority (entrenchment)**
- Remainders are scored based on retained priorities
- The highest-scoring remainder is selected

### Deterministic Tie-Breaking

A key design decision:

- If multiple remainders have equal maximal score, intersecting all of them may remove too many beliefs
- Instead, a **deterministic selection function** chooses a single preferred remainder
- This preserves more information while still respecting the principle of minimal change

---

## Expansion

Expansion is straightforward:

- Adds a new formula `φ` to the belief base
- Does **not** enforce consistency

Formally:

```

B + φ

```

---

## Revision (Levi Identity)

Revision is defined using the **Levi Identity**:

```

B * φ = (B ÷ ¬φ) + φ

```

Interpretation:

1. Remove beliefs that conflict with `φ`
2. Add `φ` to the belief base

This follows directly from the theoretical framework presented in lectures.

---

## AGM Postulates

The system is evaluated against key **AGM postulates**:

- **Success** → the new belief is included
- **Inclusion** → minimal change is preserved
- **Vacuity** → no change if there is no conflict
- **Consistency** → consistency is preserved in our tested cases when revising by satisfiable input
- **Extensionality** → logically equivalent inputs yield entailment-equivalent revision outcomes

These postulates serve as rationality criteria and help validate the correctness of the implementation.

---

## Priority System

The priority mechanism is a practical extension beyond classical AGM theory.

- Beliefs are assigned importance levels
- Lower-priority beliefs are more likely to be removed, while maximal retained-priority subsets are preferred
- This reflects more realistic reasoning behavior

Additionally:

- The priority system effectively functions as the **selection function** in partial meet contraction

---

## Trade-offs and Limitations

Some limitations arise from computational complexity:

- Exact computation of all remainders is **exponential**
- Therefore:
  - Exact methods are used for small belief bases
  - A greedy approximation is used for larger ones

This represents a practical compromise between correctness and efficiency.

---

## Key Takeaways

- Belief revision involves more than simple addition/removal of facts
- Maintaining consistency is non-trivial
- Small implementation details (e.g., tie-breaking) can significantly impact results
- Theoretical models (AGM) require adaptation for practical use

---

## Topics

- Belief base explanation
- Resolution-based entailment
- CNF transformation
- Contraction (remainders + selection)
- Deterministic tie-breaking strategy
- Levi identity
- AGM postulates
- Priority system justification
- Trade-offs and limitations
