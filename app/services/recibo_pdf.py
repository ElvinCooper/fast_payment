from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from io import BytesIO


def generar_recibo_termico(datos):
    buffer = BytesIO()

    width = 70 * mm
    height = 120 * mm  # aumentamos altura para mejor layout

    c = canvas.Canvas(buffer, pagesize=(width, height))

    y = height - 15

    # ---------------- HEADER ----------------
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width / 2, y, "BIOCAMILA")

    y -= 12
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, y, "Pagos & Servicios")

    y -= 12
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, y, f"Recibo No: {datos['nro_recibo']}")

    y -= 12
    c.setFont("Helvetica-Bold", 12)  # Fuente más grande y en negrita para la fecha
    c.drawCentredString(width / 2, y, f"{datos['fecha']}")

    # línea separadora
    y -= 10
    c.line(5, y, width - 5, y)

    # ---------------- CLIENTE ----------------
    y -= 15
    c.setFont("Helvetica-Bold", 9)
    c.drawString(5, y, "CLIENTE")

    y -= 10
    c.setFont("Helvetica", 9)
    c.drawString(5, y, datos["cliente"])

    # ---------------- DETALLE ----------------
    y -= 15
    c.line(5, y, width - 5, y)

    y -= 12
    c.setFont("Helvetica-Bold", 9)
    c.drawString(5, y, "DETALLE")

    y -= 12
    c.setFont("Helvetica", 9)

    # Etiqueta izquierda / valor derecha
    c.drawString(5, y, "Monto:")
    c.drawRightString(width - 5, y, f"${datos['monto']:,.2f}")

    y -= 10
    c.drawString(5, y, "Atendido por:")
    c.drawRightString(width - 5, y, datos["atendido_por"])

    # ---------------- TOTAL DESTACADO ----------------
    y -= 18
    c.line(5, y, width - 5, y)

    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2, y, "TOTAL PAGADO")

    y -= 18
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, f"${datos['monto']:,.2f}")

    # ---------------- FOOTER ----------------
    y -= 20
    c.line(5, y, width - 5, y)

    y -= 12
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, y, "Gracias por su pago")

    y -= 10
    c.drawCentredString(width / 2, y, "Conserve este recibo")

    y -= 12
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(width / 2, y, "ORIGINAL - CLIENTE")

    # ---------------- END ----------------
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
