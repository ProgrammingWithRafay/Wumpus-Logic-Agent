// api/game.ts
// All HTTP calls to the FastAPI backend live here.

import { GameState } from "../types";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Initialize a new game with a given grid size.
 */
export async function initGame(rows: number, cols: number): Promise<GameState> {
  const response = await fetch(`${BASE_URL}/init`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rows, cols }),
  });

  if (!response.ok) {
    throw new Error(`Init failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Ask the agent to take one step.
 * The backend handles decision + move + KB update internally.
 */
export async function stepGame(): Promise<GameState> {
  const response = await fetch(`${BASE_URL}/step`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Step failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch current state without advancing the game.
 */
export async function getState(): Promise<GameState> {
  const response = await fetch(`${BASE_URL}/state`);

  if (!response.ok) {
    throw new Error(`State fetch failed: ${response.statusText}`);
  }

  return response.json();
}
