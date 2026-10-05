"""Implementaciones propias. Orden de vecinos: inserción en EDGES."""
from collections import deque
from dataclasses import dataclass
from heapq import heappush, heappop
from itertools import count
from statistics import median
from time import perf_counter_ns
from graph_data import MANUAL_ITINERARY, heuristic, heuristic_scale


@dataclass
class SearchResult:
    path: list
    expanded: list


def reconstruct(parent, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


def manual(graph, start, goal):
    """Lee un segmento del itinerario fijo; no busca rutas alternativas."""
    a, b = MANUAL_ITINERARY.index(start), MANUAL_ITINERARY.index(goal)
    path = MANUAL_ITINERARY[a:b + 1] if a <= b else MANUAL_ITINERARY[b:a + 1][::-1]
    if any(v not in graph[u] for u, v in zip(path, path[1:])):
        return SearchResult([], [])
    return SearchResult(path, [])


def bfs(graph, start, goal):
    frontier = deque([start])
    parent = {start: None}
    expanded = []
    while frontier:
        node = frontier.popleft()
        if node == goal:
            return SearchResult(reconstruct(parent, goal), expanded)
        expanded.append(node)  # Se examinan sus vecinos; la meta no se expande.
        for neighbor in graph[node]:
            if neighbor not in parent:
                parent[neighbor] = node
                frontier.append(neighbor)
    return SearchResult([], expanded)


def dfs(graph, start, goal):
    frontier = [(start, None)]
    parent = {}
    expanded = []
    while frontier:
        node, predecessor = frontier.pop()
        if node in parent:
            continue
        parent[node] = predecessor
        if node == goal:
            return SearchResult(reconstruct(parent, goal), expanded)
        expanded.append(node)
        # reversed conserva al visitar el mismo orden de vecinos que BFS.
        for neighbor in reversed(list(graph[node])):
            if neighbor not in parent:
                frontier.append((neighbor, node))
    return SearchResult([], expanded)


def astar(graph, start, goal):
    scale = heuristic_scale(graph)
    serial = count()  # Desempate reproducible, por orden de inserción.
    frontier = [(heuristic(start, goal, scale), next(serial), start, 0.0)]
    best_cost = {start: 0.0}
    parent = {start: None}
    expanded = []
    closed = set()
    while frontier:
        _, _, node, queued_cost = heappop(frontier)
        if node in closed or queued_cost != best_cost[node]:
            continue
        if node == goal:
            return SearchResult(reconstruct(parent, goal), expanded)
        closed.add(node)
        expanded.append(node)
        for neighbor, weight in graph[node].items():
            new_cost = best_cost[node] + weight
            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost
                parent[neighbor] = node
                score = new_cost + heuristic(neighbor, goal, scale)
                heappush(frontier, (score, next(serial), neighbor, new_cost))
    return SearchResult([], expanded)


ALGORITHMS = {"Ruta base": manual, "BFS": bfs, "DFS": dfs, "A*": astar}


def path_distance(graph, path):
    if not path:
        return None
    return sum(graph[a][b] for a, b in zip(path, path[1:]))


def compare(graph, start, goal, runs=100):
    """Mismo escenario para todas las técnicas; tiempo solo del algoritmo.

    Corridas = repeticiones del mismo problema, no muestras de tráfico.
    Se usa mediana y se excluyen interfaz, dibujo y métricas posteriores.
    """
    if start not in graph or goal not in graph:
        raise ValueError("Origen y destino deben pertenecer al grafo.")
    if runs < 1:
        raise ValueError("Debe existir al menos una corrida.")
    results = {}
    for name, function in ALGORITHMS.items():
        function(graph, start, goal)  # Calentamiento excluido de la medición.
        times = []
        for _ in range(runs):
            before = perf_counter_ns()
            result = function(graph, start, goal)
            times.append((perf_counter_ns() - before) / 1_000_000)
        results[name] = {
            "result": result,
            "distance": path_distance(graph, result.path),
            "time_ms": median(times),
            "runs": runs,
        }
    return results


def comparison_rows(results):
    return [{
        "Técnica": name,
        "Estado": "Encontrada" if values["result"].path else "Sin ruta",
        "Distancia (km)": values["distance"],
        "Conexiones": len(values["result"].path) - 1 if values["result"].path else None,
        "Nodos expandidos": len(values["result"].expanded),
        "Tiempo mediano (ms)": values["time_ms"],
        "Corridas": values["runs"],
    } for name, values in results.items()]
