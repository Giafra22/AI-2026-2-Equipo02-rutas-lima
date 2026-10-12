"""Interfaz del proyecto de rutas inteligentes."""

import csv
import io

import matplotlib.pyplot as plt
import streamlit as st

from algorithms import (
    compare,
    comparison_rows,
    enumerate_routes,
)

from graph_data import (
    EDGES,
    POSITIONS,
    MANUAL_ITINERARY,
    build_graph,
    heuristic_scale,
)

from visualization import draw_graph


st.set_page_config(
    page_title="Rutas inteligentes | Equipo 02",
    page_icon="🚚",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        max-width: 1350px;
    }

    [data-testid="stMetric"] {
        background: #17243a;
        border: 1px solid #30445d;
        border-radius: 12px;
        padding: 16px;
    }

    h1 {
        letter-spacing: -1px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid #26374e;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "AGENTES INTELIGENTES · AVANCE 1 · EQUIPO 02"
)

st.title(
    "Rutas inteligentes de reparto en Lima"
)

st.write(
    "Compara un itinerario fijo con BFS, DFS y A* "
    "para conectar puntos de entrega."
)

st.caption(
    "Simulación educativa: distritos, coordenadas y "
    "distancias esquemáticas. No son rutas viales reales."
)


with st.sidebar:
    st.header("Planificar entrega")

    names = list(POSITIONS)

    start = st.selectbox(
        "Origen",
        names,
        index=names.index("Santa Anita"),
    )

    goal = st.selectbox(
        "Destino",
        names,
        index=names.index("Miraflores"),
    )

    strategy = st.selectbox(
        "Ruta que se dibuja",
        ["A*", "BFS", "DFS", "Ruta base"],
    )

    options = {
        f"{a} ↔ {b}": (a, b)
        for a, b, _ in EDGES
    }

    blocked_label = st.selectbox(
        "Conexión bloqueada",
        ["Ninguna", *options],
    )

    runs = st.selectbox(
        "Corridas por técnica",
        [100, 500, 1000],
    )

    recalculate = st.button(
        "Recalcular comparación",
        type="primary",
        width="stretch",
    )

    st.caption(
        "Se compara automáticamente al cambiar el "
        "escenario. El botón repite la medición del tiempo."
    )

    st.divider()
    st.write("**Integrantes**")

    st.caption(
        "Lucio Facundo Sánchez Bodero\n\n"
        "Gianfranco Fernandez Arias"
    )


graph = build_graph(options.get(blocked_label))

scenario = (
    start,
    goal,
    blocked_label,
    runs,
)

if (
    recalculate
    or st.session_state.get("scenario") != scenario
    or "possible_routes" not in st.session_state
):
    st.session_state["results"] = compare(
        graph,
        start,
        goal,
        runs,
    )

    st.session_state["possible_routes"] = enumerate_routes(
        graph,
        start,
        goal,
    )

    st.session_state.pop(
        "possible_route_index",
        None,
    )

    st.session_state["scenario"] = scenario


results = st.session_state["results"]
values = results[strategy]
result = values["result"]

cards = st.columns(4)

cards[0].metric(
    "Distancia simulada",
    (
        f"{values['distance']:g} km"
        if result.path
        else "Sin ruta"
    ),
)

cards[1].metric(
    "Nodos expandidos",
    len(result.expanded),
)

cards[2].metric(
    "Tiempo del algoritmo",
    f"{values['time_ms']:.4f} ms",
)

cards[3].metric(
    "Corridas",
    runs,
)


map_tab, routes_tab, explanation_tab, data_tab = st.tabs([
    "Mapa y comparación",
    "Rutas posibles",
    "Cómo funciona",
    "Datos del escenario",
])


with map_tab:
    left, right = st.columns([3, 1])

    with left:
        fig = draw_graph(
            graph,
            result.path,
            result.expanded,
            start,
            goal,
        )

        st.pyplot(fig, width="stretch")
        plt.close(fig)

        st.caption(
            "Azul: origen · Rosado: destino · "
            "Verde: ruta elegida · Ámbar: nodo expandido · "
            "Números: km simulados"
        )

    with right:
        st.subheader(strategy)

        if result.path:
            st.write(" → ".join(result.path))
        else:
            st.warning(
                "Esta técnica no encuentra una ruta "
                "en el escenario actual."
            )

        st.write("**Orden de expansión**")

        st.write(
            " → ".join(result.expanded)
            or "Sin expansiones de búsqueda."
        )

        if strategy == "Ruta base":
            st.caption(
                "La base lee el itinerario fijo. Sus "
                "0 expansiones no significan mejor "
                "calidad de ruta."
            )

        if start == goal:
            st.info(
                "Origen y destino coinciden: "
                "distancia y expansiones son 0."
            )

    st.subheader(
        "Comparación en el mismo escenario"
    )

    rows = comparison_rows(results)

    st.dataframe(
        rows,
        hide_index=True,
        width="stretch",
        column_config={
            "Tiempo mediano (ms)":
                st.column_config.NumberColumn(
                    format="%.4f"
                ),
        },
    )

    st.caption(
        "Métrica principal: distancia en km. "
        "Expansión = examinar vecinos de un nodo; "
        "la meta no se expande. "
        "Tiempo = mediana de corridas idénticas, "
        "sin interfaz ni dibujo; varía según el equipo."
    )

    base = results["Ruta base"]["distance"]
    optimal = results["A*"]["distance"]

    if base and optimal is not None:
        savings = (base - optimal) / base * 100

        st.success(
            f"En este escenario A* reduce "
            f"{savings:.1f}% la distancia "
            f"frente a la ruta base."
        )

    st.info(
        "BFS minimiza conexiones, no kilómetros. "
        "DFS sigue el orden de vecinos sin garantizar "
        "el mínimo. A* minimiza la distancia con esta "
        "heurística admisible; no necesariamente gana "
        "en tiempo ni expande menos nodos en todos "
        "los casos."
    )

    buffer = io.StringIO()

    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            *rows[0],
            "Origen",
            "Destino",
            "Bloqueo",
        ],
    )

    writer.writeheader()

    writer.writerows(
        dict(
            row,
            Origen=start,
            Destino=goal,
            Bloqueo=blocked_label,
        )
        for row in rows
    )

    st.download_button(
        "Descargar comparación CSV",
        buffer.getvalue().encode("utf-8-sig"),
        "comparacion_rutas.csv",
        "text/csv",
    )


with routes_tab:
    st.subheader(
        f"Todas las rutas de {start} a {goal}"
    )

    possible_routes = st.session_state["possible_routes"]

    st.metric(
        "Rutas posibles sin repetir puntos",
        len(possible_routes),
    )

    st.caption(
        "Se enumeran todos los caminos simples del "
        "escenario actual: ningún punto se repite, "
        "se termina al llegar al destino y se respetan "
        "los bloqueos. Permitir ciclos daría infinitos "
        "recorridos en este grafo."
    )

    if not possible_routes:
        st.warning(
            "No hay rutas disponibles entre estos "
            "puntos con las conexiones actuales."
        )

    else:
        routes_rows = [
            {
                "N.º": i + 1,
                "Recorrido": " → ".join(route["path"]),
                "Distancia (km)": route["distance"],
                "Conexiones": len(route["path"]) - 1,
            }
            for i, route in enumerate(possible_routes)
        ]

        st.write(
            "**Rutas ordenadas de menor a mayor distancia**"
        )

        st.dataframe(
            routes_rows,
            hide_index=True,
            width="stretch",
            height=350,
            column_config={
                "Distancia (km)":
                    st.column_config.NumberColumn(
                        format="%.2f"
                    ),
            },
        )

        selected = st.selectbox(
            "Selecciona una ruta para verla en el mapa",
            range(len(possible_routes)),
            format_func=lambda i: (
                f"Ruta {i + 1} · "
                f"{possible_routes[i]['distance']:g} km"
            ),
            key="possible_route_index",
        )

        chosen = possible_routes[selected]

        st.write(
            " → ".join(chosen["path"])
        )

        st.caption(
            f"Distancia: {chosen['distance']:g} km · "
            f"Conexiones: {len(chosen['path']) - 1}"
        )

        fig = draw_graph(
            graph,
            chosen["path"],
            [],
            start,
            goal,
        )

        st.pyplot(fig, width="stretch")
        plt.close(fig)

        st.caption(
            "Azul: origen · Rosado: destino · "
            "Verde: recorrido seleccionado. "
            "Esta vista no muestra expansiones "
            "de un algoritmo."
        )

        export = io.StringIO()

        writer = csv.DictWriter(
            export,
            fieldnames=[
                *routes_rows[0],
                "Origen",
                "Destino",
                "Bloqueo",
            ],
        )

        writer.writeheader()

        writer.writerows(
            dict(
                row,
                Origen=start,
                Destino=goal,
                Bloqueo=blocked_label,
            )
            for row in routes_rows
        )

        st.download_button(
            "Descargar todas las rutas CSV",
            export.getvalue().encode("utf-8-sig"),
            "rutas_posibles.csv",
            "text/csv",
        )

        st.info(
            "Esta enumeración usa DFS con retroceso "
            "para listar todas las alternativas. "
            "BFS, DFS y A* siguen devolviendo una sola "
            "ruta cada uno en la pestaña de comparación. "
            "Enumerar todas las rutas no forma parte "
            "de sus tiempos medidos."
        )


with explanation_tab:
    st.subheader(
        "Cuatro maneras de resolver la misma entrega"
    )

    st.markdown(
        """
**Ruta base.** Toma el segmento entre origen y destino
de un itinerario fijado de antemano. Si un tramo de ese
segmento está bloqueado, informa que no hay ruta base
disponible.

**BFS.** Utiliza una cola y explora por niveles.
Encuentra una ruta con el menor número de conexiones.
Como las aristas tienen pesos diferentes, esa ruta
puede recorrer más kilómetros.

**DFS.** Utiliza una pila y profundiza en un camino
antes de volver a alternativas. Evita ciclos mediante
nodos visitados; su resultado depende del orden de
vecinos.

**A*.** Utiliza una cola de prioridad con
`f(n) = g(n) + h(n)`. `g` es la distancia acumulada y
`h` es una cota inferior de la distancia restante.
La heurística es distancia euclidiana por una escala
calculada a partir de las aristas.
        """
    )

    st.code(
        " → ".join(MANUAL_ITINERARY),
        language=None,
    )

    st.write(
        "Escala de la heurística en este escenario: "
        f"{heuristic_scale(graph):.4f}."
    )

    st.write(
        "**Rutas posibles:** DFS con retroceso explora "
        "todas las alternativas sin repetir nodos. "
        "Al volver de una rama, libera sus nodos "
        "para usarlos en otros caminos. "
        "Los resultados se ordenan por distancia "
        "y se pueden dibujar o exportar."
    )

    st.caption(
        "Parte 2 prevista: comparar dos regresores "
        "para predecir tiempos por tramo y luego "
        "alimentar A*. No está implementada "
        "en este avance."
    )


with data_tab:
    st.subheader(
        "Conexiones simuladas"
    )

    st.dataframe(
        [
            {
                "Origen": a,
                "Destino": b,
                "Distancia (km)": w,
                "Estado": (
                    "Activa"
                    if b in graph[a]
                    else "Bloqueada"
                ),
            }
            for a, b, w in EDGES
        ],
        hide_index=True,
        width="stretch",
    )

    st.caption(
        "Grafo no dirigido: una conexión activa puede "
        "recorrerse en ambos sentidos. "
        "Alcance: una entrega entre origen y destino; "
        "no optimiza el orden de múltiples pedidos."
    )
