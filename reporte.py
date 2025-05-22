import pygame
from conexion import Conexion
import math
import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class reporte:
    def __init__(self, x, y, ancho, alto):
        """
        Inicializa la clase reporte con las dimensiones y posiciones proporcionadas.

        :param x: Coordenada x de la posición inicial.
        :param y: Coordenada y de la posición inicial.
        :param ancho: Ancho del área de visualización.
        :param alto: Alto del área de visualización.
        """
        pygame.font.init()
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

        # Colores para el fondo y el texto
        self.FONDO = (241, 236, 227)
        self.color_texto = (0, 0, 0)

        # Función para escalar fuentes y elementos de manera proporcional
        def fuente_relativa(base_size):
            """
            Calcula el tamaño de la fuente basado en el tamaño del área de visualización.

            :param base_size: Tamaño base de la fuente.
            :return: Tamaño de la fuente escalado.
            """
            scale = min(self.ancho / 1555, self.alto / 710)
            return int(base_size * scale)

        # Inicialización de fuentes para diferentes elementos de la interfaz
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", fuente_relativa(36), bold=True)
        self.fuente_boton = pygame.font.SysFont("Open Sans", fuente_relativa(28), bold=True)
        self.fuente_boton_agregar = pygame.font.SysFont("Open Sans", fuente_relativa(28), bold=True)
        self.fuente_boton_pdf = pygame.font.SysFont("Open Sans", fuente_relativa(28), bold=True)
        self.fuente_pie_pagina = pygame.font.SysFont("Open Sans", fuente_relativa(28), bold=True)

        # Opciones disponibles en el informe
        self.botones_opciones = ["VENTAS", "PRODUCTOS", "HORARIOS", "CORTE CAJA", "INVENTARIO", "PEDIDOS"]
        self.opcion_seleccionada = self.botones_opciones[0]

        # Calcula posiciones y tamaños relativos para los botones
        self.boton_width = int(self.ancho * 0.09)
        self.boton_rects = [
            pygame.Rect(
                self.x + int(0.013 * self.ancho) + i * (self.boton_width + int(0.01 * self.ancho)),
                self.y + int(0.11 * self.alto),
                self.boton_width,
                int(0.06 * self.alto)
            ) for i in range(len(self.botones_opciones))
        ]
        self.color_boton = (220, 220, 220)
        self.color_boton_activo = (180, 180, 255)

        # Rectángulo para el botón de agregar
        self.boton_agregar_rect = pygame.Rect(
            self.x + int(0.013 * self.ancho) + len(self.botones_opciones) * (self.boton_width + int(0.01 * self.ancho)) + int(0.012 * self.ancho),
            self.y + int(0.11 * self.alto),
            int(0.09 * self.ancho),
            int(0.06 * self.alto)
        )
        self.color_boton_agregar = (100, 200, 100)
        self.color_boton_agregar_hover = (80, 180, 80)
        self.agregar_hover = False

        # Rectángulo para el botón de PDF
        self.boton_pdf_rect = pygame.Rect(
            self.x + int(0.013 * self.ancho) + len(self.botones_opciones) * (self.boton_width + int(0.01 * self.ancho)) + int(0.12 * self.ancho),
            self.y + int(0.11 * self.alto),
            int(0.12 * self.ancho),
            int(0.06 * self.alto)
        )
        self.color_boton_pdf = (100, 100, 200)
        self.color_boton_pdf_hover = (80, 80, 180)
        self.pdf_hover = False

        # Datos de ventas por día
        self.ventas_por_dia = []
        self.max_ventas = 0

        # Datos de productos más vendidos
        self.productos_mas_vendidos = []
        self.total_unidades_vendidas = 0

        # Datos de ventas por hora
        self.ventas_por_hora = [0] * 24
        self.max_ventas_hora = 0

        # Datos del corte de caja
        self.fecha_corte = datetime.datetime.now().strftime('%Y-%m-%d')
        self.corte_caja_datos = {}
        self.metodos_pago = []
        # Selector de fecha para corte de caja - MOVIDO MÁS ABAJO
        self.fecha_seleccionada = self.fecha_corte
        self.selector_fecha_rect = None  # Se calculará dinámicamente
        self.selector_fecha_activo = False

        # Botones para cambiar fecha - también se calcularán dinámicamente
        self.boton_fecha_anterior = None
        self.boton_fecha_siguiente = None

        # Selector de fecha para corte de caja
        self.fecha_seleccionada = self.fecha_corte
        self.selector_fecha_rect = pygame.Rect(
            self.x + int(0.35 * self.ancho),
            self.y + int(0.11 * self.alto),
            int(0.15 * self.ancho),
            int(0.06 * self.alto)
        )
        self.selector_fecha_activo = False

        # Botones para cambiar fecha
        self.boton_fecha_anterior = pygame.Rect(
            self.x + int(0.32 * self.ancho),
            self.y + int(0.11 * self.alto),
            int(0.03 * self.ancho),
            int(0.06 * self.alto)
        )

        self.boton_fecha_siguiente = pygame.Rect(
            self.x + int(0.51 * self.ancho),
            self.y + int(0.11 * self.alto),
            int(0.03 * self.ancho),
            int(0.06 * self.alto)
        )

        # Datos para reporte de inventario
        self.inventario_datos = []
        self.inventario_filtro = "TODOS"  # TODOS, BAJO, AGOTADO
        self.filtros_inventario = ["TODOS", "BAJO", "AGOTADO"]
        self.botones_filtro_inventario = []
        
        # Variables de scroll para inventario
        self.inventario_scroll_y = 0
        self.inventario_scroll_max = 0
        self.inventario_scroll_speed = 30  # Píxeles por scroll
        self.inventario_visible_rows = 12  # Número de filas visibles
        self.inventario_row_height = 40
        
        # Área de scroll del inventario
        self.inventario_scroll_area = None

        # Botones para filtros de inventario
        for i, filtro in enumerate(self.filtros_inventario):
            self.botones_filtro_inventario.append(
                pygame.Rect(
                    self.x + int(0.2 * self.ancho) + i * int(0.11 * self.ancho),
                    self.y + int(0.18 * self.alto),
                    int(0.1 * self.ancho),
                    int(0.04 * self.alto)
                )
            )

        # Datos para reporte de pedidos
        self.pedidos_datos = []
        self.pedidos_filtro = "TODOS"  # TODOS, PENDIENTES, COMPLETADOS
        self.filtros_pedidos = ["TODOS", "PENDIENTES", "COMPLETADOS"]
        self.botones_filtro_pedidos = []
        
        # Variables de scroll para pedidos
        self.pedidos_scroll_y = 0
        self.pedidos_scroll_max = 0
        self.pedidos_scroll_speed = 30  # Píxeles por scroll
        self.pedidos_visible_rows = 10  # Número de filas visibles
        self.pedidos_row_height = 40
        
        # Área de scroll de pedidos
        self.pedidos_scroll_area = None

        # Botones para filtros de pedidos
        for i, filtro in enumerate(self.filtros_pedidos):
            self.botones_filtro_pedidos.append(
                pygame.Rect(
                    self.x + int(0.2 * self.ancho) + i * int(0.11 * self.ancho),
                    self.y + int(0.18 * self.alto),
                    int(0.1 * self.ancho),
                    int(0.04 * self.alto)
                )
            )

        # Variables para barra de scroll
        self.scroll_bar_width = 15
        self.scroll_handle_height = 50
        self.dragging_scroll = False
        self.drag_offset = 0

    def cargar_ventas_por_dia(self):
        """
        Carga los datos de ventas por día desde la base de datos.
        """
        conexion = Conexion()
        query = """
            SELECT DATE(Fecha_venta) as dia, SUM(Total_venta) as total
            FROM Venta
            GROUP BY dia
            ORDER BY dia ASC
            LIMIT 14
        """
        resultados = conexion.consultar(query)
        self.ventas_por_dia = [(r['dia'], float(r['total'])) for r in resultados]
        self.max_ventas = max([v for _, v in self.ventas_por_dia], default=1)

    def cargar_productos_mas_vendidos(self, top_n=8):
        """
        Carga los datos de los productos más vendidos desde la base de datos.

        :param top_n: Número de productos más vendidos a cargar.
        """
        conexion = Conexion()
        query = """
            SELECT cp.Nombre_prod AS nombre, SUM(dv.Cantidad) AS unidades
            FROM Detalle_Venta dv
            JOIN CatProducto cp ON dv.FK_ID_CatProducto = cp.ID_CatProducto
            GROUP BY cp.Nombre_prod
            ORDER BY unidades DESC
            LIMIT %s
        """
        resultados = conexion.consultar(query, (top_n,))
        self.productos_mas_vendidos = [(r['nombre'], int(r['unidades'])) for r in resultados]
        self.total_unidades_vendidas = sum([u for _, u in self.productos_mas_vendidos])

    def cargar_ventas_por_hora(self):
        """
        Carga los datos de ventas por hora desde la base de datos.
        """
        conexion = Conexion()
        query = """
            SELECT HOUR(v.Fecha_venta) AS hora, SUM(dv.Cantidad) AS total
            FROM Detalle_Venta dv
            JOIN Venta v ON dv.FK_ID_Venta = v.ID_Venta
            GROUP BY hora
            ORDER BY hora ASC
        """
        resultados = conexion.consultar(query)
        self.ventas_por_hora = [0] * 24
        for r in resultados:
            hora = int(r['hora'])
            total = int(r['total'])
            self.ventas_por_hora[hora] = total
        self.max_ventas_hora = max(self.ventas_por_hora, default=1)

    def cargar_corte_caja(self, fecha=None):
        """
        Carga los datos para el corte de caja de la fecha especificada.

        :param fecha: Fecha para la cual cargar los datos. Si no se especifica, se usa la fecha actual.
        """
        if not fecha:
            fecha = self.fecha_corte

        conexion = Conexion()

        # Ventas totales del día
        query_ventas = """
            SELECT COUNT(*) as num_ventas, SUM(Total_venta) as total_ventas
            FROM Venta
            WHERE DATE(Fecha_venta) = %s
        """
        resultado_ventas = conexion.consultar(query_ventas, (fecha,))

        # Ventas por estado
        query_estados = """
            SELECT Estado, COUNT(*) as cantidad, SUM(Total_venta) as total
            FROM Venta
            WHERE DATE(Fecha_venta) = %s
            GROUP BY Estado
        """
        resultado_estados = conexion.consultar(query_estados, (fecha,))

        # Productos vendidos ese día
        query_productos = """
            SELECT cp.Nombre_prod, SUM(dv.Cantidad) as cantidad, SUM(dv.Subtotal) as total
            FROM Detalle_Venta dv
            JOIN Venta v ON dv.FK_ID_Venta = v.ID_Venta
            JOIN CatProducto cp ON dv.FK_ID_CatProducto = cp.ID_CatProducto
            WHERE DATE(v.Fecha_venta) = %s
            GROUP BY cp.Nombre_prod
            ORDER BY cantidad DESC
            LIMIT 10
        """
        resultado_productos = conexion.consultar(query_productos, (fecha,))

        # Organizar datos
        self.corte_caja_datos = {
            'fecha': fecha,
            'ventas': resultado_ventas[0] if resultado_ventas else {'num_ventas': 0, 'total_ventas': 0},
            'estados': resultado_estados,
            'productos': resultado_productos
        }

        # Total de ventas
        total_ventas = float(self.corte_caja_datos['ventas']['total_ventas'] or 0)
        self.corte_caja_datos['total'] = total_ventas

        # Estados para el gráfico
        self.metodos_pago = [(e['Estado'], float(e['total'])) for e in resultado_estados] if resultado_estados else []

    def cargar_inventario(self):
        """
        Carga los datos del inventario desde la base de datos.
        """
        conexion = Conexion()

        # Filtro según la opción seleccionada
        filtro_sql = ""
        if self.inventario_filtro == "BAJO":
            filtro_sql = " WHERE stock_minimo <= 10 AND stock_minimo > 0"
        elif self.inventario_filtro == "AGOTADO":
            filtro_sql = " WHERE Cantidad = 0"

        # Consultar materia prima
        query_mp = f"""
            SELECT
                mp.ID_MateriaPrima AS id,
                mp.Nombre,
                mp.Cantidad,
                mc.Nombre AS Unidad,
                tmp.Nombre AS Tipo
            FROM materiaprima mp
            JOIN medidacantidad mc ON mp.FK_ID_MedidaCantidad = mc.ID_MedidaCantidad
            JOIN tipomateriaprima tmp ON mp.FK_ID_TipoMateriaPrima = tmp.ID_TipoMateriaPrima
            {filtro_sql}
            ORDER BY mp.Cantidad ASC
        """

        try:
            resultado_mp = conexion.consultar(query_mp)
            self.inventario_datos = resultado_mp
            
            # Calcular scroll máximo
            total_rows = len(self.inventario_datos)
            if total_rows > self.inventario_visible_rows:
                self.inventario_scroll_max = (total_rows - self.inventario_visible_rows) * self.inventario_row_height
            else:
                self.inventario_scroll_max = 0
                
            # Resetear scroll al cambiar filtro
            self.inventario_scroll_y = 0
            
        except Exception as e:
            print(f"Error al cargar inventario: {e}")
            self.inventario_datos = []
            self.inventario_scroll_max = 0
            self.inventario_scroll_y = 0

    def cargar_pedidos(self):
        """
        Carga los datos de los pedidos desde la base de datos.
        """
        conexion = Conexion()

        # Filtro según la opción seleccionada
        filtro_sql = ""
        if self.pedidos_filtro == "PENDIENTES":
            filtro_sql = " WHERE p.Estado IN ('Pendiente', 'En proceso')"
        elif self.pedidos_filtro == "COMPLETADOS":
            filtro_sql = " WHERE p.Estado IN ('Entregado', 'Listo')"

        # Consultar pedidos
        query = f"""
            SELECT
                p.ID_PedidoVenta as id,
                c.Nombre_cliente as cliente,
                p.Fecha_pedido,
                p.Fecha_entrega,
                p.Estado,
                p.Total,
                DATEDIFF(p.Fecha_entrega, p.Fecha_pedido) as dias_proceso
            FROM pedidoventa p
            JOIN Cliente c ON p.FK_ID_Cliente = c.ID_Cliente
            {filtro_sql}
            ORDER BY p.Fecha_entrega DESC
            LIMIT 100
        """

        try:
            self.pedidos_datos = conexion.consultar(query)
            
            # Calcular scroll máximo
            total_rows = len(self.pedidos_datos)
            if total_rows > self.pedidos_visible_rows:
                self.pedidos_scroll_max = (total_rows - self.pedidos_visible_rows) * self.pedidos_row_height
            else:
                self.pedidos_scroll_max = 0
                
            # Resetear scroll al cambiar filtro
            self.pedidos_scroll_y = 0
            
        except Exception as e:
            print(f"Error al cargar pedidos: {e}")
            self.pedidos_datos = []
            self.pedidos_scroll_max = 0
            self.pedidos_scroll_y = 0

    def dibujar_reporte(self, surface):
        """
        Dibuja el informe en la superficie proporcionada.

        :param surface: Superficie de Pygame donde se dibujará el informe.
        """
        pygame.draw.rect(surface, self.FONDO, (self.x, self.y, self.ancho, self.alto))
        # Título dentro del área
        titulo = self.fuente_titulo.render("Reportes", True, self.color_texto)
        surface.blit(titulo, (self.x + int(0.02 * self.ancho), self.y + int(0.02 * self.alto)))

        # Botones debajo del título
        for i, rect in enumerate(self.boton_rects):
            color = self.color_boton_activo if self.opcion_seleccionada == self.botones_opciones[i] else self.color_boton
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto_boton = self.fuente_boton.render(self.botones_opciones[i], True, self.color_texto)
            text_rect = texto_boton.get_rect(center=rect.center)
            surface.blit(texto_boton, text_rect)

        # Botón PDF
        color_pdf = self.color_boton_pdf_hover if self.pdf_hover else self.color_boton_pdf
        pygame.draw.rect(surface, color_pdf, self.boton_pdf_rect, border_radius=8)
        texto_pdf = self.fuente_boton_pdf.render("Descargar PDF", True, (255, 255, 255))
        text_rect_pdf = texto_pdf.get_rect(center=self.boton_pdf_rect.center)
        surface.blit(texto_pdf, text_rect_pdf)

        if self.opcion_seleccionada == "VENTAS":
            self.dibujar_grafica_barras(surface)
        elif self.opcion_seleccionada == "PRODUCTOS":
            self.dibujar_grafica_pastel_productos(surface)
        elif self.opcion_seleccionada == "HORARIOS":
            self.dibujar_grafica_lineas_horarios(surface)
        elif self.opcion_seleccionada == "CORTE CAJA":
            self.dibujar_selector_fecha(surface)
            self.dibujar_corte_caja(surface)
        elif self.opcion_seleccionada == "INVENTARIO":
            self.dibujar_filtros_inventario(surface)
            self.dibujar_inventario_con_scroll(surface)
        elif self.opcion_seleccionada == "PEDIDOS":
            self.dibujar_filtros_pedidos(surface)
            self.dibujar_pedidos_con_scroll(surface)

    def dibujar_selector_fecha(self, surface):
        """
        Dibuja el selector de fecha en la superficie proporcionada, posicionado dinámicamente.

        :param surface: Superficie de Pygame donde se dibujará el selector de fecha.
        """
        # Calcular posición dinámica para que quede debajo de los botones principales
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        
        # Posicionar selector más abajo, justo después del área de gráficas
        selector_y = graf_y + int(0.02 * graf_h)  # Un poco más abajo del inicio del área de gráficas
        selector_w = int(0.15 * self.ancho)
        selector_h = int(0.06 * self.alto)
        selector_x = graf_x + (graf_w - selector_w) // 2  # Centrado horizontalmente
        
        # Actualizar rectángulos con las nuevas posiciones
        self.selector_fecha_rect = pygame.Rect(selector_x, selector_y, selector_w, selector_h)
        
        # Botones de navegación de fecha
        boton_w = int(0.04 * self.ancho)
        boton_h = selector_h
        margen = int(0.01 * self.ancho)
        
        self.boton_fecha_anterior = pygame.Rect(
            selector_x - boton_w - margen, 
            selector_y, 
            boton_w, 
            boton_h
        )
        
        self.boton_fecha_siguiente = pygame.Rect(
            selector_x + selector_w + margen, 
            selector_y, 
            boton_w, 
            boton_h
        )

        # Dibujar label "Fecha:"
        font_label = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        label_fecha = font_label.render("Fecha:", True, (0, 0, 0))
        label_x = selector_x - label_fecha.get_width() - int(0.02 * self.ancho)
        label_y = selector_y + (selector_h - label_fecha.get_height()) // 2
        surface.blit(label_fecha, (label_x, label_y))

        # Fondo del selector
        color_fondo = (255, 255, 255)
        color_borde = (0, 120, 220) if self.selector_fecha_activo else (180, 180, 180)
        pygame.draw.rect(surface, color_fondo, self.selector_fecha_rect, border_radius=10)
        pygame.draw.rect(surface, color_borde, self.selector_fecha_rect, 3, border_radius=10)

        # Texto de la fecha
        try:
            fecha_formateada = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            fecha_formateada = self.fecha_seleccionada
            
        fuente_fecha = pygame.font.SysFont("Open Sans", int(0.028 * self.alto))
        texto_fecha = fuente_fecha.render(fecha_formateada, True, (0, 0, 0))
        text_rect = texto_fecha.get_rect(center=self.selector_fecha_rect.center)
        surface.blit(texto_fecha, text_rect)

        # Botón anterior (flecha izquierda)
        color_btn_anterior = (200, 200, 200)
        if self.boton_fecha_anterior.collidepoint(pygame.mouse.get_pos()):
            color_btn_anterior = (170, 170, 170)
        
        pygame.draw.rect(surface, color_btn_anterior, self.boton_fecha_anterior, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 100), self.boton_fecha_anterior, 2, border_radius=8)

        # Botón siguiente (flecha derecha)
        color_btn_siguiente = (200, 200, 200)
        if self.boton_fecha_siguiente.collidepoint(pygame.mouse.get_pos()):
            color_btn_siguiente = (170, 170, 170)
            
        pygame.draw.rect(surface, color_btn_siguiente, self.boton_fecha_siguiente, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 100), self.boton_fecha_siguiente, 2, border_radius=8)

        # Flechas para los botones
        flecha_font = pygame.font.SysFont("Arial", int(self.alto * 0.04), bold=True)
        flecha_izq = flecha_font.render("<-", True, (0, 0, 0))
        flecha_der = flecha_font.render("->", True, (0, 0, 0))

        rect_izq = flecha_izq.get_rect(center=self.boton_fecha_anterior.center)
        rect_der = flecha_der.get_rect(center=self.boton_fecha_siguiente.center)

        surface.blit(flecha_izq, rect_izq)
        surface.blit(flecha_der, rect_der)

    def dibujar_filtros_inventario(self, surface):
        """
        Dibuja los botones de filtro para el inventario en la superficie proporcionada.

        :param surface: Superficie de Pygame donde se dibujarán los botones de filtro.
        """
        for i, rect in enumerate(self.botones_filtro_inventario):
            color = (180, 180, 255) if self.inventario_filtro == self.filtros_inventario[i] else (220, 220, 220)
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto = self.fuente_boton.render(self.filtros_inventario[i], True, (0, 0, 0))
            text_rect = texto.get_rect(center=rect.center)
            surface.blit(texto, text_rect)

    def dibujar_filtros_pedidos(self, surface):
        """
        Dibuja los botones de filtro para los pedidos en la superficie proporcionada.

        :param surface: Superficie de Pygame donde se dibujarán los botones de filtro.
        """
        for i, rect in enumerate(self.botones_filtro_pedidos):
            color = (180, 180, 255) if self.pedidos_filtro == self.filtros_pedidos[i] else (220, 220, 220)
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto = self.fuente_boton.render(self.filtros_pedidos[i], True, (0, 0, 0))
            text_rect = texto.get_rect(center=rect.center)
            surface.blit(texto, text_rect)

    def dibujar_inventario_con_scroll(self, surface):
        """
        Dibuja el reporte de inventario con scroll en la superficie proporcionada.
        """
        # Si no hay datos, cargarlos
        if not self.inventario_datos:
            self.cargar_inventario()

        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()

        # Ajustar Y para dejar espacio a los filtros
        graf_y += 40
        graf_h -= 40

        # Fondo principal
        pygame.draw.rect(surface, (255, 255, 255), (graf_x, graf_y, graf_w, graf_h), border_radius=12)
        pygame.draw.rect(surface, (200, 200, 200), (graf_x, graf_y, graf_w, graf_h), 2, border_radius=12)

        # Si no hay inventario
        if not self.inventario_datos:
            font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto))
            msg = font.render(f"No hay datos de inventario con el filtro actual.", True, (180, 0, 0))
            surface.blit(msg, (graf_x + graf_w//4, graf_y + graf_h // 2))
            return

        # Título de la sección
        titulo_seccion = self.fuente_titulo.render(f"Inventario - {self.inventario_filtro}", True, (0, 0, 0))
        titulo_rect = titulo_seccion.get_rect(center=(graf_x + graf_w // 2, graf_y + 30))
        surface.blit(titulo_seccion, titulo_rect)

        # Área de la tabla con scroll
        tabla_x = graf_x + 20
        tabla_y = graf_y + 80
        tabla_w = graf_w - 60  # Reservar espacio para scroll bar
        tabla_h = self.inventario_visible_rows * self.inventario_row_height + 40  # +40 para encabezados
        
        # Definir área de scroll para eventos
        self.inventario_scroll_area = pygame.Rect(tabla_x, tabla_y, tabla_w, tabla_h)

        # Crear superficie para el contenido con scroll
        content_surface = pygame.Surface((tabla_w, len(self.inventario_datos) * self.inventario_row_height + 40))
        content_surface.fill((255, 255, 255))

        # Dibujar encabezados en la superficie de contenido
        font_titulo = pygame.font.SysFont("Open Sans", int(0.04 * self.alto), bold=True)
        font_normal = pygame.font.SysFont("Open Sans", int(0.035 * self.alto))

        col_widths = [int(0.1 * tabla_w), int(0.35 * tabla_w), int(0.15 * tabla_w), int(0.15 * tabla_w), int(0.25 * tabla_w)]
        col_headers = ["ID", "Nombre", "Cantidad", "Unidad", "Tipo"]

        # Dibujar encabezados
        header_y = 0
        x_pos = 0
        for i, header in enumerate(col_headers):
            pygame.draw.rect(content_surface, (220, 220, 255), (x_pos, header_y, col_widths[i], 40))
            pygame.draw.rect(content_surface, (100, 100, 200), (x_pos, header_y, col_widths[i], 40), 1)
            texto = font_titulo.render(header, True, (0, 0, 0))
            rect = texto.get_rect(center=(x_pos + col_widths[i]//2, header_y + 20))
            content_surface.blit(texto, rect)
            x_pos += col_widths[i]

        # Dibujar filas de datos
        row_y = 40
        for i, item in enumerate(self.inventario_datos):
            # Color de fondo alternado
            if i % 2 == 0:
                pygame.draw.rect(content_surface, (240, 240, 255), (0, row_y, tabla_w, self.inventario_row_height))

            # Color rojo para stock bajo o agotado
            stock_color = (0, 0, 0)
            if item['Cantidad'] == 0:
                stock_color = (255, 0, 0)  # Rojo para agotado
            elif item['Cantidad'] <= 10:
                stock_color = (255, 150, 0)  # Naranja para bajo

            # Dibujar datos
            x_pos = 0
            cols = ["id", "Nombre", "Cantidad", "Unidad", "Tipo"]
            for j, col in enumerate(cols):
                valor = str(item.get(col, ""))
                color = stock_color if col == "Cantidad" else (0, 0, 0)
                texto = font_normal.render(valor, True, color)
                rect = texto.get_rect(midleft=(x_pos + 10, row_y + self.inventario_row_height // 2))
                content_surface.blit(texto, rect)
                x_pos += col_widths[j]

            row_y += self.inventario_row_height

        # Dibujar la parte visible del contenido
        visible_rect = pygame.Rect(0, self.inventario_scroll_y, tabla_w, tabla_h)
        surface.blit(content_surface, (tabla_x, tabla_y), visible_rect)

        # Dibujar barra de scroll si es necesaria
        if self.inventario_scroll_max > 0:
            self.dibujar_scroll_bar(surface, tabla_x + tabla_w, tabla_y, tabla_h, 
                                   self.inventario_scroll_y, self.inventario_scroll_max, "inventario")

        # Estadísticas de inventario
        items_agotados = sum(1 for item in self.inventario_datos if item['Cantidad'] == 0)
        items_bajos = sum(1 for item in self.inventario_datos if 0 < item['Cantidad'] <= 10)

        resumen_font = pygame.font.SysFont("Open Sans", int(0.03 * self.alto))
        resumen_texto = resumen_font.render(
            f"Total: {len(self.inventario_datos)} | Agotados: {items_agotados} | Stock bajo: {items_bajos}",
            True, (50, 50, 120)
        )
        rect = resumen_texto.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 40))
        surface.blit(resumen_texto, rect)

        # Pie de página
        pie_inventario = self.fuente_pie_pagina.render("Reporte de Inventario", True, (50, 50, 120))
        pie_rect = pie_inventario.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
        surface.blit(pie_inventario, pie_rect)

    def dibujar_pedidos_con_scroll(self, surface):
        """
        Dibuja el reporte de pedidos con scroll en la superficie proporcionada.
        """
        # Si no hay datos, cargarlos
        if not self.pedidos_datos:
            self.cargar_pedidos()

        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()

        # Ajustar Y para dejar espacio a los filtros
        graf_y += 40
        graf_h -= 40

        # Fondo principal
        pygame.draw.rect(surface, (255, 255, 255), (graf_x, graf_y, graf_w, graf_h), border_radius=12)
        pygame.draw.rect(surface, (200, 200, 200), (graf_x, graf_y, graf_w, graf_h), 2, border_radius=12)

        # Si no hay pedidos
        if not self.pedidos_datos:
            font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto))
            msg = font.render(f"No hay datos de pedidos con el filtro actual.", True, (180, 0, 0))
            surface.blit(msg, (graf_x + graf_w//4, graf_y + graf_h // 2))
            return

        # Título de la sección
        titulo_seccion = self.fuente_titulo.render(f"Pedidos - {self.pedidos_filtro}", True, (0, 0, 0))
        titulo_rect = titulo_seccion.get_rect(center=(graf_x + graf_w // 2, graf_y + 30))
        surface.blit(titulo_seccion, titulo_rect)

        # Área de la tabla con scroll
        tabla_x = graf_x + 20
        tabla_y = graf_y + 80
        tabla_w = graf_w - 60  # Reservar espacio para scroll bar
        tabla_h = self.pedidos_visible_rows * self.pedidos_row_height + 40  # +40 para encabezados
        
        # Definir área de scroll para eventos
        self.pedidos_scroll_area = pygame.Rect(tabla_x, tabla_y, tabla_w, tabla_h)

        # Crear superficie para el contenido con scroll
        content_surface = pygame.Surface((tabla_w, len(self.pedidos_datos) * self.pedidos_row_height + 40))
        content_surface.fill((255, 255, 255))

        # Dibujar encabezados en la superficie de contenido
        font_titulo = pygame.font.SysFont("Open Sans", int(0.036 * self.alto), bold=True)
        font_normal = pygame.font.SysFont("Open Sans", int(0.03 * self.alto))

        col_widths = [
            int(0.07 * tabla_w),  # ID
            int(0.2 * tabla_w),   # Cliente
            int(0.13 * tabla_w),  # Fecha Pedido
            int(0.13 * tabla_w),  # Fecha Entrega
            int(0.12 * tabla_w),  # Estado
            int(0.13 * tabla_w),  # Total
            int(0.12 * tabla_w),  # Días Proceso
        ]
        col_headers = ["ID", "Cliente", "Fecha Pedido", "Fecha Entrega", "Estado", "Total", "Días Proceso"]

        # Dibujar encabezados
        header_y = 0
        x_pos = 0
        for i, header in enumerate(col_headers):
            pygame.draw.rect(content_surface, (220, 220, 255), (x_pos, header_y, col_widths[i], 40))
            pygame.draw.rect(content_surface, (100, 100, 200), (x_pos, header_y, col_widths[i], 40), 1)
            texto = font_titulo.render(header, True, (0, 0, 0))
            rect = texto.get_rect(center=(x_pos + col_widths[i]//2, header_y + 20))
            content_surface.blit(texto, rect)
            x_pos += col_widths[i]

        # Dibujar filas de datos
        row_y = 40
        for i, pedido in enumerate(self.pedidos_datos):
            # Color de fondo alternado
            if i % 2 == 0:
                pygame.draw.rect(content_surface, (240, 240, 255), (0, row_y, tabla_w, self.pedidos_row_height))

            # Color basado en estado
            estado_color = (0, 0, 0)
            if pedido['Estado'] == 'Pendiente':
                estado_color = (255, 150, 0)  # Naranja para pendiente
            elif pedido['Estado'] == 'En proceso':
                estado_color = (0, 150, 255)  # Azul para en proceso
            elif pedido['Estado'] == 'Listo':
                estado_color = (0, 150, 0)    # Verde para listo
            elif pedido['Estado'] == 'Entregado':
                estado_color = (100, 100, 100)  # Gris para entregado

            # Formatear fechas
            fecha_pedido = str(pedido['Fecha_pedido'])
            fecha_entrega = str(pedido['Fecha_entrega'])
            if len(fecha_pedido) > 10:
                fecha_pedido = fecha_pedido[:10]
            if len(fecha_entrega) > 10:
                fecha_entrega = fecha_entrega[:10]

            # Dibujar datos
            x_pos = 0
            cols = ["id", "cliente", "Fecha_pedido", "Fecha_entrega", "Estado", "Total", "dias_proceso"]
            for j, col in enumerate(cols):
                if col == "Fecha_pedido":
                    valor = fecha_pedido
                elif col == "Fecha_entrega":
                    valor = fecha_entrega
                elif col == "Total":
                    valor = f"${float(pedido.get(col, 0)):.2f}"
                else:
                    valor = str(pedido.get(col, ""))

                color = estado_color if col == "Estado" else (0, 0, 0)
                texto = font_normal.render(valor, True, color)
                rect = texto.get_rect(midleft=(x_pos + 10, row_y + self.pedidos_row_height // 2))
                content_surface.blit(texto, rect)
                x_pos += col_widths[j]

            row_y += self.pedidos_row_height

        # Dibujar la parte visible del contenido
        visible_rect = pygame.Rect(0, self.pedidos_scroll_y, tabla_w, tabla_h)
        surface.blit(content_surface, (tabla_x, tabla_y), visible_rect)

        # Dibujar barra de scroll si es necesaria
        if self.pedidos_scroll_max > 0:
            self.dibujar_scroll_bar(surface, tabla_x + tabla_w, tabla_y, tabla_h,
                                   self.pedidos_scroll_y, self.pedidos_scroll_max, "pedidos")

        # Estadísticas de pedidos
        pedidos_pendientes = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Pendiente' or p['Estado'] == 'En proceso')
        pedidos_listos = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Listo')
        pedidos_entregados = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Entregado')

        resumen_font = pygame.font.SysFont("Open Sans", int(0.03 * self.alto))
        resumen_texto = resumen_font.render(
            f"Total: {len(self.pedidos_datos)} | Pendientes: {pedidos_pendientes} | Listos: {pedidos_listos} | Entregados: {pedidos_entregados}",
            True, (50, 50, 120)
        )
        rect = resumen_texto.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 40))
        surface.blit(resumen_texto, rect)

        # Pie de página
        pie_pedidos = self.fuente_pie_pagina.render("Reporte de Pedidos", True, (50, 50, 120))
        pie_rect = pie_pedidos.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
        surface.blit(pie_pedidos, pie_rect)

    def dibujar_scroll_bar(self, surface, x, y, height, scroll_y, scroll_max, tipo):
        """
        Dibuja una barra de scroll vertical.
        
        :param surface: Superficie donde dibujar
        :param x: Posición X de la barra
        :param y: Posición Y de la barra
        :param height: Altura total de la barra
        :param scroll_y: Posición actual del scroll
        :param scroll_max: Máximo scroll posible
        :param tipo: Tipo de scroll ("inventario" o "pedidos")
        """
        # Fondo de la barra de scroll
        scroll_rect = pygame.Rect(x, y, self.scroll_bar_width, height)
        pygame.draw.rect(surface, (230, 230, 230), scroll_rect)
        pygame.draw.rect(surface, (180, 180, 180), scroll_rect, 1)

        # Calcular posición y tamaño del handle
        if scroll_max > 0:
            handle_ratio = height / (scroll_max + height)
            handle_height = max(self.scroll_handle_height, int(height * handle_ratio))
            
            # Posición del handle basada en el scroll actual
            handle_y_ratio = scroll_y / scroll_max if scroll_max > 0 else 0
            handle_y = y + int((height - handle_height) * handle_y_ratio)
            
            # Dibujar handle
            handle_rect = pygame.Rect(x + 2, handle_y, self.scroll_bar_width - 4, handle_height)
            pygame.draw.rect(surface, (150, 150, 150), handle_rect, border_radius=5)
            pygame.draw.rect(surface, (100, 100, 100), handle_rect, 1, border_radius=5)
            
            # Guardar rect del handle para detectar clics
            if tipo == "inventario":
                self.inventario_scroll_handle = handle_rect
            elif tipo == "pedidos":
                self.pedidos_scroll_handle = handle_rect

    def _get_grafica_area(self):
        """
        Calcula la posición y tamaño de la gráfica para que quede debajo de los botones y centrada.

        :return: Tupla con las coordenadas y dimensiones de la gráfica (graf_x, graf_y, graf_w, graf_h).
        """
        boton_y = self.y + int(0.11 * self.alto)
        boton_h = int(0.06 * self.alto)
        margen = int(0.04 * self.alto)
        graf_y = boton_y + boton_h + margen
        graf_w = int(0.85 * self.ancho)
        graf_x = self.x + (self.ancho - graf_w) // 2
        graf_h = self.alto - (graf_y - self.y) - int(0.05 * self.alto)
        return graf_x, graf_y, graf_w, graf_h

    def dibujar_grafica_barras(self, surface):
        """
        Dibuja una gráfica de barras para las ventas por día en la superficie proporcionada.

        :param surface: Superficie de Pygame donde se dibujará la gráfica de barras.
        """
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        margen_izq = int(0.06 * graf_w)
        margen_inf = int(0.08 * graf_h)

        pygame.draw.rect(surface, (255, 255, 255), (graf_x, graf_y, graf_w, graf_h), border_radius=12)
        pygame.draw.rect(surface, (200, 200, 200), (graf_x, graf_y, graf_w, graf_h), 2, border_radius=12)

        eje_color = (80, 80, 80)
        pygame.draw.line(surface, eje_color, (graf_x + margen_izq, graf_y + graf_h - margen_inf), (graf_x + graf_w - 20, graf_y + graf_h - margen_inf), 3)
        pygame.draw.line(surface, eje_color, (graf_x + margen_izq, graf_y + 30), (graf_x + margen_izq, graf_y + graf_h - margen_inf), 3)

        if not self.ventas_por_dia:
            font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto))
            msg = font.render("No hay datos de ventas.", True, (180, 0, 0))
            surface.blit(msg, (graf_x + 200, graf_y + graf_h // 2))
            return

        num_barras = len(self.ventas_por_dia)
        ancho_barra = max(30, (graf_w - margen_izq - 40) // max(num_barras, 1) - 10)
        escala = (graf_h - margen_inf - 40) / self.max_ventas if self.max_ventas > 0 else 1

        fuente_eje = pygame.font.SysFont("Open Sans", int(0.025 * self.alto))
        for i, (dia, total) in enumerate(self.ventas_por_dia):
            x = graf_x + margen_izq + i * (ancho_barra + 10)
            y = graf_y + graf_h - margen_inf - int(total * escala)
            h = int(total * escala)
            pygame.draw.rect(surface, (100, 180, 255), (x, y, ancho_barra, h))
            dia_str = str(dia)[5:]
            lbl = fuente_eje.render(dia_str, True, (0, 0, 0))
            lbl_rect = lbl.get_rect(center=(x + ancho_barra // 2, graf_y + graf_h - margen_inf + 18))
            surface.blit(lbl, lbl_rect)
            val_lbl = fuente_eje.render(f"${total:.2f}", True, (0, 80, 0))
            val_rect = val_lbl.get_rect(center=(x + ancho_barra // 2, y - 15))
            surface.blit(val_lbl, val_rect)

        max_lbl = fuente_eje.render(f"${self.max_ventas:.2f}", True, (0, 0, 0))
        surface.blit(max_lbl, (graf_x + 10, graf_y + 20))

        # Agregar pie de página
        pie_ventas = self.fuente_pie_pagina.render("Ventas por día", True, (50, 50, 120))
        pie_rect = pie_ventas.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
        surface.blit(pie_ventas, pie_rect)

    def dibujar_grafica_pastel_productos(self, surface):
        """
        Dibuja una gráfica de pastel para los productos más vendidos en la superficie proporcionada.

        :param surface: Superficie de Pygame donde se dibujará la gráfica de pastel.
        """
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        if not self.productos_mas_vendidos:
            self.cargar_productos_mas_vendidos()

        centro_x = graf_x + int(0.28 * graf_w)
        centro_y = graf_y + int(0.5 * graf_h)
        radio = int(0.32 * graf_h)
        colores = [
            (255, 99, 132), (54, 162, 235), (255, 206, 86),
            (75, 192, 192), (153, 102, 255), (255, 159, 64),
            (100, 200, 100), (200, 100, 100)
        ]

        total = self.total_unidades_vendidas
        if total == 0:
            font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto))
            msg = font.render("No hay ventas registradas.", True, (180, 0, 0))
            surface.blit(msg, (centro_x - 100, centro_y))
            return

        angulo_inicio = 0
        for i, (nombre, unidades) in enumerate(self.productos_mas_vendidos):
            porcentaje = unidades / total
            angulo_fin = angulo_inicio + porcentaje * 360
            self.dibujar_porcion_pastel(surface, centro_x, centro_y, radio, angulo_inicio, angulo_fin, colores[i % len(colores)])
            angulo_inicio = angulo_fin

        pygame.draw.circle(surface, (80, 80, 80), (centro_x, centro_y), radio, 2)

        leyenda_x = graf_x + int(0.60 * graf_w)
        leyenda_y = graf_y + int(0.12 * graf_h)
        fuente_leyenda = pygame.font.SysFont("Open Sans", int(0.031 * self.alto))
        fuente_detalle = pygame.font.SysFont("Open Sans", int(0.034 * self.alto), bold=True)
        surface.blit(fuente_detalle.render("Detalle de productos", True, (0, 0, 0)), (leyenda_x, leyenda_y - 30))

        for i, (nombre, unidades) in enumerate(self.productos_mas_vendidos):
            color = colores[i % len(colores)]
            pygame.draw.rect(surface, color, (leyenda_x, leyenda_y + i * 38, 28, 28))
            porcentaje = unidades / total * 100
            texto = f"{nombre}: {unidades} ({porcentaje:.1f}%)"
            lbl = fuente_leyenda.render(texto, True, (0, 0, 0))
            surface.blit(lbl, (leyenda_x + 38, leyenda_y + i * 38 + 4))

        # Agregar pie de página
        pie_productos = self.fuente_pie_pagina.render("Productos más vendidos", True, (50, 50, 120))
        pie_rect = pie_productos.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
        surface.blit(pie_productos, pie_rect)

    def dibujar_porcion_pastel(self, surface, cx, cy, r, ang_ini, ang_fin, color):
        """
        Dibuja una porción de pastel en la superficie proporcionada.

        :param surface: Superficie de Pygame donde se dibujará la porción de pastel.
        :param cx: Coordenada x del centro del pastel.
        :param cy: Coordenada y del centro del pastel.
        :param r: Radio del pastel.
        :param ang_ini: Ángulo inicial de la porción.
        :param ang_fin: Ángulo final de la porción.
        :param color: Color de la porción.
        """
        ang_ini_rad = math.radians(ang_ini)
        ang_fin_rad = math.radians(ang_fin)
        num_puntos = max(2, int((ang_fin - ang_ini) / 2))
        puntos = [(cx, cy)]
        for i in range(num_puntos + 1):
            ang = ang_ini_rad + (ang_fin_rad - ang_ini_rad) * i / num_puntos
            x = cx + r * math.cos(ang)
            y = cy + r * math.sin(ang)
            puntos.append((x, y))
        pygame.draw.polygon(surface, color, puntos)

    def dibujar_grafica_lineas_horarios(self, surface):
        """
        Dibuja una gráfica de líneas para las ventas por hora en la superficie proporcionada.

        :param surface: Superficie de Pygame donde se dibujará la gráfica de líneas.
        """
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        margen_izq = int(0.06 * graf_w)
        margen_inf = int(0.08 * graf_h)

        pygame.draw.rect(surface, (255, 255, 255), (graf_x, graf_y, graf_w, graf_h), border_radius=12)
        pygame.draw.rect(surface, (200, 200, 200), (graf_x, graf_y, graf_w, graf_h), 2, border_radius=12)

        eje_color = (80, 80, 80)
        pygame.draw.line(surface, eje_color, (graf_x + margen_izq, graf_y + graf_h - margen_inf), (graf_x + graf_w - 20, graf_y + graf_h - margen_inf), 3)
        pygame.draw.line(surface, eje_color, (graf_x + margen_izq, graf_y + 30), (graf_x + margen_izq, graf_y + graf_h - margen_inf), 3)

        if not hasattr(self, 'ventas_por_hora') or not any(self.ventas_por_hora):
            font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto))
            msg = font.render("No hay datos de ventas por hora.", True, (180, 0, 0))
            surface.blit(msg, (graf_x + 200, graf_y + graf_h // 2))
            return

        escala_x = (graf_w - margen_izq - 40) / 23
        escala_y = (graf_h - margen_inf - 40) / self.max_ventas_hora if self.max_ventas_hora > 0 else 1

        puntos = []
        for hora in range(24):
            x = graf_x + margen_izq + hora * escala_x
            y = graf_y + graf_h - margen_inf - self.ventas_por_hora[hora] * escala_y
            puntos.append((x, y))

        if len(puntos) > 1:
            pygame.draw.lines(surface, (255, 100, 100), False, puntos, 3)

        for hora, (x, y) in enumerate(puntos):
            pygame.draw.circle(surface, (0, 0, 255), (int(x), int(y)), 7)
            if hora % 2 == 0:
                fuente_eje = pygame.font.SysFont("Open Sans", int(0.025 * self.alto))
                lbl = fuente_eje.render(str(hora), True, (0, 0, 0))
                lbl_rect = lbl.get_rect(center=(x, graf_y + graf_h - margen_inf + 18))
                surface.blit(lbl, lbl_rect)
            if self.ventas_por_hora[hora] > 0:
                fuente_val = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
                val_lbl = fuente_val.render(str(self.ventas_por_hora[hora]), True, (0, 80, 0))
                surface.blit(val_lbl, (x - 10, y - 25))

        fuente_eje = pygame.font.SysFont("Open Sans", int(0.025 * self.alto))
        max_lbl = fuente_eje.render(f"{self.max_ventas_hora}", True, (0, 0, 0))
        surface.blit(max_lbl, (graf_x + 10, graf_y + 20))

        # Agregar pie de página
        pie_horarios = self.fuente_pie_pagina.render("Hora de mayor venta", True, (50, 50, 120))
        pie_rect = pie_horarios.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
        surface.blit(pie_horarios, pie_rect)

    def dibujar_corte_caja(self, surface):
        """
        Dibuja el informe de corte de caja en la superficie proporcionada.

        :param surface: Superficie de Pygame donde se dibujará el informe de corte de caja.
        """
        # Si no hay datos, cargarlos
        if not self.corte_caja_datos:
            self.cargar_corte_caja(self.fecha_seleccionada)

        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()

        # Ajustar área para dejar espacio al selector de fecha
        contenido_y = graf_y + int(0.12 * graf_h)  # Dejar espacio para el selector
        contenido_h = graf_h - int(0.12 * graf_h)

        # Fondo principal
        fondo_rect = pygame.Rect(graf_x, contenido_y, graf_w, contenido_h)
        pygame.draw.rect(surface, (255, 255, 255), fondo_rect, border_radius=12)
        pygame.draw.rect(surface, (200, 200, 200), fondo_rect, 2, border_radius=12)

        # Si no hay ventas
        if not self.corte_caja_datos or not self.corte_caja_datos['ventas'] or float(self.corte_caja_datos['ventas']['total_ventas'] or 0) == 0:
            font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto))
            msg = font.render(f"No hay datos de ventas para el día {self.fecha_seleccionada}.", True, (180, 0, 0))
            msg_rect = msg.get_rect(center=(graf_x + graf_w//2, contenido_y + contenido_h // 2))
            surface.blit(msg, msg_rect)

            # Pie de página
            pie_corte = self.fuente_pie_pagina.render("Corte de Caja", True, (50, 50, 120))
            pie_rect = pie_corte.get_rect(center=(graf_x + graf_w // 2, contenido_y + contenido_h - 15))
            surface.blit(pie_corte, pie_rect)
            return

        # Título de la sección
        try:
            fecha_formateada = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            fecha_formateada = self.fecha_seleccionada
            
        titulo_seccion = self.fuente_titulo.render(f"Corte de Caja - {fecha_formateada}", True, (0, 0, 0))
        titulo_rect = titulo_seccion.get_rect(center=(graf_x + graf_w // 2, contenido_y + 30))
        surface.blit(titulo_seccion, titulo_rect)

        # División de pantalla: izquierda resumen, derecha gráfico
        mitad_ancho = graf_w // 2

        # Resumen de ventas - Lado izquierdo
        y_pos = contenido_y + 80
        font_titulo = pygame.font.SysFont("Open Sans", int(0.04 * self.alto), bold=True)
        font_normal = pygame.font.SysFont("Open Sans", int(0.035 * self.alto))

        # Resumen general
        texto = font_titulo.render("Resumen General:", True, (0, 0, 100))
        surface.blit(texto, (graf_x + 40, y_pos))
        y_pos += 40

        # Total de ventas y número de ventas
        texto_ventas = font_normal.render(
            f"Cantidad de Ventas: {self.corte_caja_datos['ventas']['num_ventas']}",
            True, (0, 0, 0)
        )
        surface.blit(texto_ventas, (graf_x + 40, y_pos))
        y_pos += 40

        texto_total = font_normal.render(
            f"Total de Ventas: ${float(self.corte_caja_datos['ventas']['total_ventas'] or 0):.2f}",
            True, (0, 0, 0)
        )
        surface.blit(texto_total, (graf_x + 40, y_pos))
        y_pos += 60

        # Ventas por estado
        if 'estados' in self.corte_caja_datos and self.corte_caja_datos['estados']:
            texto = font_titulo.render("Ventas por Estado:", True, (0, 0, 100))
            surface.blit(texto, (graf_x + 40, y_pos))
            y_pos += 40

            for estado in self.corte_caja_datos['estados']:
                texto = font_normal.render(
                    f"{estado['Estado']}: ${float(estado['total']):.2f}",
                    True, (0, 0, 0)
                )
                surface.blit(texto, (graf_x + 40, y_pos))
                y_pos += 35

        # Lado derecho - Gráfico de estados
        if self.metodos_pago:
            # Título
            titulo_estados = font_titulo.render("Ventas por Estado", True, (0, 0, 100))
            titulo_rect = titulo_estados.get_rect(center=(graf_x + mitad_ancho + mitad_ancho // 2, contenido_y + 80))
            surface.blit(titulo_estados, titulo_rect)

            # Gráfico pastel para estados
            centro_x = graf_x + mitad_ancho + mitad_ancho // 2
            centro_y = contenido_y + 180
            radio = 80  # Reducido un poco para que quepa mejor

            total_estados = sum([monto for _, monto in self.metodos_pago])

            colores = [(54, 162, 235), (255, 99, 132), (255, 206, 86),
                    (75, 192, 192), (153, 102, 255), (255, 159, 64)]

            # Dibujar pastel
            angulo_inicio = 0
            for i, (estado, monto) in enumerate(self.metodos_pago):
                porcentaje = monto / total_estados
                angulo_fin = angulo_inicio + porcentaje * 360
                self.dibujar_porcion_pastel(surface, centro_x, centro_y, radio,
                                        angulo_inicio, angulo_fin, colores[i % len(colores)])
                angulo_inicio = angulo_fin

            # Círculo central
            pygame.draw.circle(surface, (80, 80, 80), (centro_x, centro_y), radio, 2)

            # Leyenda
            leyenda_y = centro_y + radio + 20
            for i, (estado, monto) in enumerate(self.metodos_pago):
                color = colores[i % len(colores)]
                pygame.draw.rect(surface, color, (centro_x - 100, leyenda_y + i * 25, 15, 15))
                porcentaje = monto / total_estados * 100
                texto = f"{estado}: ${monto:.2f} ({porcentaje:.1f}%)"
                lbl = font_normal.render(texto, True, (0, 0, 0))
                surface.blit(lbl, (centro_x - 80, leyenda_y + i * 25))

        # Productos más vendidos del día
        if self.corte_caja_datos['productos']:
            titulo_productos = font_titulo.render("Productos más vendidos del día", True, (0, 0, 100))
            y_productos = contenido_y + contenido_h - 180
            titulo_rect = titulo_productos.get_rect(center=(graf_x + graf_w // 2, y_productos))
            surface.blit(titulo_productos, titulo_rect)

            # Tabla simple de productos
            y_pos = y_productos + 40
            x_nombre = graf_x + graf_w // 4
            x_cantidad = x_nombre + graf_w // 4
            x_total = x_cantidad + graf_w // 4

            # Encabezados
            texto_nombre = font_normal.render("Producto", True, (0, 0, 0))
            texto_cantidad = font_normal.render("Cantidad", True, (0, 0, 0))
            texto_total = font_normal.render("Total", True, (0, 0, 0))

            surface.blit(texto_nombre, (x_nombre, y_pos))
            surface.blit(texto_cantidad, (x_cantidad, y_pos))
            surface.blit(texto_total, (x_total, y_pos))

            # Productos (mostrar solo los primeros 3)
            y_pos += 30
            for i, producto in enumerate(self.corte_caja_datos['productos'][:3]):
                texto_nombre = font_normal.render(producto['Nombre_prod'], True, (0, 0, 0))
                texto_cantidad = font_normal.render(str(producto['cantidad']), True, (0, 0, 0))
                texto_total = font_normal.render(f"${float(producto['total']):.2f}", True, (0, 0, 0))

                surface.blit(texto_nombre, (x_nombre, y_pos + i * 25))
                surface.blit(texto_cantidad, (x_cantidad, y_pos + i * 25))
                surface.blit(texto_total, (x_total, y_pos + i * 25))

        # Pie de página
        pie_corte = self.fuente_pie_pagina.render("Corte de Caja", True, (50, 50, 120))
        pie_rect = pie_corte.get_rect(center=(graf_x + graf_w // 2, contenido_y + contenido_h - 15))
        surface.blit(pie_corte, pie_rect)

    def handle_event(self, event):
        """
        Maneja los eventos de la interfaz, como clics en botones y scroll.
        VERSIÓN CORREGIDA para manejar mejor los eventos del selector de fecha.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Verificar clics en botones de opciones PRIMERO
            for i, rect in enumerate(self.boton_rects):
                if rect and rect.collidepoint(mouse_pos):
                    self.opcion_seleccionada = self.botones_opciones[i]
                    if self.opcion_seleccionada == "VENTAS":
                        self.cargar_ventas_por_dia()
                    elif self.opcion_seleccionada == "PRODUCTOS":
                        self.cargar_productos_mas_vendidos()
                    elif self.opcion_seleccionada == "HORARIOS":
                        self.cargar_ventas_por_hora()
                    elif self.opcion_seleccionada == "CORTE CAJA":
                        self.cargar_corte_caja(self.fecha_seleccionada)
                    elif self.opcion_seleccionada == "INVENTARIO":
                        self.cargar_inventario()
                    elif self.opcion_seleccionada == "PEDIDOS":
                        self.cargar_pedidos()
                    return

            # Verificar clic en botón PDF
            if self.boton_pdf_rect and self.boton_pdf_rect.collidepoint(mouse_pos):
                self.descargar_pdf()
                return

            # Verificar eventos específicos según la sección actual
            if self.opcion_seleccionada == "CORTE CAJA":
                # Manejar eventos del selector de fecha SOLO si estamos en corte de caja
                if self.selector_fecha_rect and self.selector_fecha_rect.collidepoint(mouse_pos):
                    self.selector_fecha_activo = not self.selector_fecha_activo
                    print(f"Selector de fecha {'activado' if self.selector_fecha_activo else 'desactivado'}")
                    return

                if self.boton_fecha_anterior and self.boton_fecha_anterior.collidepoint(mouse_pos):
                    # Cambiar a día anterior
                    try:
                        fecha_actual = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d')
                        dia_anterior = fecha_actual - datetime.timedelta(days=1)
                        self.fecha_seleccionada = dia_anterior.strftime('%Y-%m-%d')
                        print(f"Fecha cambiada a: {self.fecha_seleccionada}")
                        self.cargar_corte_caja(self.fecha_seleccionada)
                    except Exception as e:
                        print(f"Error al cambiar fecha anterior: {e}")
                    return

                if self.boton_fecha_siguiente and self.boton_fecha_siguiente.collidepoint(mouse_pos):
                    # Cambiar a día siguiente
                    try:
                        fecha_actual = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d')
                        dia_siguiente = fecha_actual + datetime.timedelta(days=1)
                        # No permitir seleccionar fechas futuras
                        if dia_siguiente.date() <= datetime.datetime.now().date():
                            self.fecha_seleccionada = dia_siguiente.strftime('%Y-%m-%d')
                            print(f"Fecha cambiada a: {self.fecha_seleccionada}")
                            self.cargar_corte_caja(self.fecha_seleccionada)
                        else:
                            print("No se puede seleccionar una fecha futura")
                    except Exception as e:
                        print(f"Error al cambiar fecha siguiente: {e}")
                    return

            elif self.opcion_seleccionada == "INVENTARIO":
                # Manejar eventos de inventario
                for i, rect in enumerate(self.botones_filtro_inventario):
                    if rect.collidepoint(mouse_pos):
                        self.inventario_filtro = self.filtros_inventario[i]
                        self.cargar_inventario()
                        return

                # Verificar clic en barra de scroll de inventario
                if hasattr(self, 'inventario_scroll_handle') and self.inventario_scroll_handle.collidepoint(mouse_pos):
                    self.dragging_scroll = True
                    self.drag_offset = mouse_pos[1] - self.inventario_scroll_handle.y
                    self.drag_type = "inventario"
                    return

            elif self.opcion_seleccionada == "PEDIDOS":
                # Manejar eventos de pedidos
                for i, rect in enumerate(self.botones_filtro_pedidos):
                    if rect.collidepoint(mouse_pos):
                        self.pedidos_filtro = self.filtros_pedidos[i]
                        self.cargar_pedidos()
                        return

                # Verificar clic en barra de scroll de pedidos
                if hasattr(self, 'pedidos_scroll_handle') and self.pedidos_scroll_handle.collidepoint(mouse_pos):
                    self.dragging_scroll = True
                    self.drag_offset = mouse_pos[1] - self.pedidos_scroll_handle.y
                    self.drag_type = "pedidos"
                    return

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_scroll:
                self.dragging_scroll = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.pdf_hover = self.boton_pdf_rect and self.boton_pdf_rect.collidepoint(mouse_pos)

            # Manejar arrastre de scroll
            if self.dragging_scroll:
                if hasattr(self, 'drag_type') and self.drag_type == "inventario":
                    # Lógica de scroll para inventario (sin cambios)
                    graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
                    tabla_y = graf_y + 120
                    tabla_h = self.inventario_visible_rows * self.inventario_row_height + 40
                    
                    new_handle_y = mouse_pos[1] - self.drag_offset
                    handle_min_y = tabla_y
                    handle_max_y = tabla_y + tabla_h - self.scroll_handle_height
                    
                    new_handle_y = max(handle_min_y, min(new_handle_y, handle_max_y))
                    
                    if handle_max_y > handle_min_y:
                        ratio = (new_handle_y - handle_min_y) / (handle_max_y - handle_min_y)
                        self.inventario_scroll_y = int(ratio * self.inventario_scroll_max)
                        
                elif hasattr(self, 'drag_type') and self.drag_type == "pedidos":
                    # Lógica de scroll para pedidos (sin cambios)
                    graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
                    tabla_y = graf_y + 120
                    tabla_h = self.pedidos_visible_rows * self.pedidos_row_height + 40
                    
                    new_handle_y = mouse_pos[1] - self.drag_offset
                    handle_min_y = tabla_y
                    handle_max_y = tabla_y + tabla_h - self.scroll_handle_height
                    
                    new_handle_y = max(handle_min_y, min(new_handle_y, handle_max_y))
                    
                    if handle_max_y > handle_min_y:
                        ratio = (new_handle_y - handle_min_y) / (handle_max_y - handle_min_y)
                        self.pedidos_scroll_y = int(ratio * self.pedidos_scroll_max)

        elif event.type == pygame.MOUSEWHEEL:
            # Manejar scroll con rueda del mouse
            if self.opcion_seleccionada == "INVENTARIO" and self.inventario_scroll_area:
                mouse_pos = pygame.mouse.get_pos()
                if self.inventario_scroll_area.collidepoint(mouse_pos):
                    scroll_delta = -event.y * self.inventario_scroll_speed
                    self.inventario_scroll_y = max(0, min(self.inventario_scroll_y + scroll_delta, self.inventario_scroll_max))
                    return
                    
            elif self.opcion_seleccionada == "PEDIDOS" and self.pedidos_scroll_area:
                mouse_pos = pygame.mouse.get_pos()
                if self.pedidos_scroll_area.collidepoint(mouse_pos):
                    scroll_delta = -event.y * self.pedidos_scroll_speed
                    self.pedidos_scroll_y = max(0, min(self.pedidos_scroll_y + scroll_delta, self.pedidos_scroll_max))
                    return
            
    def on_agregar_click(self):
        """
        Maneja el evento de clic en el botón de agregar.
        """
        print(f"Botón 'Agregar' presionado en opción: {self.opcion_seleccionada}")

    def descargar_pdf(self):
        """
        Descarga el informe actual como un archivo PDF.
        """
        # Renderiza la gráfica en una superficie temporal y la guarda como PNG
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        temp_surface = pygame.Surface((graf_w, graf_h))
        temp_surface.fill((255, 255, 255))

        if self.opcion_seleccionada == "VENTAS":
            self.cargar_ventas_por_dia()
            self.dibujar_grafica_barras(temp_surface)
            datos = self.ventas_por_dia
            encabezado = ["Día", "Total ($)"]
            nombre_pdf = "reporte_ventas.pdf"
            nombre_img = "grafica_ventas.png"
            titulo_pdf = "Ventas por día"
        elif self.opcion_seleccionada == "PRODUCTOS":
            self.cargar_productos_mas_vendidos()
            self.dibujar_grafica_pastel_productos(temp_surface)
            datos = self.productos_mas_vendidos
            encabezado = ["Producto", "Unidades"]
            nombre_pdf = "reporte_productos.pdf"
            nombre_img = "grafica_productos.png"
            titulo_pdf = "Productos más vendidos"
        elif self.opcion_seleccionada == "HORARIOS":
            self.cargar_ventas_por_hora()
            self.dibujar_grafica_lineas_horarios(temp_surface)
            datos = [(str(h), self.ventas_por_hora[h]) for h in range(24)]
            encabezado = ["Hora", "Unidades"]
            nombre_pdf = "reporte_horarios.pdf"
            nombre_img = "grafica_horarios.png"
            titulo_pdf = "Hora de mayor venta"
        elif self.opcion_seleccionada == "CORTE CAJA":
            if not self.corte_caja_datos:
                self.cargar_corte_caja(self.fecha_seleccionada)

            # Para corte de caja no necesitamos imagen de gráfica, generamos directamente el PDF
            fecha_format = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d').strftime('%d-%m-%Y')
            nombre_pdf = f"corte_caja_{fecha_format}.pdf"
            self.generar_pdf_corte_caja(nombre_pdf)
            print(f"PDF generado: {nombre_pdf}")
            return
        elif self.opcion_seleccionada == "INVENTARIO":
            if not self.inventario_datos:
                self.cargar_inventario()

            nombre_pdf = f"inventario_{self.inventario_filtro.lower()}.pdf"
            self.generar_pdf_inventario(nombre_pdf)
            print(f"PDF generado: {nombre_pdf}")
            return
        elif self.opcion_seleccionada == "PEDIDOS":
            if not self.pedidos_datos:
                self.cargar_pedidos()

            nombre_pdf = f"pedidos_{self.pedidos_filtro.lower()}.pdf"
            self.generar_pdf_pedidos(nombre_pdf)
            print(f"PDF generado: {nombre_pdf}")
            return
        else:
            return

        pygame.image.save(temp_surface, nombre_img)
        self.generar_pdf(nombre_pdf, nombre_img, encabezado, datos, titulo_pdf)
        os.remove(nombre_img)
        print(f"PDF generado: {nombre_pdf}")

    def generar_pdf(self, nombre_pdf, nombre_img, encabezado, datos, titulo_pdf):
        """
        Genera un PDF con los datos proporcionados.

        :param nombre_pdf: Nombre del archivo PDF a generar.
        :param nombre_img: Nombre de la imagen a incluir en el PDF.
        :param encabezado: Encabezado de la tabla de datos.
        :param datos: Datos a incluir en la tabla.
        :param titulo_pdf: Título del PDF.
        """
        c = canvas.Canvas(nombre_pdf, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, f"Reporte: {titulo_pdf}")
        # Imagen de la gráfica
        c.drawImage(ImageReader(nombre_img), 50, height - 400, width=500, height=300)
        # Tabla de datos
        c.setFont("Helvetica-Bold", 14)
        y = height - 420
        c.drawString(50, y, encabezado[0])
        c.drawString(250, y, encabezado[1])
        c.setFont("Helvetica", 12)
        y -= 20
        for fila in datos:
            c.drawString(50, y, str(fila[0]))
            c.drawString(250, y, str(fila[1]))
            y -= 18
            if y < 60:
                c.showPage()
                y = height - 60
        c.save()

    def generar_pdf_corte_caja(self, nombre_pdf):
        """
        Genera un PDF específico para el corte de caja.

        :param nombre_pdf: Nombre del archivo PDF a generar.
        """
        if not self.corte_caja_datos:
            return

        # Crear documento
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        titulo_style = styles['Title']

        # Título
        fecha_formateada = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d').strftime('%d/%m/%Y')
        elements.append(Paragraph(f"Corte de Caja - {fecha_formateada}", titulo_style))

        # Datos de resumen general
        elements.append(Paragraph("Resumen General:", styles['Heading2']))

        datos_resumen = [
            ["Concepto", "Valor"],
            ["Cantidad de Ventas", f"{self.corte_caja_datos['ventas']['num_ventas']}"],
            ["Total de Ventas", f"${float(self.corte_caja_datos['ventas']['total_ventas'] or 0):.2f}"]
        ]

        tabla_resumen = Table(datos_resumen, colWidths=[300, 200])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (1, -1), 1, colors.black)
        ]))
        elements.append(tabla_resumen)
        elements.append(Paragraph(" ", styles['Normal']))  # Espacio

        # Generar el PDF
        doc.build(elements)

    def generar_pdf_inventario(self, nombre_pdf):
        """
        Genera un PDF del reporte de inventario.

        :param nombre_pdf: Nombre del archivo PDF a generar.
        """
        if not self.inventario_datos:
            return

        # Crear documento
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        titulo_style = styles['Title']

        # Título
        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y')
        elements.append(Paragraph(f"Reporte de Inventario - {self.inventario_filtro}", titulo_style))
        elements.append(Paragraph(f"Fecha: {fecha_actual}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Resumen
        items_agotados = sum(1 for item in self.inventario_datos if item['stock_minimo'] == 0)
        items_bajos = sum(1 for item in self.inventario_datos if 0 < item['stock_minimo'] <= 10)

        elements.append(Paragraph("Resumen:", styles['Heading2']))
        resumen_datos = [
            ["Concepto", "Cantidad"],
            ["Total de Items", str(len(self.inventario_datos))],
            ["Items Agotados", str(items_agotados)],
            ["Items con Stock Bajo", str(items_bajos)]
        ]

        tabla_resumen = Table(resumen_datos, colWidths=[300, 200])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (1, -1), 1, colors.black)
        ]))
        elements.append(tabla_resumen)
        elements.append(Spacer(1, 20))

        # Tabla de inventario
        elements.append(Paragraph("Detalle de Inventario:", styles['Heading2']))

        # Encabezados de tabla
        datos_inventario = [["ID", "Nombre", "Stock", "Unidad", "Tipo"]]

        # Filas de datos
        for item in self.inventario_datos:
            datos_inventario.append([
                str(item['id']),
                item['Nombre'],
                str(item['stock_minimo']),
                item['Unidad'],
                item['Tipo']
            ])

        # Crear tabla
        tabla_inventario = Table(datos_inventario, colWidths=[40, 200, 60, 100, 100])
        tabla_inventario.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (4, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (4, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (4, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (4, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (4, -1), colors.beige),
            ('GRID', (0, 0), (4, -1), 1, colors.black)
        ]))

        elements.append(tabla_inventario)

        # Generar el PDF
        doc.build(elements)

    def generar_pdf_pedidos(self, nombre_pdf):
        """
        Genera un PDF del reporte de pedidos.

        :param nombre_pdf: Nombre del archivo PDF a generar.
        """
        if not self.pedidos_datos:
            return

        # Crear documento
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        titulo_style = styles['Title']

        # Títulos
        fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y')
        elements.append(Paragraph(f"Reporte de Pedidos - {self.pedidos_filtro}", titulo_style))
        elements.append(Paragraph(f"Fecha: {fecha_actual}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Resumen
        pedidos_pendientes = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Pendiente' or p['Estado'] == 'En proceso')
        pedidos_listos = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Listo')
        pedidos_entregados = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Entregado')

        elements.append(Paragraph("Resumen:", styles['Heading2']))
        resumen_datos = [
            ["Concepto", "Cantidad"],
            ["Total de Pedidos", str(len(self.pedidos_datos))],
            ["Pedidos Pendientes", str(pedidos_pendientes)],
            ["Pedidos Listos", str(pedidos_listos)],
            ["Pedidos Entregados", str(pedidos_entregados)]
        ]

        tabla_resumen = Table(resumen_datos, colWidths=[300, 200])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (1, -1), 1, colors.black)
        ]))
        elements.append(tabla_resumen)
        elements.append(Spacer(1, 20))

        # Tabla de pedidos
        elements.append(Paragraph("Detalle de Pedidos:", styles['Heading2']))

        # Encabezados de tabla
        datos_pedidos = [["ID", "Cliente", "Fecha Pedido", "Fecha Entrega", "Estado", "Total", "Días Proceso"]]

        # Filas de datos
        for pedido in self.pedidos_datos:
            # Formatear fechas
            fecha_pedido = str(pedido['Fecha_pedido'])
            fecha_entrega = str(pedido['Fecha_entrega'])
            if len(fecha_pedido) > 10:
                fecha_pedido = fecha_pedido[:10]
            if len(fecha_entrega) > 10:
                fecha_entrega = fecha_entrega[:10]

            # Formatear total
            total = f"${float(pedido.get('Total', 0)):.2f}"

            datos_pedidos.append([
                str(pedido['id']),
                pedido['cliente'],
                fecha_pedido,
                fecha_entrega,
                pedido['Estado'],
                total,
                str(pedido.get('dias_proceso', ''))
            ])

        # Crear tabla
        tabla_pedidos = Table(datos_pedidos, colWidths=[35, 100, 70, 70, 70, 70, 60])
        tabla_pedidos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (6, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (6, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (6, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (6, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (6, -1), colors.beige),
            ('GRID', (0, 0), (6, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (6, -1), 9)
        ]))

        elements.append(tabla_pedidos)

        # Generar el PDF
        doc.build(elements)