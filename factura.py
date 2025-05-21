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
    def __init__(self, x, y, ancho, alto):
        """
        Inicializa el sistema de facturación
        
        Args:
            x, y (int): Posición de la interfaz
            ancho, alto (int): Dimensiones de la interfaz
        """
        pygame.font.init()
        
        # Configuración de posición y dimensiones
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        
        # Colores temáticos
        self.FONDO = (241, 236, 227)
        self.color_texto = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 128, 0)
        self.GRAY = (200, 200, 200)
        
        # Configuración de fuentes escaladas
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", int(self.alto * 0.08), bold=True)
        self.fuente_boton = pygame.font.SysFont("Open Sans", int(self.alto * 0.045), bold=True)
        self.fuente_label = pygame.font.SysFont("Open Sans", int(self.alto * 0.04))
        self.fuente_input = pygame.font.SysFont("Open Sans", int(self.alto * 0.035))
        
        # Configuración de navegación
        self.botones_opciones = ["FACTURA", "DATOS", "SALIR"]
        self.opcion_seleccionada = self.botones_opciones[0]
        
        # Configuración de botones
        self.boton_width = int(self.ancho * 0.13)
        self.boton_height = int(self.alto * 0.07)
        self.boton_margin = int(self.ancho * 0.015)
        self.boton_rects = [
            pygame.Rect(
                self.x + self.ancho - (len(self.botones_opciones)+2-i) * (self.boton_width + self.boton_margin),
                self.y + int(self.alto * 0.11),
                self.boton_width, self.boton_height
            )
            for i in range(len(self.botones_opciones))
        ]
        self.color_boton = (220, 220, 220)
        self.color_boton_activo = (180, 180, 255)
        
        # Botón generar/enviar
        self.boton_accion_rect = pygame.Rect(
            self.x + self.ancho - self.boton_width - self.boton_margin,
            self.y + int(self.alto * 0.11),
            self.boton_width, self.boton_height
        )
        self.color_boton_accion = (100, 200, 100)
        self.color_boton_accion_hover = (80, 180, 80)
        self.accion_hover = False

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
            "fecha_nacimiento": "",
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
        self.screen = None
        self.active_field = None
        self.error_message = None
        self.error_timer = 0
        
        # Configuración de inputs
        self.inputs = []
        self.setup_inputs()
        
        # Productos para la factura
        self.productos = []
        self.error_message = None
        self.error_timer = 0

    def setup_inputs(self):
        """Configura los campos de entrada del formulario"""
        y_start = int(self.y + self.alto * 0.25)
        y_increment = int(self.alto * 0.05)
        
        self.inputs = [
            {"label": "Nombre:", "value": "", "rect": pygame.Rect(self.x + 200, y_start, 300, int(self.alto * 0.04)), "max_length": 50},
            {"label": "Apellido Paterno:", "value": "", "rect": pygame.Rect(self.x + 200, y_start + y_increment, 300, int(self.alto * 0.04)), "max_length": 50},
            {"label": "Apellido Materno:", "value": "", "rect": pygame.Rect(self.x + 200, y_start + y_increment*2, 300, int(self.alto * 0.04)), "max_length": 50},
            {"label": "Fecha de Nacimiento:", "value": "", "rect": pygame.Rect(self.x + 200, y_start + y_increment*3, 300, int(self.alto * 0.04)), "max_length": 10, "placeholder": "DD/MM/AAAA"},
            {"label": "RFC:", "value": "", "rect": pygame.Rect(self.x + 200, y_start + y_increment*4, 300, int(self.alto * 0.04)), "max_length": 13},
            {"label": "Calle:", "value": "", "rect": pygame.Rect(self.x + 200, y_start + y_increment*5, 300, int(self.alto * 0.04)), "max_length": 100},
            {"label": "Municipio:", "value": "", "rect": pygame.Rect(self.x + 200, y_start + y_increment*6, 300, int(self.alto * 0.04)), "max_length": 50},
            {"label": "Estado:", "value": "", "rect": pygame.Rect(self.x + 200, y_start + y_increment*7, 300, int(self.alto * 0.04)), "max_length": 50},
            {"label": "Código Postal:", "value": "", "rect": pygame.Rect(self.x + 200, y_start + y_increment*8, 300, int(self.alto * 0.04)), "max_length": 5},
            {"label": "Teléfono:", "value": "", "rect": pygame.Rect(self.x + 200, y_start + y_increment*9, 300, int(self.alto * 0.04)), "max_length": 15},
            {"label": "Correo:", "value": "", "rect": pygame.Rect(self.x + 200, y_start + y_increment*10, 300, int(self.alto * 0.04)), "max_length": 50}
        ]

    def validar_fecha_nacimiento(self, fecha_str):
        """
        Valida que la fecha de nacimiento tenga el formato correcto y sea una fecha válida.
        
        Args:
            fecha_str (str): Fecha en formato DD/MM/AAAA
            
        Returns:
            tuple: (bool, str) - Indica si es válida y mensaje de error
        """
        if not fecha_str:
            return False, "Fecha de nacimiento requerida"
            
        try:
            if fecha_str.count('/') != 2:
                return False, "Formato debe ser DD/MM/AAAA"
                
            dia, mes, año = fecha_str.split('/')
            
            if len(dia) != 2 or len(mes) != 2 or len(año) != 4:
                return False, "Formato debe ser DD/MM/AAAA"
                
            fecha = datetime.datetime(int(año), int(mes), int(dia))
            
            # Verificar que la fecha no sea futura
            if fecha > datetime.datetime.now():
                return False, "La fecha no puede ser en el futuro"
                
            return True, ""
            
        except ValueError:
            return False, "Fecha inválida"

    def validar_rfc(self, rfc, fecha_nacimiento):
        """
        Valida que el RFC tenga el formato correcto y que coincida con la fecha de nacimiento.
        
        Args:
            rfc (str): RFC a validar
            fecha_nacimiento (str): Fecha en formato DD/MM/AAAA
            
        Returns:
            tuple: (bool, str) - Indica si es válido y mensaje de error
        """
        # Verificar longitud
        if len(rfc) not in [12, 13]:
            return False, "El RFC debe tener 12 o 13 caracteres"
            
        # Convertir a mayúsculas
        rfc = rfc.upper()
        
        # Validar fecha de nacimiento primero
        fecha_valida, mensaje = self.validar_fecha_nacimiento(fecha_nacimiento)
        if not fecha_valida:
            return False, f"Primero valide la fecha de nacimiento: {mensaje}"
            
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
                
            fecha_rfc = rfc[3:9]
            
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
                
            fecha_rfc = rfc[4:10]
            
        # Validar que la fecha del RFC coincida con la fecha de nacimiento
        try:
            dia, mes, año = fecha_nacimiento.split('/')
            año_corto = año[-2:]
            fecha_esperada = año_corto + mes + dia
            
            if fecha_rfc != fecha_esperada:
                return False, f"La fecha en el RFC ({fecha_rfc}) no coincide con la fecha de nacimiento ({fecha_esperada})"
                
        except Exception:
            return False, "Error al comparar fechas"
        
        return True, "RFC válido"

    def leer_productos_de_ticket_pdf(self, pdf_path="ticket.pdf"):
        """Lee los productos de un archivo PDF de ticket"""
        productos = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Primero extraer el texto para debug
                    text = page.extract_text()
                    print("Texto completo del PDF:")
                    print(text)
                    
                    # Intentar extraer tablas
                    tables = page.extract_tables()
                    print(f"Número de tablas encontradas: {len(tables)}")
                    
                    if not tables:
                        # Si no encuentra tablas, intentar extraer del texto plano
                        lines = text.split('\n')
                        
                        # Buscar líneas con formato de productos
                        for line in lines:
                            # Buscar líneas que tengan $
                            if '$' in line and not ('SUBTOTAL' in line or 'TOTAL' in line or 'IVA' in line):
                                # Intentar parsear el formato: "Producto X $Y.YY $Z.ZZ"
                                parts = line.split()
                                
                                # Buscar los precios en la línea
                                precio_unitario = None
                                cantidad = None
                                nombre_parts = []
                                
                                for i, part in enumerate(parts):
                                    if part.startswith('$'):
                                        # Es un precio
                                        precio_str = part.replace('$', '').replace(',', '')
                                        try:
                                            precio = float(precio_str)
                                            if precio_unitario is None:
                                                precio_unitario = precio
                                        except:
                                            pass
                                    elif part.isdigit():
                                        # Es una cantidad
                                        cantidad = int(part)
                                    else:
                                        # Es parte del nombre
                                        nombre_parts.append(part)
                                
                                if precio_unitario and cantidad and nombre_parts:
                                    nombre = ' '.join(nombre_parts)
                                    productos.append({
                                        "nombre": nombre,
                                        "cantidad": cantidad,
                                        "precio_unitario": precio_unitario
                                    })
                        
                        if productos:
                            return productos
                    
                    # Si encuentra tablas, procesarlas
                    for table in tables:
                        if table and table[0]:
                            # Imprimir la tabla para debug
                            print("Tabla encontrada:")
                            for row in table:
                                print(row)
                            
                            # Buscar la fila con encabezados
                            header_row = None
                            for i, row in enumerate(table):
                                if row and isinstance(row, list):
                                    # Buscar si algún elemento contiene "producto" o "cantidad"
                                    row_str = str(row).lower()
                                    if any(x in row_str for x in ["producto", "cantidad", "precio"]):
                                        header_row = i
                                        break
                            
                            if header_row is not None:
                                headers = table[header_row]
                                print(f"Encabezados encontrados: {headers}")
                                
                                # Encontrar índices de columnas de manera flexible
                                idx_nombre = None
                                idx_cantidad = None
                                idx_precio = None
                                
                                for i, header in enumerate(headers):
                                    if header and isinstance(header, str):
                                        header_lower = header.lower()
                                        if "producto" in header_lower or "nombre" in header_lower:
                                            idx_nombre = i
                                        elif "cantidad" in header_lower:
                                            idx_cantidad = i
                                        elif "precio unitario" in header_lower or "precio" in header_lower:
                                            idx_precio = i
                                
                                print(f"Índices: nombre={idx_nombre}, cantidad={idx_cantidad}, precio={idx_precio}")
                                
                                # Extraer datos de productos
                                if idx_nombre is not None and idx_cantidad is not None and idx_precio is not None:
                                    for row in table[header_row + 1:]:
                                        if row and len(row) > max(idx_nombre, idx_cantidad, idx_precio):
                                            try:
                                                nombre = str(row[idx_nombre]).strip()
                                                cantidad_str = str(row[idx_cantidad]).strip()
                                                precio_str = str(row[idx_precio]).strip()
                                                
                                                # Limpiar y convertir cantidad
                                                cantidad = int(cantidad_str.replace(",", "").strip())
                                                
                                                # Limpiar y convertir precio
                                                precio_str = precio_str.replace("$", "").replace(",", "").strip()
                                                precio_unitario = float(precio_str)
                                                
                                                if nombre and cantidad > 0 and precio_unitario > 0:
                                                    productos.append({
                                                        "nombre": nombre,
                                                        "cantidad": cantidad,
                                                        "precio_unitario": precio_unitario
                                                    })
                                            except Exception as e:
                                                print(f"Error procesando fila: {e}")
                                                continue
                            
                            if productos:
                                return productos
                    
        except Exception as e:
            print(f"Error al leer PDF: {e}")
        
        return productos
    
    def calcular_totales(self, productos):
        """Calcula los totales de la factura"""
        subtotal = sum(item["cantidad"] * item["precio_unitario"] for item in productos)
        iva_porcentaje = 16
        iva = subtotal * (iva_porcentaje / 100)
        total = subtotal + iva
        return subtotal, iva, total

    def generar_factura_pdf(self, productos):
        """Genera el archivo PDF de la factura"""
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
        Fecha de Nacimiento: {self.cliente['fecha_nacimiento']}<br/>
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
        """Envía el correo con la factura adjunta"""
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
        """Configura Pygame y la pantalla"""
        # No inicializar pygame si ya está inicializado
        if not pygame.get_init():
            pygame.init()
        
        # Usar la pantalla existente si ya existe
        if pygame.display.get_surface():
            self.screen = pygame.display.get_surface()
        else:
            self.screen = pygame.display.set_mode((self.ancho, self.alto))
        
        pygame.display.set_caption("Sistema de Facturación")

    def draw_header(self):
        """Dibuja el encabezado de la interfaz"""
        # Fondo principal
        pygame.draw.rect(self.screen, self.FONDO, (self.x, self.y, self.ancho, self.alto))
        
        # Título principal
        titulo_surface = self.fuente_titulo.render("Sistema de Facturación", True, self.color_texto)
        titulo_rect = titulo_surface.get_rect(centerx=self.x + self.ancho // 2, 
                                              centery=self.y + int(self.alto * 0.06))
        self.screen.blit(titulo_surface, titulo_rect)

    def draw_navigation(self):
        """Dibuja los botones de navegación"""
        # Botones de navegación
        for i, texto in enumerate(self.botones_opciones):
            rect = self.boton_rects[i]
            color = self.color_boton_activo if texto == self.opcion_seleccionada else self.color_boton
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, self.color_texto, rect, 2, border_radius=8)
            
            texto_surface = self.fuente_boton.render(texto, True, self.color_texto)
            texto_rect = texto_surface.get_rect(center=rect.center)
            self.screen.blit(texto_surface, texto_rect)
        
        # Botón de acción
        color_accion = self.color_boton_accion_hover if self.accion_hover else self.color_boton_accion
        pygame.draw.rect(self.screen, color_accion, self.boton_accion_rect, border_radius=8)
        texto_accion = "Generar y Enviar"
        texto_surface = self.fuente_boton.render(texto_accion, True, self.WHITE)
        texto_rect = texto_surface.get_rect(center=self.boton_accion_rect.center)
        self.screen.blit(texto_surface, texto_rect)

    def draw_datos_form(self):
        """Dibuja el formulario de datos del cliente"""
        if self.opcion_seleccionada != "DATOS":
            return
            
        # Título del formulario
        subtitulo = self.fuente_label.render("Datos del Cliente", True, self.color_texto)
        self.screen.blit(subtitulo, (self.x + 30, self.y + int(self.alto * 0.2)))
        
        # Dibujar campos
        for i, field in enumerate(self.inputs):
            # Label
            label_surface = self.fuente_label.render(field["label"], True, self.color_texto)
            self.screen.blit(label_surface, (self.x + 30, field["rect"].y + 5))

            # Input box
            pygame.draw.rect(self.screen, self.WHITE, field["rect"], border_radius=5)
            pygame.draw.rect(self.screen, self.GRAY, field["rect"], 2, border_radius=5)
            if self.active_field == i:
                pygame.draw.rect(self.screen, self.BLUE, field["rect"], 3, border_radius=5)

            # Text o placeholder
            display_text = field["value"] if field["value"] else field.get("placeholder", "")
            text_color = self.color_texto if field["value"] else self.GRAY
            text_surface = self.fuente_input.render(display_text, True, text_color)
            self.screen.blit(text_surface, (field["rect"].x + 10, field["rect"].y + 5))
            
            # Validación visual para RFC y fecha de nacimiento
            if i == 3 and field["value"]:  # Fecha de nacimiento
                fecha_valida, mensaje = self.validar_fecha_nacimiento(field["value"])
                validation_color = self.GREEN if fecha_valida else self.RED
                validation_symbol = "✓" if fecha_valida else "✗"
                validation_surface = self.fuente_input.render(validation_symbol, True, validation_color)
                self.screen.blit(validation_surface, (field["rect"].x + field["rect"].width + 10, 
                                                     field["rect"].y + 5))
                
                if not fecha_valida and i == self.active_field:
                    error_surface = self.fuente_input.render(mensaje, True, self.RED)
                    self.screen.blit(error_surface, (field["rect"].x + field["rect"].width + 30, 
                                                    field["rect"].y + 5))
                    
            elif i == 4 and field["value"]:  # RFC
                fecha_nacimiento = self.inputs[3]["value"]
                rfc_valido, mensaje = self.validar_rfc(field["value"], fecha_nacimiento)
                validation_color = self.GREEN if rfc_valido else self.RED
                validation_symbol = "✓" if rfc_valido else "✗"
                validation_surface = self.fuente_input.render(validation_symbol, True, validation_color)
                self.screen.blit(validation_surface, (field["rect"].x + field["rect"].width + 10, 
                                                     field["rect"].y + 5))
                
                if not rfc_valido and i == self.active_field:
                    error_surface = self.fuente_input.render(mensaje, True, self.RED)
                    self.screen.blit(error_surface, (field["rect"].x + field["rect"].width + 30, 
                                                    field["rect"].y + 5))
        
        # Error global
        if self.error_message and self.error_timer > 0:
            y_error = self.y + int(self.alto * 0.9)
            error_surface = self.fuente_input.render(self.error_message, True, self.RED)
            error_rect = error_surface.get_rect(centerx=self.x + self.ancho // 2, 
                                                centery=y_error)
            self.screen.blit(error_surface, error_rect)
            self.error_timer -= 1

    def draw_productos_form(self):
        """Dibuja la pantalla de productos (visual solamente)"""
        if self.opcion_seleccionada != "FACTURA":
            return
            
        # Título
        subtitulo = self.fuente_label.render("Productos de la Factura", True, self.color_texto)
        self.screen.blit(subtitulo, (self.x + 30, self.y + int(self.alto * 0.2)))
        
        # Mensaje de información
        info_text = self.fuente_input.render("Los productos serán cargados desde el archivo ticket.pdf", True, self.GRAY)
        self.screen.blit(info_text, (self.x + 30, self.y + int(self.alto * 0.25)))

    def draw(self):
        """Dibuja toda la interfaz"""
        self.draw_header()
        self.draw_navigation()
        self.draw_datos_form()
        self.draw_productos_form()
        
        pygame.display.flip()

    def handle_event(self, event):
        """Maneja los eventos de la interfaz"""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.accion_hover = self.boton_accion_rect.collidepoint(mouse_pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Verificar si se hizo clic en los botones de navegación
            for i, rect in enumerate(self.boton_rects):
                if rect.collidepoint(mouse_pos):
                    self.opcion_seleccionada = self.botones_opciones[i]
                    
                    # Si se selecciona SALIR, retornar True para salir del loop
                    if self.opcion_seleccionada == "SALIR":
                        return True  # Señal para terminar el main_loop
                    return
            
            # Verificar si se hizo clic en el botón de acción
            if self.boton_accion_rect.collidepoint(mouse_pos):
                # Validar todos los campos
                fecha_nacimiento = self.inputs[3]["value"]
                rfc = self.inputs[4]["value"]
                
                # Validar fecha y RFC
                fecha_valida, mensaje_fecha = self.validar_fecha_nacimiento(fecha_nacimiento)
                if not fecha_valida:
                    self.error_message = f"Error en fecha de nacimiento: {mensaje_fecha}"
                    self.error_timer = 180
                    return
                    
                rfc_valido, mensaje_rfc = self.validar_rfc(rfc, fecha_nacimiento)
                if not rfc_valido:
                    self.error_message = f"Error en RFC: {mensaje_rfc}"
                    self.error_timer = 180
                    return
                
                # Actualizar diccionario del cliente
                self.cliente["nombre"] = self.inputs[0]["value"]
                self.cliente["apellido_paterno"] = self.inputs[1]["value"]
                self.cliente["apellido_materno"] = self.inputs[2]["value"]
                self.cliente["fecha_nacimiento"] = self.inputs[3]["value"]
                self.cliente["rfc"] = self.inputs[4]["value"]
                self.cliente["calle"] = self.inputs[5]["value"]
                self.cliente["municipio"] = self.inputs[6]["value"]
                self.cliente["estado"] = self.inputs[7]["value"]
                self.cliente["codigo_postal"] = self.inputs[8]["value"]
                self.cliente["telefono"] = self.inputs[9]["value"]
                self.cliente["correo"] = self.inputs[10]["value"]

                # Cargar productos y generar factura
                productos = self.leer_productos_de_ticket_pdf()
                if not productos:
                    self.error_message = "No se pudieron leer productos del ticket.pdf"
                    self.error_timer = 180
                    return
                
                # Generar PDF y enviar
                pdf_path = self.generar_factura_pdf(productos)
                if self.enviar_correo(self.cliente["correo"], pdf_path):
                    return True
                else:
                    self.error_message = "Error al enviar el correo"
                    self.error_timer = 180
                return
            
            # Verificar campos de entrada
            if self.opcion_seleccionada == "DATOS":
                for i, field in enumerate(self.inputs):
                    if field["rect"].collidepoint(mouse_pos):
                        self.active_field = i
                        break
                else:
                    self.active_field = None

        elif event.type == pygame.KEYDOWN and self.opcion_seleccionada == "DATOS" and self.active_field is not None:
            field = self.inputs[self.active_field]
            if event.key == pygame.K_BACKSPACE:
                field["value"] = field["value"][:-1]
            elif event.key == pygame.K_RETURN:
                self.active_field = (self.active_field + 1) % len(self.inputs)
            elif event.unicode.isprintable() and len(field["value"]) < field["max_length"]:
                field["value"] += event.unicode

    async def main_loop(self):
        """Loop principal del programa"""
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Solo cerrar completamente si no está embebido
                    if not hasattr(self, 'is_embedded'):
                        pygame.quit()
                        raise SystemExit
                    return  # Si está embebido, solo salir del loop
                    
                # Si handle_event retorna True, salir del loop
                if self.handle_event(event):
                    return  # Regresar al POS
            
            self.draw()
            clock.tick(self.FPS)
            await asyncio.sleep(0)

    async def main(self, productos=None):
        """Punto de entrada principal"""
        if productos is None:
            productos = self.leer_productos_de_ticket_pdf()
            if not productos:
                print("No se pudieron leer productos del ticket.pdf")
                # Si no hay productos, permitir continuar con campos vacíos
                # return
        
        # Marcar como embebido cuando se llama desde POS
        self.is_embedded = True
        
        self.setup()
        await self.main_loop()
        
        # Al salir del loop, limpiar referencias
        return