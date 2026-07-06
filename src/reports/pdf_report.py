from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Reporte de Analisis de Fraude Bancario', border=False, align='C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def format_nodes(nodes):
    s = " -> ".join(nodes)
    if len(s) > 80:
        return s[:77] + "..."
    return s

def trunc(text, max_len=110):
    return text[:max_len-3] + "..." if len(text) > max_len else text

def generar_reporte_pdf(stats, cadena_mas_larga, cadena_sospechosa, 
                         todas_las_cadenas, ciclos, patrones_smurfing) -> bytes:
    """
    Genera un PDF completo con todos los resultados del analisis.
    """
    pdf = PDFReport()
    pdf.add_page()
    
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, f'Fecha de generacion: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
    pdf.ln(10)
    
    # Resumen
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Resumen del Grafo', ln=True)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, f'Nodos (cuentas): {stats["total_nodes"]}', ln=True)
    pdf.cell(0, 10, f'Aristas (transacciones): {stats["total_edges"]}', ln=True)
    pdf.cell(0, 10, f'Monto promedio: ${stats["avg_amount"]:,.2f}', ln=True)
    pdf.ln(10)

    # 1. Cadena mas larga
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '1. Cadena mas larga', ln=True)
    pdf.set_font('Helvetica', '', 10)
    if cadena_mas_larga:
        texto_ruta = f'Ruta: {format_nodes(cadena_mas_larga["nodes"])}'
        pdf.cell(0, 10, trunc(texto_ruta), ln=True)
        pdf.cell(0, 10, f'Total transacciones: {cadena_mas_larga["num_hops"]} | Monto total: ${cadena_mas_larga["total_amount"]:,.2f}', ln=True)
    else:
        pdf.cell(0, 10, 'No se encontro cadena mas larga.', ln=True)
    pdf.ln(5)

    # 2. Cadena sospechosa mas larga
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '2. Cadena sospechosa mas larga', ln=True)
    pdf.set_font('Helvetica', '', 10)
    if cadena_sospechosa:
        texto_ruta = f'Ruta: {format_nodes(cadena_sospechosa["nodes"])}'
        pdf.cell(0, 10, trunc(texto_ruta), ln=True)
        pdf.cell(0, 10, f'Total transacciones: {cadena_sospechosa["num_hops"]} | Monto total: ${cadena_sospechosa["total_amount"]:,.2f}', ln=True)
    else:
        pdf.cell(0, 10, 'No se encontraron cadenas sospechosas.', ln=True)
    pdf.ln(5)

    # 3. Cadenas sospechosas (Top 20)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '3. Todas las cadenas sospechosas (Top 20)', ln=True)
    pdf.set_font('Helvetica', '', 10)
    if todas_las_cadenas:
        pdf.cell(0, 10, f'Total encontradas: {len(todas_las_cadenas)}', ln=True)
        for i, cadena in enumerate(todas_las_cadenas[:20], 1):
            texto = f'{i}. {format_nodes(cadena["nodes"])} (${cadena["total_amount"]:,.2f} en {cadena["num_hops"]} pasos)'
            pdf.cell(0, 8, trunc(texto), ln=True)
    else:
        pdf.cell(0, 10, 'No se encontraron cadenas sospechosas.', ln=True)
    pdf.ln(5)

    # 4. Ciclos (Top 20)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '4. Ciclos detectados (Top 20)', ln=True)
    pdf.set_font('Helvetica', '', 10)
    if ciclos:
        pdf.cell(0, 10, f'Total encontrados: {len(ciclos)}', ln=True)
        for i, ciclo in enumerate(ciclos[:20], 1):
            texto = f'{i}. {format_nodes(ciclo["nodes"])} (${ciclo["total_amount"]:,.2f} en {ciclo["num_hops"]} pasos)'
            pdf.cell(0, 8, trunc(texto), ln=True)
    else:
        pdf.cell(0, 10, 'No se encontraron ciclos.', ln=True)
    pdf.ln(5)

    # 5. Smurfing (Top 20)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '5. Patrones de Smurfing (Top 20)', ln=True)
    pdf.set_font('Helvetica', '', 10)
    if patrones_smurfing:
        pdf.cell(0, 10, f'Total encontrados: {len(patrones_smurfing)}', ln=True)
        for i, patron in enumerate(patrones_smurfing[:20], 1):
            texto = f'{i}. Origen: {patron["origen"]} -> Destino: {patron["destino"]} (Intermediarios: {len(patron["intermediarios"])}, Total enviado: ${patron["total_enviado"]:,.2f})'
            pdf.cell(0, 8, trunc(texto), ln=True)
    else:
        pdf.cell(0, 10, 'No se detectaron patrones de smurfing.', ln=True)

    return bytes(pdf.output())
