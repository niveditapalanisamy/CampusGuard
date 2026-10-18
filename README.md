# CampusGuard — Updated Project

CampusGuard is a Streamlit + FastAPI demo for graph-based campus route planning. It includes a 24-node / 36-edge illustrative graph, BFS and A* routing, four simulated hazard scenarios, and up to three weighted candidate routes per request.

## What changed

- Added `POST /api/routes` in FastAPI.
- The endpoint returns up to three simple paths ranked by weighted graph cost, including rank, label, node path, and cost.
- `best_route` is the lowest-cost route among the returned candidates.
- Streamlit now displays a ranked list of possible routes and highlights the best route in teal. Alternative paths use dashed lines; the selected BFS/A* path is shown separately if it differs.
- Existing `POST /api/route` remains responsible for the selected algorithm's path and search metrics.

## Run locally

Open two terminals in the extracted `CampusGuard_Updated` directory.

### Terminal 1 — FastAPI backend

```bash
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Check `http://127.0.0.1:8000/api/health` and API docs at `http://127.0.0.1:8000/docs`.

### Terminal 2 — Streamlit frontend

```bash
python -m streamlit run app.py
```

If the sidebar backend URL differs, set it to `http://127.0.0.1:8000`.

## Try the possible-route view

- Start: `ENG_GATE` (Engineering Gate)
- Destination: `SAFE_EAST` (East Assembly Point)
- Scenario: `All clear`
- Algorithm: `A*`
- Click **Find safe route**

Expected weighted candidates:

1. Best route — 5.0 units: `ENG_GATE → ENG_A → JUNCTION_C → ENG_B → SAFE_EAST`
2. Alternative 1 — 5.4 units: `ENG_GATE → ENG_A → JUNCTION_C → ENG_B → LAB → SAFE_EAST`
3. Alternative 2 — 6.0 units: `ENG_GATE → ENG_A → JUNCTION_C → JUNCTION_S → LAB → SAFE_EAST`

Switch to **Multiple obstructions** and recalculate to see the candidate routes change.

## API example

```bash
curl -X POST http://127.0.0.1:8000/api/routes \
  -H "Content-Type: application/json" \
  -d '{"start":"ENG_GATE","goal":"SAFE_EAST","algorithm":"astar","scenario":"All clear"}'
```

## Notes and limitations

- Candidate routes are ranked by weighted graph cost using uniform-cost path enumeration, not real-world walking distance or travel time.
- The graph and hazard scenarios are illustrative. They are not an official SRM KTR map and must not be used for real emergency navigation.
