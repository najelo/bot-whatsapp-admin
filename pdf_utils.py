import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def exportar_logs_a_pdf(logs):
    """Genera un archivo PDF binario en memoria listo para descargar."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor("#1e293b"), spaceAfter=10)
    subtitle_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#64748b"), spaceAfter=20)
    
    # Encabezado del PDF
    story.append(Paragraph("📋 Reporte de Logs de Transacciones", title_style))
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Admin Bot Panel", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Encabezados de la tabla
    table_data = [["Fecha / Hora", "Teléfono Cliente", "Monto", "Estado"]]
    
    for l in logs:
        fecha_clean = l['created_at'].replace("T", " ")[:19]
        monto_str = f"Bs. {float(l['monto']):,.2f}"
        estado_str = l['estado'].upper()
        table_data.append([fecha_clean, f"+{l['phone']}", monto_str, estado_str])
    
    # Diseño estético de la tabla
    tabla_pdf = Table(table_data, colWidths=[140, 130, 110, 100])
    tabla_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(tabla_pdf)
    doc.build(story)
    buffer.seek(0)
    return buffer
