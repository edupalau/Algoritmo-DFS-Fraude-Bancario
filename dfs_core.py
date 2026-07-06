#Algoritmo DFS para recorrer el grafo

import networkx as nx


def dfs(
    graph: nx.DiGraph,
    start: str,
    edge_filter=None, #Funcion filtro que retorne un booleano
    max_depth: int | None = None,
    detect_cycles: bool = False,
):
    """
    DFS con pila explícita (sin recursión).

    La lógica es intencionalmente simple, similar al estilo de clase:
    - sacar estado de la pila
    - revisar vecinos
    - apilar los siguientes pasos
    - si no pudo avanzar, guardar camino terminal

    Retorna una lista con todos los caminos encontrados.
    """
    if start not in graph:
        return []

    caminos = []

    # Cada item: (nodo_actual, camino_actual, visitados_en_este_camino)
    pila = [(start, [], [start])]

    while pila:
        nodo_actual, camino_actual, visitados = pila.pop()

        if max_depth is not None and len(camino_actual) >= max_depth:
            if camino_actual:
                caminos.append(camino_actual)
        else:
            pudo_avanzar = False
            vecinos = list(graph.successors(nodo_actual))

            # Recorremos al revés porque la pila es LIFO.
            for vecino in reversed(vecinos):
                monto = float(graph[nodo_actual][vecino].get("amount", 0.0))
                vecino_id = str(vecino)

                pasa_filtro = edge_filter is None or edge_filter(nodo_actual, vecino_id, monto)
                if pasa_filtro:
                    paso = (nodo_actual, vecino_id, monto)

                    es_cierre_ciclo = detect_cycles and vecino_id == start and camino_actual
                    if es_cierre_ciclo:
                        ciclo_en_rango = max_depth is None or len(camino_actual) + 1 <= max_depth
                        if ciclo_en_rango:
                            caminos.append(camino_actual + [paso])
                        pudo_avanzar = True
                    else:
                        if vecino_id not in visitados:
                            nuevo_camino = camino_actual + [paso]
                            nuevos_visitados = visitados + [vecino_id]
                            pila.append((vecino_id, nuevo_camino, nuevos_visitados))
                            pudo_avanzar = True

            if not pudo_avanzar and camino_actual:
                caminos.append(camino_actual)

    return caminos


def get_path_nodes(path) -> list[str]:
    #Devuelve nodos del camino en orden de aparición, sin repetir.
    ordered_nodes: list[str] = []
    seen: set[str] = set()

    for source, target, _ in path:
        if source not in seen:
            ordered_nodes.append(source)
            seen.add(source)
        if target not in seen:
            ordered_nodes.append(target)
            seen.add(target)

    return ordered_nodes


def get_path_total_amount(path) -> float:
    #Suma los montos de todos los pasos del camino
    return float(sum(amount for _, _, amount in path))


def build_path_report(path) -> dict:
    #Construye el reporte estándar de un camino
    nodes = get_path_nodes(path)
    steps = [
        {
            "from": source,
            "to": target,
            "amount": float(amount),
        }
        for source, target, amount in path
    ]

    return {
        "nodes": nodes,
        "steps": steps,
        "total_amount": get_path_total_amount(path),
        "num_accounts": len(nodes),
        "num_hops": len(path),
    }
