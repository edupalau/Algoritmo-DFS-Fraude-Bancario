#Construccion del grafo a partir de csv
#Consultas basicas acerca del grafo

import networkx as nx
import pandas as pd

from src.config import COL_AMOUNT, COL_RECEIVER, COL_SENDER


def create_graph_dict_from_csv(filepath: str):

    df = pd.read_csv(filepath)

    required_columns = {COL_SENDER, COL_RECEIVER, COL_AMOUNT}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Faltan columnas obligatorias: {missing}")

    df = df[[COL_SENDER, COL_RECEIVER, COL_AMOUNT]].copy()
    df[COL_AMOUNT] = pd.to_numeric(df[COL_AMOUNT], errors="raise").astype(float)

    # Primero acumulamos en un dict auxiliar para poder sumar A->B repetidos si es que existen.
    # aggregated["A"]["B"] = monto_total
    # Diccionario que acumula montos de transacciones de una cuenta a otra donde se repite el sender y el receiver
    # Solo como "medida de seguridad" por si existen filas en el csv repetidas en cuanto a sender-receiver
    aggregated: dict[str, dict[str, float]] = {}

    for sender, receiver, amount in df.itertuples(index=False, name=None):
        sender_id = str(sender)
        receiver_id = str(receiver)
        amount_value = float(amount)

        if sender_id not in aggregated:
            aggregated[sender_id] = {}
        if receiver_id not in aggregated[sender_id]:
            aggregated[sender_id][receiver_id] = 0.0

        aggregated[sender_id][receiver_id] += amount_value

        # Asegura que cuentas sin salidas también existan como nodo en el dict.
        if receiver_id not in aggregated:
            aggregated[receiver_id] = {}

    # Generamos el diccionario propiamente dicho que representa al grafo a partir del csv
    graph_dict = {}
    for sender_id, targets in aggregated.items():
        neighbors = []
        for receiver_id, amount_value in targets.items():
            neighbors.append((receiver_id, float(amount_value)))
        graph_dict[sender_id] = neighbors

    return graph_dict


def load_graph_from_csv(filepath: str) -> nx.DiGraph:
    #Retorna un grafo nx.DiGraph a partir del diccionario que simula un grafo a partir del csv
    graph_dict = create_graph_dict_from_csv(filepath)

    graph = nx.DiGraph()

    for sender_id, neighbors in graph_dict.items():
        graph.add_node(sender_id)
        for receiver_id, amount_value in neighbors:
            graph.add_edge(sender_id, receiver_id, amount=float(amount_value))

    return graph


def graph_to_dict(graph: nx.DiGraph):
    #Convierte un nx.DiGraph al formato de diccionario
    dict_from_graph = {}

    for node in graph.nodes:
        neighbors: list[tuple[str, float]] = []
        for neighbor, edge_data in graph[node].items():
            neighbors.append((str(neighbor), float(edge_data.get("amount", 0.0))))
        dict_from_graph[str(node)] = neighbors

    return dict_from_graph

def _top_accounts_by_degree(
    degree_view: list[tuple[str, int]],
    limit: int = 5,
) -> list[tuple[str, int]]:
    """Ordena por grado descendente y, en empate, por ID de cuenta ascendente."""
    normalized = [(str(node), int(degree)) for node, degree in degree_view]
    normalized.sort(key=lambda item: (-item[1], item[0]))
    return normalized[:limit]


def get_graph_stats(graph: nx.DiGraph) -> dict:
    """
    Calcula métricas básicas para mostrar en UI.

    Devuelve:
    - total_nodes, total_edges
    - avg_amount, max_amount, min_amount
    - top_senders (top 5 por out-degree)
    - top_receivers (top 5 por in-degree)
    """
    amounts = [float(data.get("amount", 0.0)) for _, _, data in graph.edges(data=True)]

    if amounts:
        avg_amount = sum(amounts) / len(amounts)
        max_amount = max(amounts)
        min_amount = min(amounts)
    else:
        avg_amount = 0.0
        max_amount = 0.0
        min_amount = 0.0

    # out_degree: cantidad de aristas que salen del nodo.
    # in_degree: cantidad de aristas que llegan al nodo.
    top_senders = _top_accounts_by_degree(list(graph.out_degree()), limit=5)
    top_receivers = _top_accounts_by_degree(list(graph.in_degree()), limit=5)

    return {
        "total_nodes": graph.number_of_nodes(),
        "total_edges": graph.number_of_edges(),
        "avg_amount": float(avg_amount),
        "max_amount": float(max_amount),
        "min_amount": float(min_amount),
        "top_senders": top_senders,
        "top_receivers": top_receivers,
    }
