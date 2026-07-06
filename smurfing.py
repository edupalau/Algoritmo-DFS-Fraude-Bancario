"""Deteccion de patrones de smurfing sin usar DFS."""

import networkx as nx

from src.config import SMURFING_THRESHOLD


def detectar_smurfing(grafo: nx.DiGraph) -> list[dict]:
    """
    Consigna 5: detecta patrones Origen → [Intermediarios] → Destino.

    Un patron es valido si hay 2 o mas intermediarios y cada uno reenvia
    al menos el 80% de lo recibido desde el origen hacia el mismo destino.
    """
    if grafo.number_of_nodes() == 0:
        return []

    candidatos: dict[tuple[str, str], list[dict]] = {}

    # Recorremos cada nodo como posible origen
    for origen in grafo.nodes:
        # Intermediarios directos del origen
        for inter in grafo.successors(origen):
            monto_recibido = float(grafo[origen][inter].get("amount", 0.0))

            # Destinos a los que el intermediario reenvia
            for destino in grafo.successors(inter):
                monto_enviado = float(grafo[inter][destino].get("amount", 0.0))

                if monto_recibido <= 0:
                    continue

                if monto_enviado >= SMURFING_THRESHOLD * monto_recibido:
                    clave = (str(origen), str(destino))
                    if clave not in candidatos:
                        candidatos[clave] = []

                    candidatos[clave].append(
                        {
                            "cuenta": str(inter),
                            "monto_recibido": monto_recibido,
                            "monto_enviado": monto_enviado,
                            "ratio": monto_enviado / monto_recibido,
                        }
                    )

    # Filtrar solo los patrones con 2 o mas intermediarios
    patrones = []
    for (origen, destino), intermediarios in candidatos.items():
        if len(intermediarios) < 2:
            continue

        total_recibido = sum(i["monto_recibido"] for i in intermediarios)
        total_enviado = sum(i["monto_enviado"] for i in intermediarios)

        patrones.append(
            {
                "origen": origen,
                "destino": destino,
                "intermediarios": intermediarios,
                "total_recibido": float(total_recibido),
                "total_enviado": float(total_enviado),
            }
        )

    return patrones
