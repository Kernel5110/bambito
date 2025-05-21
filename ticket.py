import pygame
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
        Limpia la lista de productos del ticket.
        """
        self.productos.clear()

    def eliminar_producto(self, nombre):
        """
        Elimina un producto del ticket por su nombre.

        :param nombre: Nombre del producto a eliminar.
        """
        self.productos = [prod for prod in self.productos if prod["nombre"] != nombre]

    def guardar_pdf(self, ruta):
        """
        Guarda el ticket como un archivo PDF en la ruta especificada.

        :param ruta: Ruta donde se guardará el archivo PDF.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 18)
        pdf.cell(0, 10, self.nombre_panaderia, ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("helvetica", "", 12)
        pdf.cell(0, 10, "Benito Juarez #106, Oaxaca, Oax", ln=True, align="C")
        pdf.cell(0, 10, "Tel. 9513060854", ln=True, align="C")
        pdf.cell(0, 10, "Ticket de compra", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(80, 10, "Producto", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(40, 10, "Precio Unitario", 1)
        pdf.cell(40, 10, "Subtotal", 1)
        pdf.ln()
        pdf.set_font("helvetica", "", 12)
        subtotal = 0
        for prod in self.productos:
            nombre = prod["nombre"]
            cantidad = int(prod["unidades"])
            precio_unitario = float(prod["precio"])
            subtotal_prod = cantidad * precio_unitario
            subtotal += subtotal_prod
            pdf.cell(80, 10, nombre, 1)
            pdf.cell(30, 10, str(cantidad), 1, align="C")
            pdf.cell(40, 10, f"${precio_unitario:.2f}", 1, align="R")
            pdf.cell(40, 10, f"${subtotal_prod:.2f}", 1, align="R")
            pdf.ln()
        pdf.set_font("helvetica", "B", 12)
        iva = subtotal * 0.16  # IVA del 16%
        total = subtotal + iva
        pdf.cell(150, 10, "SUBTOTAL", 1)
        pdf.cell(40, 10, f"${subtotal:.2f}", 1, align="R")
        pdf.ln()
        pdf.cell(150, 10, "IVA (16%)", 1)
        pdf.cell(40, 10, f"${iva:.2f}", 1, align="R")
        pdf.ln()
        pdf.cell(150, 10, "TOTAL", 1)
        pdf.cell(40, 10, f"${total:.2f}", 1, align="R")
        pdf.ln(20)
        pdf.set_font("helvetica", "I", 10)
        pdf.cell(0, 10, self.pie_pagina, ln=True, align="C")
        pdf.output(ruta)
        print(f"Ticket guardado en: {ruta}")
        self.limpiar()

    def dibujar(self, surface, x, y, w, h, fuente_titulo, fuente_producto, fuente_ticket, colores):
        """
        Dibuja el ticket en una superficie de Pygame.

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
        # colores: dict con claves "fondo", "borde", "texto"
        pygame.draw.rect(surface, colores["fondo"], (x, y, w, h), border_radius=20)
        pygame.draw.rect(surface, colores["borde"], (x, y, w, h), width=2, border_radius=20)

        # Encabezado: Título centrado
        titulo = fuente_titulo.render(self.nombre_panaderia, True, colores["texto"])
        titulo_x = x + (w - titulo.get_width()) // 2
        surface.blit(titulo, (titulo_x, y + 10))

        # Fecha (alineada a la izquierda)
        fecha_str = self.fecha.strftime("%d/%m/%Y %H:%M")
        fecha = fuente_ticket.render(fecha_str, True, colores["texto"])
        surface.blit(fecha, (x + 20, y + 60))

        # Columnas
        col_y = y + 100
        headers = ["Producto", "Cant.", "P. Unit.", "Subtotal"]
        col_xs = [x + 30, x + 350, x + 450, x + 570]
        for i, header in enumerate(headers):
            header_text = fuente_producto.render(header, True, colores["texto"])
            surface.blit(header_text, (col_xs[i], col_y))

        # Productos
        row_y = col_y + 35
        for prod in self.productos:
            nombre = fuente_ticket.render(prod["nombre"], True, colores["texto"])
            unidades = fuente_ticket.render(str(prod["unidades"]), True, colores["texto"])

            # Convertir a float para asegurar compatibilidad
            precio_valor = float(prod["precio"])
            unidades_valor = int(prod["unidades"])

            precio = fuente_ticket.render(f"${precio_valor:.2f}", True, colores["texto"])
            subtotal = fuente_ticket.render(f"${unidades_valor * precio_valor:.2f}", True, colores["texto"])

            surface.blit(nombre, (col_xs[0], row_y))
            surface.blit(unidades, (col_xs[1], row_y))
            surface.blit(precio, (col_xs[2], row_y))
            surface.blit(subtotal, (col_xs[3], row_y))
            row_y += 30

        # Línea y total
        pygame.draw.line(surface, colores["borde"], (x + 20, y + h - 100), (x + w - 20, y + h - 100), 2)
        total_text = fuente_titulo.render(f"Total: ${self.calcular_total():.2f}", True, colores["texto"])
        surface.blit(total_text, (x + 30, y + h - 80))

        # Pie de página
        pie = fuente_ticket.render(self.pie_pagina, True, colores["texto"])
        surface.blit(pie, (x + 30, y + h - 50))
        
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