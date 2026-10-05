"""Dibujo esquemático del grafo; no representa la geografía real de Lima."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from graph_data import POSITIONS


def draw_graph(graph, path, expanded, start, goal):
    fig, ax = plt.subplots(figsize=(11, 7.2), facecolor="#101a2d")
    ax.set_facecolor("#101a2d")
    route_edges = {frozenset((a, b)) for a, b in zip(path, path[1:])}
    drawn = set()
    for a, neighbors in graph.items():
        for b, cost in neighbors.items():
            edge = frozenset((a, b))
            if edge in drawn:
                continue
            drawn.add(edge)
            x1, y1 = POSITIONS[a]
            x2, y2 = POSITIONS[b]
            chosen = edge in route_edges
            ax.plot([x1, x2], [y1, y2], color="#38ddae" if chosen else "#506078",
                    linewidth=4 if chosen else 1.6, alpha=1 if chosen else .7, zorder=1)
            ax.text((x1+x2)/2, (y1+y2)/2, f"{cost:g}", ha="center", va="center",
                    fontsize=10, color="#eef4ff", zorder=2,
                    bbox=dict(facecolor="#101a2d", edgecolor="none", pad=2))
    for node, (x, y) in POSITIONS.items():
        color = "#36d6a4" if node in path else "#f5b65e" if node in expanded else "#617693"
        if node == start:
            color = "#5ca7ff"
        elif node == goal:
            color = "#ec82b7"
        ax.scatter(x, y, s=580, c=color, edgecolors="#e6eefb", linewidths=1.2, zorder=3)
        label = node.replace("Cercado de Lima", "Cercado\nde Lima")
        ax.text(x, y + .49, label, ha="center", va="bottom", fontsize=10.5,
                color="#eff5ff", weight="bold", zorder=4,
                bbox=dict(facecolor="#101a2d", edgecolor="none", alpha=.92, pad=2))
    ax.set_xlim(3.1, 9.9)
    ax.set_ylim(1.2, 9.1)
    ax.axis("off")
    fig.tight_layout(pad=1.3)
    return fig
