"""Mapa didáctico: distancias y coordenadas simuladas, no calles reales."""
from math import hypot

EDGES = [
    ("Santa Anita", "Ate", 4), ("Santa Anita", "El Agustino", 5),
    ("Santa Anita", "San Luis", 6), ("Ate", "La Molina", 6),
    ("Ate", "San Borja", 8), ("El Agustino", "San Luis", 3),
    ("El Agustino", "Cercado de Lima", 7), ("San Luis", "San Borja", 4),
    ("San Luis", "Cercado de Lima", 6), ("La Molina", "San Borja", 5),
    ("La Molina", "Surco", 7), ("San Borja", "Surco", 5),
    ("San Borja", "San Isidro", 6), ("Cercado de Lima", "San Isidro", 7),
    ("Surco", "San Isidro", 7), ("Surco", "Miraflores", 6),
    ("San Isidro", "Miraflores", 4),
]
POSITIONS = {
    "Santa Anita": (8, 2), "Ate": (9, 4), "El Agustino": (6, 2),
    "San Luis": (6, 4), "La Molina": (8, 6), "San Borja": (6, 6),
    "Cercado de Lima": (4, 2), "San Isidro": (4, 6),
    "Surco": (6, 8), "Miraflores": (4, 8),
}
# Itinerario fijado de antemano. Cada par consecutivo tiene una conexión real
# en este grafo. No depende de los costos ni usa búsqueda para optimizarse.
MANUAL_ITINERARY = [
    "Santa Anita", "Ate", "La Molina", "Surco", "Miraflores",
    "San Isidro", "Cercado de Lima", "El Agustino", "San Luis", "San Borja",
]


def build_graph(blocked=None):
    graph = {name: {} for name in POSITIONS}
    for a, b, distance in EDGES:
        if blocked and frozenset((a, b)) == frozenset(blocked):
            continue
        graph[a][b] = float(distance)
        graph[b][a] = float(distance)
    return graph


def heuristic_scale(graph):
    """Cada arista cuesta >= escala * longitud geométrica.

    Por la desigualdad triangular, h nunca sobreestima el camino más corto;
    también es consistente. Se recalcula si se editan los pesos o las aristas.
    """
    ratios = []
    for a, neighbors in graph.items():
        for b, weight in neighbors.items():
            length = hypot(POSITIONS[a][0] - POSITIONS[b][0],
                           POSITIONS[a][1] - POSITIONS[b][1])
            if length:
                ratios.append(weight / length)
    return min(ratios, default=0.0)


def heuristic(node, goal, scale):
    return scale * hypot(POSITIONS[node][0] - POSITIONS[goal][0],
                         POSITIONS[node][1] - POSITIONS[goal][1])
