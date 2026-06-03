# Roadmap — Análisis de Fraude Bancario
### Taller de Programación III — UNAHUR

> Implementar en orden. Confirmar que cada fase corre sin errores antes de pasar a la siguiente.

---

## Estructura del proyecto

```
fraud_analysis/
├── app.py                          # Streamlit — toda la UI acá, un solo archivo
├── requirements.txt
├── Transacciones.csv
└── src/
    ├── config.py                   # ✅ Constantes
    ├── data/
    │   └── graph_builder.py        # ✅ CSV → DiGraph
    └── algorithms/
        ├── dfs_core.py             # ✅ Motor DFS con pila explícita
        ├── chain_analysis.py       # ✅ Consignas 1, 2, 3, 6
        ├── cycle_detection.py      # ❌ Consignas 4, 7
        ├── smurfing.py             # ❌ Consigna 5
        └── graph_renderer.py       # ❌ Visualización pyvis
```

---

## ✅ Ya implementado

### `src/config.py`
```python
COL_SENDER   = "Sender Account ID"
COL_RECEIVER = "Receiver Account ID"
COL_AMOUNT   = "Transaction Amount"
SMURFING_THRESHOLD = 0.80
```

### `src/data/graph_builder.py`
| Función | Retorna | Descripción |
|---|---|---|
| `load_graph_from_csv(filepath)` | `nx.DiGraph` | Lee el CSV y construye el grafo. Si A→B se repite, suma los montos. |
| `graph_to_dict(graph)` | `dict` | Convierte el grafo a diccionario de adyacencia. |
| `get_graph_stats(graph)` | `dict` | Métricas: total_nodes, total_edges, avg_amount, max_amount, min_amount, top_senders, top_receivers. |

### `src/algorithms/dfs_core.py`
| Función | Retorna | Descripción |
|---|---|---|
| `dfs(graph, start, edge_filter, max_depth, detect_cycles)` | `list[list]` | DFS con pila explícita. Cada camino es lista de tuplas `(origen, destino, monto)`. |
| `get_path_nodes(path)` | `list[str]` | Lista ordenada de nodos únicos del camino. |
| `get_path_total_amount(path)` | `float` | Suma de montos del camino. |
| `build_path_report(path)` | `dict` | Reporte estándar: `nodes`, `steps`, `total_amount`, `num_accounts`, `num_hops`. |

### `src/algorithms/chain_analysis.py`
| Función | Consigna | Descripción |
|---|---|---|
| `buscar_cadena_mas_larga(grafo)` | 1 | La cadena con más hops de todo el grafo. |
| `buscar_cadena_sospechosa_mas_larga(grafo, monto_minimo, transacciones_minimas)` | 2 | La más larga filtrando por monto mínimo y hops mínimos. |
| `buscar_todas_las_cadenas_sospechosas(grafo, monto_minimo, transacciones_minimas, transacciones_maximas)` | 3 | Todas las cadenas que cumplen los tres filtros. |
| `buscar_cadenas_sospechosas_desde_cuenta(grafo, cuenta, monto_minimo, transacciones_minimas, transacciones_maximas)` | 6 | Igual que consigna 3 pero solo desde una cuenta. |

---

## FASE 3.2 — `cycle_detection.py` ❌

**Archivo:** `src/algorithms/cycle_detection.py`

Dos funciones. Ambas usan `dfs(..., detect_cycles=True)` que ya está implementado.

```python
from src.algorithms.dfs_core import dfs, build_path_report

def detectar_ciclos(grafo):
    """
    Consigna 4: encuentra todos los ciclos del grafo.
    
    Para cada nodo del grafo, corre dfs con detect_cycles=True.
    Deduplica: dos ciclos son iguales si tienen el mismo frozenset de nodos.
    Retorna lista de build_path_report(camino) para cada ciclo único.
    """

def detectar_ciclos_desde_cuenta(grafo, cuenta):
    """
    Consigna 7: ciclos que arrancan y terminan en `cuenta`.
    
    Corre dfs(grafo, cuenta, detect_cycles=True).
    Retorna lista de build_path_report(camino).
    """
```

**Notas:**
- La deduplicación es por `frozenset` de nodos: `A→B→C→A` y `B→C→A→B` se deduplicaN.
- Para ordenar los resultados: de más a menos hops.
- Si no hay ciclos, retornar lista vacía `[]`.

---

## FASE 3.3 — `smurfing.py` ❌

**Archivo:** `src/algorithms/smurfing.py`

Una función. No necesita DFS: es inspección directa de vecinos del grafo.

```python
from src.config import SMURFING_THRESHOLD

def detectar_smurfing(grafo):
    """
    Consigna 5: detecta patrones Origen → [Inter_1..N] → Destino
    donde N >= 2 y cada intermediario reenvía >= 80% de lo recibido.
    
    Algoritmo:
    1. Para cada nodo A (posible origen):
       - Para cada vecino I de A (posible intermediario):
         - monto_de_A_a_I = grafo[A][I]["amount"]
         - Para cada vecino D de I (posible destino):
           - monto_de_I_a_D = grafo[I][D]["amount"]
           - Si monto_de_I_a_D >= 0.80 * monto_de_A_a_I:
               guardar (A, D) → intermediario I con sus montos
    
    2. Para cada par (origen, destino) con 2 o más intermediarios: es smurfing.
    
    Retorna: lista de dicts con este formato:
    {
        "origen": "ACC00945",
        "destino": "ACC00562",
        "intermediarios": [
            {"cuenta": "ACC00941", "monto_recibido": 16230.0, "monto_enviado": 14607.0, "ratio": 0.90},
            {"cuenta": "ACC00247", "monto_recibido": 44372.0, "monto_enviado": 39934.0, "ratio": 0.90},
        ],
        "total_recibido": 60602.0,
        "total_enviado": 54541.0,
    }
    """
```

---

## FASE 4 — `graph_renderer.py` ❌

**Archivo:** `src/algorithms/graph_renderer.py`

Dos funciones que retornan HTML como string para embeber en Streamlit.

```python
from pyvis.network import Network

def render_path(grafo, path_report):
    """
    Recibe el grafo completo y un path_report de build_path_report().
    Crea una red pyvis solo con los nodos y aristas del camino.
    Retorna el HTML como string.
    
    Colores: primer nodo = rojo, último = verde, intermedios = azul.
    Etiquetas en aristas: monto con formato "$12,345.00".
    """

def render_smurfing(patron):
    """
    Recibe un dict de detectar_smurfing().
    Crea una red pyvis con el patrón estrella:
      origen → intermediarios → destino
    Retorna el HTML como string.
    
    Colores: origen = rojo, destino = verde, intermediarios = naranja.
    """
```

**Notas de pyvis:**
```python
# Crear red
net = Network(height="420px", width="100%", directed=True, bgcolor="#ffffff")

# Agregar nodo con color
net.add_node("ACC001", label="ACC001", color="#e74c3c", title="Origen")

# Agregar arista con etiqueta
net.add_edge("ACC001", "ACC002", label="$12,345.00", title="$12,345.00")

# Retornar como HTML string (no genera archivo)
html = net.generate_html()
return html
```

---

## FASE 5 — `app.py` ❌

App Streamlit completa en **un solo archivo**. Sin directorios `ui/`.

### Estructura general

```python
import streamlit as st
import streamlit.components.v1 as components

# imports de src...

st.set_page_config(page_title="Análisis de Fraude Bancario", layout="wide")
st.title("🏦 Análisis de Fraude Bancario")

# --- Carga del grafo ---
# Opción A (simple para el TP): hardcodear la ruta al CSV
grafo = load_graph_from_csv("Transacciones.csv")

# O con file_uploader si se prefiere:
# archivo = st.sidebar.file_uploader("Subir CSV", type="csv")
# if archivo: grafo = load_graph_from_csv(archivo)

# --- Tabs principales ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Grafo",
    "🔗 Cadenas",
    "🔄 Ciclos",
    "🎯 Smurfing",
    "👤 Por cuenta"
])
```

### Tab 1 — Visión del grafo
```
- Mostrar get_graph_stats() con st.metric()
- Top senders y top receivers en st.dataframe()
```

### Tab 2 — Cadenas (consignas 1, 2, 3)
```
Sección A: Cadena más larga
  - Botón "Buscar"
  - Resultado: st.expander con steps en tabla + render_path() embebido

Sección B: Cadena sospechosa más larga
  - st.number_input: monto mínimo, transacciones mínimas
  - Botón "Buscar"
  - Resultado igual que sección A

Sección C: Todas las cadenas sospechosas
  - st.number_input: monto mínimo, min transacciones, max transacciones
  - Botón "Buscar"
  - Lista de st.expander, uno por cadena
```

### Tab 3 — Ciclos (consigna 4)
```
- Botón "Detectar ciclos"
- Lista de st.expander, uno por ciclo
- Si no hay: st.info("No se detectaron ciclos.")
```

### Tab 4 — Smurfing (consigna 5)
```
- Botón "Detectar smurfing"
- Para cada patrón: st.expander con tabla de intermediarios + render_smurfing()
```

### Tab 5 — Por cuenta (consignas 6 y 7)
```
- st.selectbox con lista de todos los nodos del grafo
- Sub-tabs: ["Cadenas sospechosas", "Ciclos"]
  - Cadenas: mismos parámetros que consigna 3, DFS desde la cuenta seleccionada
  - Ciclos: botón, lista de resultados
```

### Mostrar un resultado (helper interno)
```python
def mostrar_cadena(resultado):
    titulo = f"Cadena: {' → '.join(resultado['nodes'])} | {resultado['num_hops']} hops | ${resultado['total_amount']:,.2f}"
    with st.expander(titulo):
        # Tabla de pasos
        pasos = [{"De": p["from"], "A": p["to"], "Monto": f"${p['amount']:,.2f}"} for p in resultado["steps"]]
        st.table(pasos)
        # Visualización
        html = render_path(grafo, resultado)
        components.html(html, height=450)
```

---

## Checklist

- [x] FASE 0: Setup y config.py
- [x] FASE 1: graph_builder.py
- [x] FASE 2: dfs_core.py
- [x] FASE 3.1: chain_analysis.py (consignas 1, 2, 3, 6)
- [ ] **FASE 3.2: cycle_detection.py (consignas 4, 7)** ← siguiente
- [ ] FASE 3.3: smurfing.py (consigna 5)
- [ ] FASE 4: graph_renderer.py (visualización)
- [ ] FASE 5: app.py (Streamlit)

---

## Dataset — referencia rápida

| Columna | Tipo | Ejemplo |
|---|---|---|
| `Sender Account ID` | str | `ACC00945` |
| `Receiver Account ID` | str | `ACC00562` |
| `Transaction Amount` | float | `44372.0` |

- 500 transacciones, ~497 nodos
- Montos: entre ~1.797 y ~29.635.693
- El grafo tiene ciclos
- Hay nodos con out-degree 4–5 (candidatos a smurfing)

---

## Reglas clave

1. **DFS propio obligatorio**: no usar `nx.all_simple_paths()` ni funciones DFS de NetworkX.
2. **`dfs()` es la base de todo**: chain_analysis y cycle_detection lo llaman, nunca duplicar lógica de traversal.
3. **Smurfing no usa DFS**: es inspección directa de vecinos del grafo.
4. **Montos siempre float**: mostrar con `f"${monto:,.2f}"`.
5. **App en un solo archivo**: no separar la UI en múltiples módulos.
