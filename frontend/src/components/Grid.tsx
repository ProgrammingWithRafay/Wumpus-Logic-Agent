import React from "react";
import { GameState, CellStatus } from "../types";

interface GridProps {
  state: GameState;
  showHazards: boolean; // reveal all hazard positions for education
}

// Check if two positions are equal
function posEq(a: [number, number], b: [number, number]) {
  return a[0] === b[0] && a[1] === b[1];
}

// Get display status of a cell
function getCellStatus(
  row: number,
  col: number,
  state: GameState,
  showHazards: boolean
): CellStatus {
  const { agent_pos, visited, safe_cells, hazards, game_over } = state;

  const isAgent = posEq(agent_pos, [row, col]);
  const isVisited = visited.some((v) => posEq(v, [row, col]));
  const isSafe = safe_cells.some((s) => posEq(s, [row, col]));
  const cellHazards = hazards[`${row}_${col}`] || [];

  // Agent's current position
  if (isAgent) return "agent";

  // Reveal hazards when game is over or showHazards is on
  if (game_over || showHazards) {
    if (cellHazards.includes("pit")) return "pit";
    if (cellHazards.includes("wumpus")) return "wumpus";
  }

  if (isVisited) return "visited-safe";
  if (isSafe) return "safe-known";

  return "unknown";
}

// Map status to CSS class name
function statusToClass(status: CellStatus): string {
  switch (status) {
    case "agent": return "cell cell-agent";
    case "visited-safe": return "cell cell-visited";
    case "safe-known": return "cell cell-safe-known";
    case "pit": return "cell cell-pit";
    case "wumpus": return "cell cell-wumpus";
    case "unknown":
    default: return "cell cell-unknown";
  }
}

// Pick icon for the cell
function getCellIcon(
  row: number,
  col: number,
  status: CellStatus,
  state: GameState
): string {
  if (status === "agent") return "😎";

  const cellHazards = state.hazards[`${row}_${col}`] || [];

  if (status === "pit") return "💀";
  if (status === "wumpus") return "👹";

  // Show gold wherever it is (always visible as a game hint)
  if (cellHazards.includes("gold")) return "🤑";

  if (status === "visited-safe") return "✅";
  if (status === "safe-known") return "❓";

  return "";
}

const Grid: React.FC<GridProps> = ({ state, showHazards }) => {
  const { rows, cols } = state;

  // Compute cell size based on grid dimensions (smaller for bigger grids)
  const cellSize = Math.max(48, Math.min(80, Math.floor(560 / Math.max(rows, cols))));

  return (
    <div className="grid-wrapper">
      <div
        className="grid-container"
        style={{
          gridTemplateColumns: `repeat(${cols}, ${cellSize}px)`,
          gridTemplateRows: `repeat(${rows}, ${cellSize}px)`,
        }}
      >
        {Array.from({ length: rows }, (_, row) =>
          Array.from({ length: cols }, (_, col) => {
            const status = getCellStatus(row, col, state, showHazards);
            const icon = getCellIcon(row, col, status, state);
            const isStart = row === 0 && col === 0;

            return (
              <div
                key={`${row}-${col}`}
                className={statusToClass(status) + (isStart ? " cell-start" : "")}
                style={{ width: cellSize, height: cellSize }}
                title={`(${row}, ${col}) — ${status}`}
              >
                <span className="cell-icon">{icon}</span>
                <span className="cell-coord">
                  {row},{col}
                </span>
              </div>
            );
          })
        )}
      </div>

      {/* Legend */}
      <div className="grid-legend">
        <span className="legend-item"><span className="legend-dot dot-agent" />Agent</span>
        <span className="legend-item"><span className="legend-dot dot-visited" />Visited (safe)</span>
        <span className="legend-item"><span className="legend-dot dot-safe-known" />KB-proven safe</span>
        <span className="legend-item"><span className="legend-dot dot-unknown" />Unknown</span>
        <span className="legend-item"><span className="legend-dot dot-hazard" />Confirmed Pit/Wumpus (Red)</span>
      </div>
    </div>
  );
};

export default Grid;
