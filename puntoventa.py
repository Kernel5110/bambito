import pygame
import os
from ticket import Ticket
from conexion import Conexion
import smtplib
from email.message import EmailMessage
from datetime import datetime
import re

# Constantes para colores y fuentes
COLOR_FONDO = (241, 236, 227)
COLOR_TEXTO = (0, 0, 0)
COLOR_BOTON = (0, 120, 220)
COLOR_BOTON_BORDE = (0, 80, 180)
COLOR_ALERTA = (255, 200, 200)
COLOR_ALERTA_BORDE = (200, 0, 0)

class InputBox:
    def __init__(self, x, y, ancho, alto, text='', font=None, numeric=False):
        pygame.font.init()
        self.FONDO = COLOR_FONDO
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.font = font or pygame.font.SysFont("Open Sans", 24)
        self.txt_surface = self.font.render(text, True, COLOR_TEXTO)
        self.active = False
        self.numeric = numeric

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if self.numeric:
                    if event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.text):
                        self.text += event.unicode
                else:
                    if len(self.text) < 50 and event.unicode.isprintable():
                        self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, COLOR_TEXTO)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_value(self):
        return self.text

class PuntoVenta:
    def __init__(self, x=0, y=0, ancho=1900, alto=1000, id_empleado=1):
        pygame.font.init()
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

        # Colores
        self.BLANCO = (255, 255, 255)
        self.NEGRO = COLOR_TEXTO
        self.AZUL_CLARO = COLOR_FONDO
        self.BORDE = (204, 208, 216)
        self.GRIS_CLARO = (230, 230, 230)

        # Fuentes escaladas
        def fuente_relativa(base_size):
            scale = min(self.ancho / 1585, self.alto / 870)
            return int(base_size * scale)

        self.fuente_producto = pygame.font.SysFont("Open Sans", fuente_relativa(24))
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", fuente_relativa(36), bold=True)
        self.fuente_ticket = pygame.font.SysFont("Open Sans", fuente_relativa(28))
        self.fuente_busqueda = pygame.font.SysFont("Open Sans", fuente_relativa(28))

        self.productos = self.cargar_productos_desde_db()
        self.imagenes_productos = []
        for prod in self.productos:
            ruta = prod["imagen"]
            if ruta and os.path.exists(ruta):
                imagen = pygame.image.load(ruta).convert_alpha()
                imagen = pygame.transform.smoothscale(imagen, (int(80 * self.ancho / 1585), int(80 * self.alto / 870)))
            else:
                imagen = pygame.Surface((int(80 * self.ancho / 1585), int(80 * self.alto / 870)))
                imagen.fill((200, 200, 200))
            self.imagenes_productos.append(imagen)

        self.ticket = Ticket(nombre_panaderia="Panadería Bambi")
        self.product_rects = []
        self.busqueda_texto = ""
        self.busqueda_activa = False
        self.boton_pagar_rect = None
        self.boton_agregar_producto_rect = None
        self.alerta = ""
        self.id_empleado = id_empleado
        self.mostrando_modal_pago = False
        self.efectivo_box = None
        self.efectivo_mensaje = ""
        self.efectivo_cambio = 0.0
        self.mostrando_formulario = False
        self.formulario_boxes = []
        self.formulario_labels = []
        self.formulario_btn_guardar = None
        self.formulario_mensaje = ""

    def cargar_productos_desde_db(self):
        try:
            conexion = Conexion()
            query = """
                SELECT ID_CatProducto, Nombre_prod AS nombre, Precio AS precio, Imagen AS imagen, Stock
                FROM CatProducto
                WHERE Estado='Disponible' AND Stock > 0
            """
            productos = conexion.consultar(query)
            for prod in productos:
                if not prod["imagen"]:
                    prod["imagen"] = "imagenes/log.png"
            return productos
        except Exception as e:
            print(f"Error en PuntoVenta.cargar_productos_desde_db: {e}")
            return []

    def mostrar_alerta(self, mensaje):
        self.alerta = mensaje
        print("ALERTA:", mensaje)

    def filtrar_productos(self):
        if not self.busqueda_texto:
            return list(enumerate(self.productos))
        texto = self.busqueda_texto.lower()
        return [(i, prod) for i, prod in enumerate(self.productos) if texto in prod["nombre"].lower()]

    def dibujar_alerta(self, surface):
        if self.alerta:
            rect = pygame.Rect(self.x + int(0.05 * self.ancho), self.y + int(0.03 * self.alto), int(0.5 * self.ancho), int(0.06 * self.alto))
            pygame.draw.rect(surface, COLOR_ALERTA, rect, border_radius=10)
            pygame.draw.rect(surface, COLOR_ALERTA_BORDE, rect, 2, border_radius=10)
            fuente_alerta = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
            texto = fuente_alerta.render(self.alerta, True, COLOR_ALERTA_BORDE)
            surface.blit(texto, (rect.x + 20, rect.y + 10))

    def dibujar_campo_busqueda(self, surface, x, y, w, h):
        color_fondo = self.BLANCO
        color_borde = (100, 100, 100) if self.busqueda_activa else (180, 180, 180)
        pygame.draw.rect(surface, color_fondo, (x, y, w, h), border_radius=10)
        pygame.draw.rect(surface, color_borde, (x, y, w, h), 2, border_radius=10)
        texto = self.busqueda_texto if self.busqueda_texto else "Buscar producto..."
        color_texto = COLOR_TEXTO if self.busqueda_texto else (150, 150, 150)
        render = self.fuente_busqueda.render(texto, True, color_texto)
        surface.blit(render, (x + 10, y + (h - render.get_height()) // 2))

        # Botón "Agregar producto"
        btn_w, btn_h = int(0.18 * self.ancho), h
        btn_x = x + w + int(0.03 * self.ancho)
        btn_y = y
        self.boton_agregar_producto_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, COLOR_BOTON, self.boton_agregar_producto_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BOTON_BORDE, self.boton_agregar_producto_rect, 2, border_radius=8)
        btn_text = self.fuente_busqueda.render("Agregar producto", True, self.BLANCO)
        surface.blit(btn_text, (btn_x + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

    def dibujar_producto(self, surface, x, y, producto, imagen):
        ancho = int(0.16 * self.ancho)
        alto = int(0.13 * self.alto)
        margen = int(0.01 * self.ancho)
        rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(surface, self.GRIS_CLARO, rect, border_radius=12)
        pygame.draw.rect(surface, self.BORDE, rect, 2, border_radius=12)
        img_rect = imagen.get_rect()
        img_rect.centerx = rect.centerx
        img_rect.top = y + margen
        surface.blit(imagen, img_rect)
        nombre_render = self.fuente_producto.render(producto["nombre"], True, COLOR_TEXTO)
        nombre_x = rect.centerx - nombre_render.get_width() // 2
        nombre_y = img_rect.bottom + 5
        surface.blit(nombre_render, (nombre_x, nombre_y))
        precio_str = f"${producto['precio']:.2f}"
        precio_render = self.fuente_ticket.render(precio_str, True, COLOR_TEXTO)
        precio_x = rect.centerx - precio_render.get_width() // 2
        precio_y = nombre_y + nombre_render.get_height() + 2
        surface.blit(precio_render, (precio_x, precio_y))
        return rect

    def calcular_total_con_iva(self):
        total = float(self.ticket.calcular_total())
        return total * 1.16

    def dibujar_ticket(self, surface):
        # Definir las dimensiones y posición del ticket
        x = self.x + int(0.65 * self.ancho)
        y = self.y + int(0.15 * self.alto)
        w = int(0.33 * self.ancho)
        h = int(0.7 * self.alto)

        # Dibujar el fondo del ticket
        pygame.draw.rect(surface, self.BLANCO, (x, y, w, h), border_radius=12)
        pygame.draw.rect(surface, self.BORDE, (x, y, w, h), 2, border_radius=12)

        # Dibujar el título del ticket
        titulo_ticket = self.fuente_titulo.render("Ticket de Compra", True, COLOR_TEXTO)
        surface.blit(titulo_ticket, (x + int(0.05 * w), y + int(0.03 * h)))

        # Dibujar la línea divisora debajo del título
        pygame.draw.line(surface, self.BORDE, (x + int(0.03 * w), y + int(0.1 * h)), (x + w - int(0.03 * w), y + int(0.1 * h)), 2)

        # Dibujar encabezados de la tabla
        headers = ["Nombre", "Unidades", "Precio"]
        header_y = y + int(0.12 * h)
        col_width = w // len(headers)
        for i, header in enumerate(headers):
            header_render = self.fuente_ticket.render(header, True, COLOR_TEXTO)
            surface.blit(header_render, (x + i * col_width + int(0.03 * col_width), header_y))

        # Dibujar la línea divisora después de los encabezados
        pygame.draw.line(surface, self.BORDE, (x, header_y + int(0.04 * h)), (x + w, header_y + int(0.04 * h)), 2)

        # Dibujar los productos en formato de tabla
        y_offset = header_y + int(0.06 * h)
        self.botones_eliminar = []  # Inicializar la lista de botones de eliminar
        for producto in self.ticket.productos:
            nombre_render = self.fuente_ticket.render(producto['nombre'], True, COLOR_TEXTO)
            unidades_render = self.fuente_ticket.render(str(producto['unidades']), True, COLOR_TEXTO)
            precio_render = self.fuente_ticket.render(f"${producto['precio'] * producto['unidades']:.2f}", True, COLOR_TEXTO)

            surface.blit(nombre_render, (x + int(0.03 * col_width), y_offset))
            surface.blit(unidades_render, (x + col_width + int(0.03 * col_width), y_offset))
            surface.blit(precio_render, (x + 2 * col_width + int(0.03 * col_width), y_offset))

            y_offset += int(0.05 * h)

        # Dibujar la línea divisora antes del total
        pygame.draw.line(surface, self.BORDE, (x + int(0.03 * w), y + h - int(0.14 * h)), (x + w - int(0.03 * w), y + h - int(0.14 * h)), 2)

        # Dibujar el total sin IVA
        total_text = self.fuente_ticket.render(f"Total: ${self.ticket.calcular_total():.2f}", True, COLOR_TEXTO)
        surface.blit(total_text, (x + int(0.05 * w), y + h - int(0.11 * h)))

        # Dibujar el total con IVA
        total_iva = self.calcular_total_con_iva()
        total_iva_text = self.fuente_titulo.render(f"Total + IVA: ${total_iva:.2f}", True, (80, 80, 80))
        surface.blit(total_iva_text, (x + int(0.05 * w), y + h - int(0.07 * h)))

        # Dibujar el botón de pagar
        btn_w, btn_h = int(0.29 * w), int(0.11 * h)
        btn_x = x + w - btn_w - int(0.02 * w)
        btn_y = y + h - btn_h - int(0.12 * h)
        self.boton_pagar_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, (0, 180, 0), self.boton_pagar_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 120, 0), self.boton_pagar_rect, 2, border_radius=10)
        btn_text = self.fuente_producto.render("Pagar", True, self.BLANCO)
        surface.blit(btn_text, (btn_x + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

        # Dibujar el botón de enviar
        btn_env_w, btn_env_h = int(0.29 * w), int(0.11 * h)
        btn_env_x = x + int(0.01 * w)
        btn_env_y = y + h - btn_env_h - int(0.12 * h)
        self.boton_enviar_rect = pygame.Rect(btn_env_x, btn_env_y, btn_env_w, btn_env_h)
        pygame.draw.rect(surface, COLOR_BOTON, self.boton_enviar_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_BOTON_BORDE, self.boton_enviar_rect, 2, border_radius=10)
        btn_env_text = self.fuente_producto.render("Enviar", True, self.BLANCO)
        surface.blit(btn_env_text, (btn_env_x + (btn_env_w - btn_env_text.get_width()) // 2, btn_env_y + (btn_env_h - btn_env_text.get_height()) // 2))

        # Dibujar el botón de factura
        btn_factura_w, btn_factura_h = int(0.39 * w), int(0.11 * h)
        btn_factura_x = x + int(0.30 * w)
        btn_factura_y = y + h - btn_factura_h - int(0.12 * h)
        self.boton_factura_rect = pygame.Rect(btn_factura_x, btn_factura_y, btn_factura_w, btn_factura_h)
        pygame.draw.rect(surface, (0, 120, 220), self.boton_factura_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 80, 180), self.boton_factura_rect, 2, border_radius=10)
        btn_factura_text = self.fuente_producto.render("Generar Factura", True, self.BLANCO)
        surface.blit(btn_factura_text, (btn_factura_x + (btn_factura_w - btn_factura_text.get_width()) // 2, btn_factura_y + (btn_factura_h - btn_factura_text.get_height()) // 2))

    def dibujar_modal_pago(self, surface):
        modal_w, modal_h = int(0.35 * self.ancho), int(0.45 * self.alto)
        modal_x = self.x + (self.ancho - modal_w) // 2
        modal_y = self.y + (self.alto - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(surface, self.BLANCO, modal_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_BOTON, modal_rect, 3, border_radius=16)
        font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto), bold=True)
        titulo = font.render("Pago en efectivo", True, COLOR_TEXTO)
        surface.blit(titulo, (modal_x + 30, modal_y + 20))

        total_iva = self.calcular_total_con_iva()
        font_total = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        total_label = font_total.render(f"Total a pagar (con IVA): ${total_iva:.2f}", True, COLOR_TEXTO)
        surface.blit(total_label, (modal_x + 30, modal_y + 70))

        font_lbl = pygame.font.SysFont("Open Sans", int(0.028 * self.alto))
        efectivo_lbl = font_lbl.render("Efectivo recibido:", True, COLOR_TEXTO)
        surface.blit(efectivo_lbl, (modal_x + 30, modal_y + 120))
        input_y = modal_y + 115
        input_h = 45
        if not self.efectivo_box:
            self.efectivo_box = InputBox(
                modal_x + 220, input_y, 120, input_h,
                font=pygame.font.SysFont("Open Sans", 28), numeric=True
            )
        else:
            self.efectivo_box.x = modal_x + 220
            self.efectivo_box.y = input_y
            self.efectivo_box.ancho = 120
            self.efectivo_box.alto = input_h
            self.efectivo_box.rect = pygame.Rect(self.efectivo_box.x, self.efectivo_box.y, self.efectivo_box.ancho, self.efectivo_box.alto)
        self.efectivo_box.draw(surface)

        efectivo_str = self.efectivo_box.get_value()
        try:
            efectivo = float(efectivo_str) if efectivo_str else 0.0
        except Exception:
            efectivo = 0.0
        cambio = efectivo - total_iva
        self.efectivo_cambio = cambio

        cambio_lbl = font_lbl.render(f"Cambio: ${cambio:.2f}", True, (0, 120, 0) if cambio >= 0 else (200, 0, 0))
        surface.blit(cambio_lbl, (modal_x + 30, modal_y + 180))

        btn_w, btn_h = 120, 50
        btn_y = modal_y + modal_h - btn_h - 25
        btn_x_confirmar = modal_x + modal_w - btn_w - 40
        btn_x_cancelar = modal_x + 40

        self.boton_modal_confirmar = pygame.Rect(btn_x_confirmar, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, (0, 180, 0), self.boton_modal_confirmar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.boton_modal_confirmar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", 28, bold=True)
        btn_text = font_btn.render("Confirmar", True, self.BLANCO)
        surface.blit(btn_text, (btn_x_confirmar + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

        self.boton_modal_cancelar_pago = pygame.Rect(btn_x_cancelar, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, (220, 0, 0), self.boton_modal_cancelar_pago, border_radius=8)
        pygame.draw.rect(surface, (180, 0, 0), self.boton_modal_cancelar_pago, 2, border_radius=8)
        btn_text_canc = font_btn.render("Cancelar", True, self.BLANCO)
        surface.blit(btn_text_canc, (btn_x_cancelar + (btn_w - btn_text_canc.get_width()) // 2, btn_y + (btn_h - btn_text_canc.get_height()) // 2))

        if self.efectivo_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", 24)
            msg = font_msg.render(self.efectivo_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_x + 30, btn_y - 35))

    def dibujar_modal_correo(self, surface):
        modal_w, modal_h = int(0.45 * self.ancho), int(0.32 * self.alto)
        modal_x = self.x + (self.ancho - modal_w) // 2
        modal_y = self.y + (self.alto - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(surface, self.BLANCO, modal_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_BOTON, modal_rect, 3, border_radius=16)
        font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto), bold=True)
        titulo = font.render("Enviar ticket por correo", True, COLOR_TEXTO)
        surface.blit(titulo, (modal_x + 30, modal_y + 30))

        input_y = modal_y + 40 + titulo.get_height() + 20
        input_h = 50
        if not hasattr(self, "correo_box") or self.correo_box is None:
            self.correo_box = InputBox(
                modal_x + 40, input_y, modal_w - 80, input_h,
                font=pygame.font.SysFont("Open Sans", 32)
            )
        else:
            self.correo_box.x = modal_x + 40
            self.correo_box.y = input_y
            self.correo_box.ancho = modal_w - 80
            self.correo_box.alto = input_h
            self.correo_box.rect = pygame.Rect(self.correo_box.x, self.correo_box.y, self.correo_box.ancho, self.correo_box.alto)
        self.correo_box.draw(surface)

        btn_w, btn_h = 145, 55
        btn_y = modal_y + modal_h - btn_h - 25
        btn_x_enviar = modal_x + modal_w - btn_w - 40
        btn_x_cancelar = modal_x + 40

        self.boton_modal_enviar = pygame.Rect(btn_x_enviar, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, (0, 180, 0), self.boton_modal_enviar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.boton_modal_enviar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", 28, bold=True)
        btn_text = font_btn.render("Enviar", True, self.BLANCO)
        surface.blit(btn_text, (btn_x_enviar + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

        self.boton_modal_cancelar = pygame.Rect(btn_x_cancelar, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, (220, 0, 0), self.boton_modal_cancelar, border_radius=8)
        pygame.draw.rect(surface, (180, 0, 0), self.boton_modal_cancelar, 2, border_radius=8)
        btn_text_canc = font_btn.render("Cancelar", True, self.BLANCO)
        surface.blit(btn_text_canc, (btn_x_cancelar + (btn_w - btn_text_canc.get_width()) // 2, btn_y + (btn_h - btn_text_canc.get_height()) // 2))

        if hasattr(self, "correo_mensaje") and self.correo_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", 24)
            msg = font_msg.render(self.correo_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_x + 40, input_y + input_h + 18))

    def dibujar_punto_venta(self, surface):
        pygame.draw.rect(surface, self.AZUL_CLARO, (self.x, self.y, self.ancho, self.alto))
        titulo = self.fuente_titulo.render("Productos Disponibles", True, COLOR_TEXTO)
        surface.blit(titulo, (self.x + int(0.02 * self.ancho), self.y + int(0.02 * self.alto)))
        self.dibujar_alerta(surface)
        busq_x = self.x + int(0.02 * self.ancho)
        busq_y = self.y + int(0.08 * self.alto)
        busq_w = int(0.38 * self.ancho)
        busq_h = int(0.05 * self.alto)
        self.dibujar_campo_busqueda(surface, busq_x, busq_y, busq_w, busq_h)
        start_x = self.x + int(0.02 * self.ancho)
        start_y = self.y + int(0.15 * self.alto)
        spacing_x = int(0.19 * self.ancho)
        spacing_y = int(0.16 * self.alto)
        cols = 3
        self.product_rects = []
        productos_filtrados = self.filtrar_productos()
        for idx, (i_original, producto) in enumerate(productos_filtrados):
            col = idx % cols
            row = idx // cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            imagen = self.imagenes_productos[i_original]
            rect = self.dibujar_producto(surface, x, y, producto, imagen)
            self.product_rects.append((rect, i_original))
        self.dibujar_ticket(surface)
        self.busq_rect = pygame.Rect(busq_x, busq_y, busq_w, busq_h)
        if self.mostrando_formulario:
            self.dibujar_formulario_agregar_producto(surface)
        if getattr(self, "mostrando_modal_correo", False):
            self.dibujar_modal_correo(surface)
        if self.mostrando_modal_pago:
            self.dibujar_modal_pago(surface)

    def handle_event(self, event):
        if self.mostrando_modal_pago:
            self.efectivo_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.boton_modal_confirmar.collidepoint(event.pos):
                    total_iva = self.ticket.calcular_total()
                    total_iva *= 1.16  # Si tu total no incluye IVA, ajusta aquí
                    efectivo_str = self.efectivo_box.get_value()
                    try:
                        efectivo = float(efectivo_str)
                    except Exception:
                        efectivo = 0.0
                    if efectivo < total_iva:
                        self.efectivo_mensaje = "Efectivo insuficiente."
                    else:
                        exito = self.registrar_venta()
                        if exito:
                            self.ticket.guardar_pdf("ticket.pdf")
                            self.mostrar_alerta(f"Venta registrada. Cambio: ${efectivo - total_iva:.2f}")
                            self.productos = self.cargar_productos_desde_db()
                            self.mostrando_modal_pago = False
                            self.efectivo_box = None
                            self.efectivo_mensaje = ""
                        else:
                            self.efectivo_mensaje = "Error al registrar la venta."
                elif self.boton_modal_cancelar_pago.collidepoint(event.pos):
                    self.mostrando_modal_pago = False
                    self.efectivo_box = None
                    self.efectivo_mensaje = ""
            return

        if getattr(self, "mostrando_modal_correo", False):
            self.correo_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.boton_modal_enviar.collidepoint(event.pos):
                    correo = self.correo_box.get_value().strip()
                    if self.validar_correo(correo):
                        enviado = self.enviar_ticket_por_correo(correo)
                        if enviado:
                            self.correo_mensaje = "¡Ticket enviado!"
                            self.mostrando_modal_correo = False
                            self.mostrar_alerta("Ticket enviado correctamente.")
                        else:
                            self.correo_mensaje = "Error al enviar el correo."
                    else:
                        self.correo_mensaje = "Correo inválido."
                elif self.boton_modal_cancelar.collidepoint(event.pos):
                    self.mostrando_modal_correo = False
                    self.correo_mensaje = ""
            return

        if self.mostrando_formulario:
            for box in self.formulario_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.formulario_btn_guardar and self.formulario_btn_guardar.collidepoint(event.pos):
                    self.guardar_formulario_agregar_producto()
                elif self.formulario_btn_cancelar and self.formulario_btn_cancelar.collidepoint(event.pos):
                    self.mostrando_formulario = False
                return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if hasattr(self, "busq_rect") and self.busq_rect and self.busq_rect.collidepoint(mouse_x, mouse_y):
                self.busqueda_activa = True
            elif hasattr(self, "boton_agregar_producto_rect") and self.boton_agregar_producto_rect and self.boton_agregar_producto_rect.collidepoint(mouse_x, mouse_y):
                self.mostrar_formulario_agregar_producto()
            elif hasattr(self, "boton_enviar_rect") and self.boton_enviar_rect and self.boton_enviar_rect.collidepoint(mouse_x, mouse_y):
                self.mostrando_modal_correo = True
                self.correo_box = None
                self.correo_mensaje = ""
                return
            elif hasattr(self, "boton_factura_rect") and self.boton_factura_rect and self.boton_factura_rect.collidepoint(mouse_x, mouse_y):
                # --- Llamada a Factura al presionar "Generar Factura" ---
                try:
                    from factura import Factura
                    import asyncio
                    factura = Factura()
                    # Si tu clase Factura ya lee los productos del ticket.pdf, solo llama main()
                    asyncio.run(factura.main())
                    self.mostrar_alerta("Factura generada correctamente.")
                except Exception as e:
                    self.mostrar_alerta(f"Error al generar factura: {e}")
                return
            else:
                self.busqueda_activa = False
                for rect, idx in self.product_rects:
                    if rect and rect.collidepoint(mouse_x, mouse_y):
                        prod = self.productos[idx]
                        if self.verificar_stock(prod["ID_CatProducto"], 1):
                            self.ticket.agregar_producto(prod["nombre"], 1, prod["precio"], prod["ID_CatProducto"])
                            self.mostrar_alerta("")
                            print(f"Producto agregado al ticket: {prod['nombre']}")
                        else:
                            self.mostrar_alerta(f"No hay suficiente stock de '{prod['nombre']}'")
                if self.boton_pagar_rect and self.boton_pagar_rect.collidepoint(mouse_x, mouse_y):
                    if self.ticket.productos:
                        self.mostrando_modal_pago = True
                        self.efectivo_box = None
                        self.efectivo_mensaje = ""
                    else:
                        self.mostrar_alerta("El ticket está vacío.")
        if event.type == pygame.KEYDOWN and self.busqueda_activa:
            if event.key == pygame.K_BACKSPACE:
                self.busqueda_texto = self.busqueda_texto[:-1]
            elif event.key == pygame.K_RETURN:
                self.busqueda_activa = False
            elif event.key == pygame.K_ESCAPE:
                self.busqueda_texto = ""
            else:
                if len(self.busqueda_texto) < 30 and event.unicode.isprintable():
                    self.busqueda_texto += event.unicode

    def mostrar_formulario_agregar_producto(self):
        self.mostrando_formulario = True
        font = pygame.font.SysFont("Open Sans", int(0.024 * self.alto))
        x, y = self.x + int(0.25 * self.ancho), self.y + int(0.20 * self.alto)
        labels = [
            "Nombre", "Precio", "Stock", "Imagen", "Caducidad (YYYY-MM-DD)",
            "Sabor", "IVA", "Descripción"
        ]
        self.formulario_labels = []
        self.formulario_boxes = []
        for i, label in enumerate(labels):
            lbl = font.render(label + ":", True, COLOR_TEXTO)
            self.formulario_labels.append((lbl, (x, y + i * int(0.06 * self.alto))))
            numeric = label in ["Precio", "Stock", "IVA"]
            box = InputBox(x + int(0.15 * self.ancho), y + i * int(0.06 * self.alto), int(0.14 * self.ancho), int(0.045 * self.alto), font=font, numeric=numeric)
            self.formulario_boxes.append(box)
        self.formulario_btn_guardar = pygame.Rect(x, y + 10 + len(labels) * int(0.06 * self.alto), int(0.13 * self.ancho), int(0.06 * self.alto))
        self.formulario_btn_cancelar = pygame.Rect(x + int(0.15 * self.ancho), y + 10 + len(labels) * int(0.06 * self.alto), int(0.13 * self.ancho), int(0.06 * self.alto))
        self.formulario_mensaje = ""

    def dibujar_formulario_agregar_producto(self, surface):
        modal_rect = pygame.Rect(self.x + int(0.18 * self.ancho), self.y + int(0.10 * self.alto), int(0.45 * self.ancho), int(0.7 * self.alto))
        pygame.draw.rect(surface, (245, 245, 245), modal_rect, border_radius=18)
        pygame.draw.rect(surface, COLOR_BOTON, modal_rect, 3, border_radius=18)
        font = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        titulo = font.render("Agregar/Actualizar Producto", True, COLOR_TEXTO)
        surface.blit(titulo, (modal_rect.x + 30, modal_rect.y + 20))
        for (lbl, pos), box in zip(self.formulario_labels, self.formulario_boxes):
            surface.blit(lbl, pos)
            box.draw(surface)
        pygame.draw.rect(surface, (0, 180, 0), self.formulario_btn_guardar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.formulario_btn_guardar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.026 * self.alto), bold=True)
        btn_text = font_btn.render("Guardar", True, self.BLANCO)
        surface.blit(btn_text, (self.formulario_btn_guardar.x + (self.formulario_btn_guardar.w - btn_text.get_width()) // 2,
                                self.formulario_btn_guardar.y + (self.formulario_btn_guardar.h - btn_text.get_height()) // 2))

        pygame.draw.rect(surface, (220, 0, 0), self.formulario_btn_cancelar, border_radius=8)
        pygame.draw.rect(surface, (180, 0, 0), self.formulario_btn_cancelar, 2, border_radius=8)
        btn_text_cancelar = font_btn.render("Cancelar", True, self.BLANCO)
        surface.blit(btn_text_cancelar, (self.formulario_btn_cancelar.x + (self.formulario_btn_cancelar.w - btn_text_cancelar.get_width()) // 2,
                                        self.formulario_btn_cancelar.y + (self.formulario_btn_cancelar.h - btn_text_cancelar.get_height()) // 2))

        if self.formulario_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
            msg = font_msg.render(self.formulario_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_rect.x + 30, modal_rect.y + modal_rect.height - 50))

    def guardar_formulario_agregar_producto(self):
        valores = [box.get_value().strip() for box in self.formulario_boxes]
        if not valores[0] or not valores[1] or not valores[2]:
            self.formulario_mensaje = "Nombre, precio y stock son obligatorios."
            return
        nombre, precio, stock, imagen, caducidad, sabor, iva, descripcion = valores
        try:
            precio = float(precio)
            stock = int(stock)
            iva = float(iva) if iva else 0.16
        except Exception:
            self.formulario_mensaje = "Datos numéricos inválidos."
            return
        estado = "Disponible"
        conexion = Conexion()
        query = "SELECT ID_CatProducto, Stock FROM CatProducto WHERE Nombre_prod = %s"
        resultado = conexion.consultar(query, (nombre,))
        if resultado:
            id_prod = resultado[0]["ID_CatProducto"]
            nuevo_stock = resultado[0]["Stock"] + stock
            update = "UPDATE CatProducto SET Stock = %s WHERE ID_CatProducto = %s"
            conexion.conectar()
            conexion.cursor.execute(update, (nuevo_stock, id_prod))
            conexion.conn.commit()
            conexion.cerrar()
            self.mostrar_alerta(f"Stock actualizado para '{nombre}'.")
        else:
            insert = """
                INSERT INTO CatProducto
                (Nombre_prod, Descripcion, Precio, Stock, Imagen, Caducidad, Sabor, IVA, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            conexion.conectar()
            conexion.cursor.execute(insert, (nombre, descripcion, precio, stock, imagen, caducidad, sabor, iva, estado))
            conexion.conn.commit()
            conexion.cerrar()
            self.mostrar_alerta(f"Producto '{nombre}' agregado.")
        self.productos = self.cargar_productos_desde_db()
        self.imagenes_productos = []
        for prod in self.productos:
            ruta = prod["imagen"]
            if ruta and os.path.exists(ruta):
                img = pygame.image.load(ruta).convert_alpha()
                img = pygame.transform.smoothscale(img, (int(80 * self.ancho / 1585), int(80 * self.alto / 870)))
            else:
                img = pygame.Surface((int(80 * self.ancho / 1585), int(80 * self.alto / 870)))
                img.fill((200, 200, 200))
            self.imagenes_productos.append(img)
        self.mostrando_formulario = False
        self.formulario_mensaje = ""

    def verificar_stock(self, id_catproducto, cantidad):
        try:
            conexion = Conexion()
            query = "SELECT Stock FROM CatProducto WHERE ID_CatProducto = %s"
            resultado = conexion.consultar(query, (id_catproducto,))
            if resultado and resultado[0]["Stock"] >= cantidad:
                return True
            return False
        except Exception as e:
            print(f"Error en PuntoVenta.verificar_stock: {e}")
            return False

    def registrar_venta(self):
        try:
            conexion = Conexion()
            total_venta = self.ticket.calcular_total()

            fecha_venta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            insert_venta_query = """
            INSERT INTO Venta (Fecha_venta, Total_venta)
            VALUES (%s, %s)
            """
            conexion.update(insert_venta_query, (fecha_venta, total_venta))

            id_venta_query = "SELECT LAST_INSERT_ID() AS ID_Venta"
            id_venta = conexion.consultar(id_venta_query)[0]['ID_Venta']

            for producto in self.ticket.productos:
                insert_detalle_venta_query = """
                INSERT INTO Detalle_Venta (Cantidad, PrecioUnitario, Subtotal, FK_ID_Venta, FK_ID_CatProducto)
                VALUES (%s, %s, %s, %s, %s)
                """
                subtotal = producto["unidades"] * producto["precio"]
                conexion.update(insert_detalle_venta_query, (producto["unidades"], producto["precio"], subtotal, id_venta, producto["id"]))

                update_catproducto_query = """
                UPDATE CatProducto
                SET Stock = Stock - %s
                WHERE ID_CatProducto = %s
                """
                conexion.update(update_catproducto_query, (producto["unidades"], producto["id"]))

            return True
        except Exception as e:
            print(f"Error durante la venta: {e}")
            return False

    def validar_correo(self, correo):
        return re.match(r"[^@]+@[^@]+\.[^@]+", correo) is not None

    def enviar_ticket_por_correo(self, correo_destino):
        try:
            pdf_path = "ticket.pdf"
            if not os.path.exists(pdf_path):
                self.ticket.guardar_pdf(pdf_path)
            remitente = "nado17hernsvas@gmail.com"
            password = "rhkt wtfb cjco swpw"
            asunto = "Su ticket de compra"
            cuerpo = "Adjunto encontrará su ticket de compra. ¡Gracias por su preferencia!"
            msg = EmailMessage()
            msg["Subject"] = asunto
            msg["From"] = remitente
            msg["To"] = correo_destino
            msg.set_content(cuerpo)
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename="ticket.pdf")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(remitente, password)
                smtp.send_message(msg)
            return True
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False
