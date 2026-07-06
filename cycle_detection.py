"""Deteccion de ciclos usando el DFS iterativo."""

import networkx as nx

from src.algorithms.dfs_core import build_path_report, dfs, get_path_nodes


def _es_ciclo_cerrado(camino, nodo_inicio: str) -> bool:
    """Verifica si el camino vuelve al nodo de inicio."""
    if not camino:
        return False

    ultimo_origen, ultimo_destino, _ = camino[-1]
    return str(ultimo_destino) == str(nodo_inicio)


def detectar_ciclos(grafo: nx.DiGraph) -> list[dict]:
    """
    Consigna 4: encuentra todos los ciclos del grafo.

    Para cada nodo del grafo:
    - corre dfs(grafo, nodo, detect_cycles=True)
    - deduplica ciclos por frozenset de nodos
    - retorna lista de build_path_report(camino)
    """
    if grafo.number_of_nodes() == 0:
        return []

    ciclos_unicos = []
    vistos = set()

    for nodo_inicio in grafo.nodes:
        caminos = dfs(grafo, str(nodo_inicio), detect_cycles=True)

        for camino in caminos:
            if not _es_ciclo_cerrado(camino, str(nodo_inicio)):
                continue

            nodos = get_path_nodes(camino)
            clave = frozenset(nodos)
            if clave in vistos:
                continue

            vistos.add(clave)
            ciclos_unicos.append(camino)

    # Ordenar de mas a menos hops
    ciclos_unicos.sort(key=lambda c: len(c), reverse=True)
    return [build_path_report(ciclo) for ciclo in ciclos_unicos]


def detectar_ciclos_desde_cuenta(grafo: nx.DiGraph, cuenta: str) -> list[dict]:
    """
    Consigna 7: ciclos que arrancan y terminan en `cuenta`.

    - corre dfs(grafo, cuenta, detect_cycles=True)
    - retorna lista de build_path_report(camino)
    """
    if cuenta not in grafo:
        raise ValueError(f"La cuenta '{cuenta}' no existe en el grafo.")

    ciclos = []
    caminos = dfs(grafo, str(cuenta), detect_cycles=True)

    for camino in caminos:
        if _es_ciclo_cerrado(camino, str(cuenta)):
            ciclos.append(camino)

    # Ordenar de mas a menos hops
    ciclos.sort(key=lambda c: len(c), reverse=True)
    return [build_path_report(ciclo) for ciclo in ciclos]


# Alias en ingles para compatibilidad con el roadmap original
def find_all_cycles(graph: nx.DiGraph) -> list[dict]:
    return detectar_ciclos(graph)


def find_cycles_from_account(graph: nx.DiGraph, account: str) -> list[dict]:
    return detectar_ciclos_desde_cuenta(graph, account)
