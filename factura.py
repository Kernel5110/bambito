import asyncio
import platform
import pygame
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import pdfplumber

class Factura:
    def __init__(self):
        # Datos de la empresa
        self.empresa = {
            "nombre": "Panaderia Bambi",
            "ruc": "1234567890",
            "direccion": "Benito Juarez #106, Oaxaca, Oax",
            "telefono": "9513060854"
        }

        # Datos del cliente (inicialmente vacíos, se llenan con el formulario)
        self.cliente = {
            "nombre": "",
            "apellido_paterno": "",
            "apellido_materno": "",
            "rfc": "",
            "calle": "",
            "municipio": "",
            "estado": "",
            "codigo_postal": "",
            "telefono": "",
            "correo": ""
        }

        # Credenciales del remitente
        self.remitente = "nado17hernsvas@gmail.com"
        self.password = "rhkt wtfb cjco swpw"

        # Configuración de Pygame
        self.FPS = 60
        self.WIDTH, self.HEIGHT = 800, 650  # Increased height for more fields
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 128, 0)
        self.screen = None
        self.font = None
        self.inputs = []
        self.active_field = None
        self.submit_button = None
        self.error_message = None
        self.error_timer = 0

    def validar_rfc(self, rfc):
        """
        Valida que el RFC tenga el formato correcto según las reglas mexicanas.
        Personas físicas: 13 caracteres (AAAA######XXX)
        Personas morales: 12 caracteres (AAA######XXX)
        Donde A=letra, #=número, X=alfanumérico
        """
        # Verificar longitud
        if len(rfc) not in [12, 13]:
            return False, "El RFC debe tener 12 o 13 caracteres"
        
        # RFC Persona moral (12 caracteres)
        if len(rfc) == 12:
            # Primeros 3 caracteres deben ser letras
            if not rfc[:3].isalpha():
                return False, "Los primeros 3 caracteres deben ser letras"
            # Siguientes 6 caracteres deben ser números (fecha)
            if not rfc[3:9].isdigit():
                return False, "Los caracteres 4-9 deben ser dígitos (fecha)"
            # Últimos 3 caracteres deben ser alfanuméricos
            if not all(c.isalnum() for c in rfc[9:]):
                return False, "Los últimos 3 caracteres deben ser alfanuméricos"
        
        # RFC Persona física (13 caracteres)
        elif len(rfc) == 13:
            # Primeros 4 caracteres deben ser letras
            if not rfc[:4].isalpha():
                return False, "Los primeros 4 caracteres deben ser letras"
            # Siguientes 6 caracteres deben ser números (fecha)
            if not rfc[4:10].isdigit():
                return False, "Los caracteres 5-10 deben ser dígitos (fecha)"
            # Últimos 3 caracteres deben ser alfanuméricos
            if not all(c.isalnum() for c in rfc[10:]):
                return False, "Los últimos 3 caracteres deben ser alfanuméricos"
        
        # Verificación adicional de la fecha (básica)
        try:
            if len(rfc) == 12:  # Persona moral
                year = int(rfc[3:5])
                month = int(rfc[5:7])
                day = int(rfc[7:9])
            else:  # Persona física
                year = int(rfc[4:6])
                month = int(rfc[6:8])
                day = int(rfc[8:10])
            
            # Verificar mes entre 1-12
            if month < 1 or month > 12:
                return False, "El mes en el RFC debe estar entre 01-12"
            
            # Verificar día entre 1-31 (simplificado)
            if day < 1 or day > 31:
                return False, "El día en el RFC debe estar entre 01-31"
                
        except ValueError:
            return False, "Error en la fecha del RFC"
        
        return True, "RFC válido"

    def leer_productos_de_ticket_pdf(self, pdf_path="ticket.pdf"):
        productos = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    # Busca la tabla que tiene encabezados típicos
                    if table and table[0] and any("Producto" in str(cell) or "Cantidad" in str(cell) for cell in table[0]):
                        # Encuentra los índices de las columnas relevantes
                        headers = [h.lower() if h else "" for h in table[0]]
                        try:
                            idx_nombre = headers.index("producto")
                        except ValueError:
                            idx_nombre = None
                        try:
                            idx_cantidad = headers.index("cantidad")
                        except ValueError:
                            idx_cantidad = None
                        try:
                            idx_precio = headers.index("precio unitario")
                        except ValueError:
                            idx_precio = None
                        # Si encuentra las columnas necesarias, extrae los productos
                        if idx_nombre is not None and idx_cantidad is not None and idx_precio is not None:
                            for row in table[1:]:
                                try:
                                    nombre = row[idx_nombre]
                                    cantidad = int(str(row[idx_cantidad]).replace(",", "").strip())
                                    precio_unitario = float(str(row[idx_precio]).replace("$", "").replace(",", "").strip())
                                    productos.append({
                                        "nombre": nombre,
                                        "cantidad": cantidad,
                                        "precio_unitario": precio_unitario
                                    })
                                except Exception:
                                    continue
                        # Si ya encontró una tabla válida, no busca más
                        if productos:
                            return productos
        return productos
    
    def calcular_totales(self, productos):
        subtotal = sum(item["cantidad"] * item["precio_unitario"] for item in productos)
        iva_porcentaje = 16
        iva = subtotal * (iva_porcentaje / 100)
        total = subtotal + iva
        return subtotal, iva, total

    def generar_factura_pdf(self, productos):
        # Crear documento PDF
        pdf_path = "factura.pdf"
        pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name='Title',
            fontSize=16,
            alignment=1,
            spaceAfter=12
        )
        normal_style = styles['Normal']

        # Título
        elements.append(Paragraph("FACTURA", title_style))
        elements.append(Spacer(1, 0.2*inch))

        # Formato del nombre completo
        nombre_completo = f"{self.cliente['nombre']} {self.cliente['apellido_paterno']} {self.cliente['apellido_materno']}"
        
        # Formato de la dirección completa
        direccion_completa = f"{self.cliente['calle']}, {self.cliente['municipio']}, {self.cliente['estado']}, C.P. {self.cliente['codigo_postal']}"

        # Datos empresa y cliente
        datos_empresa = f"""
        <b>{self.empresa['nombre']}</b><br/>
        RUC: {self.empresa['ruc']}<br/>
        Dirección: {self.empresa['direccion']}<br/>
        Teléfono: {self.empresa['telefono']}
        """
        datos_cliente = f"""
        <b>Datos del Cliente</b><br/>
        Nombre: {nombre_completo}<br/>
        RFC: {self.cliente['rfc']}<br/>
        Dirección: {direccion_completa}<br/>
        Teléfono: {self.cliente['telefono']}<br/>
        Correo: {self.cliente['correo']}
        """

        # Tabla para datos empresa y cliente
        datos_tabla = [[Paragraph(datos_empresa, normal_style), Paragraph(datos_cliente, normal_style)]]
        tabla_datos = Table(datos_tabla, colWidths=[3*inch, 3*inch])
        tabla_datos.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(tabla_datos)
        elements.append(Spacer(1, 0.2*inch))

        # Fecha y número factura
        fecha = datetime.datetime.now().strftime('%d/%m/%Y')
        elements.append(Paragraph(f"Fecha: {fecha}    No. Factura: 001-001-000000123", normal_style))
        elements.append(Spacer(1, 0.2*inch))

        # Tabla de productos
        data = [['Descripción', 'Cantidad', 'P. Unitario', 'Total']]
        for item in productos:
            total_item = item["cantidad"] * item["precio_unitario"]
            data.append([
                item['nombre'],
                str(item['cantidad']),
                f"${item['precio_unitario']:.2f}",
                f"${total_item:.2f}"
            ])

        tabla_productos = Table(data, colWidths=[3.5*inch, 1*inch, 1*inch, 1*inch])
        tabla_productos.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(tabla_productos)
        elements.append(Spacer(1, 0.2*inch))

        # Totales
        subtotal, iva, total = self.calcular_totales(productos)
        totales = f"""
        Subtotal: ${subtotal:.2f}<br/>
        IVA (16%): ${iva:.2f}<br/>
        <b>TOTAL: ${total:.2f}</b>
        """
        elements.append(Paragraph(totales, ParagraphStyle(name='Right', alignment=2)))

        # Generar PDF
        pdf.build(elements)
        return pdf_path

    def enviar_correo(self, destinatario, archivo_adjunto):
        # Configurar el mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = self.remitente
        mensaje['To'] = destinatario
        mensaje['Subject'] = "Factura de Panaderia Bambi"

        # Cuerpo del correo
        cuerpo = "Adjunto encontrará su factura."
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar el archivo PDF
        try:
            with open(archivo_adjunto, "rb") as attachment:
                parte = MIMEBase("application", "octet-stream")
                parte.set_payload(attachment.read())
                encoders.encode_base64(parte)
                parte.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {archivo_adjunto}",
                )
                mensaje.attach(parte)

            # Enviar el correo
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.remitente, self.password)
                server.sendmail(self.remitente, destinatario, mensaje.as_string())
            print("Correo enviado exitosamente.")
            return True
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            return False

    def setup(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Formulario de Factura")
        self.font = pygame.font.Font(None, 32)

        # Input fields - repositioned with more fields
        y_start = 80
        y_increment = 45
        
        self.inputs = [
            {"label": "Nombre:", "value": "", "rect": pygame.Rect(300, y_start, 400, 30), "max_length": 50},
            {"label": "Apellido Paterno:", "value": "", "rect": pygame.Rect(300, y_start + y_increment, 400, 30), "max_length": 50},
            {"label": "Apellido Materno:", "value": "", "rect": pygame.Rect(300, y_start + y_increment*2, 400, 30), "max_length": 50},
            {"label": "RFC:", "value": "", "rect": pygame.Rect(300, y_start + y_increment*3, 400, 30), "max_length": 13},
            {"label": "Calle:", "value": "", "rect": pygame.Rect(300, y_start + y_increment*4, 400, 30), "max_length": 100},
            {"label": "Municipio:", "value": "", "rect": pygame.Rect(300, y_start + y_increment*5, 400, 30), "max_length": 50},
            {"label": "Estado:", "value": "", "rect": pygame.Rect(300, y_start + y_increment*6, 400, 30), "max_length": 50},
            {"label": "Código Postal:", "value": "", "rect": pygame.Rect(300, y_start + y_increment*7, 400, 30), "max_length": 5},
            {"label": "Teléfono:", "value": "", "rect": pygame.Rect(300, y_start + y_increment*8, 400, 30), "max_length": 15},
            {"label": "Correo:", "value": "", "rect": pygame.Rect(300, y_start + y_increment*9, 400, 30), "max_length": 50},
        ]

        self.active_field = None
        self.submit_button = pygame.Rect(300, y_start + y_increment*10 + 10, 100, 40)
        self.error_message = None
        self.error_timer = 0

    def draw(self):
        self.screen.fill(self.WHITE)
        
        # Title
        title_font = pygame.font.Font(None, 40)
        title_surface = title_font.render("Formulario de Factura", True, self.BLACK)
        self.screen.blit(title_surface, (self.WIDTH//2 - title_surface.get_width()//2, 20))

        # Draw labels and input boxes
        for i, field in enumerate(self.inputs):
            # Label
            label_surface = self.font.render(field["label"], True, self.BLACK)
            self.screen.blit(label_surface, (100, field["rect"].y + 5))

            # Input box
            pygame.draw.rect(self.screen, self.GRAY, field["rect"], 2)
            if self.active_field == i:
                pygame.draw.rect(self.screen, self.BLUE, field["rect"], 2)

            # Text
            text_surface = self.font.render(field["value"], True, self.BLACK)
            self.screen.blit(text_surface, (field["rect"].x + 5, field["rect"].y + 5))
            
            # Validación visual para el RFC (campo 3)
            if i == 3 and field["value"]:
                rfc_valido, mensaje = self.validar_rfc(field["value"])
                validation_font = pygame.font.Font(None, 20)
                if rfc_valido:
                    validation_surface = validation_font.render("✓", True, self.GREEN)
                else:
                    validation_surface = validation_font.render("✗", True, self.RED)
                self.screen.blit(validation_surface, (field["rect"].x + field["rect"].width + 10, 
                                                    field["rect"].y + 5))

        # Submit button
        pygame.draw.rect(self.screen, self.BLUE, self.submit_button)
        submit_text = self.font.render("Enviar", True, self.WHITE)
        self.screen.blit(submit_text, (self.submit_button.x + 10, self.submit_button.y + 5))
        
        # Error message if exists and timer is active
        if self.error_message and self.error_timer > 0:
            error_font = pygame.font.Font(None, 24)
            error_surface = error_font.render(self.error_message, True, self.RED)
            self.screen.blit(error_surface, (self.submit_button.x + 120, self.submit_button.y + 10))
            self.error_timer -= 1

        pygame.display.flip()

    def update_loop(self, productos):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicking an input field
                for i, field in enumerate(self.inputs):
                    if field["rect"].collidepoint(event.pos):
                        self.active_field = i
                        break
                else:
                    self.active_field = None

                # Check if clicking submit button
                if self.submit_button.collidepoint(event.pos):
                    # Validar RFC antes de procesar
                    rfc_valido, mensaje = self.validar_rfc(self.inputs[3]["value"])
                    
                    if not rfc_valido:
                        # Mostrar mensaje de error
                        self.error_message = mensaje
                        self.error_timer = 180  # 3 segundos a 60 FPS
                    else:
                        # Actualizar diccionario del cliente con la nueva estructura de campos
                        self.cliente["nombre"] = self.inputs[0]["value"]
                        self.cliente["apellido_paterno"] = self.inputs[1]["value"]
                        self.cliente["apellido_materno"] = self.inputs[2]["value"]
                        self.cliente["rfc"] = self.inputs[3]["value"]
                        self.cliente["calle"] = self.inputs[4]["value"]
                        self.cliente["municipio"] = self.inputs[5]["value"]
                        self.cliente["estado"] = self.inputs[6]["value"]
                        self.cliente["codigo_postal"] = self.inputs[7]["value"]
                        self.cliente["telefono"] = self.inputs[8]["value"]
                        self.cliente["correo"] = self.inputs[9]["value"]

                        # Generar PDF con el array de productos
                        pdf_path = self.generar_factura_pdf(productos)

                        # Enviar correo con el PDF adjunto y cerrar si es exitoso
                        if self.enviar_correo(self.cliente["correo"], pdf_path):
                            pygame.quit()
                            raise SystemExit

            if event.type == pygame.KEYDOWN and self.active_field is not None:
                field = self.inputs[self.active_field]
                if event.key == pygame.K_BACKSPACE:
                    field["value"] = field["value"][:-1]
                elif event.key == pygame.K_RETURN:
                    self.active_field = (self.active_field + 1) % len(self.inputs)
                elif event.unicode.isprintable() and len(field["value"]) < field["max_length"]:
                    field["value"] += event.unicode

        self.draw()

    async def main(self, productos=None):
        if productos is None:
            productos = self.leer_productos_de_ticket_pdf()
            if not productos:
                print("No se pudieron leer productos del ticket.pdf")
                return
        self.setup()
        while True:
            self.update_loop(productos)
            await asyncio.sleep(1.0 / self.FPS)

if platform.system() == "Emscripten":
    factura = Factura()
    asyncio.ensure_future(factura.main())
else:
    if __name__ == "__main__":
        factura = Factura()
        asyncio.run(factura.main())