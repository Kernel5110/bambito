"""
Sistema de Punto de Venta para Panadería - CORREGIDO Y OPTIMIZADO
----------------------------------------------------------------
Sistema completo de punto de venta con las siguientes correcciones:
- Métodos llamados correctamente con paréntesis
- Carga perezosa de datos pesados
- Mejor manejo de errores
- Optimización de consultas a la base de datos
- Cache de imágenes y datos
- Validaciones mejoradas

Versión: 1.1 Corregida
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
import threading
import time

# Constantes para colores y fuentes
COLOR_FONDO = (241, 236, 227)
COLOR_TEXTO = (0, 0, 0)
COLOR_BOTON = (0, 120, 220)
COLOR_BOTON_BORDE = (0, 80, 180)
COLOR_ALERTA = (255, 200, 200)
COLOR_ALERTA_BORDE = (200, 0, 0)

class InputBox:
    """Clase para crear campos de entrada de texto personalizados"""
    
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
        """Maneja eventos de mouse y teclado para el campo"""
        if event.type == pygame.MOUSEBUTTONDOWN:
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
                            if self.numeric:
                                valid_chars = '0123456789.'
                                filtered_text = ''.join(c for c in clipboard_text if c in valid_chars)
                                if filtered_text.count('.') > 1:
                                    parts = filtered_text.split('.')
                                    filtered_text = parts[0] + '.' + ''.join(parts[1:])
                                if filtered_text and (not self.text or '.' not in self.text):
                                    self.text += filtered_text
                            else:
                                if len(self.text + clipboard_text) <= 50:
                                    self.text += clipboard_text
                    except Exception as e:
                        print(f"Error al pegar texto: {e}")
                return
            
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
        """Actualiza el ancho del campo según el contenido"""
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        """Dibuja el campo en la pantalla"""
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_value(self):
        """Obtiene el valor actual del campo"""
        return self.text

class DataCache:
    """Clase para manejar el cache de datos y optimizar consultas"""
    
    def __init__(self):
        self.productos = []
        self.promedios_ventas = []
        self.imagenes_productos = []
        self.last_refresh = 0
        self.refresh_interval = 30  # 30 segundos
        self._loading = False
    
    def needs_refresh(self):
        """Verifica si los datos necesitan actualizarse"""
        return time.time() - self.last_refresh > self.refresh_interval
    
    def is_loading(self):
        """Verifica si los datos se están cargando"""
        return self._loading
    
    def refresh_data(self, pos_instance):
        """Actualiza los datos en segundo plano"""
        if self._loading:
            return
            
        def load_data():
            self._loading = True
            try:
                # Cargar productos
                self.productos = pos_instance.cargar_productos_desde_db()
                # Cargar promedios de ventas
                self.promedios_ventas = pos_instance.obtener_promedios_ventas()
                # Cargar imágenes
                self.imagenes_productos = pos_instance.cargar_imagenes_desde_cache()
                self.last_refresh = time.time()
                print("Cache de datos actualizado")
            except Exception as e:
                print(f"Error al actualizar cache: {e}")
            finally:
                self._loading = False
        
        # Ejecutar en hilo separado para no bloquear la UI
        thread = threading.Thread(target=load_data)
        thread.daemon = True
        thread.start()

class PuntoVenta:
    """Clase principal del sistema de punto de venta - OPTIMIZADA"""
    
    def __init__(self, x=0, y=0, ancho=1900, alto=1000, id_empleado=1):
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
            scale = min(self.ancho / 1585, self.alto / 870)
            return int(base_size * scale)

        self.fuente_producto = pygame.font.SysFont("Open Sans", fuente_relativa(28))
        self.fuente_tit = pygame.font.SysFont("Times New Roman", int(self.alto * 0.08), bold=True)
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", fuente_relativa(36), bold=True)
        self.fuente_ticket = pygame.font.SysFont("Open Sans", fuente_relativa(28))
        self.fuente_busqueda = pygame.font.SysFont("Open Sans", fuente_relativa(28))

        # Inicializar cache de datos
        self.data_cache = DataCache()
        
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
        
        # Variables para scroll - AJUSTADAS PARA DISEÑO AMPLIADO
        self.scroll_productos = 0
        self.productos_por_fila = 2  # CAMBIO: Ahora 2 productos por fila
        self.filas_visibles = 3      # CAMBIO: Menos filas visibles debido al mayor tamaño
        self.scroll_ticket = 0
        self.productos_ticket_visibles = 6

        # Tiempos de alerta visible
        self.alerta = ""
        self.tiempo_alerta = 0
        self.duracion_alerta = 5000  # 5 segundos

        # CORREGIDO: Llamar correctamente al método
        self.minimo = []  # Inicializar como lista vacía
        
        # Cargar datos inicial
        self.cargar_datos_inicial()

    def cargar_datos_inicial(self):
        """Carga los datos iniciales de forma optimizada"""
        try:
            # Cargar productos
            self.productos = self.cargar_productos_desde_db()
            # Cargar promedios de ventas
            self.minimo = self.obtener_promedios_ventas()  # CORREGIDO: Ahora con paréntesis
            # Cargar imágenes
            self.cargar_imagenes()
            # Actualizar cache
            self.data_cache.productos = self.productos
            self.data_cache.promedios_ventas = self.minimo
            self.data_cache.last_refresh = time.time()
        except Exception as e:
            print(f"Error al cargar datos iniciales: {e}")
            # Valores por defecto en caso de error
            self.productos = []
            self.minimo = []
            self.imagenes_productos = []

    def cargar_imagenes(self):
        """Carga las imágenes de productos de forma optimizada - TAMAÑO AMPLIADO"""
        try:
            # Si no hay productos, no cargar imágenes
            if not hasattr(self, 'productos') or not self.productos:
                self.productos = self.cargar_productos_desde_db()
            
            self.imagenes_productos = []
            # TAMAÑO AMPLIADO: Imágenes más grandes para las tarjetas ampliadas
            tamaño_imagen = (int(145 * self.ancho / 1585), int(145 * self.alto / 870))
            
            for prod in self.productos:
                ruta_imagen = prod.get("imagen", "imagenes/log.png")
                try:
                    if os.path.exists(ruta_imagen):
                        imagen = pygame.image.load(ruta_imagen).convert_alpha()
                        imagen = pygame.transform.smoothscale(imagen, tamaño_imagen)
                    else:
                        # Imagen por defecto MÁS GRANDE con mejor diseño
                        imagen = pygame.Surface(tamaño_imagen)
                        imagen.fill((245, 245, 245))
                        
                        # Marco decorativo
                        pygame.draw.rect(imagen, (200, 200, 200), imagen.get_rect(), 2)
                        
                        # Icono de imagen faltante más grande
                        centro_x, centro_y = tamaño_imagen[0] // 2, tamaño_imagen[1] // 2
                        
                        # Dibujar un icono de imagen simple
                        icon_size = min(tamaño_imagen) // 3
                        icon_rect = pygame.Rect(centro_x - icon_size//2, centro_y - icon_size//2 - 10, icon_size, icon_size//2)
                        pygame.draw.rect(imagen, (180, 180, 180), icon_rect, 3)
                        
                        # Círculo para representar una imagen
                        pygame.draw.circle(imagen, (180, 180, 180), (centro_x - icon_size//4, centro_y - icon_size//4), icon_size//8, 2)
                        
                        # Texto "Sin imagen" más legible
                        font = pygame.font.SysFont("Arial", int(16 * self.ancho / 1585), bold=True)
                        text = font.render("Sin imagen", True, (120, 120, 120))
                        text_rect = text.get_rect(center=(centro_x, centro_y + 20))
                        imagen.blit(text, text_rect)
                        
                except Exception as e:
                    print(f"Error al cargar imagen {ruta_imagen}: {e}")
                    # Imagen de error más informativa
                    imagen = pygame.Surface(tamaño_imagen)
                    imagen.fill((255, 240, 240))
                    
                    pygame.draw.rect(imagen, (200, 0, 0), imagen.get_rect(), 2)
                    
                    font = pygame.font.SysFont("Arial", int(14 * self.ancho / 1585), bold=True)
                    error_text = font.render("Error de", True, (200, 0, 0))
                    error_text2 = font.render("imagen", True, (200, 0, 0))
                    
                    centro_x, centro_y = tamaño_imagen[0] // 2, tamaño_imagen[1] // 2
                    imagen.blit(error_text, (centro_x - error_text.get_width()//2, centro_y - 15))
                    imagen.blit(error_text2, (centro_x - error_text2.get_width()//2, centro_y + 5))
                
                self.imagenes_productos.append(imagen)
        except Exception as e:
            print(f"Error en cargar_imagenes: {e}")
            self.imagenes_productos = []

    def cargar_imagenes_desde_cache(self):
        """Carga imágenes usando el cache"""
        if hasattr(self, 'imagenes_productos') and self.imagenes_productos:
            return self.imagenes_productos
        else:
            self.cargar_imagenes()
            return self.imagenes_productos

    def cargar_productos_desde_db(self):
        """Carga productos desde la base de datos con manejo de errores mejorado"""
        try:
            conexion = Conexion()
            query = """
                SELECT ID_CatProducto, Nombre_prod AS nombre, Precio AS precio, 
                       Imagen AS imagen, Stock
                FROM CatProducto
                WHERE Estado='Disponible' AND Stock > 0
                ORDER BY Nombre_prod
            """
            productos = conexion.consultar(query)
            
            if not productos:
                print("No se encontraron productos disponibles")
                return []
            
            # Asignar imagen por defecto si no existe
            for prod in productos:
                if not prod.get("imagen"):
                    prod["imagen"] = "imagenes/log.png"
            
            return productos
        except Exception as e:
            print(f"Error en cargar_productos_desde_db: {e}")
            return []

    def obtener_promedios_ventas(self):
        """Obtiene promedios de ventas con manejo de errores mejorado"""
        try:
            conexion = Conexion()
            query = """
                SELECT 
                    dv.fk_id_catproducto AS fk_id, 
                    COALESCE(AVG(dv.Cantidad), 5) AS minimo,
                    cp.nombre_prod
                FROM 
                    detalle_venta dv
                RIGHT JOIN 
                    catproducto cp ON dv.fk_id_catproducto = cp.id_catproducto
                WHERE cp.Estado = 'Disponible'
                GROUP BY 
                    cp.id_catproducto, cp.nombre_prod
            """
            promedios = conexion.consultar(query)
            
            if not promedios:
                print("No se encontraron datos de ventas, usando valores por defecto")
                return []
            
            # Redondear minimo a 2 decimales
            for prom in promedios:
                prom["minimo"] = round(float(prom["minimo"]), 2)
            
            return promedios
        except Exception as e:
            print(f"Error en obtener_promedios_ventas: {e}")
            return []

    def obtener_stock_actual(self, id_producto):
        """Obtiene el stock actual de un producto"""
        try:
            conexion = Conexion()
            query = "SELECT Stock FROM CatProducto WHERE ID_CatProducto = %s"
            resultado = conexion.consultar(query, (id_producto,))
            if resultado:
                return resultado[0]["Stock"]
            return 0
        except Exception as e:
            print(f"Error al obtener stock actual: {e}")
            return 0

    def mostrar_alerta(self, mensaje):
        """Muestra un mensaje de alerta en la interfaz"""
        self.alerta = mensaje
        self.tiempo_alerta = pygame.time.get_ticks()
        print("ALERTA:", mensaje)

    def filtrar_productos(self):
        """Filtra los productos según el texto de búsqueda"""
        if not self.busqueda_texto:
            return list(enumerate(self.productos))
        texto = self.busqueda_texto.lower()
        return [(i, prod) for i, prod in enumerate(self.productos) if texto in prod["nombre"].lower()]

    def dibujar_alerta(self, surface):
        """Dibuja la alerta actual en la pantalla con desvanecimiento"""
        if self.alerta:
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self.tiempo_alerta >= self.duracion_alerta:
                self.alerta = ""
            else:
                rect = pygame.Rect(self.x + int(0.05 * self.ancho), self.y + int(0.03 * self.alto), 
                                int(0.5 * self.ancho), int(0.06 * self.alto))
                pygame.draw.rect(surface, COLOR_ALERTA, rect, border_radius=10)
                pygame.draw.rect(surface, COLOR_ALERTA_BORDE, rect, 2, border_radius=10)
                fuente_alerta = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
                texto = fuente_alerta.render(self.alerta, True, COLOR_ALERTA_BORDE)
                surface.blit(texto, (rect.x + 20, rect.y + 10))
                
                # Efecto de desvanecimiento
                tiempo_restante = self.duracion_alerta - (tiempo_actual - self.tiempo_alerta)
                if tiempo_restante < 1000:
                    transparencia = int(255 * (tiempo_restante / 1000))
                    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    s.fill((241, 236, 227, 255 - transparencia))
                    surface.blit(s, (rect.x, rect.y))

    def dibujar_campo_busqueda(self, surface, x, y, w, h):
        """Dibuja el campo de búsqueda y el botón agregar producto"""
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
        """Dibuja una tarjeta de producto individual - TAMAÑO AMPLIADO"""
        ancho = int(0.25 * self.ancho)    # AMPLIADO: Era 0.16, ahora 0.25
        alto = int(0.30 * self.alto)      # AMPLIADO: Era 0.16, ahora 0.28 (altura doble)
        margen = int(0.015 * self.ancho)  # Mayor margen para mejor espaciado
        rect = pygame.Rect(x, y, ancho, alto)
        
        # Fondo de la tarjeta con sombra sutil
        pygame.draw.rect(surface, (220, 220, 220), (rect.x + 3, rect.y + 3, ancho, alto), border_radius=15)  # Sombra
        pygame.draw.rect(surface, self.GRIS_CLARO, rect, border_radius=15)
        pygame.draw.rect(surface, self.BORDE, rect, 3, border_radius=15)
        
        # Imagen del producto - MÁS GRANDE
        if imagen:
            # Redimensionar imagen para el nuevo tamaño
            nueva_imagen = pygame.transform.scale(imagen, (int(140 * self.ancho / 1585), int(135 * self.alto / 870)))
            img_rect = nueva_imagen.get_rect()
            img_rect.centerx = rect.centerx
            img_rect.top = y + margen
            surface.blit(nueva_imagen, img_rect)
            y_siguiente = img_rect.bottom + int(0.02 * self.alto)
        else:
            y_siguiente = y + int(0.15 * self.alto)
        
        # Nombre del producto - FUENTE MÁS GRANDE
        fuente_nombre_ampliada = pygame.font.SysFont("Open Sans", int(self.fuente_producto.get_height() * 1.4), bold=True)
        nombre_texto = producto["nombre"]
        # Truncar nombre si es muy largo para el nuevo tamaño
        if len(nombre_texto) > 20:
            nombre_texto = nombre_texto[:17] + "..."
        
        nombre_render = fuente_nombre_ampliada.render(nombre_texto, True, COLOR_TEXTO)
        nombre_x = rect.centerx - nombre_render.get_width() // 2
        surface.blit(nombre_render, (nombre_x, y_siguiente))
        
        # Precio del producto - FUENTE MÁS GRANDE Y DESTACADA
        fuente_precio_ampliada = pygame.font.SysFont("Open Sans", int(self.fuente_ticket.get_height() * 1.6), bold=True)
        precio_str = f"${producto['precio']:.2f}"
        precio_render = fuente_precio_ampliada.render(precio_str, True, (0, 120, 0))  # Verde para destacar
        precio_x = rect.centerx - precio_render.get_width() // 2
        precio_y = y_siguiente + nombre_render.get_height() + int(0.01 * self.alto)
        
        # Fondo para el precio
        precio_bg = pygame.Rect(precio_x - 8, precio_y - 2, precio_render.get_width() + 16, precio_render.get_height() + 4)
        pygame.draw.rect(surface, (219, 237, 232), precio_bg, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), precio_bg, 2, border_radius=8)
        surface.blit(precio_render, (precio_x, precio_y))
        
        # Stock disponible - MÁS VISIBLE
        fuente_stock_ampliada = pygame.font.SysFont("Open Sans", int(self.fuente_producto.get_height() * 1.2), bold=True)
        stock_disponible = producto.get('Stock', 0)
        stock_str = f"Stock: {stock_disponible}"
        
        # Color según el stock
        color_stock = (0, 150, 0) if stock_disponible > 10 else (200, 100, 0) if stock_disponible > 5 else (200, 0, 0)
        stock_render = fuente_stock_ampliada.render(stock_str, True, color_stock)
        stock_x = rect.centerx - stock_render.get_width() // 2
        stock_y = precio_y + precio_render.get_height() + int(0.015 * self.alto)
        surface.blit(stock_render, (stock_x, stock_y))
        
        # Indicador visual de stock bajo
        if stock_disponible <= 5:
            # Dibujar icono de advertencia
            warning_rect = pygame.Rect(rect.right - 25, rect.top + 5, 20, 20)
            pygame.draw.circle(surface, (255, 165, 0), warning_rect.center, 10)
            pygame.draw.circle(surface, (255, 255, 255), warning_rect.center, 8)
            fuente_warning = pygame.font.SysFont("Arial", 12, bold=True)
            warning_text = fuente_warning.render("!", True, (255, 165, 0))
            surface.blit(warning_text, (warning_rect.centerx - 3, warning_rect.centery - 6))
        
        # Borde de selección visual al pasar el mouse (opcional)
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, (0, 150, 255), rect, 4, border_radius=15)
        
        return rect

    def calcular_total_con_iva(self):
        """Calcula el total de la venta incluyendo IVA"""
        try:
            total = float(self.ticket.calcular_total())
            return total * 1.16
        except Exception as e:
            print(f"Error al calcular total con IVA: {e}")
            return 0.0

    def dibujar_ticket(self, surface):
        """Dibuja el ticket de venta con todos los productos y botones"""
        # Definir dimensiones del ticket
        x = self.x + int(0.65 * self.ancho)
        y = self.y + int(0.15 * self.alto)
        w = int(0.33 * self.ancho)
        h = int(0.9 * self.alto)

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
        productos_area_h = h - int(0.3 * h)

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
                
                # Fondo alternado
                if (i - start_idx) % 2 == 0:
                    pygame.draw.rect(surface, (250, 250, 250), producto_rect)

                # Dibujar datos del producto
                col_x = x + int(0.03 * w)

                # Nombre (truncar si es muy largo)
                nombre_texto = producto['nombre']
                if len(nombre_texto) > 15:
                    nombre_texto = nombre_texto[:12] + "..."
                nombre_render = self.fuente_ticket.render(nombre_texto, True, COLOR_TEXTO)
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
                self.ticket_productos_rects.append((producto_rect, i, btn_decrementar, btn_incrementar))

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

        # Botones del ticket
        self.dibujar_botones_ticket(surface, x, y, w, h)

    def dibujar_botones_ticket(self, surface, x, y, w, h):
        """Dibuja los botones del ticket de venta"""
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
        """Dibuja el modal de pago en efectivo"""
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

        # Botones
        self.dibujar_botones_modal_pago(surface, modal_x, modal_y, modal_w, modal_h)

        # Mensaje de error
        if self.efectivo_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", 24)
            msg = font_msg.render(self.efectivo_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_x + 30, modal_y + modal_h - 120))

    def dibujar_botones_modal_pago(self, surface, modal_x, modal_y, modal_w, modal_h):
        """Dibuja los botones del modal de pago"""
        btn_w, btn_h = 120, 50
        btn_y = modal_y + modal_h - btn_h - 70
        btn_x_confirmar = modal_x + modal_w - btn_w - 40
        btn_x_cancelar = modal_x + 40

        # Botón confirmar
        self.boton_modal_confirmar = pygame.Rect(btn_x_confirmar, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, (0, 180, 0), self.boton_modal_confirmar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.boton_modal_confirmar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", 28, bold=True)
        btn_text = font_btn.render("Confirmar", True, self.BLANCO)
        surface.blit(btn_text, (btn_x_confirmar + (btn_w - btn_text.get_width()) // 2, btn_y + (btn_h - btn_text.get_height()) // 2))

        # Botón cancelar
        self.boton_modal_cancelar_pago = pygame.Rect(btn_x_cancelar, btn_y, btn_w, btn_h)
        pygame.draw.rect(surface, (220, 0, 0), self.boton_modal_cancelar_pago, border_radius=8)
        pygame.draw.rect(surface, (180, 0, 0), self.boton_modal_cancelar_pago, 2, border_radius=8)
        btn_text_canc = font_btn.render("Cancelar", True, self.BLANCO)
        surface.blit(btn_text_canc, (btn_x_cancelar + (btn_w - btn_text_canc.get_width()) // 2, btn_y + (btn_h - btn_text_canc.get_height()) // 2))

        # Botón de pago con tarjeta
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

    def dibujar_modal_correo(self, surface):
        """Dibuja el modal para envío por correo"""
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

        # Botones
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
        """Dibuja la interfaz completa del punto de venta"""
        # Verificar si necesitamos actualizar el cache
        if self.data_cache.needs_refresh() and not self.data_cache.is_loading():
            self.data_cache.refresh_data(self)
        
        # Fondo de la interfaz
        pygame.draw.rect(surface, self.AZUL_CLARO, (self.x, self.y, self.ancho, self.alto))
        
        # Título principal - MEJORADO
        titulo = self.fuente_tit.render("Catálogo de Productos", True, COLOR_TEXTO)
        surface.blit(titulo, (self.x + int(0.02 * self.ancho), self.y + int(0.01 * self.alto)))
        
        # Mostrar alerta si existe
        self.dibujar_alerta(surface)
        
        # Campo de búsqueda - REPOSICIONADO
        busq_x = self.x + int(0.02 * self.ancho)
        busq_y = self.y + int(0.1 * self.alto)  # Movido más abajo para el subtítulo
        busq_w = int(0.38 * self.ancho)
        busq_h = int(0.05 * self.alto)
        self.dibujar_campo_busqueda(surface, busq_x, busq_y, busq_w, busq_h)
        
        # Catálogo de productos con scroll
        self.dibujar_catalogo_productos(surface)
        
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
        if getattr(self, "mostrando_pago_tarjeta", False):
            if hasattr(self, 'pago_tarjeta_instance'):
                self.pago_tarjeta_instance.dibujar(surface)

    def dibujar_catalogo_productos(self, surface):
        """Dibuja el catálogo de productos con scroll - DISEÑO AMPLIADO (2 columnas)"""
        start_x = self.x + int(0.02 * self.ancho)
        start_y = self.y + int(0.16 * self.alto)  # AJUSTADO: Más abajo para acomodar subtítulo
        spacing_x = int(0.28 * self.ancho)  # Mayor espaciado horizontal para 2 columnas
        spacing_y = int(0.32 * self.alto)   # Mayor espaciado vertical para tarjetas más altas
        cols = 2  # CAMBIO: Ahora 2 columnas en lugar de 3
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
                
                # Verificar que tenemos la imagen correspondiente - TAMAÑO AMPLIADO
                if i_original < len(self.imagenes_productos):
                    imagen = self.imagenes_productos[i_original]
                else:
                    # Crear imagen por defecto más grande
                    imagen = pygame.Surface((int(140 * self.ancho / 1585), int(140 * self.alto / 870)))
                    imagen.fill((200, 200, 200))
                    # Agregar texto "Sin imagen" más grande
                    font = pygame.font.SysFont("Arial", int(18 * self.ancho / 1585))
                    text = font.render("Sin imagen", True, (100, 100, 100))
                    imagen.blit(text, (20, 60))
                
                rect = self.dibujar_producto(surface, x, y, producto, imagen)
                self.product_rects.append((rect, i_original))
        
        # Indicador de scroll para productos - AJUSTADO PARA NUEVA POSICIÓN
        if max_scroll > 0:
            scroll_x = self.x + int(0.59 * self.ancho)  # Mantener posición
            scroll_y = start_y
            scroll_h = int(self.filas_visibles * spacing_y * 0.8)  # Ajustar altura
            
            # Barra de fondo
            pygame.draw.rect(surface, (200, 200, 200), (scroll_x, scroll_y, 10, scroll_h))
            
            # Barra de scroll
            bar_height = int(scroll_h * self.filas_visibles / total_filas)
            bar_y = scroll_y + int(scroll_h * self.scroll_productos / max_scroll)
            pygame.draw.rect(surface, (100, 100, 100), (scroll_x, bar_y, 10, bar_height))

    def handle_event(self, event):
        """Maneja todos los eventos del sistema con mejor estructura"""
        try:
            # Eventos del formulario de productos
            if self.mostrando_formulario:
                return self._handle_formulario_events(event)
            
            # Eventos del modal de correo
            if getattr(self, "mostrando_modal_correo", False):
                return self._handle_correo_events(event)
            
            # Eventos del modal de pago
            if self.mostrando_modal_pago:
                return self._handle_pago_events(event)
            
            # Eventos principales del POS
            self._handle_main_events(event)
            
        except Exception as e:
            print(f"Error en handle_event: {e}")
            self.mostrar_alerta("Error interno del sistema")

    def _handle_formulario_events(self, event):
        """Maneja eventos del formulario de productos"""
        # Manejar eventos de teclado para todos los campos
        for box in self.formulario_boxes:
            box.handle_event(event)
        
        # Manejar clics en botones
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.formulario_btn_guardar and self.formulario_btn_guardar.collidepoint(event.pos):
                self.guardar_formulario_agregar_producto()
            elif self.formulario_btn_cancelar and self.formulario_btn_cancelar.collidepoint(event.pos):
                self.mostrando_formulario = False

    def _handle_correo_events(self, event):
        """Maneja eventos del modal de correo"""
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
                        self.ticket.limpiar()  # CORREGIDO: Agregar paréntesis
                        self.mostrando_modal_correo = False
                        self.mostrar_alerta("Ticket enviado correctamente.")
                    else:
                        self.correo_mensaje = "Error al enviar el correo."
                else:
                    self.correo_mensaje = "Correo inválido."
            elif self.boton_modal_cancelar.collidepoint(event.pos):
                self.mostrando_modal_correo = False
                self.correo_mensaje = ""

    def _handle_pago_events(self, event):
        """Maneja eventos del modal de pago"""
        if self.efectivo_box:
            self.efectivo_box.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_modal_confirmar.collidepoint(event.pos):
                total_iva = self.calcular_total_con_iva()
                efectivo_str = self.efectivo_box.get_value()
                try:
                    efectivo = float(efectivo_str)
                except Exception:
                    efectivo = 0.0
                
                if efectivo < total_iva:
                    self.efectivo_mensaje = "Efectivo insuficiente."
                else:
                    exito = self.registrar_venta("Efectivo")
                    if exito:
                        self.ticket.efectivo_recibido = efectivo
                        self.ticket.cambio = efectivo - total_iva
                        self.ticket.guardar_pdf()
                        self.ticket.limpiar()  # CORREGIDO: Agregar paréntesis
                        self.mostrar_alerta(f"Venta registrada. Cambio: ${efectivo - total_iva:.2f}")
                        self.cargar_datos_inicial()  # Recargar datos
                        self.mostrando_modal_pago = False
                        self.efectivo_box = None
                        self.efectivo_mensaje = ""
                    else:
                        self.efectivo_mensaje = "Error al registrar la venta."
            
            elif self.boton_modal_cancelar_pago.collidepoint(event.pos):
                self.mostrando_modal_pago = False
                self.efectivo_box = None
                self.efectivo_mensaje = ""
            
            elif self.boton_pago_tarjeta.collidepoint(event.pos):
                total_iva = self.calcular_total_con_iva()
                self.procesar_pago_tarjeta(total_iva)

    def _handle_main_events(self, event):
        """Maneja eventos principales del POS"""
        # Manejo de scroll con rueda del mouse
        if event.type == pygame.MOUSEWHEEL:
            self._handle_scroll_events(event)
        
        # Manejo de clics del mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_clicks(event)
        
        # Eventos de teclado para búsqueda
        if event.type == pygame.KEYDOWN and self.busqueda_activa:
            self._handle_search_keyboard(event)

    def _handle_scroll_events(self, event):
        """Maneja eventos de scroll del mouse - AJUSTADO PARA DISEÑO AMPLIADO"""
        mouse_pos = pygame.mouse.get_pos()

        # Scroll en el panel de productos - ÁREA AJUSTADA
        if (self.x + int(0.02 * self.ancho) <= mouse_pos[0] <= self.x + int(0.6 * self.ancho) and
            self.y + int(0.16 * self.alto) <= mouse_pos[1] <= self.y + int(0.9 * self.alto)):  # Ajustado start_y
            if event.y > 0:  # Scroll arriba
                self.scroll_productos = max(0, self.scroll_productos - 1)
            else:  # Scroll abajo
                productos_filtrados = self.filtrar_productos()
                # CAMBIO: Ahora usar 2 columnas en lugar de 3
                total_filas = (len(productos_filtrados) + 1) // 2  # División por 2 columnas
                max_scroll = max(0, total_filas - self.filas_visibles)
                self.scroll_productos = min(max_scroll, self.scroll_productos + 1)

        # Scroll en el ticket (sin cambios)
        elif (self.x + int(0.65 * self.ancho) <= mouse_pos[0] <= self.x + int(0.98 * self.ancho) and
              self.y + int(0.15 * self.alto) <= mouse_pos[1] <= self.y + int(0.8 * self.alto)):
            if event.y > 0:  # Scroll arriba
                self.scroll_ticket = max(0, self.scroll_ticket - 1)
            else:  # Scroll abajo
                max_scroll = max(0, len(self.ticket.productos) - self.productos_ticket_visibles)
                self.scroll_ticket = min(max_scroll, self.scroll_ticket + 1)

    def _handle_mouse_clicks(self, event):
        """Maneja clics del mouse"""
        mouse_x, mouse_y = event.pos
        
        # Clic derecho para eliminar productos del ticket
        if event.button == 3:  # Botón derecho
            self._handle_right_click(mouse_x, mouse_y)
            return
        
        # Clics principales
        if hasattr(self, "busq_rect") and self.busq_rect and self.busq_rect.collidepoint(mouse_x, mouse_y):
            self.busqueda_activa = True
        elif hasattr(self, "boton_agregar_producto_rect") and self.boton_agregar_producto_rect and self.boton_agregar_producto_rect.collidepoint(mouse_x, mouse_y):
            self.mostrar_formulario_agregar_producto()
        elif hasattr(self, "boton_enviar_rect") and self.boton_enviar_rect and self.boton_enviar_rect.collidepoint(mouse_x, mouse_y):
            self.mostrando_modal_correo = True
            self.correo_box = None
            self.correo_mensaje = ""
        elif hasattr(self, "boton_factura_rect") and self.boton_factura_rect and self.boton_factura_rect.collidepoint(mouse_x, mouse_y):
            self._handle_factura_click()
        elif self.boton_pagar_rect and self.boton_pagar_rect.collidepoint(mouse_x, mouse_y):
            if self.ticket.productos:
                self.mostrando_modal_pago = True
                self.efectivo_box = None
                self.efectivo_mensaje = ""
            else:
                self.mostrar_alerta("El ticket está vacío.")
        else:
            self.busqueda_activa = False
            self._handle_product_clicks(mouse_x, mouse_y)
        
        # Botones de incrementar/decrementar del ticket
        self._handle_ticket_buttons(event)

    def _handle_right_click(self, mouse_x, mouse_y):
        """Maneja clic derecho para eliminar productos"""
        if hasattr(self, 'ticket_productos_rects'):
            for rect_data in self.ticket_productos_rects:
                if len(rect_data) >= 2:
                    rect, idx = rect_data[0], rect_data[1]
                    if rect.collidepoint(mouse_x, mouse_y):
                        if 0 <= idx < len(self.ticket.productos):
                            producto_eliminado = self.ticket.productos[idx]
                            self.ticket.eliminar_producto(idx)
                            self.mostrar_alerta(f"Producto '{producto_eliminado['nombre']}' eliminado del ticket")
                            max_scroll = max(0, len(self.ticket.productos) - self.productos_ticket_visibles)
                            self.scroll_ticket = min(self.scroll_ticket, max_scroll)
                        break

    def _handle_product_clicks(self, mouse_x, mouse_y):
        """Maneja clics en productos del catálogo"""
        for rect, idx in self.product_rects:
            if rect and rect.collidepoint(mouse_x, mouse_y):
                if idx < len(self.productos):
                    prod = self.productos[idx]
                    # Verificar si el producto ya está en el ticket
                    if self.ticket.buscar_producto_por_nombre(prod["nombre"]):
                        cantidad_actual = self.ticket.obtener_cantidad_producto(prod["nombre"])
                        cantidad_nueva = cantidad_actual + 1
                        
                        if self.verificar_stock(prod["ID_CatProducto"], cantidad_nueva):
                            self.ticket.agregar_producto(prod["nombre"], 1, prod["precio"], prod["ID_CatProducto"])
                            self.mostrar_alerta(f"Incrementada cantidad de {prod['nombre']} en el ticket")
                        else:
                            self.mostrar_alerta(f"No hay suficiente stock para agregar más '{prod['nombre']}'")
                    else:
                        if self.verificar_stock(prod["ID_CatProducto"], 1):
                            self.ticket.agregar_producto(prod["nombre"], 1, prod["precio"], prod["ID_CatProducto"])
                            self.mostrar_alerta(f"Producto agregado al ticket: {prod['nombre']}")
                        else:
                            self.mostrar_alerta(f"No hay suficiente stock de '{prod['nombre']}'")
                break

    def _handle_ticket_buttons(self, event):
        """Maneja botones de incrementar/decrementar del ticket"""
        if hasattr(self, 'ticket_productos_rects'):
            for rect_data in self.ticket_productos_rects:
                if len(rect_data) >= 4:
                    rect, idx, btn_decrementar, btn_incrementar = rect_data
                    
                    if btn_decrementar.collidepoint(event.pos):
                        if 0 <= idx < len(self.ticket.productos):
                            producto = self.ticket.productos[idx]
                            if producto['unidades'] > 1:
                                producto['unidades'] -= 1
                            else:
                                self.ticket.eliminar_producto(idx)
                                self.mostrar_alerta(f"Producto '{producto['nombre']}' eliminado del ticket")
                                max_scroll = max(0, len(self.ticket.productos) - self.productos_ticket_visibles)
                                self.scroll_ticket = min(self.scroll_ticket, max_scroll)
                    
                    elif btn_incrementar.collidepoint(event.pos):
                        if 0 <= idx < len(self.ticket.productos):
                            producto = self.ticket.productos[idx]
                            # Obtener stock mínimo con valor por defecto
                            minimo_producto = self._get_minimo_producto(producto['id'])
                            
                            if self.verificar_stock(producto['id'], producto['unidades'] + 1):
                                producto['unidades'] += 1
                                stock_actual = self.obtener_stock_actual(producto['id'])
                                if stock_actual - producto['unidades'] <= minimo_producto:
                                    self.mostrar_alerta(f"Se recomienda hornear más de '{producto['nombre']}': mínimo alcanzado")
                            else:
                                self.mostrar_alerta(f"Stock insuficiente de '{producto['nombre']}'")

    def _get_minimo_producto(self, producto_id):
        """Obtiene el mínimo de stock para un producto"""
        try:
            # CORREGIDO: Verificar que self.minimo es una lista y no un método
            if isinstance(self.minimo, list):
                for item in self.minimo:
                    if item.get('fk_id') == producto_id:
                        return float(item.get('minimo', 5))
            return 5.0  # Valor por defecto
        except Exception as e:
            print(f"Error al obtener mínimo del producto: {e}")
            return 5.0

    def _handle_search_keyboard(self, event):
        """Maneja eventos de teclado para búsqueda"""
        if event.key == pygame.K_BACKSPACE:
            self.busqueda_texto = self.busqueda_texto[:-1]
        elif event.key == pygame.K_RETURN:
            self.busqueda_activa = False
        elif event.key == pygame.K_ESCAPE:
            self.busqueda_texto = ""
            self.busqueda_activa = False
        else:
            if len(self.busqueda_texto) < 30 and event.unicode.isprintable():
                self.busqueda_texto += event.unicode

    def _handle_factura_click(self):
        """Maneja clic en botón de factura"""
        try:
            from factura import Factura
            import asyncio
            factura = Factura(self.x, self.y, self.ancho, self.alto)
            asyncio.run(factura.main())
        except Exception as e:
            self.mostrar_alerta(f"Error al generar factura: {e}")

    def mostrar_formulario_agregar_producto(self):
        """Configura y muestra el formulario para agregar/actualizar productos"""
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
            box = InputBox(x + int(0.15 * self.ancho), y + i * int(0.06 * self.alto), 
                          int(0.14 * self.ancho), int(0.045 * self.alto), font=font, numeric=numeric)
            self.formulario_boxes.append(box)
        
        # Botones del formulario
        self.formulario_btn_guardar = pygame.Rect(x, y + 10 + len(labels) * int(0.06 * self.alto), 
                                                 int(0.13 * self.ancho), int(0.06 * self.alto))
        self.formulario_btn_cancelar = pygame.Rect(x + int(0.15 * self.ancho), y + 10 + len(labels) * int(0.06 * self.alto), 
                                                  int(0.13 * self.ancho), int(0.06 * self.alto))
        self.formulario_mensaje = ""

    def dibujar_formulario_agregar_producto(self, surface):
        """Dibuja el formulario para agregar productos"""
        modal_rect = pygame.Rect(self.x + int(0.18 * self.ancho), self.y + int(0.10 * self.alto), 
                                int(0.45 * self.ancho), int(0.7 * self.alto))
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
        
        # Dibujar botones
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

        # Mensaje
        if self.formulario_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
            msg = font_msg.render(self.formulario_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_rect.x + 30, modal_rect.y + modal_rect.height - 50))

    def guardar_formulario_agregar_producto(self):
        """Guarda o actualiza un producto en la base de datos"""
        try:
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
            
            # Recargar datos
            self.cargar_datos_inicial()
            
            # Cerrar formulario
            self.mostrando_formulario = False
            self.formulario_mensaje = ""
            
        except Exception as e:
            print(f"Error al guardar producto: {e}")
            self.formulario_mensaje = f"Error al guardar: {str(e)}"

    def verificar_stock(self, id_catproducto, cantidad):
        """Verifica si hay stock suficiente de un producto"""
        try:
            conexion = Conexion()
            query = "SELECT Stock FROM CatProducto WHERE ID_CatProducto = %s"
            resultado = conexion.consultar(query, (id_catproducto,))
            if resultado and resultado[0]["Stock"] >= cantidad:
                return True
            return False
        except Exception as e:
            print(f"Error en verificar_stock: {e}")
            return False

    def registrar_venta(self, tipo_pago="Efectivo"):
        """Registra una venta completa en la base de datos"""
        try:
            conexion = Conexion()
            conexion.conectar()
            
            if not conexion.conn:
                print("Error: No se pudo conectar a la base de datos")
                return False
                
            total_venta = self.calcular_total_con_iva()
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
                
                # Actualizar el ticket con el tipo de pago
                self.ticket.tipo_pago = tipo_pago
                
                print(f"Venta completada exitosamente. Tipo de pago: {tipo_pago}")
                return True
                
            except Exception as e:
                print(f"Error al insertar en la base de datos: {e}")
                if conexion.conn:
                    conexion.conn.rollback()
                return False
                
        except Exception as e:
            print(f"Error durante la venta: {e}")
            return False
        finally:
            conexion.cerrar()

    def validar_correo(self, correo):
        """Valida el formato de un correo electrónico"""
        return re.match(r"[^@]+@[^@]+\.[^@]+", correo) is not None

    def enviar_ticket_por_correo(self, correo_destino):
        """Envía el ticket como archivo PDF adjunto por correo electrónico"""
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
        """Procesa el pago con tarjeta usando la terminal MercadoPago"""
        try:
            from pagotarjeta import PagoTarjeta
            
            # Crear y mostrar la ventana de pago con tarjeta
            pago_tarjeta = PagoTarjeta(self.x, self.y, self.ancho, self.alto, total)
            
            # Esperar a que el usuario complete el pago
            self.mostrando_pago_tarjeta = True
            self.pago_tarjeta_instance = pago_tarjeta
            
        except Exception as e:
            self.mostrar_alerta(f"Error al procesar pago con tarjeta: {e}")