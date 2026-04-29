# The Knowledge-Based Wumpus Agent using propositional logic.

from typing import Dict, List, Optional, Set, Tuple

from knowledge_base import Clause, neg, pl_resolution


class WumpusAgent:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols

        # Current agent position
        self.position: Tuple[int, int] = (0, 0)

        # Cells the agent has visited
        self.visited: Set[Tuple[int, int]] = set()

        # Cells known to be safe (proven by resolution or directly observed)
        self.safe_cells: Set[Tuple[int, int]] = set()

        # Cells confirmed to have hazards (from KB unit clauses)
        self.confirmed_pits: Set[Tuple[int, int]] = set()
        self.confirmed_wumpus: Set[Tuple[int, int]] = set()

        # The knowledge base: list of CNF clauses
        self.kb: List[Clause] = []

        # Tracking metrics
        self.total_inference_steps: int = 0
        self.last_percepts: Dict[str, bool] = {}
        self.last_safe_inferred: bool = False
        self.status_message: str = "Agent initialized."

        # Initialize: start cell (0,0) is safe (agent spawned there alive)
        self._mark_safe(0, 0)
        self.visited.add((0, 0))

    # -----------------------------------------------------------------
    # Helper: cell ID strings for propositional variables
    # -----------------------------------------------------------------

    def _pit_id(self, r: int, c: int) -> str:
        return f"Pit_{r}_{c}"

    def _wumpus_id(self, r: int, c: int) -> str:
        return f"Wumpus_{r}_{c}"

    def _get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbors.append((nr, nc))
        return neighbors

    def _mark_safe(self, r: int, c: int):
        """Add unit clauses asserting no pit and no wumpus at (r,c)."""
        self.safe_cells.add((r, c))
        # Add as unit clauses: -Pit_r_c and -Wumpus_r_c
        no_pit = frozenset({neg(self._pit_id(r, c))})
        no_wumpus = frozenset({neg(self._wumpus_id(r, c))})
        if no_pit not in self.kb:
            self.kb.append(no_pit)
        if no_wumpus not in self.kb:
            self.kb.append(no_wumpus)

    # -----------------------------------------------------------------
    # TELL: update KB from percepts at current position
    # -----------------------------------------------------------------

    def tell(self, pos: Tuple[int, int], percepts: Dict[str, bool]):
        # Encode percepts as rules and add to KB
        r, c = pos
        neighbors = self._get_neighbors(r, c)
        self.last_percepts = percepts

        # -- Breeze rules --
        if not percepts.get("breeze", False):
            # No breeze => no pit in any adjacent cell
            for nr, nc in neighbors:
                clause = frozenset({neg(self._pit_id(nr, nc))})
                if clause not in self.kb:
                    self.kb.append(clause)
                    # Also directly mark the neighbor's pit status
                    self.safe_cells.add((nr, nc))
        else:
            # Breeze => at least one neighbor has a pit (disjunctive clause)
            pit_lits = frozenset(self._pit_id(nr, nc) for nr, nc in neighbors)
            if pit_lits not in self.kb:
                self.kb.append(pit_lits)

        # -- Stench rules --
        if not percepts.get("stench", False):
            # No stench => no wumpus in any adjacent cell
            for nr, nc in neighbors:
                clause = frozenset({neg(self._wumpus_id(nr, nc))})
                if clause not in self.kb:
                    self.kb.append(clause)
        else:
            # Stench => at least one neighbor has the wumpus
            wumpus_lits = frozenset(self._wumpus_id(nr, nc) for nr, nc in neighbors)
            if wumpus_lits not in self.kb:
                self.kb.append(wumpus_lits)

        # The current cell is safe (agent is alive here)
        self._mark_safe(r, c)

    # -----------------------------------------------------------------
    # ASK: query KB using resolution refutation
    # -----------------------------------------------------------------

    def ask_is_safe(self, pos: Tuple[int, int]) -> Tuple[bool, int]:
        # Query: Is cell 'pos' safe? (does KB entail NOT Pit AND NOT Wumpus?)
        r, c = pos

        # --- Prove NOT Pit(r,c) ---
        # Negated query: Pit(r,c) is true (unit clause)
        negated_not_pit = [frozenset({self._pit_id(r, c)})]
        no_pit_proved, steps1 = pl_resolution(self.kb, negated_not_pit)

        # --- Prove NOT Wumpus(r,c) ---
        negated_not_wumpus = [frozenset({self._wumpus_id(r, c)})]
        no_wumpus_proved, steps2 = pl_resolution(self.kb, negated_not_wumpus)

        total_steps = steps1 + steps2
        return (no_pit_proved and no_wumpus_proved), total_steps

    # -----------------------------------------------------------------
    # Decision: choose next move
    # -----------------------------------------------------------------

    def decide_move(self) -> Tuple[Optional[Tuple[int, int]], bool, int]:
        # Decide which cell to move to next.
        r, c = self.position
        neighbors = self._get_neighbors(r, c)
        unvisited_neighbors = [n for n in neighbors if n not in self.visited]

        total_steps = 0

        # Check each unvisited neighbor
        for candidate in unvisited_neighbors:
            # First check if it's already in the safe set (from previous no-breeze rules)
            if candidate in self.safe_cells:
                self.last_safe_inferred = True
                self.status_message = f"Safe move to {candidate} (already known safe)"
                return candidate, True, total_steps

            # Use resolution to check
            is_safe, steps = self.ask_is_safe(candidate)
            total_steps += steps
            self.total_inference_steps += steps

            if is_safe:
                self.safe_cells.add(candidate)
                self.last_safe_inferred = True
                self.status_message = f"Safe move to {candidate} (proven by resolution)"
                return candidate, True, total_steps

        # No safe neighbor found via resolution.
        # Look for any unvisited safe cell we can navigate to (simple fallback).
        reachable_safe = [
            cell for cell in self.safe_cells
            if cell not in self.visited
        ]
        if reachable_safe:
            target = reachable_safe[0]
            self.last_safe_inferred = True
            self.status_message = f"Backtracking to safe cell {target}"
            return target, True, total_steps

        # Truly stuck: no provably safe move available
        self.last_safe_inferred = False
        self.status_message = "No safe move can be proven. Agent is uncertain."
        return None, False, total_steps

    def move_to(self, pos: Tuple[int, int]):
        """Update agent position and mark cell as visited."""
        self.position = pos
        self.visited.add(pos)
