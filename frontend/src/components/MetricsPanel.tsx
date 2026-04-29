import React from "react";
import { GameState } from "../types";

interface MetricsPanelProps {
  state: GameState;
}


function Metric({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="metric-row">
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
    </div>
  );
}


function PerceptBadge({ label, active }: { label: string; active: boolean }) {
  return (
    <span className={`percept-badge ${active ? "percept-active" : "percept-inactive"}`}>
      {label}
    </span>
  );
}

const MetricsPanel: React.FC<MetricsPanelProps> = ({ state }) => {
  const {
    agent_pos,
    percepts,
    total_inference_steps,
    steps_this_turn,
    visited_count,
    kb_size,
    safe_inferred,
    message,
    game_over,
    won,
    death_cause,
    rows,
    cols,
  } = state;

  return (
    <div className="metrics-panel">
      <h2 className="metrics-title">📈 Agent Stats</h2>

      {/* Status banner */}
      {game_over && (
        <div className={`status-banner ${won ? "banner-won" : "banner-dead"}`}>
          {won ? "🤑 Agent secured the bag!" : `💀 Bruh... Agent died from a ${death_cause}!`}
        </div>
      )}

      {/* Current message */}
      <div className="metric-message">{message}</div>

      <div className="metrics-divider" />

      {/* Position */}
      <Metric
        label="Agent Position"
        value={`(row ${agent_pos[0]}, col ${agent_pos[1]})`}
      />

      {/* Percepts */}
      <div className="metric-row">
        <span className="metric-label">Percepts</span>
        <div className="percept-list">
          <PerceptBadge label="🌬️ Breeze" active={percepts?.breeze ?? false} />
          <PerceptBadge label="🤢 Stench" active={percepts?.stench ?? false} />
          <PerceptBadge label="✨ Glitter" active={percepts?.glitter ?? false} />
        </div>
      </div>

      <div className="metrics-divider" />

      {/* Inference */}
      <Metric
        label="Safe Move Inferred?"
        value={
          <span className={safe_inferred ? "text-green" : "text-orange"}>
            {safe_inferred ? "Yep 👍" : "Nope 👎"}
          </span>
        }
      />
      <Metric label="Inference Steps (this turn)" value={steps_this_turn} />
      <Metric label="Total Inference Steps" value={total_inference_steps} />
      <Metric label="KB Clause Count" value={kb_size} />

      <div className="metrics-divider" />

      {/* Navigation stats */}
      <Metric label="Cells Visited" value={`${visited_count} / ${rows * cols}`} />

      {/* Explanation box */}
      <div className="metrics-explanation">
        <strong>How resolution refutation works:</strong>
        <br />
        To prove a cell is safe, the agent adds <em>¬Safe</em> (i.e., "assume it has a hazard")
        to the KB as a unit clause and runs resolution. If the empty clause is
        derived (contradiction), the hazard assumption is refuted → cell is proven safe.
      </div>
    </div>
  );
};

export default MetricsPanel;
