# knowledge_base.py
# Propositional Logic KB and Resolution Refutation
from typing import List, Set, Tuple, FrozenSet

# Type aliases for readability
Literal = str
Clause = FrozenSet[Literal]

# Limit resolution steps to keep the demo responsive
MAX_RESOLUTION_STEPS = 20000


def neg(literal: Literal) -> Literal:
    """Negate a literal. '-Pit_1_2' -> 'Pit_1_2', 'Pit_1_2' -> '-Pit_1_2'."""
    if literal.startswith("-"):
        return literal[1:]
    return f"-{literal}"


def is_tautology(clause: Clause) -> bool:
    """A clause is a tautology if it contains both a literal and its negation."""
    return any(neg(lit) in clause for lit in clause)


def resolve(c1: Clause, c2: Clause) -> List[Clause]:
    resolvents = []
    for lit in c1:
        if neg(lit) in c2:
            # Combine the two clauses minus the complementary pair
            resolvent = frozenset((c1 - {lit}) | (c2 - {neg(lit)}))
            if not is_tautology(resolvent):
                resolvents.append(resolvent)
    return resolvents


def pl_resolution(kb_clauses: List[Clause], negated_query: List[Clause]) -> Tuple[bool, int]:
    clauses: Set[Clause] = set(kb_clauses) | set(negated_query)
    clauses = {c for c in clauses if not is_tautology(c)}
    
    # We maintain a list for indexing
    clause_list = list(clauses)
    steps = 0
    last_round_start = 0
    
    while True:
        n = len(clause_list)
        new_clauses = set()
        
        # Sort clause_list to prioritize unit clauses (Unit Preference heuristic)
        # This makes resolution MUCH faster.
        clause_list.sort(key=len)

        for i in range(n):
            # Optimization: focus on resolving at least one 'new' clause
            # (new from the previous iteration)
            start_j = last_round_start if i < last_round_start else i + 1
            
            for j in range(start_j, n):
                steps += 1
                if steps > MAX_RESOLUTION_STEPS:
                    return False, steps
                
                # Try to resolve
                c1, c2 = clause_list[i], clause_list[j]
                
                # Optimization: check if they can even resolve before calling resolve()
                # They must share a literal that appears negated in the other.
                can_resolve = any(neg(lit) in c2 for lit in c1)
                if not can_resolve:
                    continue

                resolvents = resolve(c1, c2)
                for r in resolvents:
                    if len(r) == 0:
                        return True, steps
                    if r not in clauses:
                        new_clauses.add(r)
                        # If we found a new unit clause, it's very valuable
                        if len(r) == 1:
                            # We could restart or prioritize, but just adding is good
                            pass

        if not new_clauses:
            return False, steps
            
        last_round_start = n
        for c in new_clauses:
            if c not in clauses:
                clauses.add(c)
                clause_list.append(c)


