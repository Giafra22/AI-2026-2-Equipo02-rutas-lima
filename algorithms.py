"""Algoritmos de búsqueda y enumeración de rutas."""

from collections import deque
from dataclasses import dataclass
from heapq import heappush, heappop
from itertools import count
from statistics import median
from time import perf_counter_ns

from graph_data import (
    MANUAL_ITINERARY,
    heuristic,
    heuristic_scale,
)


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
    """Obtiene una ruta del itinerario fijo."""

    a = MANUAL_ITINERARY.index(start)
    b = MANUAL_ITINERARY.index(goal)

    if a <= b:
        path = MANUAL_ITINERARY[a:b + 1]
    else:
        path = MANUAL_ITINERARY[b:a + 1][::-1]

    if any(v not in graph[u] for u, v in zip(path, path[1:])):
        return SearchResult([], [])

    return SearchResult(path, [])


def bfs(graph, start, goal):
    """Busca por niveles mediante una cola."""

    frontier = deque([start])
    parent = {start: None}
    expanded = []

    while frontier:
        node = frontier.popleft()

        if node == goal:
            return SearchResult(
                reconstruct(parent, goal),
                expanded,
            )

        expanded.append(node)

        for neighbor in graph[node]:
            if neighbor not in parent:
                parent[neighbor] = node
                frontier.append(neighbor)

    return SearchResult([], expanded)


def dfs(graph, start, goal):
    """Busca en profundidad mediante una pila."""

    frontier = [(start, None)]
    parent = {}
    expanded = []

    while frontier:
        node, predecessor = frontier.pop()

        if node in parent:
            continue

        parent[node] = predecessor

        if node == goal:
            return SearchResult(
                reconstruct(parent, goal),
                expanded,
            )

        expanded.append(node)

        for neighbor in reversed(list(graph[node])):
            if neighbor not in parent:
                frontier.append((neighbor, node))

    return SearchResult([], expanded)


def astar(graph, start, goal):
    """Busca utilizando costo acumulado y heurística."""

    scale = heuristic_scale(graph)
    serial = count()

    frontier = [
        (
            heuristic(start, goal, scale),
            next(serial),
            start,
            0.0,
        )
    ]

    best_cost = {start: 0.0}
    parent = {start: None}
    expanded = []
    closed = set()

    while frontier:
        _, _, node, queued_cost = heappop(frontier)

        if node in closed or queued_cost != best_cost[node]:
            continue

        if node == goal:
            return SearchResult(
                reconstruct(parent, goal),
                expanded,
            )

        closed.add(node)
        expanded.append(node)

        for neighbor, weight in graph[node].items():
            new_cost = best_cost[node] + weight

            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost
                parent[neighbor] = node

                score = (
                    new_cost
                    + heuristic(neighbor, goal, scale)
                )

                heappush(
                    frontier,
                    (
                        score,
                        next(serial),
                        neighbor,
                        new_cost,
                    ),
                )

    return SearchResult([], expanded)


ALGORITHMS = {
    "Ruta base": manual,
    "BFS": bfs,
    "DFS": dfs,
    "A*": astar,
}


def path_distance(graph, path):
    if not path:
        return None

    return sum(
        graph[a][b]
        for a, b in zip(path, path[1:])
    )


def enumerate_routes(graph, start, goal):
    """Encuentra todos los caminos sin repetir nodos.

    Utiliza DFS con retroceso. Los nodos visitados
    pertenecen solamente al camino que se está explorando.
    """

    if start not in graph or goal not in graph:
        raise ValueError(
            "Origen y destino deben pertenecer al grafo."
        )

    routes = []
    path = [start]
    visited = {start}

    def explore(node, distance):
        if node == goal:
            routes.append({
                "path": path.copy(),
                "distance": distance,
            })
            return

        for neighbor, weight in graph[node].items():
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)

                explore(neighbor, distance + weight)

                # Retroceder para explorar otra alternativa.
                path.pop()
                visited.remove(neighbor)

    explore(start, 0.0)

    routes.sort(
        key=lambda route: (
            route["distance"],
            len(route["path"]),
            tuple(route["path"]),
        )
    )

    return routes


def compare(graph, start, goal, runs=100):
    """Compara las técnicas bajo el mismo escenario.

    El tiempo excluye el dibujo y la enumeración
    de todas las rutas posibles.
    """

    if start not in graph or goal not in graph:
        raise ValueError(
            "Origen y destino deben pertenecer al grafo."
        )

    if runs < 1:
        raise ValueError(
            "Debe existir al menos una corrida."
        )

    results = {}

    for name, function in ALGORITHMS.items():
        # Calentamiento excluido de la medición.
        function(graph, start, goal)

        times = []

        for _ in range(runs):
            before = perf_counter_ns()
            result = function(graph, start, goal)

            elapsed = (
                perf_counter_ns() - before
            ) / 1_000_000

            times.append(elapsed)

        results[name] = {
            "result": result,
            "distance": path_distance(graph, result.path),
            "time_ms": median(times),
            "runs": runs,
        }

    return results


def comparison_rows(results):
    rows = []

    for name, values in results.items():
        result = values["result"]

        rows.append({
            "Técnica": name,
            "Estado": (
                "Encontrada"
                if result.path
                else "Sin ruta"
            ),
            "Distancia (km)": values["distance"],
            "Conexiones": (
                len(result.path) - 1
                if result.path
                else None
            ),
            "Nodos expandidos": len(result.expanded),
            "Tiempo mediano (ms)": values["time_ms"],
            "Corridas": values["runs"],
        })

    return rows
