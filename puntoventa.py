"""
Sistema de Punto de Venta para Panadería
---------------------------------------
Sistema completo de punto de venta desarrollado en Pygame que incluye:
- Catálogo de productos con imágenes
- Búsqueda de productos
- Gestión de ventas con tickets
- Cálculo automático de IVA
- Pago en efectivo con cálculo de cambio
- Envío de tickets por correo electrónico
- Integración con facturación
- Control de inventario

Autor: Sistema POS Bambi
Versión: 1.0
"""

from binascii import Error
import pygame
import os
import requests
from ticket import Ticket
from receta import Conexion
import smtplib
from email.message import EmailMessage
from datetime import datetime
import re
from io import BytesIO
import pyperclip

# Constantes para colores y fuentes
COLOR_FONDO = (241, 236, 227)  # Color de fondo principal
COLOR_TEXTO = (0, 0, 0)        # Color del texto
COLOR_BOTON = (0, 120, 220)    # Color de botones principales
COLOR_BOTON_BORDE = (0, 80, 180)  # Color del borde de botones
COLOR_ALERTA = (255, 200, 200)  # Color de fondo para alertas
COLOR_ALERTA_BORDE = (200, 0, 0)  # Color del borde de alertas

class InputBox:
    """
    Clase para crear campos de entrada de texto personalizados
    
    Permite crear inputs reutilizables con validación numérica opcional
    y manejo de eventos de teclado/mouse.
    
    Attributes:
        x, y (int): Posición del campo
        ancho, alto (int): Dimensiones del campo
        text (str): Texto actual del campo
        numeric (bool): Si True, solo permite números y punto decimal
        active (bool): Estado de activación del campo
        color (pygame.Color): Color actual del borde
    """
    
    def __init__(self, x, y, ancho, alto, text='', font=None, numeric=False):
        """
        Inicializa un campo de entrada
        
        Args:
            x, y (int): Posición del campo
            ancho, alto (int): Dimensiones del campo
            text (str, optional): Texto inicial. Defaults to ''.
            font (pygame.font.Font, optional): Fuente personalizada. Defaults to None.
            numeric (bool, optional): Solo permite números. Defaults to False.
        """
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
        """
        Maneja eventos de mouse y teclado para el campo
        ACTUALIZADO: Ahora incluye soporte para Ctrl+V
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Activar/desactivar campo según clic
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN and self.active:
            # Detectar Ctrl+V para pegar
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                if event.key == pygame.K_v:
                    try:
                        clipboard_text = pyperclip.paste()
                        if clipboard_text:
                            # Validar contenido según tipo de campo
                            if self.numeric:
                                # Solo permitir números y un punto decimal
                                valid_chars = '0123456789.'
                                filtered_text = ''.join(c for c in clipboard_text if c in valid_chars)
                                # Asegurar solo un punto decimal
                                if filtered_text.count('.') > 1:
                                    parts = filtered_text.split('.')
                                    filtered_text = parts[0] + '.' + ''.join(parts[1:])
                                if filtered_text and (not self.text or '.' not in self.text):
                                    self.text += filtered_text
                            else:
                                # Campo de texto normal - limitar longitud
                                if len(self.text + clipboard_text) <= 50:
                                    self.text += clipboard_text
                    except Exception as e:
                        print(f"Error al pegar texto: {e}")
                return
            
            # Manejar otras teclas normalmente
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Validar entrada según tipo de campo
                if self.numeric:
                    if event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.text):
                        self.text += event.unicode
                else:
                    if len(self.text) < 50 and event.unicode.isprintable():
                        self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, COLOR_TEXTO)

    def update(self):
        """Actualiza el ancho del campo según el contenido"""
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        """
        Dibuja el campo en la pantalla
        
        Args:
            screen (pygame.Surface): Superficie donde dibujar
        """
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_value(self):
        """
        Obtiene el valor actual del campo
        
        Returns:
            str: Texto actual del campo
        """
        return self.text
  
class PuntoVenta:
    """
    Clase principal del sistema de punto de venta
    
    Maneja la interfaz completa del POS incluyendo:
    - Catálogo de productos
    - Búsqueda y filtrado
    - Gestión del ticket de venta
    - Pago y facturación
    - Envío por correo
    - Control de inventario
    
    Attributes:
        x, y (int): Posición de la interfaz
        ancho, alto (int): Dimensiones de la interfaz
        productos (list): Lista de productos disponibles
        ticket (Ticket): Objeto para gestionar la venta actual
        id_empleado (int): ID del empleado usando el sistema
        mostrando_modal_pago (bool): Estado del modal de pago
        mostrando_formulario (bool): Estado del formulario de productos
    """
    
    def __init__(self, x=0, y=0, ancho=1900, alto=1000, id_empleado=1):
        """
        Inicializa el sistema de punto de venta
        
        Args:
            x, y (int, optional): Posición de la interfaz. Defaults to 0, 0.
            ancho, alto (int, optional): Dimensiones. Defaults to 1900, 1000.
            id_empleado (int, optional): ID del empleado. Defaults to 1.
        """
        pygame.font.init()
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

        # Configuración de colores
        self.BLANCO = (255, 255, 255)
        self.NEGRO = COLOR_TEXTO
        self.AZUL_CLARO = COLOR_FONDO
        self.BORDE = (204, 208, 216)
        self.GRIS_CLARO = (230, 230, 230)

        # Configuración de fuentes escaladas
        def fuente_relativa(base_size):
            """Calcula tamaño de fuente relativo a las dimensiones"""
            scale = min(self.ancho / 1585, self.alto / 870)
            return int(base_size * scale)

        self.fuente_producto = pygame.font.SysFont("Open Sans", fuente_relativa(24))
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", fuente_relativa(36), bold=True)
        self.fuente_ticket = pygame.font.SysFont("Open Sans", fuente_relativa(28))
        self.fuente_busqueda = pygame.font.SysFont("Open Sans", fuente_relativa(28))

        # Cargar productos e imágenes
        self.productos = self.cargar_productos_desde_db()
        self.imagenes_productos = []
        for prod in self.productos:
            imagen_url = prod["imagen"]
            try:
                response = requests.get(imagen_url)
                if response.status_code == 200:
                    imagen_data = BytesIO(response.content)
                    imagen = pygame.image.load(imagen_data).convert_alpha()
                    imagen = pygame.transform.smoothscale(imagen, (int(80 * self.ancho / 1585), int(80 * self.alto / 870)))
                else:
                    # Imagen por defecto si no se puede descargar
                    imagen = pygame.Surface((int(80 * self.ancho / 1585), int(80 * self.alto / 870)))
                    imagen.fill((200, 200, 200))
            except Exception as e:
                print(f"Error al descargar la imagen: {e}")
                # Imagen por defecto en caso de error
                imagen = pygame.Surface((int(80 * self.ancho / 1585), int(80 * self.alto / 870)))
                imagen.fill((200, 200, 200))
            self.imagenes_productos.append(imagen)

        # Inicializar variables del sistema
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
        # Variables para scroll de productos
        self.scroll_productos = 0
        self.productos_por_fila = 3
        self.filas_visibles = 5  # Número de filas visibles
        
        # Variables para scroll del ticket
        self.scroll_ticket = 0
        self.productos_ticket_visibles = 6  # Número de productos visibles en el ticket

        #Tiempos de aletra visible
        self.alerta = ""
        self.tiempo_alerta = 0  # Para rastrear cuando se mostró la alerta
        self.duracion_alerta = 5000  # 5000 milisegundos = 5 segundos

    def cargar_productos_desde_db(self):
        """
        Carga todos los productos disponibles desde la base de datos
        Returns:
            list: Lista de diccionarios con información de productos
        """
        try:
            conexion = Conexion()
            query = """
                SELECT ID_CatProducto, Nombre_prod AS nombre, Precio AS precio, Imagen AS imagen, Stock
                FROM CatProducto
                WHERE Estado='Disponible' AND Stock > 0
            """
            productos = conexion.consultar(query)
            # Asignar imagen por defecto si no existe
            for prod in productos:
                if not prod["imagen"]:
                    prod["imagen"] = "https://github.com/Kernel5110/bambito/blob/main/imagenes/log.png"  # URL de imagen por defecto
            return productos
        except Exception as e:
            print(f"Error en PuntoVenta.cargar_productos_desde_db: {e}")
            return []

    def mostrar_alerta(self, mensaje):
        """
        Muestra un mensaje de alerta en la interfaz
        
        Args:
            mensaje (str): Mensaje a mostrar
        """
        self.alerta = mensaje
        # Registrar el tiempo en que se mostró la alerta
        self.tiempo_alerta = pygame.time.get_ticks()
        print("ALERTA:", mensaje)

    def filtrar_productos(self):
        """
        Filtra los productos según el texto de búsqueda
        
        Returns:
            list: Lista de tuplas (índice, producto) filtrada
        """
        if not self.busqueda_texto:
            return list(enumerate(self.productos))
        texto = self.busqueda_texto.lower()
        return [(i, prod) for i, prod in enumerate(self.productos) if texto in prod["nombre"].lower()]

    def dibujar_alerta(self, surface):
        """
        Dibuja la alerta actual en la pantalla si no han pasado 5 segundos
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Verificar si hay una alerta para mostrar
        if self.alerta:
            # Verificar si han pasado 5 segundos desde que se mostró la alerta
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self.tiempo_alerta >= self.duracion_alerta:
                # Han pasado 5 segundos, eliminar la alerta
                self.alerta = ""
            else:
                # Dibujar la alerta en la pantalla
                rect = pygame.Rect(self.x + int(0.05 * self.ancho), self.y + int(0.03 * self.alto), 
                                int(0.5 * self.ancho), int(0.06 * self.alto))
                pygame.draw.rect(surface, COLOR_ALERTA, rect, border_radius=10)
                pygame.draw.rect(surface, COLOR_ALERTA_BORDE, rect, 2, border_radius=10)
                fuente_alerta = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
                texto = fuente_alerta.render(self.alerta, True, COLOR_ALERTA_BORDE)
                surface.blit(texto, (rect.x + 20, rect.y + 10))
                
                # Opcional: Efecto de desvanecimiento
                # Calcular transparencia basada en el tiempo restante
                tiempo_restante = self.duracion_alerta - (tiempo_actual - self.tiempo_alerta)
                if tiempo_restante < 1000:  # Último segundo
                    # Dibujar un rectángulo semitransparente encima para crear efecto de desvanecimiento
                    transparencia = int(255 * (tiempo_restante / 1000))
                    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    s.fill((241, 236, 227, 255 - transparencia))  # COLOR_FONDO con alpha
                    surface.blit(s, (rect.x, rect.y))

    def dibujar_campo_busqueda(self, surface, x, y, w, h):
        """
        Dibuja el campo de búsqueda y el botón "Agregar producto"
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            x, y (int): Posición del campo
            w, h (int): Dimensiones del campo
        """
        # Campo de búsqueda
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
        """
        Dibuja una tarjeta de producto individual
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            x, y (int): Posición de la tarjeta
            producto (dict): Información del producto
            imagen (pygame.Surface): Imagen del producto
            
        Returns:
            pygame.Rect: Rectángulo de la tarjeta para detección de clics
        """
        ancho = int(0.16 * self.ancho)
        alto = int(0.16 * self.alto)
        margen = int(0.01 * self.ancho)
        rect = pygame.Rect(x, y, ancho, alto)
        
        # Fondo de la tarjeta
        pygame.draw.rect(surface, self.GRIS_CLARO, rect, border_radius=12)
        pygame.draw.rect(surface, self.BORDE, rect, 2, border_radius=12)
        
        # Imagen del producto
        img_rect = imagen.get_rect()
        img_rect.centerx = rect.centerx
        img_rect.top = y + margen
        surface.blit(imagen, img_rect)
        
        # Nombre del producto
        nombre_render = self.fuente_producto.render(producto["nombre"], True, COLOR_TEXTO)
        nombre_x = rect.centerx - nombre_render.get_width() // 2
        nombre_y = img_rect.bottom + 5
        surface.blit(nombre_render, (nombre_x, nombre_y))
        
        # Precio del producto
        precio_str = f"${producto['precio']:.2f}"
        precio_render = self.fuente_ticket.render(precio_str, True, COLOR_TEXTO)
        precio_x = rect.centerx - precio_render.get_width() // 2
        precio_y = nombre_y + nombre_render.get_height() + 2
        surface.blit(precio_render, (precio_x, precio_y))
        
        return rect

    def calcular_total_con_iva(self):
        """
        Calcula el total de la venta incluyendo IVA
        
        Returns:
            float: Total con IVA incluido
        """
        total = float(self.ticket.calcular_total())
        return total * 1.16

    def dibujar_ticket(self, surface):
        """
        Dibuja el ticket de venta con todos los productos y botones
        """
        # Definir dimensiones del ticket
        x = self.x + int(0.65 * self.ancho)
        y = self.y + int(0.15 * self.alto)
        w = int(0.33 * self.ancho)
        h = int(0.7 * self.alto)

        # Fondo del ticket
        pygame.draw.rect(surface, self.BLANCO, (x, y, w, h), border_radius=12)
        pygame.draw.rect(surface, self.BORDE, (x, y, w, h), 2, border_radius=12)

        # Título del ticket
        titulo_ticket = self.fuente_titulo.render("Ticket de Compra", True, COLOR_TEXTO)
        surface.blit(titulo_ticket, (x + int(0.05 * w), y + int(0.03 * h)))

        # Línea divisora
        pygame.draw.line(surface, self.BORDE, (x + int(0.03 * w), y + int(0.1 * h)), (x + w - int(0.03 * w), y + int(0.1 * h)), 2)

        # Encabezados de la tabla
        headers = ["Nombre", "Unidades", "Precio", "Acción"]
        header_y = y + int(0.12 * h)
        col_widths = [int(w*0.4), int(w*0.2), int(w*0.2), int(w*0.2)]
        col_x = x + int(0.03 * w)

        for i, header in enumerate(headers):
            header_render = self.fuente_ticket.render(header, True, COLOR_TEXTO)
            surface.blit(header_render, (col_x, header_y))
            col_x += col_widths[i]

        # Línea divisora después de encabezados
        pygame.draw.line(surface, self.BORDE, (x, header_y + int(0.04 * h)), (x + w, header_y + int(0.04 * h)), 2)

        # Área de productos con scroll
        productos_area_y = header_y + int(0.06 * h)
        productos_area_h = h - int(0.3 * h)  # Espacio para productos

        # Calcular límites para el scroll del ticket
        total_productos = len(self.ticket.productos)
        max_scroll_ticket = max(0, total_productos - self.productos_ticket_visibles)
        self.scroll_ticket = max(0, min(self.scroll_ticket, max_scroll_ticket))

        # Guardar referencia para detección de clics
        self.ticket_productos_rects = []

        # Dibujar productos visibles
        y_offset = productos_area_y
        start_idx = self.scroll_ticket
        end_idx = min(start_idx + self.productos_ticket_visibles, total_productos)

        for i in range(start_idx, end_idx):
            if i < len(self.ticket.productos):
                producto = self.ticket.productos[i]

                # Crear rect para cada producto
                producto_rect = pygame.Rect(x, y_offset, w, int(0.05 * h))
                self.ticket_productos_rects.append((producto_rect, i))

                # Fondo alternado
                if (i - start_idx) % 2 == 0:
                    pygame.draw.rect(surface, (250, 250, 250), producto_rect)

                # Dibujar datos del producto
                col_x = x + int(0.03 * w)

                # Nombre
                nombre_render = self.fuente_ticket.render(producto['nombre'], True, COLOR_TEXTO)
                surface.blit(nombre_render, (col_x, y_offset))
                col_x += col_widths[0]

                # Unidades
                unidades_render = self.fuente_ticket.render(str(producto['unidades']), True, COLOR_TEXTO)
                surface.blit(unidades_render, (col_x, y_offset))
                col_x += col_widths[1]

                # Precio
                precio_render = self.fuente_ticket.render(f"${producto['precio'] * producto['unidades']:.2f}", True, COLOR_TEXTO)
                surface.blit(precio_render, (col_x, y_offset))
                col_x += col_widths[2]

                # Botones de incrementar y decrementar
                btn_w, btn_h = int(0.08 * w), int(0.04 * h)
                btn_y = y_offset + (int(0.05 * h) - btn_h) // 2

                # Botón de decrementar
                btn_decrementar = pygame.Rect(col_x, btn_y, btn_w, btn_h)
                pygame.draw.rect(surface, (220, 0, 0), btn_decrementar, border_radius=5)
                pygame.draw.rect(surface, (180, 0, 0), btn_decrementar, 2, border_radius=5)
                btn_text = self.fuente_producto.render("-", True, self.BLANCO)
                surface.blit(btn_text, (col_x + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

                # Botón de incrementar
                btn_incrementar = pygame.Rect(col_x + btn_w + 10, btn_y, btn_w, btn_h)
                pygame.draw.rect(surface, (0, 180, 0), btn_incrementar, border_radius=5)
                pygame.draw.rect(surface, (0, 120, 0), btn_incrementar, 2, border_radius=5)
                btn_text = self.fuente_producto.render("+", True, self.BLANCO)
                surface.blit(btn_text, (col_x + btn_w + 10 + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

                # Guardar referencias a los botones
                self.ticket_productos_rects[-1] = (producto_rect, i, btn_decrementar, btn_incrementar)

                y_offset += int(0.05 * h)

        # Indicador de scroll para ticket
        if max_scroll_ticket > 0:
            scroll_x = x + w - 15
            scroll_y = productos_area_y
            scroll_h = productos_area_h - int(0.1 * h)

            # Barra de fondo
            pygame.draw.rect(surface, (200, 200, 200), (scroll_x, scroll_y, 10, scroll_h))

            # Barra de scroll
            bar_height = int(scroll_h * self.productos_ticket_visibles / total_productos)
            bar_y = scroll_y + int(scroll_h * self.scroll_ticket / max_scroll_ticket)
            pygame.draw.rect(surface, (100, 100, 100), (scroll_x, bar_y, 10, bar_height))

        # Línea divisora antes del total
        total_y = y + h - int(0.14 * h)
        pygame.draw.line(surface, self.BORDE, (x + int(0.03 * w), total_y), (x + w - int(0.03 * w), total_y), 2)

        # Total sin IVA
        total_text = self.fuente_ticket.render(f"Total: ${self.ticket.calcular_total():.2f}", True, COLOR_TEXTO)
        surface.blit(total_text, (x + int(0.05 * w), total_y + 20))

        # Total con IVA
        total_iva = self.calcular_total_con_iva()
        total_iva_text = self.fuente_titulo.render(f"Total + IVA: ${total_iva:.2f}", True, (80, 80, 80))
        surface.blit(total_iva_text, (x + int(0.05 * w), y + h - int(0.07 * h)))

        # Botón de pagar
        btn_w, btn_h = int(0.29 * w), int(0.11 * h)
        btn_x = x + w - btn_w - int(0.02 * w)
        btn_y = y + h - btn_h - int(0.12 * h)
        self.boton_pagar_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, (0, 180, 0), self.boton_pagar_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 120, 0), self.boton_pagar_rect, 2, border_radius=10)
        btn_text = self.fuente_producto.render("Pagar", True, self.BLANCO)
        surface.blit(btn_text, (btn_x + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

        # Botón de enviar
        btn_env_w, btn_env_h = int(0.29 * w), int(0.11 * h)
        btn_env_x = x + int(0.01 * w)
        btn_env_y = y + h - btn_env_h - int(0.12 * h)
        self.boton_enviar_rect = pygame.Rect(btn_env_x, btn_env_y, btn_env_w, btn_env_h)
        pygame.draw.rect(surface, COLOR_BOTON, self.boton_enviar_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_BOTON_BORDE, self.boton_enviar_rect, 2, border_radius=10)
        btn_env_text = self.fuente_producto.render("Enviar", True, self.BLANCO)
        surface.blit(btn_env_text, (btn_env_x + (btn_env_w - btn_env_text.get_width()) // 2, btn_env_y + (btn_env_h - btn_env_text.get_height()) // 2))

        # Botón de factura
        btn_factura_w, btn_factura_h = int(0.39 * w), int(0.11 * h)
        btn_factura_x = x + int(0.30 * w)
        btn_factura_y = y + h - btn_factura_h - int(0.12 * h)
        self.boton_factura_rect = pygame.Rect(btn_factura_x, btn_factura_y, btn_factura_w, btn_factura_h)
        pygame.draw.rect(surface, (0, 120, 220), self.boton_factura_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 80, 180), self.boton_factura_rect, 2, border_radius=10)
        btn_factura_text = self.fuente_producto.render("Generar Factura", True, self.BLANCO)
        surface.blit(btn_factura_text, (btn_factura_x + (btn_factura_w - btn_factura_text.get_width()) // 2, btn_factura_y + (btn_factura_h - btn_factura_text.get_height()) // 2))

    def dibujar_ticket(self, surface):
        """
        Dibuja el ticket de venta con todos los productos y botones
        """
        # Definir dimensiones del ticket
        x = self.x + int(0.65 * self.ancho)
        y = self.y + int(0.15 * self.alto)
        w = int(0.33 * self.ancho)
        h = int(0.7 * self.alto)

        # Fondo del ticket
        pygame.draw.rect(surface, self.BLANCO, (x, y, w, h), border_radius=12)
        pygame.draw.rect(surface, self.BORDE, (x, y, w, h), 2, border_radius=12)

        # Título del ticket
        titulo_ticket = self.fuente_titulo.render("Ticket de Compra", True, COLOR_TEXTO)
        surface.blit(titulo_ticket, (x + int(0.05 * w), y + int(0.03 * h)))

        # Línea divisora
        pygame.draw.line(surface, self.BORDE, (x + int(0.03 * w), y + int(0.1 * h)), (x + w - int(0.03 * w), y + int(0.1 * h)), 2)

        # Encabezados de la tabla
        headers = ["Nombre", "Unidades", "Precio", "Acción"]
        header_y = y + int(0.12 * h)
        col_widths = [int(w*0.4), int(w*0.2), int(w*0.2), int(w*0.2)]
        col_x = x + int(0.03 * w)

        for i, header in enumerate(headers):
            header_render = self.fuente_ticket.render(header, True, COLOR_TEXTO)
            surface.blit(header_render, (col_x, header_y))
            col_x += col_widths[i]

        # Línea divisora después de encabezados
        pygame.draw.line(surface, self.BORDE, (x, header_y + int(0.04 * h)), (x + w, header_y + int(0.04 * h)), 2)

        # Área de productos con scroll
        productos_area_y = header_y + int(0.06 * h)
        productos_area_h = h - int(0.3 * h)  # Espacio para productos

        # Calcular límites para el scroll del ticket
        total_productos = len(self.ticket.productos)
        max_scroll_ticket = max(0, total_productos - self.productos_ticket_visibles)
        self.scroll_ticket = max(0, min(self.scroll_ticket, max_scroll_ticket))

        # Guardar referencia para detección de clics
        self.ticket_productos_rects = []

        # Dibujar productos visibles
        y_offset = productos_area_y
        start_idx = self.scroll_ticket
        end_idx = min(start_idx + self.productos_ticket_visibles, total_productos)

        for i in range(start_idx, end_idx):
            if i < len(self.ticket.productos):
                producto = self.ticket.productos[i]

                # Crear rect para cada producto
                producto_rect = pygame.Rect(x, y_offset, w, int(0.05 * h))
                self.ticket_productos_rects.append((producto_rect, i))

                # Fondo alternado
                if (i - start_idx) % 2 == 0:
                    pygame.draw.rect(surface, (250, 250, 250), producto_rect)

                # Dibujar datos del producto
                col_x = x + int(0.03 * w)

                # Nombre
                nombre_render = self.fuente_ticket.render(producto['nombre'], True, COLOR_TEXTO)
                surface.blit(nombre_render, (col_x, y_offset))
                col_x += col_widths[0]

                # Unidades
                unidades_render = self.fuente_ticket.render(str(producto['unidades']), True, COLOR_TEXTO)
                surface.blit(unidades_render, (col_x, y_offset))
                col_x += col_widths[1]

                # Precio
                precio_render = self.fuente_ticket.render(f"${producto['precio'] * producto['unidades']:.2f}", True, COLOR_TEXTO)
                surface.blit(precio_render, (col_x, y_offset))
                col_x += col_widths[2]

                # Botones de incrementar y decrementar
                btn_w, btn_h = int(0.08 * w), int(0.04 * h)
                btn_y = y_offset + (int(0.05 * h) - btn_h) // 2

                # Botón de decrementar
                btn_decrementar = pygame.Rect(col_x, btn_y, btn_w, btn_h)
                pygame.draw.rect(surface, (220, 0, 0), btn_decrementar, border_radius=5)
                pygame.draw.rect(surface, (180, 0, 0), btn_decrementar, 2, border_radius=5)
                btn_text = self.fuente_producto.render("-", True, self.BLANCO)
                surface.blit(btn_text, (col_x + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

                # Botón de incrementar
                btn_incrementar = pygame.Rect(col_x + btn_w + 8, btn_y, btn_w, btn_h)
                pygame.draw.rect(surface, (0, 180, 0), btn_incrementar, border_radius=5)
                pygame.draw.rect(surface, (0, 120, 0), btn_incrementar, 2, border_radius=5)
                btn_text = self.fuente_producto.render("+", True, self.BLANCO)
                surface.blit(btn_text, (col_x + btn_w + 9 + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

                # Guardar referencias a los botones
                self.ticket_productos_rects[-1] = (producto_rect, i, btn_decrementar, btn_incrementar)

                y_offset += int(0.05 * h)

        # Indicador de scroll para ticket
        if max_scroll_ticket > 0:
            scroll_x = x + w - 15
            scroll_y = productos_area_y
            scroll_h = productos_area_h - int(0.1 * h)

            # Barra de fondo
            pygame.draw.rect(surface, (200, 200, 200), (scroll_x, scroll_y, 10, scroll_h))

            # Barra de scroll
            bar_height = int(scroll_h * self.productos_ticket_visibles / total_productos)
            bar_y = scroll_y + int(scroll_h * self.scroll_ticket / max_scroll_ticket)
            pygame.draw.rect(surface, (100, 100, 100), (scroll_x, bar_y, 10, bar_height))

        # Línea divisora antes del total
        total_y = y + h - int(0.14 * h)
        pygame.draw.line(surface, self.BORDE, (x + int(0.03 * w), total_y), (x + w - int(0.03 * w), total_y), 2)

        # Total sin IVA
        total_text = self.fuente_ticket.render(f"Total: ${self.ticket.calcular_total():.2f}", True, COLOR_TEXTO)
        surface.blit(total_text, (x + int(0.05 * w), total_y + 5))

        # Total con IVA
        total_iva = self.calcular_total_con_iva()
        total_iva_text = self.fuente_titulo.render(f"Total + IVA: ${total_iva:.2f}", True, (80, 80, 80))
        surface.blit(total_iva_text, (x + int(0.05 * w), y + h - int(0.07 * h)))

        # Botón de pagar
        btn_w, btn_h = int(0.29 * w), int(0.11 * h)
        btn_x = x + w - btn_w - int(0.02 * w)
        btn_y = y + h - btn_h - int(0.12 * h)
        self.boton_pagar_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, (0, 180, 0), self.boton_pagar_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 120, 0), self.boton_pagar_rect, 2, border_radius=10)
        btn_text = self.fuente_producto.render("Pagar", True, self.BLANCO)
        surface.blit(btn_text, (btn_x + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

        # Botón de enviar
        btn_env_w, btn_env_h = int(0.29 * w), int(0.11 * h)
        btn_env_x = x + int(0.01 * w)
        btn_env_y = y + h - btn_env_h - int(0.12 * h)
        self.boton_enviar_rect = pygame.Rect(btn_env_x, btn_env_y, btn_env_w, btn_env_h)
        pygame.draw.rect(surface, COLOR_BOTON, self.boton_enviar_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_BOTON_BORDE, self.boton_enviar_rect, 2, border_radius=10)
        btn_env_text = self.fuente_producto.render("Enviar", True, self.BLANCO)
        surface.blit(btn_env_text, (btn_env_x + (btn_env_w - btn_env_text.get_width()) // 2, btn_env_y + (btn_env_h - btn_env_text.get_height()) // 2))

        # Botón de factura
        btn_factura_w, btn_factura_h = int(0.39 * w), int(0.11 * h)
        btn_factura_x = x + int(0.30 * w)
        btn_factura_y = y + h - btn_factura_h - int(0.12 * h)
        self.boton_factura_rect = pygame.Rect(btn_factura_x, btn_factura_y, btn_factura_w, btn_factura_h)
        pygame.draw.rect(surface, (0, 120, 220), self.boton_factura_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 80, 180), self.boton_factura_rect, 2, border_radius=10)
        btn_factura_text = self.fuente_producto.render("Generar Factura", True, self.BLANCO)
        surface.blit(btn_factura_text, (btn_factura_x + (btn_factura_w - btn_factura_text.get_width()) // 2, btn_factura_y + (btn_factura_h - btn_factura_text.get_height()) // 2))

    def dibujar_modal_pago(self, surface):
        """
        Dibuja el modal de pago en efectivo
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        modal_w, modal_h = int(0.35 * self.ancho), int(0.55 * self.alto)
        modal_x = self.x + (self.ancho - modal_w) // 2
        modal_y = self.y + (self.alto - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        
        # Fondo del modal
        pygame.draw.rect(surface, self.BLANCO, modal_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_BOTON, modal_rect, 3, border_radius=16)
        
        # Título
        font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto), bold=True)
        titulo = font.render("Pago en efectivo", True, COLOR_TEXTO)
        surface.blit(titulo, (modal_x + 30, modal_y + 20))

        # Total a pagar
        total_iva = self.calcular_total_con_iva()
        font_total = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        total_label = font_total.render(f"Total a pagar (con IVA): ${total_iva:.2f}", True, COLOR_TEXTO)
        surface.blit(total_label, (modal_x + 30, modal_y + 70))

        # Campo de efectivo recibido
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
            # Actualizar posición del campo
            self.efectivo_box.x = modal_x + 220
            self.efectivo_box.y = input_y
            self.efectivo_box.ancho = 120
            self.efectivo_box.alto = input_h
            self.efectivo_box.rect = pygame.Rect(self.efectivo_box.x, self.efectivo_box.y, self.efectivo_box.ancho, self.efectivo_box.alto)
        self.efectivo_box.draw(surface)

        # Calcular cambio
        efectivo_str = self.efectivo_box.get_value()
        try:
            efectivo = float(efectivo_str) if efectivo_str else 0.0
        except Exception:
            efectivo = 0.0
        cambio = efectivo - total_iva
        self.efectivo_cambio = cambio

        # Mostrar cambio
        cambio_lbl = font_lbl.render(f"Cambio: ${cambio:.2f}", True, (0, 120, 0) if cambio >= 0 else (200, 0, 0))
        surface.blit(cambio_lbl, (modal_x + 30, modal_y + 180))

        # Botones confirmar y cancelar
        btn_w, btn_h = 120, 50
        btn_y = modal_y + modal_h - btn_h - 70  # Ajustado para acomodar el nuevo botón
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

        # Botón de pago con tarjeta - NUEVO
        btn_tarjeta_w = 280
        btn_tarjeta_h = 50
        btn_tarjeta_x = modal_x + (modal_w - btn_tarjeta_w) // 2
        btn_tarjeta_y = modal_y + modal_h - btn_tarjeta_h - 15
        
        self.boton_pago_tarjeta = pygame.Rect(btn_tarjeta_x, btn_tarjeta_y, btn_tarjeta_w, btn_tarjeta_h)
        pygame.draw.rect(surface, (0, 100, 200), self.boton_pago_tarjeta, border_radius=8)
        pygame.draw.rect(surface, (0, 80, 170), self.boton_pago_tarjeta, 2, border_radius=8)
        btn_tarjeta_text = font_btn.render("Pagar con Tarjeta", True, self.BLANCO)
        surface.blit(btn_tarjeta_text, (btn_tarjeta_x + (btn_tarjeta_w - btn_tarjeta_text.get_width()) // 2, 
                                    btn_tarjeta_y + (btn_tarjeta_h - btn_tarjeta_text.get_height()) // 2))

        # Mensaje de error
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
        """
        Dibuja la interfaz completa del punto de venta
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Fondo de la interfaz
        pygame.draw.rect(surface, self.AZUL_CLARO, (self.x, self.y, self.ancho, self.alto))
        
        # Título principal
        titulo = self.fuente_titulo.render("Productos Disponibles", True, COLOR_TEXTO)
        surface.blit(titulo, (self.x + int(0.02 * self.ancho), self.y + int(0.02 * self.alto)))
        
        # Mostrar alerta si existe
        self.dibujar_alerta(surface)
        
        # Campo de búsqueda
        busq_x = self.x + int(0.02 * self.ancho)
        busq_y = self.y + int(0.08 * self.alto)
        busq_w = int(0.38 * self.ancho)
        busq_h = int(0.05 * self.alto)
        self.dibujar_campo_busqueda(surface, busq_x, busq_y, busq_w, busq_h)
        
        # Catálogo de productos con scroll
        start_x = self.x + int(0.02 * self.ancho)
        start_y = self.y + int(0.15 * self.alto)
        spacing_x = int(0.19 * self.ancho)
        spacing_y = int(0.20 * self.alto)
        cols = 3
        self.product_rects = []
        productos_filtrados = self.filtrar_productos()
        
        # Calcular límites para el scroll
        total_filas = (len(productos_filtrados) + cols - 1) // cols
        max_scroll = max(0, total_filas - self.filas_visibles)
        self.scroll_productos = max(0, min(self.scroll_productos, max_scroll))
        
        # Dibujar solo los productos visibles
        start_idx = self.scroll_productos * cols
        end_idx = min(start_idx + self.filas_visibles * cols, len(productos_filtrados))
        
        for idx in range(start_idx, end_idx):
            if idx < len(productos_filtrados):
                i_original, producto = productos_filtrados[idx]
                col = (idx - start_idx) % cols
                row = (idx - start_idx) // cols
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                imagen = self.imagenes_productos[i_original]
                rect = self.dibujar_producto(surface, x, y, producto, imagen)
                self.product_rects.append((rect, i_original))
        
        # Indicador de scroll para productos
        if max_scroll > 0:
            # Área del scroll
            scroll_x = self.x + int(0.59 * self.ancho)
            scroll_y = start_y
            scroll_h = self.filas_visibles * spacing_y
            
            # Barra de fondo
            pygame.draw.rect(surface, (200, 200, 200), (scroll_x, scroll_y, 10, scroll_h))
            
            # Barra de scroll
            bar_height = int(scroll_h * self.filas_visibles / total_filas)
            bar_y = scroll_y + int(scroll_h * self.scroll_productos / max_scroll)
            pygame.draw.rect(surface, (100, 100, 100), (scroll_x, bar_y, 10, bar_height))
        
        # Ticket de venta
        self.dibujar_ticket(surface)
        
        # Almacenar rectángulo de búsqueda para detección de clics
        self.busq_rect = pygame.Rect(busq_x, busq_y, busq_w, busq_h)
        
        # Dibujar modales si están activos
        if self.mostrando_formulario:
            self.dibujar_formulario_agregar_producto(surface)
        if getattr(self, "mostrando_modal_correo", False):
            self.dibujar_modal_correo(surface)
        if self.mostrando_modal_pago:
            self.dibujar_modal_pago(surface)
        # Dibujar ventana de pago con tarjeta si está activa
        if getattr(self, "mostrando_pago_tarjeta", False):
            if hasattr(self, 'pago_tarjeta_instance'):
                self.pago_tarjeta_instance.dibujar(surface)
                
                # Manejar eventos
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    
                    resultado = self.pago_tarjeta_instance.handle_event(event)
                    if resultado == "completado":
                        # Pago exitoso, registrar venta
                        exito = self.registrar_venta()
                        if exito:
                            self.ticket.guardar_pdf()
                            self.mostrar_alerta("Pago aprobado. Venta registrada.")
                            self.productos = self.cargar_productos_desde_db()
                            self.mostrando_modal_pago = False
                            self.mostrando_pago_tarjeta = False
                        else:
                            self.mostrar_alerta("Error al registrar la venta.")
                    elif resultado == "cancelar":
                        # Cancelar y volver al modal de pago
                        self.mostrando_pago_tarjeta = False

    def handle_event(self, event):
        """
        Maneja todos los eventos del sistema
        """
        # IMPORTANTE: Manejar eventos de teclado para modales ANTES de cualquier return
        
        # Eventos del formulario de productos - MOVER AL PRINCIPIO
        if self.mostrando_formulario:
            # Manejar eventos de teclado para todos los campos
            for box in self.formulario_boxes:
                box.handle_event(event)
            
            # Manejar clics en botones
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.formulario_btn_guardar and self.formulario_btn_guardar.collidepoint(event.pos):
                    self.guardar_formulario_agregar_producto()
                elif self.formulario_btn_cancelar and self.formulario_btn_cancelar.collidepoint(event.pos):
                    self.mostrando_formulario = False
            return  # Solo retornar después de manejar TODOS los eventos

        # Eventos del modal de correo - MOVER AL PRINCIPIO
        if getattr(self, "mostrando_modal_correo", False):
            # Manejar eventos de teclado para el campo de correo
            if self.correo_box:
                self.correo_box.handle_event(event)
            
            # Manejar clics en botones
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
            return  # Solo retornar después de manejar TODOS los eventos

        # Eventos del modal de pago
        if self.mostrando_modal_pago:
            self.efectivo_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.boton_modal_confirmar.collidepoint(event.pos):
                    total_iva = self.ticket.calcular_total()
                    total_iva *= 1.16  # Aplicar IVA
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
                            self.ticket.efectivo_recibido=efectivo
                            self.ticket.cambio=efectivo-total_iva
                            self.ticket.guardar_pdf()
                            self.ticket.limpiar
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
                elif self.boton_pago_tarjeta.collidepoint(event.pos):  # NUEVO
                    # Pagar con tarjeta
                    total_iva = self.calcular_total_con_iva()
                    self.procesar_pago_tarjeta(total_iva)
            return

        # Manejo de scroll con rueda del mouse
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()

            # Scroll en el panel de productos
            if (self.x + int(0.02 * self.ancho) <= mouse_pos[0] <= self.x + int(0.6 * self.ancho) and
                self.y + int(0.15 * self.alto) <= mouse_pos[1] <= self.y + int(0.9 * self.alto)):
                if event.y > 0:  # Scroll arriba
                    self.scroll_productos = max(0, self.scroll_productos - 1)
                else:  # Scroll abajo
                    productos_filtrados = self.filtrar_productos()
                    total_filas = (len(productos_filtrados) + 2) // 3
                    max_scroll = max(0, total_filas - self.filas_visibles)
                    self.scroll_productos = min(max_scroll, self.scroll_productos + 1)

            # Scroll en el ticket
            elif (self.x + int(0.65 * self.ancho) <= mouse_pos[0] <= self.x + int(0.98 * self.ancho) and
                self.y + int(0.15 * self.alto) <= mouse_pos[1] <= self.y + int(0.8 * self.alto)):
                if event.y > 0:  # Scroll arriba
                    self.scroll_ticket = max(0, self.scroll_ticket - 1)
                else:  # Scroll abajo
                    max_scroll = max(0, len(self.ticket.productos) - self.productos_ticket_visibles)
                    self.scroll_ticket = min(max_scroll, self.scroll_ticket + 1)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Clic derecho para eliminar productos del ticket
            if event.button == 3:  # Botón derecho
                if hasattr(self, 'ticket_productos_rects'):
                    for rect, idx, btn_decrementar, btn_incrementar in self.ticket_productos_rects:
                        if rect.collidepoint(event.pos):
                            if 0 <= idx < len(self.ticket.productos):
                                producto_eliminado = self.ticket.productos[idx]
                                # Eliminar producto del ticket
                                self.ticket.eliminar_producto(idx)
                                self.mostrar_alerta(f"Producto '{producto_eliminado['nombre']}' eliminado del ticket")
                                # Ajustar scroll si es necesario
                                max_scroll = max(0, len(self.ticket.productos) - self.productos_ticket_visibles)
                                self.scroll_ticket = min(self.scroll_ticket, max_scroll)
                            break

            # Eventos principales del POS
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Campo de búsqueda
                if hasattr(self, "busq_rect") and self.busq_rect and self.busq_rect.collidepoint(mouse_x, mouse_y):
                    self.busqueda_activa = True
                # Botón agregar producto
                elif hasattr(self, "boton_agregar_producto_rect") and self.boton_agregar_producto_rect and self.boton_agregar_producto_rect.collidepoint(mouse_x, mouse_y):
                    self.mostrar_formulario_agregar_producto()
                # Botón enviar por correo
                elif hasattr(self, "boton_enviar_rect") and self.boton_enviar_rect and self.boton_enviar_rect.collidepoint(mouse_x, mouse_y):
                    self.mostrando_modal_correo = True
                    self.correo_box = None
                    self.correo_mensaje = ""
                # Botón generar factura
                elif hasattr(self, "boton_factura_rect") and self.boton_factura_rect and self.boton_factura_rect.collidepoint(mouse_x, mouse_y):
                    try:
                        from factura import Factura
                        import asyncio
                        # Crear una instancia de factura
                        factura = Factura(self.x, self.y, self.ancho, self.alto)
                        # Integración con sistema de facturación
                        asyncio.run(factura.main())
                    except Exception as e:
                        self.mostrar_alerta(f"Error al generar factura: {e}")
                else:
                    self.busqueda_activa = False

                    # Detectar clic en productos
                    for rect, idx in self.product_rects:
                        if rect and rect.collidepoint(mouse_x, mouse_y):
                            prod = self.productos[idx]
                            # Verificar si el producto ya está en el ticket
                            if self.ticket.buscar_producto_por_nombre(prod["nombre"]):
                                # Si ya está, obtener la cantidad actual en el ticket
                                cantidad_actual = self.ticket.obtener_cantidad_producto(prod["nombre"])
                                cantidad_nueva = cantidad_actual + 1
                                print(cantidad_nueva)
                                # Verificar si hay suficiente stock para la nueva cantidad
                                if self.verificar_stock(prod["ID_CatProducto"], cantidad_nueva):
                                    self.ticket.agregar_producto(prod["nombre"], 1, prod["precio"], prod["ID_CatProducto"])
                                    self.mostrar_alerta(f"Incrementada cantidad de {prod['nombre']} en el ticket")
                                    print(f"Incrementada cantidad de {prod['nombre']} en el ticket")
                                else:
                                    self.mostrar_alerta(f"No hay suficiente stock para agregar más '{prod['nombre']}'")
                            else:
                                # Si no está, verificar stock para 1 unidad
                                if self.verificar_stock(prod["ID_CatProducto"], 1):
                                    self.ticket.agregar_producto(prod["nombre"], 1, prod["precio"], prod["ID_CatProducto"])
                                    self.mostrar_alerta(f"Producto agregado al ticket: {prod['nombre']}")
                                    print(f"Producto agregado al ticket: {prod['nombre']}")
                                else:
                                    self.mostrar_alerta(f"No hay suficiente stock de '{prod['nombre']}'")
                            break  # Salir del bucle una vez que se encuentra el producto seleccionado

                    # Botón pagar
                    if self.boton_pagar_rect and self.boton_pagar_rect.collidepoint(mouse_x, mouse_y):
                        if self.ticket.productos:
                            self.mostrando_modal_pago = True
                            self.efectivo_box = None
                            self.efectivo_mensaje = ""
                            
                        else:
                            self.mostrar_alerta("El ticket está vacío.")

                    # Botones de incrementar y decrementar unidades
                    if hasattr(self, 'ticket_productos_rects'):
                        for rect, idx, btn_decrementar, btn_incrementar in self.ticket_productos_rects:
                            if btn_decrementar.collidepoint(event.pos):
                                if 0 <= idx < len(self.ticket.productos):
                                    producto = self.ticket.productos[idx]
                                    if producto['unidades'] > 1:
                                        producto['unidades'] -= 1
                                    else:
                                        # Eliminar producto si las unidades llegan a 0
                                        self.ticket.eliminar_producto(idx)
                                        self.mostrar_alerta(f"Producto '{producto['nombre']}' eliminado del ticket")
                                        # Ajustar scroll si es necesario
                                        max_scroll = max(0, len(self.ticket.productos) - self.productos_ticket_visibles)
                                        self.scroll_ticket = min(self.scroll_ticket, max_scroll)
                            elif btn_incrementar.collidepoint(event.pos):
                                if 0 <= idx < len(self.ticket.productos):
                                    producto = self.ticket.productos[idx]
                                    if self.verificar_stock(producto['id'], producto['unidades'] + 1):
                                        producto['unidades'] += 1
                                    else:
                                        self.mostrar_alerta(f"No hay suficiente stock de '{producto['nombre']}'")

        # Eventos de teclado para búsqueda
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
        """
        Configura y muestra el formulario para agregar/actualizar productos
        """
        self.mostrando_formulario = True
        font = pygame.font.SysFont("Open Sans", int(0.024 * self.alto))
        x, y = self.x + int(0.25 * self.ancho), self.y + int(0.20 * self.alto)
        
        # Campos del formulario
        labels = [
            "Nombre", "Precio", "Stock", "Imagen", "Caducidad (YYYY-MM-DD)",
            "Sabor", "IVA", "Descripción"
        ]
        
        self.formulario_labels = []
        self.formulario_boxes = []
        
        for i, label in enumerate(labels):
            lbl = font.render(label + ":", True, COLOR_TEXTO)
            self.formulario_labels.append((lbl, (x, y + i * int(0.06 * self.alto))))
            
            # Campos numéricos
            numeric = label in ["Precio", "Stock", "IVA"]
            box = InputBox(x + int(0.15 * self.ancho), y + i * int(0.06 * self.alto), int(0.14 * self.ancho), int(0.045 * self.alto), font=font, numeric=numeric)
            self.formulario_boxes.append(box)
        
        # Botones del formulario
        self.formulario_btn_guardar = pygame.Rect(x, y + 10 + len(labels) * int(0.06 * self.alto), int(0.13 * self.ancho), int(0.06 * self.alto))
        self.formulario_btn_cancelar = pygame.Rect(x + int(0.15 * self.ancho), y + 10 + len(labels) * int(0.06 * self.alto), int(0.13 * self.ancho), int(0.06 * self.alto))
        self.formulario_mensaje = ""

    def dibujar_formulario_agregar_producto(self, surface):
        """
        Dibuja el formulario para agregar productos
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Fondo del modal
        modal_rect = pygame.Rect(self.x + int(0.18 * self.ancho), self.y + int(0.10 * self.alto), int(0.45 * self.ancho), int(0.7 * self.alto))
        pygame.draw.rect(surface, (245, 245, 245), modal_rect, border_radius=18)
        pygame.draw.rect(surface, COLOR_BOTON, modal_rect, 3, border_radius=18)
        
        # Título
        font = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        titulo = font.render("Agregar/Actualizar Producto", True, COLOR_TEXTO)
        surface.blit(titulo, (modal_rect.x + 30, modal_rect.y + 20))
        
        # Dibujar labels y campos
        for (lbl, pos), box in zip(self.formulario_labels, self.formulario_boxes):
            surface.blit(lbl, pos)
            box.draw(surface)
        
        # Botón guardar
        pygame.draw.rect(surface, (0, 180, 0), self.formulario_btn_guardar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.formulario_btn_guardar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.026 * self.alto), bold=True)
        btn_text = font_btn.render("Guardar", True, self.BLANCO)
        surface.blit(btn_text, (self.formulario_btn_guardar.x + (self.formulario_btn_guardar.w - btn_text.get_width()) // 2,
                                self.formulario_btn_guardar.y + (self.formulario_btn_guardar.h - btn_text.get_height()) // 2))

        # Botón cancelar
        pygame.draw.rect(surface, (220, 0, 0), self.formulario_btn_cancelar, border_radius=8)
        pygame.draw.rect(surface, (180, 0, 0), self.formulario_btn_cancelar, 2, border_radius=8)
        btn_text_cancelar = font_btn.render("Cancelar", True, self.BLANCO)
        surface.blit(btn_text_cancelar, (self.formulario_btn_cancelar.x + (self.formulario_btn_cancelar.w - btn_text_cancelar.get_width()) // 2,
                                        self.formulario_btn_cancelar.y + (self.formulario_btn_cancelar.h - btn_text_cancelar.get_height()) // 2))

        # Mensaje de error/éxito
        if self.formulario_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
            msg = font_msg.render(self.formulario_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_rect.x + 30, modal_rect.y + modal_rect.height - 50))

    def guardar_formulario_agregar_producto(self):
        """
        Guarda o actualiza un producto en la base de datos
        
        Validaciones:
        - Nombre, precio y stock son obligatorios
        - Precio y stock deben ser numéricos
        - Si el producto existe, actualiza el stock
        - Si no existe, lo crea nuevo
        """
        valores = [box.get_value().strip() for box in self.formulario_boxes]
        
        # Validar campos obligatorios
        if not valores[0] or not valores[1] or not valores[2]:
            self.formulario_mensaje = "Nombre, precio y stock son obligatorios."
            return
            
        nombre, precio, stock, imagen, caducidad, sabor, iva, descripcion = valores
        
        # Validar datos numéricos
        try:
            precio = float(precio)
            stock = int(stock)
            iva = float(iva) if iva else 0.16
        except Exception:
            self.formulario_mensaje = "Datos numéricos inválidos."
            return
        
        estado = "Disponible"
        conexion = Conexion()
        
        # Verificar si el producto ya existe
        query = "SELECT ID_CatProducto, Stock FROM CatProducto WHERE Nombre_prod = %s"
        resultado = conexion.consultar(query, (nombre,))
        
        if resultado:
            # Actualizar stock del producto existente
            id_prod = resultado[0]["ID_CatProducto"]
            nuevo_stock = resultado[0]["Stock"] + stock
            update = "UPDATE CatProducto SET Stock = %s WHERE ID_CatProducto = %s"
            conexion.conectar()
            conexion.cursor.execute(update, (nuevo_stock, id_prod))
            conexion.conn.commit()
            conexion.cerrar()
            self.mostrar_alerta(f"Stock actualizado para '{nombre}'.")
        else:
            # Crear nuevo producto
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
        
        # Recargar productos e imágenes
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
        
        # Cerrar formulario
        self.mostrando_formulario = False
        self.formulario_mensaje = ""

    def verificar_stock(self, id_catproducto, cantidad):
        """
        Verifica si hay stock suficiente de un producto
        
        Args:
            id_catproducto (int): ID del producto en catálogo
            cantidad (int): Cantidad solicitada
            
        Returns:
            bool: True si hay stock suficiente, False en caso contrario
        """
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

    def registrar_venta(self, tipo_pago="Efectivo"):
            """
            Registra una venta completa en la base de datos
            
            Proceso:
            1. Inserta la venta principal con fecha y total
            2. Inserta el detalle de cada producto
            3. Actualiza el stock de cada producto
            
            Args:
                tipo_pago (str): Tipo de pago usado ("Efectivo" o "Tarjeta")
            
            Returns:
                bool: True si la venta se registró exitosamente
            """
            try:
                conexion = Conexion()
                conexion.conectar()
                
                if not conexion.conn:
                    print("Error: No se pudo conectar a la base de datos")
                    return False
                    
                total_venta = self.calcular_total_con_iva()  # Total con IVA
                fecha_venta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Insertar venta principal
                insert_venta_query = """
                INSERT INTO Venta (Fecha_venta, Total_venta)
                VALUES (%s, %s)
                """
                
                try:
                    conexion.cursor.execute(insert_venta_query, (fecha_venta, total_venta))
                    conexion.conn.commit()
                    
                    # Obtener ID de la venta recién creada
                    id_venta = conexion.cursor.lastrowid
                    print(f"Venta registrada con ID: {id_venta}")
                    
                    # Insertar detalles de la venta
                    for producto in self.ticket.productos:
                        insert_detalle_venta_query = """
                        INSERT INTO Detalle_Venta (Cantidad, PrecioUnitario, Subtotal, FK_ID_Venta, FK_ID_CatProducto)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        subtotal = float(producto["unidades"]) * float(producto["precio"])
                        
                        conexion.cursor.execute(insert_detalle_venta_query, 
                            (producto["unidades"], producto["precio"], subtotal, id_venta, producto["id"]))
                        
                        # Actualizar stock del producto
                        update_catproducto_query = """
                        UPDATE CatProducto
                        SET Stock = Stock - %s
                        WHERE ID_CatProducto = %s
                        """
                        conexion.cursor.execute(update_catproducto_query, 
                            (producto["unidades"], producto["id"]))
                    
                    # Confirmar todos los cambios
                    conexion.conn.commit()
                    
                    # Actualizar el ticket con el tipo de pago antes de guardar el PDF
                    self.ticket.tipo_pago = tipo_pago
                    
                    
                    print(f"Venta completada exitosamente. Tipo de pago: {tipo_pago}")
                    return True
                    
                except Error as e:
                    print(f"Error al insertar en la base de datos: {e}")
                    conexion.conn.rollback()
                    return False
                    
            except Exception as e:
                print(f"Error durante la venta: {e}")
                return False
            finally:
                conexion.cerrar()

    def validar_correo(self, correo):
        """
        Valida el formato de un correo electrónico
        
        Args:
            correo (str): Dirección de correo a validar
            
        Returns:
            bool: True si el formato es válido
        """
        return re.match(r"[^@]+@[^@]+\.[^@]+", correo) is not None

    def enviar_ticket_por_correo(self, correo_destino):
        """
        Envía el ticket como archivo PDF adjunto por correo electrónico
        
        Args:
            correo_destino (str): Dirección de correo del destinatario
            
        Returns:
            bool: True si el correo se envió exitosamente
        """
        try:
            pdf_path = "ticket.pdf"
            
            # Guardar ticket si no existe
            if not os.path.exists(pdf_path):
                self.ticket.guardar_pdf(pdf_path)
            
            # Configuración del correo
            remitente = "nado17hernsvas@gmail.com"
            password = "rhkt wtfb cjco swpw"  # App password de Gmail
            asunto = "Su ticket de compra"
            cuerpo = "Adjunto encontrará su ticket de compra. ¡Gracias por su preferencia!"
            
            # Crear mensaje
            msg = EmailMessage()
            msg["Subject"] = asunto
            msg["From"] = remitente
            msg["To"] = correo_destino
            msg.set_content(cuerpo)
            
            # Adjuntar PDF
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename="ticket.pdf")
            
            # Enviar correo
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(remitente, password)
                smtp.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False
        
    def procesar_pago_tarjeta(self, total):
        """
        Procesa el pago con tarjeta usando la terminal MercadoPago
        
        Args:
            total (float): Total a cobrar
        """
        try:
            from pagotarjeta import PagoTarjeta
            
            # Crear y mostrar la ventana de pago con tarjeta
            pago_tarjeta = PagoTarjeta(self.x, self.y, self.ancho, self.alto, total)
            
            # Esperar a que el usuario complete el pago
            self.mostrando_pago_tarjeta = True
            self.pago_tarjeta_instance = pago_tarjeta
            
        except Exception as e:
            self.mostrar_alerta(f"Error al procesar pago con tarjeta: {e}")