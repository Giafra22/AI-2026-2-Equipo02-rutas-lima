"""Pruebas contra Dijkstra (solo verificación; no técnica de la interfaz)."""
from heapq import heappop, heappush
from collections import deque
from algorithms import ALGORITHMS, path_distance, compare, comparison_rows
from graph_data import EDGES, POSITIONS, build_graph, heuristic, heuristic_scale


def dijkstra_distance(graph, start, goal):
    queue = [(0.0, start)]
    distances = {start: 0.0}
    while queue:
        cost, node = heappop(queue)
        if cost != distances[node]:
            continue
        if node == goal:
            return cost
        for other, weight in graph[node].items():
            candidate = cost + weight
            if candidate < distances.get(other, float("inf")):
                distances[other] = candidate
                heappush(queue, (candidate, other))
    return None


def minimum_hops(graph, start, goal):
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        node, hops = queue.popleft()
        if node == goal:
            return hops
        for other in graph[node]:
            if other not in seen:
                seen.add(other)
                queue.append((other, hops + 1))
    return None


def verify_graph(graph):
    checked = 0
    scale = heuristic_scale(graph)
    for start in graph:
        for goal in graph:
            optimum = dijkstra_distance(graph, start, goal)
            for node in graph:
                for neighbor, weight in graph[node].items():
                    assert heuristic(node, goal, scale) <= weight + heuristic(neighbor, goal, scale) + 1e-9
            for name, algorithm in ALGORITHMS.items():
                result = algorithm(graph, start, goal)
                assert len(result.expanded) == len(set(result.expanded))
                if result.path:
                    assert result.path[0] == start and result.path[-1] == goal
                    assert len(result.path) == len(set(result.path))
                    assert all(b in graph[a] for a, b in zip(result.path, result.path[1:]))
                if name != "Ruta base":
                    assert bool(result.path) == (optimum is not None)
                if name == "A*":
                    assert path_distance(graph, result.path) == optimum
                if name == "BFS" and result.path:
                    assert len(result.path) - 1 == minimum_hops(graph, start, goal)
            checked += 1
    return checked


def run_checks():
    total = verify_graph(build_graph())
    for a, b, _ in EDGES:
        total += verify_graph(build_graph((a, b)))
    disconnected = {name: {} for name in POSITIONS}
    total += verify_graph(disconnected)
    edited = build_graph()
    edited["San Luis"]["San Borja"] = edited["San Borja"]["San Luis"] = .25
    total += verify_graph(edited)
    graph = build_graph()
    demo = compare(graph, "Santa Anita", "Miraflores", 100)
    assert demo["A*"]["distance"] == 20
    assert demo["BFS"]["distance"] == 23
    assert demo["Ruta base"]["distance"] == 23
    for row in comparison_rows(demo):
        assert row["Tiempo mediano (ms)"] >= 0 and row["Corridas"] == 100
    print(f"OK: {total} escenarios origen/destino; rutas válidas, BFS mínimo en conexiones y A* óptimo en distancia.")
    print("Escenario Santa Anita -> Miraflores:")
    for name, value in demo.items():
        print(f"{name}: {value['distance']} km; {len(value['result'].expanded)} nodos expandidos; {value['time_ms']:.4f} ms.")


if __name__ == "__main__":
    run_checks()
