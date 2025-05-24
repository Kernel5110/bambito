import pygame
import os
from datetime import datetime
from fpdf import FPDF
from decimal import Decimal

class Ticket:
    def __init__(self, nombre_panaderia="Panadería Bambi"):
        """
        Inicializa una instancia de la clase Ticket.

        :param nombre_panaderia: Nombre de la panadería. Por defecto es "Panadería Bambi".
        """
        self.nombre_panaderia = nombre_panaderia
        self.fecha = datetime.now()
        self.productos = []  # Lista de productos, cada uno es un diccionario: {"nombre":..., "unidades":..., "precio":..., "id":...}
        self.pie_pagina = "¡Gracias por su compra!"
        self.tipo_pago = "Efectivo"  # Por defecto es efectivo
        self.efectivo_recibido = 0.0  # Monto de efectivo recibido
        self.cambio = 0.0  # Cambio a entregar

    def crear_nombre_archivo(self):
        """
        Crea el nombre del archivo del ticket con formato: ticket(YYYYMMDD_HHMMSS).pdf
        
        :return: Nombre del archivo con formato específico
        """
        timestamp = self.fecha.strftime("%Y%m%d_%H%M%S")
        return f"ticket({timestamp}).pdf"

    def crear_carpeta_tickets(self):
        """
        Crea la carpeta 'tickets' si no existe
        
        :return: Ruta de la carpeta tickets
        """
        carpeta_tickets = "tickets"
        if not os.path.exists(carpeta_tickets):
            os.makedirs(carpeta_tickets)
            print(f"Carpeta '{carpeta_tickets}' creada exitosamente.")
        return carpeta_tickets

    def obtener_ruta_completa(self):
        """
        Obtiene la ruta completa donde se guardará el ticket
        
        :return: Ruta completa del archivo
        """
        carpeta = self.crear_carpeta_tickets()
        nombre_archivo = self.crear_nombre_archivo()
        return os.path.join(carpeta, nombre_archivo)

    def agregar_producto(self, nombre, unidades, precio, id_producto):
        """
        Agrega un producto al ticket. Si el producto ya existe, suma las unidades.

        :param nombre: Nombre del producto.
        :param unidades: Número de unidades del producto.
        :param precio: Precio unitario del producto.
        :param id_producto: Identificador único del producto.
        """
        # Convertir valores a tipos nativos para evitar problemas con Decimal
        unidades = int(unidades)
        precio = float(precio) if not isinstance(precio, Decimal) else float(precio)

        # Si el producto ya está, suma unidades
        for prod in self.productos:
            if prod["nombre"] == nombre and prod["precio"] == precio and prod["id"] == id_producto:
                prod["unidades"] += unidades
                return
        self.productos.append({"nombre": nombre, "unidades": unidades, "precio": precio, "id": id_producto})

    def obtener_cantidad_producto(self, nombre):
        """
        Obtiene la cantidad actual de un producto en el ticket buscando por su nombre.
        
        Args:
            nombre (str): Nombre del producto a buscar
            
        Returns:
            int: Cantidad del producto en el ticket; 0 si no se encuentra o si hay un error
        """
        for producto in self.productos:
            if not isinstance(producto, dict):
                continue  # Saltar si no es un diccionario
            if producto.get("nombre", "").lower() == nombre.lower():
                return producto.get("unidades", 0) 
        return 0

    def buscar_producto_por_nombre(self, nombre):
        """
        Verifica si un producto con el nombre dado está en la lista de productos.
        
        Args:
            nombre (str): Nombre del producto a buscar
            
        Returns:
            bool: True si el producto está en la lista, False si no lo está
        """
        for producto in self.productos:
            if producto["nombre"].lower() == nombre.lower():
                return True
        return False

    def calcular_total(self):
        """
        Calcula el total del ticket sumando el subtotal de cada producto.

        :return: Total del ticket.
        """
        total = 0
        for prod in self.productos:
            # Asegurar que las operaciones sean entre tipos compatibles
            precio = float(prod["precio"])
            unidades = int(prod["unidades"])
            total += unidades * precio
        return total

    def limpiar(self):
        """
        Limpia la lista de productos del ticket y reinicia valores de pago.
        """
        self.productos.clear()
        self.tipo_pago = "Efectivo"
        self.efectivo_recibido = 0.0
        self.cambio = 0.0

    def eliminar_producto(self, nombre):
        """
        Elimina un producto del ticket por su nombre.

        :param nombre: Nombre del producto a eliminar.
        """
        self.productos = [prod for prod in self.productos if prod["nombre"] != nombre]

    def guardar_pdf(self, ruta=None):
        """
        Guarda el ticket como un archivo PDF en formato de ticket de venta (angosto).
        Si no se especifica ruta, se guarda automáticamente en la carpeta 'tickets'.

        :param ruta: Ruta donde se guardará el archivo PDF. Si es None, usa la ruta automática.
        :return: Ruta donde se guardó el archivo
        """
        # Si no se especifica ruta, usar la ruta automática
        if ruta is None:
            ruta_final = self.obtener_ruta_completa()
        else:
            ruta_final = ruta
        
        # Configurar página angosta como ticket de venta (80mm de ancho aproximadamente)
        pdf = FPDF(unit='mm', format=(80, 200))  # 80mm ancho, 200mm alto inicial
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=10)
        
        # Configurar márgenes pequeños
        pdf.set_margins(5, 5, 5)
        
        # ENCABEZADO
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, self.nombre_panaderia, ln=True, align="C")
        
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 4, "Benito Juarez #106", ln=True, align="C")
        pdf.cell(0, 4, "Oaxaca, Oax", ln=True, align="C")
        pdf.cell(0, 4, "Tel. 9513060854", ln=True, align="C")
        
        # Línea separadora
        pdf.ln(2)
        pdf.cell(0, 1, "="*40, ln=True, align="C")
        pdf.ln(1)
        
        # INFORMACIÓN DE VENTA
        fecha_hora = self.fecha.strftime("%d/%m/%Y %H:%M:%S")
        pdf.set_font("Arial", "", 8)
        pdf.cell(0, 4, f"Fecha: {fecha_hora}", ln=True, align="L")
        pdf.cell(0, 4, f"Cajero: Sistema POS", ln=True, align="L")
        
        # Número de ticket
        numero_ticket = self.crear_nombre_archivo().replace('.pdf', '').replace('ticket(', '').replace(')', '')
        pdf.cell(0, 4, f"Ticket: {numero_ticket}", ln=True, align="L")
        
        pdf.ln(2)
        pdf.cell(0, 1, "-"*40, ln=True, align="C")
        pdf.ln(1)
        
        # PRODUCTOS
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 4, "PRODUCTOS", ln=True, align="C")
        pdf.ln(1)
        
        subtotal_general = 0
        pdf.set_font("Arial", "", 8)
        
        for prod in self.productos:
            nombre = prod["nombre"]
            cantidad = int(prod["unidades"])
            precio_unitario = float(prod["precio"])
            subtotal_prod = cantidad * precio_unitario
            subtotal_general += subtotal_prod
            
            # Nombre del producto
            if len(nombre) > 25:
                nombre = nombre[:22] + "..."
            pdf.cell(0, 4, nombre, ln=True, align="L")
            
            # Cantidad x Precio = Subtotal
            linea_detalle = f"{cantidad} x ${precio_unitario:.2f} = ${subtotal_prod:.2f}"
            pdf.cell(0, 4, linea_detalle, ln=True, align="R")
            pdf.ln(1)
        
        # TOTALES
        pdf.ln(1)
        pdf.cell(0, 1, "-"*40, ln=True, align="C")
        pdf.ln(1)
        
        iva = subtotal_general * 0.16  # IVA del 16%
        total_con_iva = subtotal_general + iva
        
        pdf.set_font("Arial", "", 9)
        pdf.cell(35, 4, "SUBTOTAL:", 0, 0, 'L')
        pdf.cell(0, 4, f"${subtotal_general:.2f}", ln=True, align="R")
        
        pdf.cell(35, 4, "IVA (16%):", 0, 0, 'L')
        pdf.cell(0, 4, f"${iva:.2f}", ln=True, align="R")
        
        pdf.set_font("Arial", "B", 11)
        pdf.cell(35, 6, "TOTAL:", 0, 0, 'L')
        pdf.cell(0, 6, f"${total_con_iva:.2f}", ln=True, align="R")
        
        # INFORMACIÓN DE PAGO
        pdf.ln(2)
        pdf.cell(0, 1, "="*40, ln=True, align="C")
        pdf.ln(1)
        
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 5, f"PAGO: {self.tipo_pago.upper()}", ln=True, align="C")
        
        if self.tipo_pago == "Efectivo" and self.efectivo_recibido > 0:
            pdf.set_font("Arial", "", 8)
            pdf.cell(35, 4, "Recibido:", 0, 0, 'L')
            pdf.cell(0, 4, f"${self.efectivo_recibido:.2f}", ln=True, align="R")
            
            pdf.cell(35, 4, "Cambio:", 0, 0, 'L')
            pdf.cell(0, 4, f"${self.cambio:.2f}", ln=True, align="R")
        
        # PIE DE PÁGINA
        pdf.ln(3)
        pdf.cell(0, 1, "="*40, ln=True, align="C")
        pdf.ln(2)
        
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 4, self.pie_pagina, ln=True, align="C")
        pdf.cell(0, 4, "Conserve su ticket", ln=True, align="C")
        
        # Código de barras simulado (opcional)
        pdf.ln(2)
        pdf.set_font("Arial", "", 6)
        ticket_id = f"TKT{self.fecha.strftime('%Y%m%d%H%M%S')}"
        pdf.cell(0, 3, ticket_id, ln=True, align="C")
        
        # Guardar el archivo
        try:
            pdf.output(ruta_final)
            print(f"Ticket guardado en: {ruta_final}")
            # NO limpiar aquí para permitir múltiples operaciones con el mismo ticket
            return ruta_final
        except Exception as e:
            print(f"Error al guardar el ticket: {e}")
            return None

    def dibujar(self, surface, x, y, w, h, fuente_titulo, fuente_producto, fuente_ticket, colores):
        """
        Dibuja el ticket en una superficie de Pygame con formato mejorado y más angosto.

        :param surface: Superficie de Pygame donde se dibujará el ticket.
        :param x: Coordenada x de la posición inicial.
        :param y: Coordenada y de la posición inicial.
        :param w: Ancho del área de dibujo.
        :param h: Alto del área de dibujo.
        :param fuente_titulo: Fuente para el título.
        :param fuente_producto: Fuente para los nombres de los productos.
        :param fuente_ticket: Fuente para el resto del texto.
        :param colores: Diccionario con colores para el fondo, borde y texto.
        """
        # Hacer el ticket más angosto (formato ticket de venta)
        ticket_w = min(w, 280)  # Máximo 280 píxeles de ancho
        ticket_x = x + (w - ticket_w) // 2  # Centrar horizontalmente
        
        # Fondo del ticket con bordes redondeados
        pygame.draw.rect(surface, colores["fondo"], (ticket_x, y, ticket_w, h), border_radius=15)
        pygame.draw.rect(surface, colores["borde"], (ticket_x, y, ticket_w, h), width=2, border_radius=15)
        
        current_y = y + 15
        
        # ENCABEZADO - Nombre de la panadería
        titulo = fuente_titulo.render(self.nombre_panaderia, True, colores["texto"])
        titulo_x = ticket_x + (ticket_w - titulo.get_width()) // 2
        surface.blit(titulo, (titulo_x, current_y))
        current_y += titulo.get_height() + 5
        
        # Información del negocio
        fuente_info = pygame.font.Font(None, 18)
        info_lines = [
            "Benito Juarez #106",
            "Oaxaca, Oax",
            "Tel. 9513060854"
        ]
        
        for line in info_lines:
            text = fuente_info.render(line, True, colores["texto"])
            text_x = ticket_x + (ticket_w - text.get_width()) // 2
            surface.blit(text, (text_x, current_y))
            current_y += text.get_height() + 2
        
        # Línea separadora
        current_y += 8
        pygame.draw.line(surface, colores["borde"], 
                        (ticket_x + 15, current_y), 
                        (ticket_x + ticket_w - 15, current_y), 2)
        current_y += 10
        
        # Fecha y hora
        fecha_str = self.fecha.strftime("%d/%m/%Y %H:%M:%S")
        fecha_text = fuente_ticket.render(f"Fecha: {fecha_str}", True, colores["texto"])
        surface.blit(fecha_text, (ticket_x + 15, current_y))
        current_y += fecha_text.get_height() + 5
        
        # Tipo de pago
        pago_text = fuente_ticket.render(f"Pago: {self.tipo_pago}", True, colores["texto"])
        surface.blit(pago_text, (ticket_x + 15, current_y))
        current_y += pago_text.get_height() + 10
        
        # Línea separadora productos
        pygame.draw.line(surface, colores["borde"], 
                        (ticket_x + 15, current_y), 
                        (ticket_x + ticket_w - 15, current_y), 1)
        current_y += 8
        
        # Encabezado "PRODUCTOS"
        productos_header = fuente_producto.render("PRODUCTOS", True, colores["texto"])
        header_x = ticket_x + (ticket_w - productos_header.get_width()) // 2
        surface.blit(productos_header, (header_x, current_y))
        current_y += productos_header.get_height() + 8
        
        # Lista de productos
        subtotal_general = 0
        fuente_pequeña = pygame.font.Font(None, 20)
        
        for prod in self.productos:
            nombre = prod["nombre"]
            cantidad = int(prod["unidades"])
            precio_unitario = float(prod["precio"])
            subtotal_prod = cantidad * precio_unitario
            subtotal_general += subtotal_prod
            
            # Truncar el nombre si es muy largo
            if len(nombre) > 20:
                nombre = nombre[:17] + "..."
            
            # Nombre del producto
            nombre_text = fuente_ticket.render(nombre, True, colores["texto"])
            surface.blit(nombre_text, (ticket_x + 15, current_y))
            current_y += nombre_text.get_height() + 2
            
            # Cantidad x Precio = Subtotal
            detalle = f"{cantidad} x ${precio_unitario:.2f} = ${subtotal_prod:.2f}"
            detalle_text = fuente_pequeña.render(detalle, True, colores["texto"])
            detalle_x = ticket_x + ticket_w - detalle_text.get_width() - 15
            surface.blit(detalle_text, (detalle_x, current_y))
            current_y += detalle_text.get_height() + 8
        
        # Línea separadora totales
        current_y += 5
        pygame.draw.line(surface, colores["borde"], 
                        (ticket_x + 15, current_y), 
                        (ticket_x + ticket_w - 15, current_y), 1)
        current_y += 10
        
        # Cálculos de totales
        iva = subtotal_general * 0.16
        total_con_iva = subtotal_general + iva
        
        # Subtotal
        subtotal_text = fuente_ticket.render("Subtotal:", True, colores["texto"])
        subtotal_valor = fuente_ticket.render(f"${subtotal_general:.2f}", True, colores["texto"])
        surface.blit(subtotal_text, (ticket_x + 15, current_y))
        surface.blit(subtotal_valor, (ticket_x + ticket_w - subtotal_valor.get_width() - 15, current_y))
        current_y += subtotal_text.get_height() + 3
        
        # IVA
        iva_text = fuente_ticket.render("IVA (16%):", True, colores["texto"])
        iva_valor = fuente_ticket.render(f"${iva:.2f}", True, colores["texto"])
        surface.blit(iva_text, (ticket_x + 15, current_y))
        surface.blit(iva_valor, (ticket_x + ticket_w - iva_valor.get_width() - 15, current_y))
        current_y += iva_text.get_height() + 5
        
        # Total (resaltado)
        fuente_total = pygame.font.Font(None, 32)
        total_text = fuente_total.render("TOTAL:", True, colores["texto"])
        total_valor = fuente_total.render(f"${total_con_iva:.2f}", True, (0, 128, 0))  # Verde para el total
        
        surface.blit(total_text, (ticket_x + 15, current_y))
        surface.blit(total_valor, (ticket_x + ticket_w - total_valor.get_width() - 15, current_y))
        current_y += total_text.get_height() + 10
        
        # Información de pago en efectivo
        if self.tipo_pago == "Efectivo" and self.efectivo_recibido > 0:
            pygame.draw.line(surface, colores["borde"], 
                            (ticket_x + 15, current_y), 
                            (ticket_x + ticket_w - 15, current_y), 1)
            current_y += 8
            
            recibido_text = fuente_ticket.render("Recibido:", True, colores["texto"])
            recibido_valor = fuente_ticket.render(f"${self.efectivo_recibido:.2f}", True, colores["texto"])
            surface.blit(recibido_text, (ticket_x + 15, current_y))
            surface.blit(recibido_valor, (ticket_x + ticket_w - recibido_valor.get_width() - 15, current_y))
            current_y += recibido_text.get_height() + 3
            
            cambio_text = fuente_ticket.render("Cambio:", True, colores["texto"])
            cambio_valor = fuente_ticket.render(f"${self.cambio:.2f}", True, colores["texto"])
            surface.blit(cambio_text, (ticket_x + 15, current_y))
            surface.blit(cambio_valor, (ticket_x + ticket_w - cambio_valor.get_width() - 15, current_y))
            current_y += cambio_text.get_height() + 10
        
        # Línea final
        pygame.draw.line(surface, colores["borde"], 
                        (ticket_x + 15, current_y), 
                        (ticket_x + ticket_w - 15, current_y), 2)
        current_y += 10
        
        # Pie de página
        fuente_pie = pygame.font.Font(None, 22)
        pie = fuente_pie.render(self.pie_pagina, True, colores["texto"])
        pie_x = ticket_x + (ticket_w - pie.get_width()) // 2
        surface.blit(pie, (pie_x, current_y))
        current_y += pie.get_height() + 5
        
        conserve_text = fuente_pie.render("Conserve su ticket", True, colores["texto"])
        conserve_x = ticket_x + (ticket_w - conserve_text.get_width()) // 2
        surface.blit(conserve_text, (conserve_x, current_y))
        
    def eliminar_producto(self, indice):
        """
        Elimina un producto del ticket por su índice
        
        Args:
            indice (int): Índice del producto a eliminar
        
        Returns:
            bool: True si el producto fue eliminado, False si no existe
        """
        if 0 <= indice < len(self.productos):
            self.productos.pop(indice)
            return True
        return False