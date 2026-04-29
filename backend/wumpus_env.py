# Simulates the Wumpus World environment.

import random
from typing import Dict, List, Set, Tuple


class WumpusEnvironment:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.agent_pos: Tuple[int, int] = (0, 0)
        self.game_over: bool = False
        self.won: bool = False
        self.death_cause: str = ""

        # grid stores which hazards exist at each cell
        # key: (row, col), value: set containing 'pit', 'wumpus', or 'gold'
        self.grid: Dict[Tuple[int, int], Set[str]] = {}

        self._place_hazards()

    def _get_all_cells(self) -> List[Tuple[int, int]]:
        return [(r, c) for r in range(self.rows) for c in range(self.cols)]

    def _place_hazards(self):
        # Place one Wumpus and pits randomly. (0,0) is safe.
        all_cells = self._get_all_cells()
        # Start cell must remain safe
        candidate_cells = [cell for cell in all_cells if cell != (0, 0)]

        if not candidate_cells:
            return  # Edge case: 1x1 grid

        # Place exactly one Wumpus
        wumpus_pos = random.choice(candidate_cells)
        self.grid.setdefault(wumpus_pos, set()).add("wumpus")

        # Place pits in approximately 20% of non-start cells
        non_wumpus = [c for c in candidate_cells if c != wumpus_pos]
        num_pits = max(1, len(candidate_cells) // 5)
        pit_cells = random.sample(non_wumpus, min(num_pits, len(non_wumpus)))
        for cell in pit_cells:
            self.grid.setdefault(cell, set()).add("pit")

        # Optionally place gold somewhere (not at start)
        gold_pos = random.choice(candidate_cells)
        self.grid.setdefault(gold_pos, set()).add("gold")

    def get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Return valid adjacent cells (up, down, left, right)."""
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbors.append((nr, nc))
        return neighbors

    def get_percepts(self, pos: Tuple[int, int]) -> Dict[str, bool]:
        # Compute percepts at given pos
        r, c = pos
        neighbors = self.get_neighbors(r, c)

        breeze = any("pit" in self.grid.get(n, set()) for n in neighbors)
        stench = any("wumpus" in self.grid.get(n, set()) for n in neighbors)
        glitter = "gold" in self.grid.get(pos, set())

        return {"breeze": breeze, "stench": stench, "glitter": glitter}

    def move_agent(self, new_pos: Tuple[int, int]) -> Dict:
        # Move agent to new_pos and check if it dies
        r, c = new_pos
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return {"success": False, "reason": "Out of bounds"}

        self.agent_pos = new_pos
        contents = self.grid.get(new_pos, set())

        # Check if agent dies
        if "pit" in contents:
            self.game_over = True
            self.death_cause = "pit"
            return {"success": True, "died": True, "cause": "pit"}

        if "wumpus" in contents:
            self.game_over = True
            self.death_cause = "wumpus"
            return {"success": True, "died": True, "cause": "wumpus"}

        percepts = self.get_percepts(new_pos)
        return {"success": True, "died": False, "percepts": percepts}

    def get_hazard_map(self) -> Dict[str, List[str]]:
        """Return all hazard locations as a serializable dict for the frontend."""
        result = {}
        for (r, c), contents in self.grid.items():
            key = f"{r}_{c}"
            result[key] = list(contents)
        return result
