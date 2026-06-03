# Prompt para GitHub Copilot Agent — Análisis de Fraude Bancario

> Pegar este prompt completo en el chat de Copilot Agent (modo "Agent" en VS Code).

---

## PROMPT (copiar desde acá)

---

Sos un desarrollador Python. Tu tarea es continuar implementando un sistema de análisis de fraude bancario. El proyecto ya tiene varias partes implementadas — leelas antes de escribir código nuevo.

---

### PASO 0 — Antes de escribir código, leer estos archivos

Leer en este orden:

1. `ROADMAP_fraude_bancario_v2.md` — el plan completo (qué está hecho, qué falta)
2. `src/algorithms/dfs_core.py` — el motor DFS ya implementado
3. `src/algorithms/chain_analysis.py` — ejemplo del estilo de código a seguir
4. `src/data/graph_builder.py` — para entender la estructura del grafo
5. `src/config.py` — constantes del proyecto

Una vez que leíste los cinco archivos, confirmame qué entendiste del proyecto y empezá con la FASE 3.2.

---

### CONTEXTO DEL PROYECTO

El sistema analiza una red de transacciones bancarias para detectar fraude. El grafo se construye así:
- Cada **cuenta bancaria** es un **nodo**
- Cada **transacción** es una **arista dirigida** (origen → destino) con peso = monto
- El archivo `Transacciones.csv` tiene las columnas `Sender Account ID`, `Receiver Account ID`, `Transaction Amount`

Los patrones de fraude a detectar son:
- **Layering**: cadenas largas de transferencias
- **Smurfing**: un origen envía a múltiples intermediarios que reenvían ≥80% al mismo destino
- **Ciclos**: el dinero vuelve al nodo de origen

---

### LO QUE YA ESTÁ IMPLEMENTADO ✅

- `src/config.py`: constantes (`COL_SENDER`, `COL_RECEIVER`, `COL_AMOUNT`, `SMURFING_THRESHOLD = 0.80`)
- `src/data/graph_builder.py`: `load_graph_from_csv()`, `graph_to_dict()`, `get_graph_stats()`
- `src/algorithms/dfs_core.py`: `dfs()`, `get_path_nodes()`, `get_path_total_amount()`, `build_path_report()`
- `src/algorithms/chain_analysis.py`: `buscar_cadena_mas_larga()`, `buscar_cadena_sospechosa_mas_larga()`, `buscar_todas_las_cadenas_sospechosas()`, `buscar_cadenas_sospechosas_desde_cuenta()`

---

### LO QUE HAY QUE IMPLEMENTAR ❌

En este orden exacto. No saltar fases.

---

### FASE 3.2 — `src/algorithms/cycle_detection.py`

Implementar dos funciones. Usá `dfs()` de `dfs_core.py` con `detect_cycles=True`.

```python
from src.algorithms.dfs_core import dfs, build_path_report

def detectar_ciclos(grafo):
    """
    Consigna 4: encuentra todos los ciclos del grafo.
    
    Para cada nodo del grafo:
        - corre dfs(grafo, nodo, detect_cycles=True)
        - por cada camino retornado, guardarlo si no está ya en la lista
    
    Deduplicación: dos ciclos son iguales si tienen el mismo frozenset de nodos.
    Ejemplo: A→B→C→A y B→C→A→B tienen los mismos nodos → es el mismo ciclo.
    
    Retorna: lista de build_path_report(camino) para cada ciclo único.
    Si no hay ciclos, retornar [].
    """

def detectar_ciclos_desde_cuenta(grafo, cuenta):
    """
    Consigna 7: ciclos donde `cuenta` es el nodo de inicio y fin.
    
    Corre dfs(grafo, cuenta, detect_cycles=True).
    Retorna lista de build_path_report(camino).
    Si no hay ciclos, retornar [].
    """
```

Después de implementar: probalo ejecutando:
```python
grafo = load_graph_from_csv("Transacciones.csv")
ciclos = detectar_ciclos(grafo)
print(f"Ciclos encontrados: {len(ciclos)}")
if ciclos:
    print(ciclos[0])
```
Confirmame cuántos ciclos encontró antes de continuar.

---

### FASE 3.3 — `src/algorithms/smurfing.py`

Implementar una función. **No usar DFS** — es inspección directa de vecinos del grafo.

```python
from src.config import SMURFING_THRESHOLD

def detectar_smurfing(grafo):
    """
    Consigna 5: detecta patrones Origen → [Inter_1..N] → Destino
    donde N >= 2 y cada intermediario reenvía >= 80% de lo recibido al mismo destino.
    
    Algoritmo (sin DFS, solo iteración sobre vecinos):
    
    1. Crear un diccionario `candidatos` donde:
       candidatos[(origen, destino)] = lista de intermediarios
    
    2. Para cada nodo A en el grafo:
         Para cada vecino I de A:
           monto_a_i = grafo[A][I]["amount"]
           Para cada vecino D de I:
             monto_i_d = grafo[I][D]["amount"]
             Si monto_i_d >= SMURFING_THRESHOLD * monto_a_i:
               agregar a candidatos[(A, D)] el dict:
               {"cuenta": I, "monto_recibido": monto_a_i, "monto_enviado": monto_i_d, "ratio": monto_i_d / monto_a_i}
    
    3. Filtrar: solo los pares (origen, destino) con 2 o más intermediarios.
    
    4. Para cada patrón válido, armar el dict de resultado:
    {
        "origen": str,
        "destino": str,
        "intermediarios": [{"cuenta": str, "monto_recibido": float, "monto_enviado": float, "ratio": float}],
        "total_recibido": float,   # suma de monto_recibido de todos los intermediarios
        "total_enviado": float,    # suma de monto_enviado de todos los intermediarios
    }
    
    Retornar la lista de todos los patrones detectados.
    """
```

Después de implementar: probalo ejecutando:
```python
grafo = load_graph_from_csv("Transacciones.csv")
patrones = detectar_smurfing(grafo)
print(f"Patrones de smurfing: {len(patrones)}")
if patrones:
    print(patrones[0])
```
Confirmame cuántos patrones encontró. En el dataset real hay al menos uno con origen ACC00945 y destino ACC00562.

---

### FASE 4 — `src/algorithms/graph_renderer.py`

Implementar dos funciones que retornan HTML como string (para embeber en Streamlit).

```python
from pyvis.network import Network

def render_path(grafo, path_report):
    """
    Visualiza un camino de transacciones como grafo interactivo.
    
    `path_report` es un dict de build_path_report() con keys: nodes, steps, total_amount, num_accounts, num_hops.
    
    Pasos:
    1. Crear Network(height="420px", width="100%", directed=True, bgcolor="#ffffff")
    2. Para cada nodo en path_report["nodes"]:
       - Si es el primero: color rojo (#e74c3c), title "Origen"
       - Si es el último: color verde (#2ecc71), title "Destino"
       - Si es intermedio: color azul claro (#3498db), title "Intermediario"
       net.add_node(nodo, label=nodo, color=color, title=title)
    3. Para cada step en path_report["steps"]:
       etiqueta = f"${step['amount']:,.0f}"
       net.add_edge(step["from"], step["to"], label=etiqueta, title=etiqueta)
    4. Retornar net.generate_html()
    """

def render_smurfing(patron):
    """
    Visualiza un patrón de smurfing como grafo interactivo.
    
    `patron` es un dict de detectar_smurfing() con keys: origen, destino, intermediarios.
    
    Pasos:
    1. Crear Network(height="420px", width="100%", directed=True, bgcolor="#ffffff")
    2. Agregar nodo origen (rojo), nodo destino (verde)
    3. Para cada intermediario en patron["intermediarios"]:
       - Agregar nodo con color naranja (#e67e22)
       - Agregar arista origen → intermediario con etiqueta monto_recibido
       - Agregar arista intermediario → destino con etiqueta monto_enviado y ratio
    4. Retornar net.generate_html()
    """
```

---

### FASE 5 — `app.py`

App Streamlit completa en **un solo archivo**. Simple y directa.

```python
import streamlit as st
import streamlit.components.v1 as components
from src.data.graph_builder import load_graph_from_csv, get_graph_stats
from src.algorithms.chain_analysis import (
    buscar_cadena_mas_larga,
    buscar_cadena_sospechosa_mas_larga,
    buscar_todas_las_cadenas_sospechosas,
    buscar_cadenas_sospechosas_desde_cuenta,
)
from src.algorithms.cycle_detection import detectar_ciclos, detectar_ciclos_desde_cuenta
from src.algorithms.smurfing import detectar_smurfing
from src.algorithms.graph_renderer import render_path, render_smurfing

st.set_page_config(page_title="Análisis de Fraude Bancario", layout="wide")
st.title("🏦 Análisis de Fraude Bancario")
st.caption("Taller de Programación III — UNAHUR")

# --- Carga del grafo ---
# Cargar con @st.cache_data para no releer el CSV cada vez que el usuario interactúa
@st.cache_data
def cargar_grafo():
    return load_graph_from_csv("Transacciones.csv")

grafo = cargar_grafo()

# --- Helper para mostrar un resultado de cadena ---
def mostrar_cadena(resultado, grafo):
    nodos_str = " → ".join(resultado["nodes"])
    titulo = f"{nodos_str[:80]}... | {resultado['num_hops']} hops | ${resultado['total_amount']:,.2f}"
    with st.expander(titulo):
        pasos = [{"De": p["from"], "A": p["to"], "Monto": f"${p['amount']:,.2f}"} for p in resultado["steps"]]
        st.table(pasos)
        html = render_path(grafo, resultado)
        components.html(html, height=450, scrolling=False)

# --- Tabs principales ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Grafo", "🔗 Cadenas", "🔄 Ciclos", "🎯 Smurfing", "👤 Por cuenta"])

# TAB 1: Estadísticas del grafo
with tab1:
    stats = get_graph_stats(grafo)
    col1, col2, col3 = st.columns(3)
    col1.metric("Nodos (cuentas)", stats["total_nodes"])
    col2.metric("Aristas (transacciones)", stats["total_edges"])
    col3.metric("Monto promedio", f"${stats['avg_amount']:,.2f}")
    # ... top senders y receivers en dataframes

# TAB 2: Cadenas (consignas 1, 2, 3)
with tab2:
    st.subheader("Cadena más larga")
    if st.button("Buscar cadena más larga"):
        resultado = buscar_cadena_mas_larga(grafo)
        if resultado:
            mostrar_cadena(resultado, grafo)
    
    st.divider()
    st.subheader("Cadena sospechosa más larga")
    # number_input para parámetros + botón + mostrar_cadena(...)
    
    st.divider()
    st.subheader("Todas las cadenas sospechosas")
    # number_input para los tres parámetros + botón + loop de mostrar_cadena(...)

# TAB 3: Ciclos (consigna 4)
with tab3:
    st.subheader("Ciclos en el grafo")
    if st.button("Detectar ciclos"):
        ciclos = detectar_ciclos(grafo)
        if ciclos:
            st.success(f"Se encontraron {len(ciclos)} ciclos.")
            for ciclo in ciclos:
                mostrar_cadena(ciclo, grafo)
        else:
            st.info("No se detectaron ciclos en el grafo.")

# TAB 4: Smurfing (consigna 5)
with tab4:
    st.subheader("Detección de Smurfing")
    st.caption(f"Umbral: el intermediario reenvía el {int(0.80 * 100)}% o más de lo recibido al destino.")
    if st.button("Detectar smurfing"):
        patrones = detectar_smurfing(grafo)
        if patrones:
            st.success(f"Se encontraron {len(patrones)} patrones de smurfing.")
            for patron in patrones:
                titulo = f"Origen: {patron['origen']} → Destino: {patron['destino']} | {len(patron['intermediarios'])} intermediarios"
                with st.expander(titulo):
                    filas = [{"Intermediario": i["cuenta"], "Recibido": f"${i['monto_recibido']:,.2f}", "Enviado": f"${i['monto_enviado']:,.2f}", "Ratio": f"{i['ratio']:.0%}"} for i in patron["intermediarios"]]
                    st.table(filas)
                    html = render_smurfing(patron)
                    components.html(html, height=450, scrolling=False)
        else:
            st.info("No se detectaron patrones de smurfing.")

# TAB 5: Por cuenta (consignas 6 y 7)
with tab5:
    st.subheader("Análisis por cuenta")
    nodos = sorted(grafo.nodes())
    cuenta = st.selectbox("Seleccionar cuenta", nodos)
    
    sub1, sub2 = st.tabs(["Cadenas sospechosas", "Ciclos"])
    
    with sub1:
        # number_input para parámetros + botón + loop de mostrar_cadena(...)
        pass
    
    with sub2:
        if st.button("Detectar ciclos desde esta cuenta"):
            ciclos = detectar_ciclos_desde_cuenta(grafo, cuenta)
            # mostrar resultados...
```

Implementá la app completa, rellenando los `# ...` con el código correspondiente siguiendo el mismo patrón de cada sección.

---

### REGLAS DE IMPLEMENTACIÓN

1. **Código simple**: sin type hints complejos, sin generadores, sin abstracciones innecesarias. Estilo similar al código de clase (bucles `for/while` directos, listas y diccionarios simples).
2. **No usar `nx.all_simple_paths()`** — el DFS es propio y ya está en `dfs_core.py`.
3. **No duplicar lógica de DFS** — cycle_detection importa `dfs` de `dfs_core.py`.
4. **Smurfing sin DFS** — es solo iteración sobre `grafo.successors()` y `grafo[A][B]["amount"]`.
5. **Montos siempre float**: mostrar como `f"${monto:,.2f}"`.
6. **Un archivo por fase**: no crear archivos extra que no estén en el roadmap.

---

### ORDEN DE TRABAJO

1. Leé los cinco archivos del PASO 0.
2. Implementá FASE 3.2 (`cycle_detection.py`) completa.
3. Probá con el CSV y confirmame cuántos ciclos encontró.
4. Implementá FASE 3.3 (`smurfing.py`) completa.
5. Probá y confirmame cuántos patrones encontró.
6. Implementá FASE 4 (`graph_renderer.py`).
7. Implementá FASE 5 (`app.py`) completa.
8. Confirmá que `streamlit run app.py` corre sin errores.

Empezá ahora con la FASE 3.2.
