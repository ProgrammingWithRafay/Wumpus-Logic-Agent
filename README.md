# Dynamic Wumpus Logic Agent

A web-based Wumpus World agent that navigates an unknown grid using propositional logic
and resolution refutation. The agent never guesses — it only moves when it can logically
prove a cell is safe.
It is live on Vercel right now. You can check it here:https://wumpus-logic-agent-nu.vercel.app/

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Browser                            │
│   React + TypeScript (Vite)                             │
│   ┌──────────┐  ┌───────────────┐  ┌──────────────┐     │
│   │ Controls │  │     Grid      │  │ MetricsPanel │     │
│   └──────────┘  └───────────────┘  └──────────────┘     │
└─────────────────────────┬───────────────────────────────┘
                          │ REST (HTTP / JSON)
                          │ POST /init, POST /step, GET /state
┌─────────────────────────▼───────────────────────────────┐
│                   FastAPI (Python)                       │
│   ┌────────────────┐  ┌─────────────┐  ┌────────────┐    │
│   │ wumpus_env.py  │  │   agent.py  │  │  main.py   │    │
│   │ (environment)  │  │  TELL / ASK │  │ (routes)   │    │
│   └────────────────┘  └──────┬──────┘  └────────────┘    │
│                              │                           │
│                   ┌──────────▼──────────┐                │
│                   │  knowledge_base.py  │                │
│                   │  CNF + Resolution   │                │
│                   └─────────────────────┘                │
└─────────────────────────────────────────────────────────┘
```

**Why REST instead of WebSocket?**
The agent moves one step at a time on user request (or on a timer). There is no continuous
stream of data, so plain HTTP POST calls are simpler and sufficient.

---

## Folder Structure

```
wumpus-agent/
├── backend/
│   ├── main.py              ← FastAPI routes
│   ├── wumpus_env.py        ← Environment simulation
│   ├── agent.py             ← Knowledge-based agent (TELL / ASK)
│   ├── knowledge_base.py    ← CNF clauses + resolution refutation
│   └── requirements.txt
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── types/
        │   └── index.ts         ← TypeScript types
        ├── api/
        │   └── game.ts          ← Fetch wrappers for backend calls
        └── components/
            ├── Grid.tsx          ← Visual grid with color-coded cells
            ├── MetricsPanel.tsx  ← Inference stats, percepts
            └── Controls.tsx      ← Grid size inputs, step/auto buttons
```

---

## Setup and Run Instructions

### 1. Backend (Python)

```bash
cd wumpus-agent/backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

The API will be live at: **http://localhost:8000**

Interactive docs: http://localhost:8000/docs

### 2. Frontend (React)

```bash
cd wumpus-agent/frontend

# Install node modules
npm install

# Start development server
npm run dev
```

Open your browser at: **http://localhost:5173**

---

## API Routes

| Method | Route   | Description                                      |
|--------|---------|--------------------------------------------------|
| GET    | /health | Health check — returns `{"status": "ok"}`        |
| POST   | /init   | Start a new game. Body: `{"rows": 4, "cols": 4}` |
| POST   | /step   | Agent takes one step (decide → move → tell KB)   |
| GET    | /state  | Read current state without advancing the game    |

### Example Request

```bash
curl -X POST http://localhost:8000/init \
  -H "Content-Type: application/json" \
  -d '{"rows": 4, "cols": 4}'
```

### Example Response (partial)

```json
{
  "rows": 4,
  "cols": 4,
  "agent_pos": [0, 0],
  "visited": [[0, 0]],
  "safe_cells": [[0, 0], [1, 0], [0, 1]],
  "percepts": {"breeze": false, "stench": false, "glitter": false},
  "total_inference_steps": 12,
  "steps_this_turn": 12,
  "safe_inferred": true,
  "kb_size": 6,
  "message": "Moved to [1, 0]..."
}
```

---

## Logic Design

### Knowledge Representation

Every proposition is a string:
- `Pit_r_c`    — cell (r, c) contains a pit
- `Wumpus_r_c` — cell (r, c) contains the Wumpus
- `-Pit_r_c`   — negation: no pit at (r, c)

A **clause** is a `frozenset` of literals (an OR of literals in CNF form).

### TELL

When the agent visits cell (r, c) and receives percepts:

- **No Breeze** → for each neighbor (nr, nc): add unit clause `{-Pit_nr_nc}`
- **Breeze**    → add disjunctive clause `{Pit_n1, Pit_n2, ...}` for all neighbors
- **No Stench** → for each neighbor (nr, nc): add unit clause `{-Wumpus_nr_nc}`
- **Stench**    → add disjunctive clause `{Wumpus_n1, Wumpus_n2, ...}`

The agent's current cell always gets `{-Pit_r_c}` and `{-Wumpus_r_c}` as unit clauses
(it's alive, so no hazard is present).

### ASK (Resolution Refutation)

To prove `¬Pit(r, c)`:
1. Take the **negation**: assume `Pit(r, c)` is true → add `{Pit_r_c}` to KB.
2. Run propositional resolution: repeatedly resolve pairs of clauses.
3. If the **empty clause** `{}` is derived → contradiction → `¬Pit(r, c)` is entailed.
4. If no new clauses can be generated → cannot prove it (cell might be dangerous).

Cell is **safe** when BOTH `¬Pit` and `¬Wumpus` are proven by refutation.

### Resolution Algorithm

```
clauses = KB ∪ {negated_query_clause}

loop:
    new = {}
    for each pair (Ci, Cj) in clauses:
        resolvent = resolve(Ci, Cj)
        if resolvent == {} → return ENTAILED  ← contradiction!
        new.add(resolvent)
    
    if new ⊆ clauses → return NOT_ENTAILED   ← no new info
    clauses = clauses ∪ new
```

The `resolve` function: for each literal L in C1 where ¬L is in C2,
produce `(C1 − {L}) ∪ (C2 − {¬L})`.

---

## UI Design

The grid cells are color-coded:

| Color       | Meaning                           |
|-------------|-----------------------------------|
| 🟦 Blue     | Agent's current position          |
| 🟩 Green    | Visited and safe                  |
| 🌿 Dark green | KB-proven safe (not yet visited) |
| ⬛ Dark     | Unknown — no information yet      |
| 🟥 Red      | Hazard (Pit or Wumpus)           |

The **Metrics Panel** on the right shows:
- Current percepts (active badges)
- Whether this step's move was safely inferred
- Inference steps for this turn and total
- Number of KB clauses
- Cells visited vs. total

The **"Reveal Hazards"** toggle shows all pit and Wumpus positions — useful for verifying
that the agent's logic is correct.

---

## Conclusion

This project demonstrates a knowledge-based agent from first principles. The agent
maintains a propositional logic KB, converts observations to CNF clauses via TELL, and
checks cell safety via ASK using resolution refutation — the same algorithm covered in
the textbook (Russell & Norvig). The web interface makes the agent's reasoning visible
and verifiable, which is the main educational goal.
