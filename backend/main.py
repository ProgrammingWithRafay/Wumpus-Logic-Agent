# FastAPI server for the Dynamic Wumpus Logic Agent.

from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import WumpusAgent
from wumpus_env import WumpusEnvironment

app = FastAPI(title="Wumpus Logic Agent API")

# Allow requests from the React frontend (localhost:5173 by default for Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game state (single-session demo)
env: Optional[WumpusEnvironment] = None
agent: Optional[WumpusAgent] = None


# -----------------------------------------------------------------
# Request / Response models
# -----------------------------------------------------------------

class InitRequest(BaseModel):
    rows: int
    cols: int


# -----------------------------------------------------------------
# Helper: build the full state dict to return to frontend
# -----------------------------------------------------------------

def build_state(extra_message: str = "", safe_inferred: bool = False,
                steps_this_turn: int = 0) -> Dict[str, Any]:
    return {
        "rows": env.rows,
        "cols": env.cols,
        "agent_pos": list(env.agent_pos),
        "visited": [list(v) for v in agent.visited],
        "safe_cells": [list(s) for s in agent.safe_cells],
        "confirmed_pits": [list(p) for p in agent.confirmed_pits],
        "confirmed_wumpus": [list(w) for w in agent.confirmed_wumpus],
        "hazards": env.get_hazard_map(),          # full map (for educational display)
        "percepts": agent.last_percepts,
        "total_inference_steps": agent.total_inference_steps,
        "steps_this_turn": steps_this_turn,
        "game_over": env.game_over,
        "won": env.won,
        "death_cause": env.death_cause,
        "visited_count": len(agent.visited),
        "kb_size": len(agent.kb),
        "safe_inferred": safe_inferred,
        "message": extra_message or agent.status_message,
    }


# -----------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/init")
def init_game(req: InitRequest):
    global env, agent

    rows = max(2, min(req.rows, 10))
    cols = max(2, min(req.cols, 10))

    env = WumpusEnvironment(rows, cols)
    agent = WumpusAgent(rows, cols)

    # Collect percepts at start position (0,0) and update KB
    percepts = env.get_percepts((0, 0))
    agent.tell((0, 0), percepts)

    return build_state(
        extra_message=f"New game started on {rows}x{cols} grid. Agent at (0,0).",
        safe_inferred=False,
        steps_this_turn=0,
    )


@app.post("/step")
def step_game():
    global env, agent

    if env is None or agent is None:
        return {"error": "Game not initialized. Call /init first."}

    if env.game_over:
        return build_state(extra_message="Game is already over. Call /init to restart.")

    # --- DECIDE ---
    next_pos, safe_inferred, steps_this_turn = agent.decide_move()
    agent.total_inference_steps += steps_this_turn

    if next_pos is None:
        # Agent is stuck — no safe move provable
        return build_state(
            extra_message="Agent cannot prove any safe move. It stops rather than guess.",
            safe_inferred=False,
            steps_this_turn=steps_this_turn,
        )

    # --- MOVE ---
    result = env.move_agent(next_pos)
    agent.move_to(next_pos)

    if result.get("died"):
        cause = result["cause"]
        return build_state(
            extra_message=f"Agent stepped into a {cause} at {next_pos} and died!",
            safe_inferred=safe_inferred,
            steps_this_turn=steps_this_turn,
        )

    # --- TELL: update KB with new percepts ---
    percepts = result.get("percepts", {})
    agent.tell(next_pos, percepts)

    return build_state(
        extra_message=f"Moved to {list(next_pos)}. Percepts: {percepts}",
        safe_inferred=safe_inferred,
        steps_this_turn=steps_this_turn,
    )


@app.get("/state")
def get_state():
    if env is None or agent is None:
        return {"error": "Game not initialized. Call /init first."}
    return build_state()
