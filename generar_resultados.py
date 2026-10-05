"""Regenera evidencia con tiempos medidos en la máquina donde se ejecuta."""
import csv
from pathlib import Path
from algorithms import compare, comparison_rows
from graph_data import build_graph


def generate():
    root = Path(__file__).resolve().parent
    rows = comparison_rows(compare(build_graph(), "Santa Anita", "Miraflores", 100))
    with (root / "resultados_demo.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("Escenario: Santa Anita -> Miraflores, sin bloqueos, 100 corridas idénticas por técnica.")
    print("Copiar estas cuatro filas en la tabla del README si se quiere actualizar el tiempo:")
    for row in rows:
        print(f"| {row['Técnica']} | {row['Distancia (km)']:g} | {row['Nodos expandidos']} | {row['Tiempo mediano (ms)']:.4f} | {row['Corridas']} |")


if __name__ == "__main__":
    generate()
