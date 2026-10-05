# Sistema inteligente de rutas de reparto en Lima mediante algoritmos de búsqueda

**Equipo:** 02 · **Integrantes:** Lucio Facundo Sánchez Bodero y Gianfranco Fernandez Arias.

**Problema y quién lo sufre.** Repartidores y empresas de distribución pueden recorrer kilómetros innecesarios con itinerarios fijos. Comparamos rutas para una entrega entre dos puntos en un grafo didáctico de Lima: 10 nodos, 17 conexiones bidireccionales y distancias simuladas; no representa calles ni tráfico reales.

**Modo base y técnicas.** Base: segmento de un itinerario predeterminado, sin búsqueda ni desvíos. Parte 1: BFS (mínimas conexiones), DFS (profundidad) y A* (mínima distancia con heurística euclidiana escalada admisible). Parte 2 prevista: regresión lineal y árbol regresor para predecir tiempos por tramo; todavía no implementada.

**Resultados medidos.** Santa Anita → Miraflores, sin bloqueos. Distancia es la métrica principal. Tiempo solo del algoritmo: mediana de 100 repeticiones idénticas tras calentamiento, medido en el entorno de preparación; varía por equipo. Nodos expandidos = nodos cuyos vecinos se examinan; se excluye la meta. La base no expande nodos.

| Técnica | Distancia (km) | Nodos expandidos | Tiempo (ms) | Corridas |
|---|---:|---:|---:|---:|
| Ruta base | 23 | 0 | 0.0010 | 100 |
| BFS | 23 | 9 | 0.0021 | 100 |
| DFS | 49 | 9 | 0.0034 | 100 |
| A* | 20 | 8 | 0.0160 | 100 |

A* recorre 20 km frente a 23 km de la base (13.0% menos); su costo de procesamiento puede ser mayor en este grafo pequeño. Rutas y métricas se calculan en la app, con bloqueo opcional de una conexión y exportación CSV.

**Ejecución.** App pública: **PENDIENTE: pegar URL de Streamlit**. Repositorio: **PENDIENTE: pegar URL de GitHub**. Con Python 3.12, desde la carpeta del proyecto:
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Pruebas: `python verificar_proyecto.py`. Evidencia local: `python generar_resultados.py`; copiar sus filas si se actualizan los tiempos de esta tabla.

**Uso de IA.** Con asistencia de ChatGPT se generaron `app.py`, `graph_data.py`, `algorithms.py`, `visualization.py`, scripts de pruebas/resultados, configuración y documentación. El paquete adapta el caso a distritos de Lima, agrega bloqueos y calcula una escala admisible. Modificaciones propias del equipo: **PENDIENTE: registrar cambios reales, o indicar que no hubo cambios posteriores**. Cada integrante debe revisar y poder explicar lo presentado.

**Roles y evidencia.** **PENDIENTE antes de entregar:** Lucio Facundo Sánchez Bodero: aporte real y [enlace a su commit]; Gianfranco Fernandez Arias: aporte real y [enlace a su commit]. Reparto sugerido: Lucio revisa caso, métricas y explicación; Gianfranco instala, valida y publica. Confirmar el reparto realizado y reemplazar estos campos.
