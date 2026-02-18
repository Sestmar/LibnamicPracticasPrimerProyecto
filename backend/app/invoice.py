import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT


def generate_invoice_pdf(order, user) -> bytes:
    """
    Genera una factura en formato PDF a partir de los datos del pedido y del usuario.
    Devuelve los bytes del PDF listo para enviar como respuesta HTTP.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle('InvoiceTitle', parent=styles['Title'], fontSize=22, textColor=colors.HexColor('#2c3e50'))
    company_style = ParagraphStyle('Company', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#7f8c8d'))
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#2c3e50'), spaceAfter=8)
    normal_style = styles['Normal']
    right_style = ParagraphStyle('Right', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=10)
    
    elements = []
    
    # --- Cabecera ---
    invoice_number = f"INV-{order.id:05d}"
    date_str = order.created_at.strftime('%d/%m/%Y') if order.created_at else datetime.utcnow().strftime('%d/%m/%Y')
    
    header_data = [
        [
            Paragraph("FACTURA", title_style),
            Paragraph(f"<b>Nº:</b> {invoice_number}<br/><b>Fecha:</b> {date_str}<br/><b>Estado:</b> {order.status}", right_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[300, 200])
    header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(header_table)
    
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph("LibnamicShop — Sistema de Gestión de Inventario", company_style))
    elements.append(Spacer(1, 8*mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    elements.append(Spacer(1, 6*mm))
    
    # --- Datos del Cliente ---
    elements.append(Paragraph("Datos del Cliente", section_style))
    
    client_name = f"{user.first_name} {user.last_name}"
    client_info = f"<b>Nombre:</b> {client_name}<br/><b>Email:</b> {user.email}"
    if user.phone:
        client_info += f"<br/><b>Teléfono:</b> {user.phone}"
    
    elements.append(Paragraph(client_info, normal_style))
    elements.append(Spacer(1, 8*mm))
    
    # --- Tabla de Productos ---
    elements.append(Paragraph("Detalle del Pedido", section_style))
    
    # Cabecera de la tabla
    table_data = [['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]
    
    for item in order.items:
        product_name = item.product.name if item.product else f"Producto #{item.product_id}"
        subtotal = item.unit_price * item.quantity
        table_data.append([
            product_name,
            str(item.quantity),
            f"{item.unit_price:.2f} €",
            f"{subtotal:.2f} €"
        ])
    
    # Fila del total
    table_data.append(['', '', Paragraph('<b>TOTAL</b>', right_style), Paragraph(f"<b>{order.total_price:.2f} €</b>", normal_style)])
    
    product_table = Table(table_data, colWidths=[220, 80, 100, 100])
    product_table.setStyle(TableStyle([
        # Cabecera
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        # Filas
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        # Fila total
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#2c3e50')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        # Bordes generales
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    
    elements.append(product_table)
    elements.append(Spacer(1, 15*mm))
    
    # --- Pie de factura ---
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#a0aec0'), alignment=TA_CENTER)
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("LibnamicShop — Documento generado automáticamente. No constituye factura fiscal.", footer_style))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
