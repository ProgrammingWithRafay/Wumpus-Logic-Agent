// components/Controls.tsx
// Top control bar: set grid size, start a new game, step the agent.

import React, { useState } from "react";

interface ControlsProps {
  onInit: (rows: number, cols: number) => void;
  onStep: () => void;
  onAutoPlay: () => void;
  isAutoPlaying: boolean;
  gameOver: boolean;
  loading: boolean;
  showHazards: boolean;
  onToggleHazards: () => void;
}

const Controls: React.FC<ControlsProps> = ({
  onInit,
  onStep,
  onAutoPlay,
  isAutoPlaying,
  gameOver,
  loading,
  showHazards,
  onToggleHazards,
}) => {
  const [rows, setRows] = useState(4);
  const [cols, setCols] = useState(4);

  const handleInit = () => {
    onInit(rows, cols);
  };

  return (
    <div className="controls-bar">
      {/* Grid size inputs */}
      <div className="control-group">
        <label className="control-label">Rows</label>
        <input
          type="number"
          min={2}
          max={10}
          value={rows}
          onChange={(e) => setRows(Number(e.target.value))}
          className="control-input"
        />
      </div>

      <div className="control-group">
        <label className="control-label">Cols</label>
        <input
          type="number"
          min={2}
          max={10}
          value={cols}
          onChange={(e) => setCols(Number(e.target.value))}
          className="control-input"
        />
      </div>

      {/* New game button */}
      <button
        className="btn btn-primary"
        onClick={handleInit}
        disabled={loading}
      >
        🗺️ New Game
      </button>

      {/* Step button */}
      <button
        className="btn btn-secondary"
        onClick={onStep}
        disabled={loading || gameOver || isAutoPlaying}
      >
        👣 Step
      </button>

      {/* Auto-play toggle */}
      <button
        className={`btn ${isAutoPlaying ? "btn-stop" : "btn-autoplay"}`}
        onClick={onAutoPlay}
        disabled={loading || gameOver}
      >
        {isAutoPlaying ? "⏹ Stop" : "▶ Auto-Play"}
      </button>

      {/* Toggle hazard visibility */}
      <button
        className={`btn ${showHazards ? "btn-reveal-on" : "btn-reveal-off"}`}
        onClick={onToggleHazards}
      >
        {showHazards ? "🙈 Hide Hazards" : "👁 Reveal Hazards"}
      </button>
    </div>
  );
};

export default Controls;
