from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from Pedidos.models import Pedido
import os
import locale

try:
    locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        pass

'''
-------------------------------------------------
Funcion que genera archivos PDF en base a uno o
varios pedidos usando xhtml2pdf
-------------------------------------------------
'''

def pdf_un_pedido(request, pedido_id):
    pedido = Pedido.objects.prefetch_related('producto_set').get(id=pedido_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="orden_compra_{pedido.cod_orden_compra}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2.5*cm,
        leftMargin=2.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    DOC_WIDTH = doc.width

    # Colores
    COLOR_PRIMARIO = colors.HexColor("#34495e")
    COLOR_FONDO_TABLA = colors.HexColor("#ecf0f1")
    COLOR_TITULO_TABLA = colors.HexColor("#bdc3c7")

    # Estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TituloPrincipal", fontSize=18, leading=22,
        alignment=TA_LEFT, fontName='Helvetica-Bold',
        textColor=COLOR_PRIMARIO, spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name="Subtitulo", fontSize=12, leading=14,
        alignment=TA_LEFT, fontName='Helvetica-Bold',
        textColor=COLOR_PRIMARIO, spaceAfter=6
    ))
    styles["Normal"].fontSize = 10
    styles["Normal"].fontName = 'Helvetica'
    styles.add(ParagraphStyle(name="Left", fontSize=10, alignment=TA_LEFT, fontName='Helvetica'))
    styles.add(ParagraphStyle(name="Right", fontSize=10, alignment=TA_RIGHT, fontName='Helvetica'))
    styles.add(ParagraphStyle(name="Center", fontSize=10, alignment=TA_CENTER, fontName='Helvetica'))
    styles.add(ParagraphStyle(name="NormalBold", fontSize=10, fontName='Helvetica-Bold', textColor=COLOR_PRIMARIO))
    styles.add(ParagraphStyle(name="Footer", fontSize=8, alignment=TA_CENTER, fontName='Helvetica-Oblique', textColor=colors.grey))

    contenido = []

    # Línea horizontal
    class Line(Flowable):
        def __init__(self, width, thickness, color):
            super().__init__()
            self.width = width
            self.thickness = thickness
            self.color = color
        def draw(self):
            self.canv.setStrokeColor(self.color)
            self.canv.setLineWidth(self.thickness)
            self.canv.line(0, 0, self.width, 0)

    # Función para formato de moneda
    def format_currency(amount):
        try:
            return locale.currency(amount, grouping=True)
        except:
            return f"${amount:,.2f}"

    # --- Encabezado empresa ---
    direccion_cliente = pedido.cliente.direccioncliente_set.first()
    direccion_texto = (
        f"{direccion_cliente.calle} {direccion_cliente.numero}, {direccion_cliente.comuna}, {direccion_cliente.ciudad}"
        if direccion_cliente else "Dirección no registrada"
    )

    logo_path = os.path.join("static", "images", "logo azul.png")
    logo_width = 3.5*cm
    logo_height = 1.75*cm

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=logo_width, height=logo_height)
    else:
        logo = Paragraph("<b>[ LOGO EMPRESA ]</b>", styles["NormalBold"])

    datos_empresa_parrafos = [
        Paragraph("SIM CONVERTIDORA", styles["Subtitulo"]),
        Paragraph("Bolsas personalizadas", styles["Normal"]),
        Paragraph("Av. Dirección Test, Santiago", styles["Normal"]),
        Paragraph("Tel: +56 2 2222 3333", styles["Normal"]),
    ]
    datos_empresa_cell = [datos_empresa_parrafos]

    tabla_encabezado = Table(
        [[logo, datos_empresa_cell]],
        colWidths=[logo_width + 1*cm, DOC_WIDTH - logo_width - 1*cm],
        hAlign='LEFT'
    )
    tabla_encabezado.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    contenido.append(tabla_encabezado)
    contenido.append(Spacer(1, 10))
    contenido.append(Line(DOC_WIDTH, 2, COLOR_PRIMARIO))
    contenido.append(Spacer(1, 15))

    # --- Título de la orden ---
    contenido.append(Paragraph(f"ORDEN DE COMPRA N° {pedido.cod_orden_compra}", styles["TituloPrincipal"]))
    contenido.append(Spacer(1, 10))

    # --- Información del pedido ---
    contenido.append(Paragraph("Información del Pedido", styles["Subtitulo"]))
    fecha_formateada = pedido.fecha_pedido.strftime("%d/%m/%Y")
    datos = [
        [Paragraph("<b>Cliente:</b>", styles["NormalBold"]), Paragraph(pedido.cliente.razon_social_cliente, styles["Normal"])],
        [Paragraph("<b>RUT:</b>", styles["NormalBold"]), Paragraph(getattr(pedido.cliente, 'rut_cliente', 'N/A'), styles["Normal"])],
        [Paragraph("<b>Dirección:</b>", styles["NormalBold"]), Paragraph(direccion_texto, styles["Normal"])],
        [Paragraph("<b>Fecha Pedido:</b>", styles["NormalBold"]), Paragraph(fecha_formateada, styles["Normal"])],
    ]
    tabla_datos = Table(datos, colWidths=[3.5*cm, DOC_WIDTH - 3.5*cm - 0.5*cm], hAlign='LEFT')
    tabla_datos.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
        ('BACKGROUND', (0,0), (0,-1), COLOR_FONDO_TABLA),
    ]))
    contenido.append(tabla_datos)
    contenido.append(Spacer(1, 20))

    # --- Tabla de productos ---
    contenido.append(Paragraph("Detalle de Productos Solicitados", styles["Subtitulo"]))
    encabezado = [
        Paragraph("<b>Nombre</b>", styles["Center"]),
        Paragraph("<b>Tipo</b>", styles["Center"]),
        Paragraph("<b>Tamaño</b>", styles["Center"]),
        Paragraph("<b>Observación</b>", styles["Center"]),
        Paragraph("<b>Cantidad</b>", styles["Center"]),
        Paragraph("<b>Precio Unitario</b>", styles["Center"]),
        Paragraph("<b>Subtotal</b>", styles["Center"]),
    ]
    filas = []
    for p in pedido.producto_set.all():
        filas.append([
            Paragraph(p.nombre_producto, styles["Left"]),
            Paragraph(p.tipo_producto, styles["Left"]),
            Paragraph(p.tamano_producto, styles["Left"]),
            Paragraph(p.observacion_producto or "-", styles["Left"]),
            Paragraph(str(p.cantidad_producto), styles["Right"]),
            Paragraph(format_currency(p.precio_unitario_producto), styles["Right"]),
            Paragraph(format_currency(p.cantidad_producto * p.precio_unitario_producto), styles["Right"]),
        ])
    col_widths_productos = [
        DOC_WIDTH*0.18, DOC_WIDTH*0.15, DOC_WIDTH*0.12, DOC_WIDTH*0.17,
        DOC_WIDTH*0.13, DOC_WIDTH*0.15, DOC_WIDTH*0.20
    ]
    tabla_productos = Table([encabezado] + filas, colWidths=col_widths_productos, repeatRows=1)
    tabla_productos.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), COLOR_TITULO_TABLA),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    contenido.append(tabla_productos)
    contenido.append(Spacer(1, 20))

    # --- Totales ---
    totales_data = [
        [Paragraph("Neto:", styles["Right"]), Paragraph(format_currency(pedido.total_neto_pedido), styles["Right"])],
        [Paragraph(f"IVA ({pedido.iva_pedido * 100:.0f}%):", styles["Right"]), Paragraph(format_currency(pedido.total_pedido - pedido.total_neto_pedido), styles["Right"])],
        [Paragraph("<b>TOTAL:</b>", styles["Right"]), Paragraph(format_currency(pedido.total_pedido), styles["Right"])],
    ]

    col_widths_totales = [DOC_WIDTH * 0.25, DOC_WIDTH * 0.3]
    tabla_totales = Table(totales_data, colWidths=col_widths_totales, hAlign='RIGHT')
    tabla_totales.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-2), 'Helvetica'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('BACKGROUND', (0,0), (-1,-2), COLOR_FONDO_TABLA),
        ('BACKGROUND', (0,-1), (-1,-1), COLOR_TITULO_TABLA),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    contenido.append(tabla_totales)
    contenido.append(Spacer(1, 25))

    # --- Firmas ---
    datos_firmas = [
        [Paragraph("_______________________________", styles["Center"]),
         Paragraph("_______________________________", styles["Center"])],
        [Paragraph("Firma y Timbre del Proveedor", styles["Center"]),
         Paragraph("Firma del Comprador", styles["Center"])],
    ]
    tabla_firmas = Table(datos_firmas, colWidths=[DOC_WIDTH/2, DOC_WIDTH/2], hAlign='LEFT')
    tabla_firmas.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    contenido.append(tabla_firmas)
    contenido.append(Spacer(1, 20))

    # --- Footer ---
    contenido.append(Paragraph(
        "Documento generado automáticamente por el sistema ERP Comercial. Favor verificar los datos antes de proceder.",
        styles["Footer"]
    ))

    doc.build(contenido)
    return response