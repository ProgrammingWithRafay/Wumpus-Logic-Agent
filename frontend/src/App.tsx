import React, { useState, useEffect, useRef } from "react";
import { GameState } from "./types";
import { initGame, stepGame } from "./api/game";
import Grid from "./components/Grid";
import MetricsPanel from "./components/MetricsPanel";
import Controls from "./components/Controls";
import "./index.css";

const App: React.FC = () => {
  const [state, setState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showHazards, setShowHazards] = useState(false);
  const [isAutoPlaying, setIsAutoPlaying] = useState(false);



  const handleInit = async (rows: number, cols: number) => {
    setLoading(true);
    setError(null);
    setIsAutoPlaying(false);

    try {
      const newState = await initGame(rows, cols);
      setState(newState);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to initialize game");
    } finally {
      setLoading(false);
    }
  };

  const handleStep = async () => {
    if (!state || state.game_over) return;
    setLoading(true);

    try {
      const newState = await stepGame();
      setState(newState);

      // Stop auto-play if game ended or agent is stuck
      if (newState.game_over || !newState.safe_inferred) {
        setIsAutoPlaying(false);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Step failed");
      setIsAutoPlaying(false);
    } finally {
      setLoading(false);
    }
  };

  const handleAutoPlay = () => {
    setIsAutoPlaying((prev) => !prev);
  };

  // Manage auto-play: trigger a step every 800ms when active
  useEffect(() => {
    if (!isAutoPlaying || !state || state.game_over || loading) {
      return;
    }

    const timer = setTimeout(() => {
      handleStep();
    }, 800);

    return () => clearTimeout(timer);
  }, [isAutoPlaying, state, loading]);



  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Dynamic Wumpus Logic Agent</h1>
        <p className="app-subtitle">
          A knowledge-based agent using propositional logic and resolution refutation
        </p>
      </header>

      <Controls
        onInit={handleInit}
        onStep={handleStep}
        onAutoPlay={handleAutoPlay}
        isAutoPlaying={isAutoPlaying}
        gameOver={state?.game_over ?? false}
        loading={loading}
        showHazards={showHazards}
        onToggleHazards={() => setShowHazards((prev) => !prev)}
      />

      {error && (
        <div className="error-banner">
          ⚠️ {error} — Is the backend running on port 8000?
        </div>
      )}

      {!state && !error && (
        <div className="welcome-box">
          <p>Set the grid size above and click <strong>New Game</strong> to begin.</p>
          <p>The agent will explore using logical inference — no guessing!</p>
        </div>
      )}

      {state && (
        <div className="game-layout">
          {/* Left: Grid */}
          <div className="game-left">
            <Grid state={state} showHazards={showHazards} />
          </div>

          {/* Right: Metrics */}
          <div className="game-right">
            <MetricsPanel state={state} />
          </div>
        </div>
      )}

      <footer className="app-footer">
        Dynamic Wumpus Logic Agent
      </footer>
    </div>
  );
};

export default App;
