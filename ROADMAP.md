# Roadmap — Análisis de Fraude Bancario

### Taller de Programación III — UNAHUR

> Estado del proyecto al 2026-07-06. Contiene auditoría completa del código,
> mapeo de consignas, mejoras pendientes y plan de implementación del reporte PDF.

---

## Estructura actual del proyecto

```
fraude/
├── app.py                              # ✅ Streamlit UI — archivo único
├── requirements.txt                    # ✅ Dependencias (incluye fpdf2)
├── Transacciones.csv                   # Dataset de 500 transacciones
├── ROADMAP.md                          # ← este archivo
├── copilot/                            # Prompts y roadmaps previos (referencia)
│   ├── COPILOT_PROMPT_v2.md
│   └── ROADMAP_fraude_bancario_v2.md
├── src/
│   ├── __init__.py
│   ├── config.py                       # ✅ Constantes globales
│   ├── data/
│   │   ├── __init__.py
│   │   └── graph_builder.py            # ✅ CSV → DiGraph + estadísticas
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── dfs_core.py                 # ✅ Motor DFS con pila explícita
│   │   ├── chain_analysis.py           # ✅ Consignas 1, 2, 3, 6
│   │   ├── cycle_detection.py          # ✅ Consignas 4, 7
│   │   ├── smurfing.py                 # ✅ Consigna 5
│   │   └── graph_renderer.py           # ✅ Visualización pyvis (HTML)
│   └── reports/                        # ✅ Reportes exportables
│       ├── __init__.py
│       └── pdf_report.py               # ✅ Generador de PDF con fpdf2
```

---

## Auditoría de archivos y funciones

### `src/config.py` — Constantes globales

| Constante                  | Valor                       | Uso                                    |
|----------------------------|-----------------------------|----------------------------------------|
| `COL_SENDER`               | `"Sender Account ID"`      | Nombre de columna del CSV              |
| `COL_RECEIVER`             | `"Receiver Account ID"`    | Nombre de columna del CSV              |
| `COL_AMOUNT`               | `"Transaction Amount"`     | Nombre de columna del CSV              |
| `DEFAULT_MIN_AMOUNT`       | `10_000`                   | Monto mínimo por defecto               |
| `DEFAULT_MIN_TRANSACTIONS` | `3`                        | Transacciones mínimas por defecto      |
| `DEFAULT_MAX_TRANSACTIONS` | `10`                       | Transacciones máximas por defecto      |
| `SMURFING_THRESHOLD`       | `0.80`                     | Umbral de reenvío para smurfing (80%)  |

---

### `src/data/graph_builder.py` — Construcción del grafo

| Función                          | Retorna         | Responsabilidad                                                                 |
|----------------------------------|-----------------|---------------------------------------------------------------------------------|
| `create_graph_dict_from_csv(fp)` | `dict`          | Lee CSV con pandas, agrega montos si A→B se repite, retorna dict de adyacencia. |
| `load_graph_from_csv(fp)`        | `nx.DiGraph`    | Llama a `create_graph_dict_from_csv` y construye el DiGraph de NetworkX.        |
| `graph_to_dict(graph)`           | `dict`          | Convierte un DiGraph de vuelta a dict de adyacencia (utilidad inversa).         |
| `_top_accounts_by_degree(...)`   | `list[tuple]`   | Helper interno: ordena cuentas por grado (out/in) descendente, top N.           |
| `get_graph_stats(graph)`         | `dict`          | Métricas: total_nodes, total_edges, avg/max/min_amount, top senders/receivers.  |

---

### `src/algorithms/dfs_core.py` — Motor DFS (pila explícita)

| Función                       | Retorna       | Responsabilidad                                                                        |
|-------------------------------|---------------|----------------------------------------------------------------------------------------|
| `dfs(graph, start, ...)`      | `list[list]`  | DFS iterativo con pila. Soporta `edge_filter`, `max_depth`, `detect_cycles`. Retorna todos los caminos encontrados. Cada camino es una lista de tuplas `(origen, destino, monto)`. |
| `get_path_nodes(path)`        | `list[str]`   | Extrae nodos únicos en orden de aparición a partir de un camino.                       |
| `get_path_total_amount(path)` | `float`       | Suma los montos de todas las aristas de un camino.                                     |
| `build_path_report(path)`     | `dict`        | Genera reporte estándar: `nodes`, `steps`, `total_amount`, `num_accounts`, `num_hops`. |

---

### `src/algorithms/chain_analysis.py` — Cadenas (Consignas 1, 2, 3, 6)

| Función                                          | Consigna | Responsabilidad                                                                |
|--------------------------------------------------|----------|--------------------------------------------------------------------------------|
| `_camino_es_mejor(candidato, mejor_actual)`      | —        | Helper: compara dos caminos por cantidad de hops y, en empate, por monto.      |
| `_filtro_monto_minimo(monto_minimo)`              | —        | Helper: retorna función filtro `(origen, destino, monto) → bool`.              |
| `_deduplicar_y_ordenar(caminos)`                  | —        | Helper: deduplica por `frozenset` de tuplas, ordena por hops+monto desc.       |
| `buscar_cadena_mas_larga(grafo)`                  | 1        | DFS desde cada nodo, retorna la cadena con más hops.                           |
| `buscar_cadena_sospechosa_mas_larga(grafo, ...)`  | 2        | DFS con filtro de monto + mínimo de hops. Retorna la más larga.               |
| `buscar_todas_las_cadenas_sospechosas(grafo, ...)` | 3       | DFS desde cada nodo con filtro. Retorna todas las que cumplen rango de hops.  |
| `buscar_cadenas_sospechosas_desde_cuenta(grafo, cuenta, ...)` | 6 | Igual que consigna 3 pero solo DFS desde una cuenta específica.            |

---

### `src/algorithms/cycle_detection.py` — Ciclos (Consignas 4, 7)

| Función                                      | Consigna | Responsabilidad                                                           |
|----------------------------------------------|----------|---------------------------------------------------------------------------|
| `_es_ciclo_cerrado(camino, nodo_inicio)`     | —        | Helper: verifica si el último destino del camino coincide con el inicio.  |
| `detectar_ciclos(grafo)`                     | 4        | DFS con `detect_cycles=True` desde cada nodo. Deduplica por `frozenset`. |
| `detectar_ciclos_desde_cuenta(grafo, cuenta)` | 7       | DFS con `detect_cycles=True` solo desde una cuenta específica.            |
| `find_all_cycles(graph)`                     | —        | Alias en inglés de `detectar_ciclos`.                                     |
| `find_cycles_from_account(graph, account)`   | —        | Alias en inglés de `detectar_ciclos_desde_cuenta`.                        |

---

### `src/algorithms/smurfing.py` — Smurfing (Consigna 5)

| Función                    | Consigna | Responsabilidad                                                                               |
|----------------------------|----------|-----------------------------------------------------------------------------------------------|
| `detectar_smurfing(grafo)` | 5        | Inspección directa de vecinos (sin DFS). Para cada tripleta A→I→D verifica si el ratio de reenvío ≥ 80%. Agrupa por par (origen, destino) y filtra los que tienen ≥ 2 intermediarios. |

---

### `src/algorithms/graph_renderer.py` — Visualización (Extra opcional ✅)

| Función                        | Responsabilidad                                                                  |
|--------------------------------|----------------------------------------------------------------------------------|
| `_formatear_monto(monto)`     | Helper: formatea float como `"$12,345.00"`.                                      |
| `render_path(grafo, report)`  | Genera HTML interactivo con pyvis para un camino (rojo → azul → verde).          |
| `render_smurfing(patron)`     | Genera HTML interactivo con pyvis para un patrón smurfing (rojo → naranja → verde). |

---

### `app.py` — Interfaz Streamlit (Consignas 1-7 + extras)

| Sección / Función                 | Responsabilidad                                                              |
|-----------------------------------|------------------------------------------------------------------------------|
| `cargar_grafo_desde_path(path)`   | Cachea la carga del grafo desde ruta en disco.                               |
| `cargar_grafo_desde_bytes(bytes)` | Cachea la carga del grafo desde archivo subido por file_uploader.            |
| `mostrar_cadena(resultado, grafo)`| Helper: expander con tabla de pasos + render_path embebido.                  |
| `mostrar_ciclo(resultado, grafo)` | Helper: igual que mostrar_cadena pero con prefijo "Ciclo:" en el título.     |
| **Tab 1 — Grafo**                | Muestra métricas (nodos, aristas, monto promedio) + top senders/receivers.   |
| **Tab 2 — Cadenas**              | Consignas 1, 2, 3 con botones y parámetros ajustables.                      |
| **Tab 3 — Ciclos**               | Consigna 4 con botón de detección.                                           |
| **Tab 4 — Smurfing**             | Consigna 5 con botón de detección.                                           |
| **Tab 5 — Por cuenta**           | Consignas 6 y 7 con selectbox de cuenta + sub-tabs.                          |

---

### Directorios vacíos (sin uso actual)

| Directorio          | Estado   | Notas                                                          |
|---------------------|----------|----------------------------------------------------------------|
| `src/reports/`      | ❌ Vacío | Solo `__init__.py`. Destinado a la generación de reportes PDF. |
| `src/visualization/`| ❌ Vacío | Solo `__init__.py`. No se usa; la lógica de visualización está en `graph_renderer.py`. |
| `ui/`               | ❌ Vacío | Solo `__init__.py` + `components/`. No se usa; la UI está en `app.py` como archivo único. |

---

## Mapeo de consignas del TP

| # | Consigna                              | Archivo                  | Estado | Notas                                          |
|---|---------------------------------------|--------------------------|--------|-------------------------------------------------|
| 1 | Cadena más larga                      | `chain_analysis.py`      | ✅     | `buscar_cadena_mas_larga()`                     |
| 2 | Cadena sospechosa más larga           | `chain_analysis.py`      | ✅     | `buscar_cadena_sospechosa_mas_larga()`          |
| 3 | Todas las cadenas sospechosas         | `chain_analysis.py`      | ✅     | `buscar_todas_las_cadenas_sospechosas()`        |
| 4 | Cadenas cíclicas (todos los ciclos)   | `cycle_detection.py`     | ✅     | `detectar_ciclos()`                             |
| 5 | Detección de Smurfing                 | `smurfing.py`            | ✅     | `detectar_smurfing()`                           |
| 6 | Cadenas sospechosas desde una cuenta  | `chain_analysis.py`      | ✅     | `buscar_cadenas_sospechosas_desde_cuenta()`     |
| 7 | Cadenas cíclicas desde una cuenta     | `cycle_detection.py`     | ✅     | `detectar_ciclos_desde_cuenta()`                |

### Extras opcionales del TP

| Extra                                            | Estado    | Notas                                          |
|--------------------------------------------------|-----------|-------------------------------------------------|
| Visualizaciones interactivas con colores         | ✅ Hecho  | `graph_renderer.py` con pyvis (rojo/azul/verde/naranja) |
| Exportar rutas sospechosas a CSV o Excel         | ❌ Pendiente| Se puede agregar con `pandas.to_csv()`        |
| Reporte automático PDF con FPDF                  | ✅ Hecho  | `src/reports/pdf_report.py` con `fpdf2` integrado en `app.py` |

---

## Observaciones y mejoras detectadas

### Código funcional — issues menores (✅ Todas resueltas)

1. **`mostrar_cadena` y `mostrar_ciclo` unificadas**: se unificaron en `mostrar_resultado`.
2. **Directorios vacíos**: `ui/` y `src/visualization/` fueron eliminados.
3. **Renderizado masivo corregido**: se limitó a 20 resultados en la UI.
4. **Implementación de fpdf2**: se agregó la generación de reportes en `src/reports/pdf_report.py`.
5. **Typo corregido**: en `graph_builder.py`.

---

## Plan de implementación — Fases paso a paso

---

### FASE 1 — Configuración y grafo ✅ COMPLETA

- [x] `src/config.py` — constantes del proyecto
- [x] `src/data/graph_builder.py` — carga de CSV, construcción de DiGraph, estadísticas
- [x] `requirements.txt` — dependencias

---

### FASE 2 — Motor DFS ✅ COMPLETA

- [x] `src/algorithms/dfs_core.py` — DFS iterativo con pila explícita
- [x] Soporte para `edge_filter`, `max_depth`, `detect_cycles`
- [x] Funciones de utilidad: `get_path_nodes`, `get_path_total_amount`, `build_path_report`

---

### FASE 3.1 — Cadenas (Consignas 1, 2, 3, 6) ✅ COMPLETA

- [x] `buscar_cadena_mas_larga()` — Consigna 1
- [x] `buscar_cadena_sospechosa_mas_larga()` — Consigna 2
- [x] `buscar_todas_las_cadenas_sospechosas()` — Consigna 3
- [x] `buscar_cadenas_sospechosas_desde_cuenta()` — Consigna 6

---

### FASE 3.2 — Ciclos (Consignas 4, 7) ✅ COMPLETA

- [x] `detectar_ciclos()` — Consigna 4
- [x] `detectar_ciclos_desde_cuenta()` — Consigna 7
- [x] Deduplicación por `frozenset` de nodos

---

### FASE 3.3 — Smurfing (Consigna 5) ✅ COMPLETA

- [x] `detectar_smurfing()` — sin DFS, inspección directa de vecinos
- [x] Filtro por `SMURFING_THRESHOLD` (80%)
- [x] Agrupación por par (origen, destino), filtro ≥ 2 intermediarios

---

### FASE 4 — Visualización interactiva (Extra ✅) ✅ COMPLETA

- [x] `render_path()` — caminos y ciclos con pyvis
- [x] `render_smurfing()` — patrón estrella con pyvis
- [x] Colores por tipo de nodo (rojo/azul/verde/naranja)

---

### FASE 5 — App Streamlit ✅ COMPLETA

- [x] Archivo único `app.py`
- [x] 5 tabs: Grafo, Cadenas, Ciclos, Smurfing, Por cuenta
- [x] Carga por file_uploader o ruta hardcodeada
- [x] Visualizaciones pyvis embebidas con `components.html()`
- [x] Límite de renderizado (top 20 resultados)

---

### FASE 6 — Reporte PDF con FPDF ✅ COMPLETA

**Objetivo**: agregar un botón "📄 Generar Reporte PDF" en la UI de Streamlit que genere un PDF completo con los resultados del análisis y lo descargue directamente al navegador.

Implementado en `src/reports/pdf_report.py` e integrado en la barra lateral de `app.py`.

---

### FASE 7 — Exportar a CSV (Extra opcional) ❌ PENDIENTE

**Objetivo**: agregar botones de exportación a CSV en cada tab de resultados.

Baja prioridad — se puede implementar con `pandas.DataFrame.to_csv()` + `st.download_button()`.

---

### FASE 8 — Limpieza de proyecto ✅ COMPLETA

- [x] Eliminar directorios vacíos sin uso: `src/visualization/`, `ui/`
- [x] Unificar `mostrar_cadena()` y `mostrar_ciclo()` en una sola función
- [x] Corregir typo en comentario de `graph_builder.py` ("Gneramos" → "Generamos")
- [x] Actualizar el roadmap viejo en `copilot/` marcando todo como completado

---

## Checklist general

- [x] FASE 1: Configuración y grafo
- [x] FASE 2: Motor DFS
- [x] FASE 3.1: Cadenas (consignas 1, 2, 3, 6)
- [x] FASE 3.2: Ciclos (consignas 4, 7)
- [x] FASE 3.3: Smurfing (consigna 5)
- [x] FASE 4: Visualización interactiva (extra)
- [x] FASE 5: App Streamlit
- [x] **FASE 6: Reporte PDF con FPDF** 
- [ ] FASE 7: Exportar a CSV (extra opcional)
- [x] FASE 8: Limpieza de proyecto

---

## Dataset — referencia rápida

| Columna                | Tipo    | Ejemplo      |
|------------------------|---------|--------------|
| `Sender Account ID`   | `str`   | `ACC00945`   |
| `Receiver Account ID` | `str`   | `ACC00562`   |
| `Transaction Amount`  | `float` | `44372.0`    |

- 500 transacciones, ~497 nodos
- Montos: entre ~1.797 y ~29.635.693
- El grafo tiene ciclos
- Hay nodos con out-degree 4-5 (candidatos a smurfing)

---

## Reglas clave del proyecto

1. **DFS propio obligatorio**: no usar `nx.all_simple_paths()` ni funciones DFS de NetworkX.
2. **`dfs()` es la base de todo**: chain_analysis y cycle_detection lo importan, nunca duplicar lógica.
3. **Smurfing no usa DFS**: es inspección directa de vecinos del grafo.
4. **Montos siempre float**: mostrar con `f"${monto:,.2f}"`.
5. **App en un solo archivo**: no separar la UI en múltiples módulos.
6. **Código simple**: estilo de clase, sin abstracciones innecesarias.
