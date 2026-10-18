from collections import deque
from heapq import heappush, heappop
import math
import time
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="CampusGuard Routing API", version="1.0.0", description="Graph-based campus evacuation route service")

N = {'ENG_GATE': ('Engineering Gate', 60, 260, 'start'), 'ENG_A': ('Engineering Block A', 155, 190, 'building'), 'JUNCTION_N': ('North Junction', 255, 120, 'junction'), 'LIBRARY': ('Library Walkway', 355, 150, 'building'), 'SAFE_NORTH': ('North Assembly Point', 535, 90, 'exit'), 'JUNCTION_C': ('Central Walkway', 270, 265, 'junction'), 'ENG_B': ('Engineering Block B', 385, 270, 'building'), 'LAB': ('Laboratory Complex', 465, 365, 'building'), 'SAFE_EAST': ('East Assembly Point', 570, 300, 'exit'), 'HOSTEL_PATH': ('Hostel Connector', 160, 390, 'building'), 'JUNCTION_S': ('South Junction', 285, 405, 'junction'), 'SAFE_SOUTH': ('South Assembly Point', 430, 470, 'exit'), 'ADMIN_BLOCK': ('Administrative Block', 95, 115, 'building'), 'AUDITORIUM': ('Main Auditorium', 185, 65, 'building'), 'FOOD_COURT': ('Food Court', 75, 355, 'building'), 'BOYS_HOSTEL': ('Boys Hostel Connector', 75, 445, 'building'), 'GIRLS_HOSTEL': ('Girls Hostel Connector', 190, 475, 'building'), 'SPORTS_COMPLEX': ('Sports Complex', 330, 500, 'building'), 'MEDICAL_CENTRE': ('Medical Centre', 555, 420, 'building'), 'TECH_PARK': ('Tech Park', 470, 205, 'building'), 'PARKING_AREA': ('Parking Area', 610, 175, 'building'), 'SAFE_WEST': ('West Assembly Point', 35, 75, 'exit'), 'SAFE_CENTRAL': ('Central Assembly Point', 330, 45, 'exit'), 'SAFE_MEDICAL': ('Medical-side Assembly Point', 630, 455, 'exit')}

E = [('ENG_GATE', 'ENG_A', 1), ('ENG_A', 'JUNCTION_N', 1.2), ('JUNCTION_N', 'LIBRARY', 1), ('LIBRARY', 'SAFE_NORTH', 1.7), ('ENG_A', 'JUNCTION_C', 1.1), ('JUNCTION_N', 'JUNCTION_C', 1), ('JUNCTION_C', 'ENG_B', 1.1), ('ENG_B', 'SAFE_EAST', 1.8), ('ENG_B', 'LAB', 1.2), ('LAB', 'SAFE_EAST', 1), ('JUNCTION_C', 'HOSTEL_PATH', 1.5), ('HOSTEL_PATH', 'JUNCTION_S', 1.1), ('JUNCTION_S', 'SAFE_SOUTH', 1.6), ('JUNCTION_S', 'LAB', 1.4), ('JUNCTION_C', 'JUNCTION_S', 1.5), ('LIBRARY', 'ENG_B', 1.8), ('ENG_GATE', 'ADMIN_BLOCK', 1.1), ('ADMIN_BLOCK', 'AUDITORIUM', 1.0), ('AUDITORIUM', 'JUNCTION_N', 1.3), ('ADMIN_BLOCK', 'SAFE_WEST', 1.5), ('ENG_GATE', 'FOOD_COURT', 1.4), ('FOOD_COURT', 'HOSTEL_PATH', 1.2), ('FOOD_COURT', 'BOYS_HOSTEL', 1.1), ('BOYS_HOSTEL', 'GIRLS_HOSTEL', 1.3), ('GIRLS_HOSTEL', 'JUNCTION_S', 1.2), ('JUNCTION_S', 'SPORTS_COMPLEX', 1.1), ('SPORTS_COMPLEX', 'SAFE_SOUTH', 1.0), ('AUDITORIUM', 'SAFE_CENTRAL', 1.4), ('SAFE_CENTRAL', 'LIBRARY', 1.6), ('LIBRARY', 'TECH_PARK', 1.2), ('TECH_PARK', 'ENG_B', 1.0), ('TECH_PARK', 'PARKING_AREA', 1.1), ('PARKING_AREA', 'SAFE_NORTH', 1.4), ('LAB', 'MEDICAL_CENTRE', 1.0), ('MEDICAL_CENTRE', 'SAFE_MEDICAL', 1.2), ('MEDICAL_CENTRE', 'SAFE_EAST', 1.5)]

S = {'All clear': ([], [], 'All demo walkways are open.'), 'North walkway blocked': ([('JUNCTION_N', 'LIBRARY'), ('LIBRARY', 'SAFE_NORTH')], [], 'North approach closed.'), 'Lab-area incident': ([('ENG_B', 'LAB'), ('LAB', 'SAFE_EAST'), ('JUNCTION_S', 'LAB')], ['LAB'], 'Laboratory complex excluded.'), 'Multiple obstructions': ([('JUNCTION_N', 'LIBRARY'), ('ENG_B', 'SAFE_EAST'), ('JUNCTION_C', 'JUNCTION_S')], [], 'Multiple corridors closed.')}

class RouteRequest(BaseModel):
    start: str = Field(..., description="Start node ID from the campus graph")
    goal: str = Field(..., description="Safe destination node ID from the campus graph")
    algorithm: str = Field(default="astar", description="astar or bfs")
    scenario: str = Field(default="All clear", description="Named hazard scenario")


def build_graph(scenario: str):
    blocked_edges, blocked_nodes, _ = S[scenario]
    blocked_edges = {frozenset(edge) for edge in blocked_edges}
    graph = {node: [] for node in N if node not in blocked_nodes}
    for a, b, weight in E:
        if a in blocked_nodes or b in blocked_nodes or frozenset((a, b)) in blocked_edges:
            continue
        graph[a].append((b, weight))
        graph[b].append((a, weight))
    return graph


def solve_route(request: RouteRequest):
    if request.start not in N:
        raise HTTPException(status_code=400, detail=f"Unknown start node: {request.start}")
    if request.goal not in N:
        raise HTTPException(status_code=400, detail=f"Unknown destination node: {request.goal}")
    if request.scenario not in S:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {request.scenario}")
    algorithm = request.algorithm.lower().strip()
    if algorithm not in {"bfs", "astar", "a*"}:
        raise HTTPException(status_code=400, detail="algorithm must be 'bfs' or 'astar'")

    graph = build_graph(request.scenario)
    if request.start not in graph or request.goal not in graph:
        return {"path": None, "explored": [], "cost": None, "elapsed_ms": 0.0, "algorithm": algorithm, "message": "Start or destination is unavailable in this hazard scenario."}

    started = time.perf_counter()
    explored = []
    parent = {request.start: None}

    if algorithm == "bfs":
        queue = deque([request.start])
        while queue:
            node = queue.popleft()
            explored.append(node)
            if node == request.goal:
                break
            for neighbor, _weight in graph.get(node, []):
                if neighbor not in parent:
                    parent[neighbor] = node
                    queue.append(neighbor)
        edge_weights = {(a, b): weight for a, b, weight in E}
        def route_cost(path):
            return sum(edge_weights.get((a, b), edge_weights.get((b, a), 1.0)) for a, b in zip(path, path[1:]))
    else:
        heuristic = lambda node: math.dist(N[node][1:3], N[request.goal][1:3]) / 100
        frontier = [(heuristic(request.start), 0.0, request.start)]
        costs = {request.start: 0.0}
        while frontier:
            _priority, cost_so_far, node = heappop(frontier)
            if cost_so_far > costs.get(node, float("inf")):
                continue
            explored.append(node)
            if node == request.goal:
                break
            for neighbor, weight in graph.get(node, []):
                new_cost = costs[node] + weight
                if new_cost < costs.get(neighbor, float("inf")):
                    costs[neighbor] = new_cost
                    parent[neighbor] = node
                    heappush(frontier, (new_cost + heuristic(neighbor), new_cost, neighbor))
        def route_cost(path):
            return costs[request.goal]

    elapsed_ms = (time.perf_counter() - started) * 1000
    if request.goal not in parent:
        return {"path": None, "explored": explored, "cost": None, "elapsed_ms": elapsed_ms, "algorithm": algorithm, "message": "No route is available for this scenario."}
    path = []
    node: Optional[str] = request.goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return {"path": path, "explored": explored, "cost": route_cost(path), "elapsed_ms": elapsed_ms, "algorithm": algorithm, "message": "Route calculated successfully."}


def find_possible_routes(start: str, goal: str, scenario: str, limit: int = 3):
    """Return up to `limit` lowest-cost simple paths using uniform-cost path search."""
    graph = build_graph(scenario)
    if start not in graph or goal not in graph:
        return []
    frontier = [(0.0, (start,))]
    found = []
    expansions = 0
    max_expansions = 50000
    while frontier and len(found) < limit and expansions < max_expansions:
        cost, path = heappop(frontier)
        node = path[-1]
        if node == goal:
            found.append({"path": list(path), "cost": round(cost, 3)})
            continue
        for neighbor, weight in graph.get(node, []):
            if neighbor not in path:  # keep each candidate simple (no repeated nodes)
                heappush(frontier, (cost + weight, path + (neighbor,)))
        expansions += 1
    for index, route in enumerate(found, start=1):
        route["rank"] = index
        route["label"] = "Best route" if index == 1 else f"Alternative {index - 1}"
    return found


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CampusGuard Routing API", "nodes": len(N), "edges": len(E)}


@app.get("/api/locations")
def locations():
    return {"locations": [{"id": key, "name": value[0], "x": value[1], "y": value[2], "kind": value[3]} for key, value in N.items()], "scenarios": list(S)}


@app.post("/api/route")
def route(request: RouteRequest):
    return solve_route(request)


@app.post("/api/route/bfs")
def bfs_route(request: RouteRequest):
    request.algorithm = "bfs"
    return solve_route(request)


@app.post("/api/route/astar")
def astar_route(request: RouteRequest):
    request.algorithm = "astar"
    return solve_route(request)


@app.post("/api/routes")
def possible_routes(request: RouteRequest):
    if request.start not in N:
        raise HTTPException(status_code=400, detail=f"Unknown start node: {request.start}")
    if request.goal not in N:
        raise HTTPException(status_code=400, detail=f"Unknown destination node: {request.goal}")
    if request.scenario not in S:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {request.scenario}")
    routes = find_possible_routes(request.start, request.goal, request.scenario, limit=3)
    return {
        "start": request.start,
        "goal": request.goal,
        "scenario": request.scenario,
        "routes": routes,
        "best_route": routes[0] if routes else None,
        "route_count": len(routes),
        "ranking": "lowest total weighted graph cost first",
    }
