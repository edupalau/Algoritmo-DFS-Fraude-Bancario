"""Análisis de cadenas de transacciones sobre el motor DFS."""

import networkx as nx

from src.algorithms.dfs_core import build_path_report, dfs, get_path_total_amount


def _camino_es_mejor(candidato, mejor_actual) -> bool:
    """Compara caminos por hops y, en empate, por monto total."""
    if mejor_actual is None:
        return True

    hops_candidato = len(candidato)
    hops_mejor = len(mejor_actual)
    if hops_candidato != hops_mejor:
        return hops_candidato > hops_mejor

    return get_path_total_amount(candidato) > get_path_total_amount(mejor_actual)


def _filtro_monto_minimo(monto_minimo: float):
    """Crea una función filtro para usar en el DFS."""

    def filtro(_origen: str, _destino: str, monto: float) -> bool:
        return monto >= float(monto_minimo)

    return filtro


def _deduplicar_y_ordenar(caminos):
    """Elimina duplicados y ordena por hops/monto descendente."""
    vistos = set()
    unicos = []

    for camino in caminos:
        clave = frozenset(camino)
        if clave not in vistos:
            vistos.add(clave)
            unicos.append(camino)

    unicos.sort(key=lambda c: (len(c), get_path_total_amount(c)), reverse=True)
    return unicos


def buscar_cadena_mas_larga(grafo: nx.DiGraph) -> dict | None:
    """Retorna la cadena más larga de todo el grafo."""
    if grafo.number_of_nodes() == 0:
        return None

    mejor_camino = None

    # Probamos DFS desde cada nodo del grafo.
    for nodo_inicio in grafo.nodes:
        for camino in dfs(grafo, str(nodo_inicio)):
            if _camino_es_mejor(camino, mejor_camino):
                mejor_camino = camino

    if mejor_camino is None:
        return None
    return build_path_report(mejor_camino)


def buscar_cadena_sospechosa_mas_larga(
    grafo: nx.DiGraph,
    monto_minimo: float,
    transacciones_minimas: int,
) -> dict | None:
    """Retorna la cadena sospechosa más larga según monto mínimo y hops mínimos."""
    if grafo.number_of_nodes() == 0:
        return None

    filtro = _filtro_monto_minimo(monto_minimo)
    mejor_camino = None

    for nodo_inicio in grafo.nodes:
        for camino in dfs(grafo, str(nodo_inicio), edge_filter=filtro):
            if len(camino) >= int(transacciones_minimas) and _camino_es_mejor(camino, mejor_camino):
                mejor_camino = camino

    if mejor_camino is None:
        return None
    return build_path_report(mejor_camino)


def buscar_todas_las_cadenas_sospechosas(
    grafo: nx.DiGraph,
    monto_minimo: float,
    transacciones_minimas: int,
    transacciones_maximas: int,
) -> list[dict]:
    """Retorna todas las cadenas sospechosas del grafo, deduplicadas y ordenadas."""
    if grafo.number_of_nodes() == 0:
        return []

    filtro = _filtro_monto_minimo(monto_minimo)
    candidatos = []

    # Recorremos todo el grafo y acumulamos candidatos válidos.
    for nodo_inicio in grafo.nodes:
        caminos = dfs(
            grafo,
            str(nodo_inicio),
            edge_filter=filtro,
            max_depth=transacciones_maximas,
        )

        for camino in caminos:
            hops = len(camino)
            if int(transacciones_minimas) <= hops <= int(transacciones_maximas):
                candidatos.append(camino)

    caminos_finales = _deduplicar_y_ordenar(candidatos)
    return [build_path_report(camino) for camino in caminos_finales]


def buscar_cadenas_sospechosas_desde_cuenta(
    grafo: nx.DiGraph,
    cuenta: str,
    monto_minimo: float,
    transacciones_minimas: int,
    transacciones_maximas: int,
) -> list[dict]:
    """Retorna cadenas sospechosas partiendo solo desde una cuenta."""
    if cuenta not in grafo:
        raise ValueError(f"La cuenta '{cuenta}' no existe en el grafo.")

    filtro = _filtro_monto_minimo(monto_minimo)
    candidatos = []

    caminos = dfs(
        grafo,
        cuenta,
        edge_filter=filtro,
        max_depth=transacciones_maximas,
    )

    # Mismo criterio de rango que en el análisis global.
    for camino in caminos:
        hops = len(camino)
        if int(transacciones_minimas) <= hops <= int(transacciones_maximas):
            candidatos.append(camino)

    caminos_finales = _deduplicar_y_ordenar(candidatos)
    return [build_path_report(camino) for camino in caminos_finales]