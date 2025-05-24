import asyncio
import platform
import pygame
import datetime
import smtplib
import os
import glob
import uuid
import hashlib
import random
import string
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Rect
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
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

        # Datos de la empresa (EMISOR)
        self.empresa = {
            "nombre": "Panaderia Bambi",
            "rfc": "BAM250205123",
            "regimen_fiscal": "626 - Régimen Simplificado de Confianza",
            "direccion": "Benito Juarez #106, Oaxaca, Oax",
            "telefono": "9513060854",
            "codigo_postal": "68000"
        }

        # Datos del cliente (RECEPTOR - inicialmente vacíos)
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
            "correo": "",
            "uso_cfdi": "G03 - Gastos en general"
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

    def generar_folio_serie(self):
        """Genera folio y serie basado en fecha, hora, seg, miliseg"""
        now = datetime.datetime.now()
        folio = now.strftime("%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}"
        serie = "A"
        return serie, folio

    def generar_uuid_cfdi(self):
        """Genera UUID simulado para el CFDI"""
        return str(uuid.uuid4()).upper()

    def generar_sello_digital(self, cadena_original):
        """Genera sello digital simulado"""
        # Simular sello digital con hash SHA-256
        sello = hashlib.sha256(cadena_original.encode()).hexdigest()
        return sello.upper()

    def generar_certificado_digital(self):
        """Genera datos simulados del certificado digital"""
        numero_serie = "".join(random.choices(string.digits, k=20))
        return {
            "numero_serie": numero_serie,
            "fecha_inicio": "2024-01-01T00:00:00",
            "fecha_fin": "2028-12-31T23:59:59"
        }

    def extraer_forma_pago_ticket(self, pdf_path):
        """Extrae la forma de pago del ticket PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    lines = text.split('\n')
                    
                    for line in lines:
                        if 'PAGO:' in line.upper():
                            # Extraer el tipo de pago después de "PAGO:"
                            pago_part = line.upper().split('PAGO:')[1].strip()
                            if 'EFECTIVO' in pago_part:
                                return "01 - Efectivo"
                            elif 'TARJETA' in pago_part:
                                return "04 - Tarjeta de crédito"
                            elif 'TRANSFERENCIA' in pago_part:
                                return "03 - Transferencia electrónica"
            
            return "01 - Efectivo"  # Default
        except:
            return "01 - Efectivo"

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

    def validar_rfc_completo(self, rfc, nombre, apellido_paterno, apellido_materno, fecha_nacimiento):
        """
        Valida RFC completo incluyendo iniciales de nombres y fecha
        
        Args:
            rfc (str): RFC a validar
            nombre, apellido_paterno, apellido_materno (str): Nombres
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
        
        # Generar las iniciales esperadas
        try:
            # Para persona física (13 caracteres)
            if len(rfc) == 13:
                # Extraer consonante interna del apellido paterno
                consonantes_paterno = [c for c in apellido_paterno.upper()[1:] if c in 'BCDFGHJKLMNPQRSTVWXYZ']
                consonante_paterno = consonantes_paterno[0] if consonantes_paterno else 'X'
                
                # Iniciales esperadas: APELLIDO_PATERNO[0] + VOCAL_INTERNA_PATERNO + APELLIDO_MATERNO[0] + NOMBRE[0]
                vocal_interna_paterno = None
                for c in apellido_paterno.upper()[1:]:
                    if c in 'AEIOU':
                        vocal_interna_paterno = c
                        break
                vocal_interna_paterno = vocal_interna_paterno or 'X'
                
                iniciales_esperadas = (apellido_paterno[0].upper() + 
                                     vocal_interna_paterno + 
                                     apellido_materno[0].upper() + 
                                     nombre[0].upper())
                
                # Verificar iniciales
                if rfc[:4] != iniciales_esperadas:
                    return False, f"Las iniciales del RFC ({rfc[:4]}) no coinciden con las esperadas ({iniciales_esperadas})"
                
                # Verificar fecha (posiciones 4-9)
                dia, mes, año = fecha_nacimiento.split('/')
                fecha_esperada = año[-2:] + mes + dia
                
                if rfc[4:10] != fecha_esperada:
                    return False, f"La fecha en el RFC ({rfc[4:10]}) no coincide con la fecha de nacimiento ({fecha_esperada})"
                
                # Verificar homoclave (posiciones 10-12)
                if not rfc[10:13].isalnum():
                    return False, "La homoclave debe ser alfanumérica"
                    
            else:  # Persona moral (12 caracteres)
                return True, "RFC válido (persona moral)"
                
        except Exception as e:
            return False, f"Error en validación: {str(e)}"
        
        return True, "RFC válido"

    def obtener_ultimo_ticket(self):
        """
        Obtiene la ruta del último ticket generado en la carpeta tickets
        
        Returns:
            str: Ruta del último ticket o None si no encuentra ninguno
        """
        try:
            # Buscar todos los archivos PDF en la carpeta tickets
            patron = "tickets/ticket(*.pdf"
            archivos_ticket = glob.glob(patron)
            
            if not archivos_ticket:
                # Si no hay archivos en la carpeta tickets, buscar ticket.pdf en la raíz
                if os.path.exists("ticket.pdf"):
                    return "ticket.pdf"
                return None
            
            # Ordenar por fecha de modificación (más reciente primero)
            archivos_ticket.sort(key=os.path.getmtime, reverse=True)
            
            # Retornar el más reciente
            return archivos_ticket[0]
            
        except Exception as e:
            print(f"Error al buscar último ticket: {e}")
            return None

    def leer_productos_de_ticket_pdf(self, pdf_path=None):
        """Lee los productos de un archivo PDF de ticket"""
        # Si no se especifica ruta, buscar el último ticket
        if pdf_path is None:
            pdf_path = self.obtener_ultimo_ticket()
            if not pdf_path:
                print("No se encontró ningún ticket para procesar")
                return []
        
        print(f"Leyendo productos del archivo: {pdf_path}")
        productos = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Primero extraer el texto para debug
                    text = page.extract_text()
                    print("Texto completo del PDF:")
                    print(text)
                    
                    # Intentar extraer del texto plano
                    lines = text.split('\n')
                    
                    # Buscar líneas con formato de productos
                    for i, line in enumerate(lines):
                        # Buscar líneas que tengan formato "cantidad x $precio = $total"
                        if 'x $' in line and '= $' in line and not ('SUBTOTAL' in line or 'TOTAL' in line or 'IVA' in line):
                            try:
                                # Formato esperado: "2 x $15.00 = $30.00"
                                parts = line.split(' x $')
                                if len(parts) >= 2:
                                    # Extraer cantidad
                                    cantidad_part = parts[0].strip()
                                    cantidad = int(cantidad_part) if cantidad_part.isdigit() else 1
                                    
                                    # Extraer precios
                                    precio_part = parts[1]
                                    if ' = $' in precio_part:
                                        precio_unitario_str, precio_total_str = precio_part.split(' = $')
                                        precio_unitario = float(precio_unitario_str.strip())
                                        
                                        # Buscar el nombre del producto en líneas anteriores
                                        if i > 0:
                                            nombre = lines[i - 1].strip()
                                            if nombre and not any(x in nombre.upper() for x in ['PRODUCTOS', 'FECHA', 'PAGO', 'CAJERO']):
                                                productos.append({
                                                    "nombre": nombre,
                                                    "cantidad": cantidad,
                                                    "precio_unitario": precio_unitario,
                                                    "clave_sat": "50181900",  # Clave SAT para productos de panadería
                                                    "unidad_medida": "H87"   # Unidad SAT - Pieza
                                                })
                            except Exception as e:
                                print(f"Error procesando línea '{line}': {e}")
                                continue
                
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
        """Genera el archivo PDF de la factura con un formato mejorado"""
        # Crear documento PDF
        now = datetime.datetime.now()
        pdf_filename = f"facturas/factura_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf = SimpleDocTemplate(
            pdf_filename,
            pagesize=letter,
            topMargin=0.3*inch,
            bottomMargin=0.3*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        elements = []

        # Estilos mejorados
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name='Title',
            parent=styles['Title'],
            fontSize=22,
            alignment=TA_CENTER,
            spaceAfter=8,
            textColor=colors.HexColor("#1E3A8A"),  # Azul oscuro elegante
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            name='Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=6,
            textColor=colors.HexColor("#4B5563"),  # Gris oscuro
            fontName='Helvetica'
        )
        header_style = ParagraphStyle(
            name='Header',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=5,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            leading=14
        )
        normal_style = ParagraphStyle(
            name='Normal',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=3,
            textColor=colors.black,
            fontName='Helvetica',
            leading=12
        )
        small_style = ParagraphStyle(
            name='Small',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            spaceAfter=3,
            textColor=colors.HexColor("#6B7280"),  # Gris medio
            fontName='Helvetica',
            leading=10
        )
        thank_you_style = ParagraphStyle(
            name='ThankYou',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=5,
            textColor=colors.HexColor("#1E3A8A"),
            fontName='Helvetica-Oblique',
            leading=12
        )

        # Encabezado con fondo, logo y título
        logo_path = "imagenes/log.png"
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=1.2*inch, height=1.2*inch)
        else:
            # Placeholder para el logo (rectángulo con texto)
            drawing = Drawing(1.2*inch, 1.2*inch)
            drawing.add(Rect(0, 0, 1.2*inch, 1.2*inch, fillColor=colors.HexColor("#E5E7EB"), strokeColor=colors.black))
            drawing.add(Paragraph("Logo Panadería Bambi", small_style, x=10, y=1.2*inch-20))
            logo = drawing

        # Título y subtítulo
        title = Paragraph("Panadería Bambi", title_style)
        subtitle = Paragraph("Comprobante Fiscal Digital por Internet (CFDI)", subtitle_style)
        header_data = [[logo, title]]
        header_table = Table(header_data, colWidths=[1.5*inch, 5.5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E0F2FE")),  # Fondo azul claro
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3A8A")),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(header_table)
        elements.append(subtitle)
        elements.append(Spacer(1, 0.1*inch))

        # Línea divisoria elegante
        drawing = Drawing(7.5*inch, 2)
        drawing.add(Rect(0, 0, 7.5*inch, 2, fillColor=colors.HexColor("#1E3A8A")))
        elements.append(drawing)
        elements.append(Spacer(1, 0.05*inch))

        # Datos fiscales principales
        serie, folio = self.generar_folio_serie()
        uuid_cfdi = self.generar_uuid_cfdi()
        forma_pago = self.extraer_forma_pago_ticket(self.obtener_ultimo_ticket())
        
        datos_fiscales = [
            ["Serie:", serie, "Folio:", folio],
            ["No. Factura:", f"{serie}-{folio}", "Versión CFDI:", "4.0"],
            ["Fecha de Emisión:", now.strftime('%d/%m/%Y %H:%M:%S'), "Lugar de Expedición:", "Oaxaca, Oaxaca"],
            ["", "", "", self.empresa['direccion']],
            ["Forma de Pago:", forma_pago, "Método de Pago:", "PUE - Pago en Una Sola Exhibición"],
            ["Moneda:", "MXN - Peso Mexicano", "Tipo de Comprobante:", "I - Ingreso"]
        ]

        tabla_fiscal = Table(datos_fiscales, colWidths=[2.5 * cm, 4.5 * cm])
        tabla_fiscal.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(tabla_fiscal)
        elements.append(Spacer(1, 0.1*inch))

        # Datos del emisor y receptor
        nombre_completo = f"{self.cliente['nombre']} {self.cliente['apellido_paterno']} {self.cliente['apellido_materno']}"
        direccion_completa = f"{self.cliente['calle']}, {self.cliente['municipio']}, {self.cliente['estado']}, C.P. {self.cliente['codigo_postal']}"

        datos_empresa = f"""
        <b>DATOS DEL EMISOR</b><br/>
        <b>{self.empresa['nombre']}</b><br/>
        RFC: {self.empresa['rfc']}<br/>
        Régimen Fiscal: {self.empresa['regimen_fiscal']}<br/>
        Dirección: {self.empresa['direccion']}<br/>
        Teléfono: {self.empresa['telefono']}
        """
        datos_cliente = f"""
        <b>DATOS DEL RECEPTOR</b><br/>
        <b>{nombre_completo}</b><br/>
        RFC: {self.cliente['rfc']}<br/>
        Uso del CFDI: {self.cliente['uso_cfdi']}<br/>
        Dirección: {direccion_completa}<br/>
        Teléfono: {self.cliente['telefono']}<br/>
        Correo: {self.cliente['correo']}
        """

        datos_tabla = [[Paragraph(datos_empresa, normal_style), Paragraph(datos_cliente, normal_style)]]
        tabla_datos = Table(datos_tabla, colWidths=[3.5*inch, 3.5*inch])
        tabla_datos.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#D1D5DB")),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E5E7EB")),  # Fondo azul claro
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#1E3A8A")),  # Borde externo azul
        ]))
        elements.append(tabla_datos)
        elements.append(Spacer(1, 0.15*inch))

        # Tabla de productos
        data = [['Clave SAT', 'Descripción', 'Unidad', 'Cantidad', 'Valor Unitario', 'Importe']]
        for item in productos:
            importe = item["cantidad"] * item["precio_unitario"]
            data.append([
                item.get('clave_sat', '50181900'),
                item['nombre'],
                item.get('unidad_medida', 'H87'),
                str(item['cantidad']),
                f"${item['precio_unitario']:.2f}",
                f"${importe:.2f}"
            ])

        tabla_productos = Table(data, colWidths=[0.9*inch, 2.6*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
        tabla_productos.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),  # Encabezado azul oscuro
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (1,1), (1,-1), 'LEFT'),  # Descripción alineada a la izquierda
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,1), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F9FAFB")),  # Filas en gris claro
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#D1D5DB")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#1E3A8A")),  # Borde externo
        ]))
        elements.append(tabla_productos)
        elements.append(Spacer(1, 0.15*inch))

        # Totales
        subtotal, iva, total = self.calcular_totales(productos)
        totales_data = [
            ["Subtotal:", f"${subtotal:.2f}"],
            ["IVA (16%):", f"${iva:.2f}"],
            ["Total:", f"${total:.2f}"]
        ]
        tabla_totales = Table(totales_data, colWidths=[5.5*inch, 1.5*inch])
        tabla_totales.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,-1), 'RIGHT'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('FONTSIZE', (0,2), (-1,2), 14),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#DCFCE7")),  # Total en verde claro
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#D1D5DB")),
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#1E3A8A")),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ]))
        elements.append(tabla_totales)
        elements.append(Spacer(1, 0.2*inch))

        # Datos fiscales digitales
        cadena_original = f"||1.1|{serie}|{folio}|{now.isoformat()}|{self.empresa['rfc']}|{self.cliente['rfc']}|{total:.2f}||"
        sello_emisor = self.generar_sello_digital(cadena_original)
        sello_sat = self.generar_sello_digital(sello_emisor + "SAT")
        certificado = self.generar_certificado_digital()

        elements.append(Paragraph("<b>DATOS FISCALES DIGITALES</b>", header_style))
        fiscal_data = f"""
        <b>UUID (Folio Fiscal):</b> {uuid_cfdi}<br/>
        <b>No. Serie del Certificado Emisor:</b> {certificado['numero_serie']}<br/>
        <b>No. Serie del Certificado SAT:</b> {"".join(random.choices(string.digits, k=20))}<br/>
        <b>Fecha y Hora de Certificación:</b> {now.strftime('%Y-%m-%dT%H:%M:%S')}<br/>
        <b>Sello Digital del Emisor:</b><br/>
        {sello_emisor[:100]}...<br/>
        <b>Sello Digital del SAT:</b><br/>
        {sello_sat[:100]}...<br/>
        <b>Cadena Original del Complemento de Certificación Digital del SAT:</b><br/>
        {cadena_original}
        """
        elements.append(Paragraph(fiscal_data, small_style))
        elements.append(Spacer(1, 0.05*inch))

        # Código QR con borde
        qr_url = f"https://verificacfdi.facturaelectronica.sat.gob.mx/?id={uuid_cfdi}&re={self.empresa['rfc']}&rr={self.cliente['rfc']}&tt={total:.2f}"
        qr = QrCodeWidget(qr_url)
        qr.barWidth = 1.5*inch
        qr.barHeight = 1.5*inch
        qr_drawing = Drawing(1.5*inch, 1.5*inch)
        qr_drawing.add(Rect(0, 0, 1.5*inch, 1.5*inch, fillColor=colors.white, strokeColor=colors.HexColor("#1E3A8A"), strokeWidth=2))
        qr_drawing.add(qr)
        qr_table = Table([[qr_drawing, Paragraph(f"<b>Código QR</b><br/>Escanee para verificar en el portal del SAT", small_style)]],
                        colWidths=[1.8*inch, 5.2*inch])
        qr_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('LEFTPADDING', (1,0), (1,0), 10),
        ]))
        elements.append(qr_table)
        elements.append(Spacer(1, 0.1*inch))

        # Mensaje de agradecimiento
        thank_you_message = Paragraph(
            f"¡Gracias por su compra, {self.cliente['nombre']}!<br/>Esperamos verlo pronto de nuevo en Panadería Bambi.",
            thank_you_style
        )
        thank_you_table = Table([[thank_you_message]], colWidths=[7.5*inch])
        thank_you_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F9FF")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3A8A")),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(thank_you_table)
        elements.append(Spacer(1, 0.1*inch))

        # Pie de página
        footer = Paragraph(
            "Este documento es una representación impresa de un CFDI. Panadería Bambi - Todos los derechos reservados 2025.",
            small_style
        )
        footer_table = Table([[footer]], colWidths=[7.5*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F3F4F6")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1E3A8A")),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(footer_table)

        # Generar PDF
        pdf.build(elements)
        return pdf_filename

    def enviar_correo(self, destinatario, archivo_adjunto):
        """Envía el correo con la factura adjunta"""
        # Configurar el mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = self.remitente
        mensaje['To'] = destinatario
        mensaje['Subject'] = "Factura Electrónica - Panaderia Bambi"

        # Cuerpo del correo
        cuerpo = """
        Estimado cliente,
        
        Adjunto encontrará su Comprobante Fiscal Digital por Internet (CFDI).
        
        Esta factura electrónica tiene plena validez fiscal de acuerdo con las disposiciones del SAT.
        
        Saludos cordiales,
        Panadería Bambi
        """
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
            print("Factura enviada exitosamente por correo.")
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
        
        pygame.display.set_caption("Sistema de Facturación Fiscal")

    def draw_header(self):
        """Dibuja el encabezado de la interfaz"""
        # Fondo principal
        pygame.draw.rect(self.screen, self.FONDO, (self.x, self.y, self.ancho, self.alto))
        
        # Título principal
        titulo_surface = self.fuente_titulo.render("Sistema de Facturación Fiscal", True, self.color_texto)
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
        texto_accion = "Generar CFDI"
        texto_surface = self.fuente_boton.render(texto_accion, True, self.WHITE)
        texto_rect = texto_surface.get_rect(center=self.boton_accion_rect.center)
        self.screen.blit(texto_surface, texto_rect)

    def draw_datos_form(self):
        """Dibuja el formulario de datos del cliente"""
        if self.opcion_seleccionada != "DATOS":
            return
            
        # Título del formulario
        subtitulo = self.fuente_label.render("Datos del Receptor (Cliente)", True, self.color_texto)
        self.screen.blit(subtitulo, (self.x + 30, self.y + int(self.alto * 0.2)))
        
        # Información adicional
        info_text = self.fuente_input.render("Complete todos los campos para generar el CFDI", True, self.GRAY)
        self.screen.blit(info_text, (self.x + 30, self.y + int(self.alto * 0.22)))
        
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
                nombre = self.inputs[0]["value"]
                apellido_paterno = self.inputs[1]["value"]
                apellido_materno = self.inputs[2]["value"]
                fecha_nacimiento = self.inputs[3]["value"]
                
                if nombre and apellido_paterno and apellido_materno and fecha_nacimiento:
                    rfc_valido, mensaje = self.validar_rfc_completo(
                        field["value"], nombre, apellido_paterno, apellido_materno, fecha_nacimiento
                    )
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
        """Dibuja la pantalla de productos"""
        if self.opcion_seleccionada != "FACTURA":
            return
            
        # Título
        subtitulo = self.fuente_label.render("Productos del CFDI", True, self.color_texto)
        self.screen.blit(subtitulo, (self.x + 30, self.y + int(self.alto * 0.2)))
        
        # Información del emisor
        info_lines = [
            f"Emisor: {self.empresa['nombre']}",
            f"RFC Emisor: {self.empresa['rfc']}",
            f"Régimen: {self.empresa['regimen_fiscal']}",
            "",
            "Los productos se cargarán automáticamente del último ticket generado.",
            "Incluye claves SAT y datos fiscales requeridos."
        ]
        
        y_offset = self.y + int(self.alto * 0.25)
        for line in info_lines:
            if line:
                color = self.color_texto if not line.startswith("Los productos") else self.GRAY
                text = self.fuente_input.render(line, True, color)
                self.screen.blit(text, (self.x + 30, y_offset))
            y_offset += 25

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
                nombre = self.inputs[0]["value"]
                apellido_paterno = self.inputs[1]["value"]
                apellido_materno = self.inputs[2]["value"]
                fecha_nacimiento = self.inputs[3]["value"]
                rfc = self.inputs[4]["value"]
                
                # Validar campos obligatorios
                if not all([nombre, apellido_paterno, apellido_materno, fecha_nacimiento, rfc]):
                    self.error_message = "Todos los campos son obligatorios"
                    self.error_timer = 180
                    return
                
                # Validar fecha y RFC
                fecha_valida, mensaje_fecha = self.validar_fecha_nacimiento(fecha_nacimiento)
                if not fecha_valida:
                    self.error_message = f"Error en fecha: {mensaje_fecha}"
                    self.error_timer = 180
                    return
                    
                rfc_valido, mensaje_rfc = self.validar_rfc_completo(
                    rfc, nombre, apellido_paterno, apellido_materno, fecha_nacimiento
                )
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
                    self.error_message = "No se encontraron productos en el ticket"
                    self.error_timer = 180
                    return
                
                # Generar CFDI y enviar
                pdf_path = self.generar_factura_pdf(productos)
                if pdf_path and self.enviar_correo(self.cliente["correo"], pdf_path):
                    self.error_message = "¡CFDI generado y enviado exitosamente!"
                    self.error_timer = 180
                    return True
                else:
                    self.error_message = "Error al generar o enviar el CFDI"
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
            # Buscar automáticamente el último ticket generado
            ultimo_ticket = self.obtener_ultimo_ticket()
            if ultimo_ticket:
                print(f"Procesando último ticket: {ultimo_ticket}")
                productos = self.leer_productos_de_ticket_pdf(ultimo_ticket)
            else:
                print("No se encontró ningún ticket para procesar")
                productos = []
        
        # Marcar como embebido cuando se llama desde POS
        self.is_embedded = True
        
        self.setup()
        await self.main_loop()
        
        # Al salir del loop, limpiar referencias
        return