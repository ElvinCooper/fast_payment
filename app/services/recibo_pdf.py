from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from io import BytesIO


def generar_recibo_termico(datos):
    buffer = BytesIO()
    # Tamaño tipo ticket (80mm ancho x 200mm alto)
    width = 70 * mm
    height = 80 * mm

    c = canvas.Canvas(buffer, pagesize=(width, height))

    y = height - 20  # posición inicial

    # --- Header ---
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "PAGOS BIOCAMILA APP")

    y -= 15
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, y, f"Recibo: {datos['nro_recibo']}")

    y -= 12
    c.drawCentredString(width / 2, y, f"Fecha: {datos['fecha']}")

    # Línea separadora
    y -= 10
    c.line(10, y, width - 10, y)

    # --- Cuerpo ---
    y -= 20
    c.setFont("Helvetica-Bold", 9)
    c.drawString(10, y, "Cliente:")
    c.setFont("Helvetica", 9)
    y -= 12
    c.drawString(10, y, datos["cliente"])

    # Línea separadora
    y -= 15
    c.line(10, y, width - 10, y)

    # --- Monto destacado ---
    y -= 25
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, y, "MONTO PAGADO")

    y -= 18
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, f"${datos['monto']:,.2f}")

    # Línea separadora
    y -= 15
    c.line(10, y, width - 10, y)

    y -= 15
    c.setFont("Helvetica-Bold", 9)
    c.drawString(10, y, "Atendido por:")
    y -= 10
    c.setFont("Helvetica", 9)
    c.drawString(10, y, datos["atendido_por"])

    # --- Nota final ---
    y -= 30
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, y, "ORIGINAL - CLIENTE")

    c.showPage()
    c.save()
    buffer.seek(0)
    # return filename
    return buffer


# Ejemplo de uso
# datos_pago = {
#     "nro_recibo": "500922",
#     "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
#     "cliente": "Elvin Cooper",
#     # "concepto": "Pago Cuota Marzo",
#     "monto": 2500.00,
#     # "status": "COMPLETADO",
#     "atendido_por": "Kelly"
# }

# generar_recibo_termico(datos_pago)
