// Types shared across the frontend components

export interface Percepts {
  breeze: boolean;
  stench: boolean;
  glitter: boolean;
}

export interface GameState {
  rows: number;
  cols: number;
  agent_pos: [number, number];
  visited: [number, number][];
  safe_cells: [number, number][];
  confirmed_pits: [number, number][];
  confirmed_wumpus: [number, number][];
  // hazards: revealed for educational display, key = "row_col"
  hazards: Record<string, string[]>;
  percepts: Percepts;
  total_inference_steps: number;
  steps_this_turn: number;
  game_over: boolean;
  won: boolean;
  death_cause: string;
  visited_count: number;
  kb_size: number;
  safe_inferred: boolean;
  message: string;
}

export type CellStatus =
  | "agent"        // agent is currently here
  | "visited-safe" // visited and safe (no hazard)
  | "safe-known"   // not yet visited but KB proves it safe
  | "unknown"      // no information
  | "pit"          // confirmed pit (shown after death or for education)
  | "wumpus"       // confirmed wumpus
  | "start";       // start cell (0,0)
