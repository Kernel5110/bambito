import pygame
from conexion import Conexion
import math
import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class reporte:
    def __init__(self, x, y, ancho, alto):
        """
        Inicializa la clase reporte con las dimensiones y posiciones proporcionadas.
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
            scale = min(self.ancho / 1555, self.alto / 710)
            return int(base_size * scale)

        # Inicialización de fuentes
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", int(self.alto * 0.08), bold=True)
        self.fuente_boton = pygame.font.SysFont("Open Sans", int(self.alto * 0.045), bold=True)
        self.fuente_boton_agregar = pygame.font.SysFont("Open Sans", int(self.alto * 0.045), bold=True)
        self.fuente_boton_pdf = pygame.font.SysFont("Open Sans", int(self.alto * 0.045), bold=True)
        self.fuente_pie_pagina = pygame.font.SysFont("Open Sans", fuente_relativa(28), bold=True)

        # Opciones disponibles en el informe
        self.botones_opciones = ["VENTAS", "PRODUCTOS", "HORARIOS", "CORTE CAJA", "INVENTARIO", "PEDIDOS"]
        self.opcion_seleccionada = self.botones_opciones[0]

        # Configuración de botones y rectángulos
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

        # Botón PDF
        self.boton_pdf_rect = pygame.Rect(
            self.x + int(0.013 * self.ancho) + len(self.botones_opciones) * (self.boton_width + int(0.01 * self.ancho)) + int(0.12 * self.ancho),
            self.y + int(0.11 * self.alto),
            int(0.12 * self.ancho),
            int(0.06 * self.alto)
        )
        self.color_boton_pdf = (100, 100, 200)
        self.color_boton_pdf_hover = (80, 80, 180)
        self.pdf_hover = False

        # Variables de datos
        self.ventas_por_dia = []
        self.max_ventas = 0
        self.productos_mas_vendidos = []
        self.total_unidades_vendidas = 0
        self.ventas_por_hora = [0] * 24
        self.max_ventas_hora = 0
        
        # Configuración del corte de caja
        self.fecha_corte = datetime.datetime.now().strftime('%Y-%m-%d')
        self.corte_caja_datos = {}
        self.metodos_pago = []
        self.fecha_seleccionada = self.fecha_corte
        
        # Selector de fecha
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

        # Configuración de inventario
        self.inventario_datos = []
        self.inventario_filtro = "TODOS"
        self.filtros_inventario = ["TODOS", "BAJO", "AGOTADO"]
        self.botones_filtro_inventario = []
        
        self.inventario_scroll_y = 0
        self.inventario_scroll_max = 0
        self.inventario_scroll_speed = 30
        self.inventario_visible_rows = 12
        self.inventario_row_height = 40
        self.inventario_scroll_area = None

        # Configuración de pedidos
        self.pedidos_datos = []
        self.pedidos_filtro = "TODOS"
        self.filtros_pedidos = ["TODOS", "PENDIENTES", "COMPLETADOS"]
        self.botones_filtro_pedidos = []
        
        self.pedidos_scroll_y = 0
        self.pedidos_scroll_max = 0
        self.pedidos_scroll_speed = 30
        self.pedidos_visible_rows = 10
        self.pedidos_row_height = 40
        self.pedidos_scroll_area = None

        # Configuración de scroll
        self.scroll_bar_width = 15
        self.scroll_handle_height = 50
        self.dragging_scroll = False
        self.drag_offset = 0

        # Crear botones de filtro
        for i, filtro in enumerate(self.filtros_inventario):
            self.botones_filtro_inventario.append(
                pygame.Rect(
                    self.x + int(0.2 * self.ancho) + i * int(0.11 * self.ancho),
                    self.y + int(0.18 * self.alto),
                    int(0.1 * self.ancho),
                    int(0.04 * self.alto)
                )
            )

        for i, filtro in enumerate(self.filtros_pedidos):
            self.botones_filtro_pedidos.append(
                pygame.Rect(
                    self.x + int(0.2 * self.ancho) + i * int(0.11 * self.ancho),
                    self.y + int(0.18 * self.alto),
                    int(0.1 * self.ancho),
                    int(0.04 * self.alto)
                )
            )

    # [Métodos de carga de datos permanecen igual...]
    def cargar_ventas_por_dia(self):
        """Carga los datos de ventas por día desde la base de datos."""
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
        """Carga los datos de los productos más vendidos desde la base de datos."""
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
        """Carga los datos de ventas por hora desde la base de datos."""
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

    def dibujar_grafica_barras_mejorada(self, surface):
        """Dibuja una gráfica de barras mejorada con gradientes y efectos visuales."""
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        margen_izq = int(0.08 * graf_w)
        margen_inf = int(0.12 * graf_h)
        margen_sup = int(0.08 * graf_h)

        # Fondo con gradiente suave
        pygame.draw.rect(surface, (248, 250, 252), (graf_x, graf_y, graf_w, graf_h), border_radius=15)
        pygame.draw.rect(surface, (200, 210, 220), (graf_x, graf_y, graf_w, graf_h), 3, border_radius=15)

        # Título de la gráfica
        titulo_font = pygame.font.SysFont("Arial Black", int(0.04 * self.alto))
        titulo = titulo_font.render("VENTAS POR DÍA", True, (50, 70, 120))
        titulo_rect = titulo.get_rect(center=(graf_x + graf_w//2, graf_y + margen_sup//2))
        surface.blit(titulo, titulo_rect)

        # Ejes más elegantes
        eje_color = (100, 120, 140)
        # Eje X
        pygame.draw.line(surface, eje_color, 
                        (graf_x + margen_izq, graf_y + graf_h - margen_inf), 
                        (graf_x + graf_w - 30, graf_y + graf_h - margen_inf), 4)
        # Eje Y
        pygame.draw.line(surface, eje_color, 
                        (graf_x + margen_izq, graf_y + margen_sup), 
                        (graf_x + margen_izq, graf_y + graf_h - margen_inf), 4)

        if not self.ventas_por_dia:
            font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto))
            msg = font.render("No hay datos de ventas disponibles", True, (180, 60, 60))
            msg_rect = msg.get_rect(center=(graf_x + graf_w//2, graf_y + graf_h//2))
            surface.blit(msg, msg_rect)
            return

        # Configuración de barras
        num_barras = len(self.ventas_por_dia)
        area_barras = graf_w - margen_izq - 50
        ancho_barra = max(25, (area_barras // max(num_barras, 1)) - 15)
        escala = (graf_h - margen_inf - margen_sup - 20) / self.max_ventas if self.max_ventas > 0 else 1

        # Líneas de cuadrícula horizontales
        for i in range(1, 6):
            y_grid = graf_y + margen_sup + (graf_h - margen_inf - margen_sup) * i / 5
            pygame.draw.line(surface, (220, 230, 240), 
                           (graf_x + margen_izq, int(y_grid)), 
                           (graf_x + graf_w - 30, int(y_grid)), 1)

        # Dibujar barras con gradiente
        for i, (dia, total) in enumerate(self.ventas_por_dia):
            x = graf_x + margen_izq + 20 + i * (ancho_barra + 15)
            altura_barra = int(total * escala)
            y = graf_y + graf_h - margen_inf - altura_barra
            
            # Crear efecto de gradiente para las barras
            for j in range(altura_barra):
                factor = j / max(altura_barra, 1)
                color_r = int(70 + factor * 120)  # De azul oscuro a azul claro
                color_g = int(130 + factor * 80)
                color_b = int(255 - factor * 50)
                color = (min(255, color_r), min(255, color_g), min(255, color_b))
                pygame.draw.rect(surface, color, (x, y + altura_barra - j - 1, ancho_barra, 1))
            
            # Borde de la barra
            pygame.draw.rect(surface, (50, 80, 150), (x, y, ancho_barra, altura_barra), 2, border_radius=5)
            
            # Etiqueta del día
            dia_str = str(dia)[5:] if len(str(dia)) > 5 else str(dia)
            fuente_eje = pygame.font.SysFont("Open Sans", int(0.025 * self.alto), bold=True)
            lbl_dia = fuente_eje.render(dia_str, True, (60, 60, 60))
            lbl_rect = lbl_dia.get_rect(center=(x + ancho_barra // 2, graf_y + graf_h - margen_inf + 20))
            surface.blit(lbl_dia, lbl_rect)
            
            # Valor sobre la barra
            if altura_barra > 20:  # Solo mostrar si hay espacio
                fuente_valor = pygame.font.SysFont("Open Sans", int(0.022 * self.alto), bold=True)
                val_text = f"${total:.0f}" if total >= 1000 else f"${total:.2f}"
                val_lbl = fuente_valor.render(val_text, True, (255, 255, 255))
                val_rect = val_lbl.get_rect(center=(x + ancho_barra // 2, y + altura_barra // 2))
                
                # Fondo semi-transparente para el texto
                bg_rect = pygame.Rect(val_rect.x - 5, val_rect.y - 2, val_rect.width + 10, val_rect.height + 4)
                pygame.draw.rect(surface, (0, 0, 0, 100), bg_rect, border_radius=3)
                surface.blit(val_lbl, val_rect)

        # Etiquetas del eje Y
        fuente_eje_y = pygame.font.SysFont("Open Sans", int(0.023 * self.alto))
        for i in range(6):
            valor = (self.max_ventas * i) / 5
            y_pos = graf_y + graf_h - margen_inf - (graf_h - margen_inf - margen_sup) * i / 5
            val_text = f"${valor:.0f}" if valor >= 100 else f"${valor:.1f}"
            lbl = fuente_eje_y.render(val_text, True, (80, 80, 80))
            surface.blit(lbl, (graf_x + 5, int(y_pos) - 8))

    def dibujar_grafica_pastel_mejorada(self, surface):
        """Dibuja una gráfica de pastel mejorada con efectos 3D y mejor diseño."""
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        
        if not self.productos_mas_vendidos:
            self.cargar_productos_mas_vendidos()

        # Fondo elegante
        pygame.draw.rect(surface, (248, 250, 252), (graf_x, graf_y, graf_w, graf_h), border_radius=15)
        pygame.draw.rect(surface, (200, 210, 220), (graf_x, graf_y, graf_w, graf_h), 3, border_radius=15)

        # Título
        titulo_font = pygame.font.SysFont("Arial Black", int(0.04 * self.alto))
        titulo = titulo_font.render("PRODUCTOS MÁS VENDIDOS", True, (50, 70, 120))
        titulo_rect = titulo.get_rect(center=(graf_x + graf_w//2, graf_y + 30))
        surface.blit(titulo, titulo_rect)

        centro_x = graf_x + int(0.3 * graf_w)
        centro_y = graf_y + int(0.55 * graf_h)
        radio = int(0.25 * graf_h)
        
        # Colores más atractivos
        colores = [
            (255, 107, 107), (54, 162, 235), (255, 206, 84),
            (75, 192, 192), (153, 102, 255), (255, 159, 64),
            (46, 204, 113), (231, 76, 60)
        ]

        total = self.total_unidades_vendidas
        if total == 0:
            font = pygame.font.SysFont("Open Sans", int(0.04 * self.alto))
            msg = font.render("No hay datos de productos vendidos", True, (180, 60, 60))
            msg_rect = msg.get_rect(center=(centro_x, centro_y))
            surface.blit(msg, msg_rect)
            return

        # Efecto 3D - sombra
        sombra_offset = 6
        angulo_inicio = 0
        for i, (nombre, unidades) in enumerate(self.productos_mas_vendidos):
            porcentaje = unidades / total
            angulo_fin = angulo_inicio + porcentaje * 360
            color_sombra = (100, 100, 100)
            self.dibujar_porcion_pastel(surface, centro_x + sombra_offset, centro_y + sombra_offset, 
                                      radio, angulo_inicio, angulo_fin, color_sombra)
            angulo_inicio = angulo_fin

        # Pastel principal
        angulo_inicio = 0
        for i, (nombre, unidades) in enumerate(self.productos_mas_vendidos):
            porcentaje = unidades / total
            angulo_fin = angulo_inicio + porcentaje * 360
            color = colores[i % len(colores)]
            self.dibujar_porcion_pastel(surface, centro_x, centro_y, radio, angulo_inicio, angulo_fin, color)
            angulo_inicio = angulo_fin

        # Borde del pastel
        pygame.draw.circle(surface, (80, 80, 80), (centro_x, centro_y), radio, 3)
        pygame.draw.circle(surface, (255, 255, 255), (centro_x, centro_y), int(radio * 0.3))
        pygame.draw.circle(surface, (180, 180, 180), (centro_x, centro_y), int(radio * 0.3), 2)

        # Leyenda mejorada
        leyenda_x = graf_x + int(0.62 * graf_w)
        leyenda_y = graf_y + int(0.15 * graf_h)
        
        # Título de la leyenda
        fuente_titulo_leyenda = pygame.font.SysFont("Arial", int(0.035 * self.alto), bold=True)
        titulo_leyenda = fuente_titulo_leyenda.render("Detalle por Producto", True, (50, 70, 120))
        surface.blit(titulo_leyenda, (leyenda_x, leyenda_y))
        
        leyenda_y += 35
        fuente_leyenda = pygame.font.SysFont("Open Sans", int(0.028 * self.alto))
        
        for i, (nombre, unidades) in enumerate(self.productos_mas_vendidos):
            color = colores[i % len(colores)]
            
            # Cuadro de color con borde
            color_rect = pygame.Rect(leyenda_x, leyenda_y + i * 32, 24, 24)
            pygame.draw.rect(surface, color, color_rect, border_radius=4)
            pygame.draw.rect(surface, (100, 100, 100), color_rect, 2, border_radius=4)
            
            # Texto de la leyenda
            porcentaje = unidades / total * 100
            nombre_corto = nombre[:15] + "..." if len(nombre) > 15 else nombre
            texto = f"{nombre_corto}"
            lbl_nombre = fuente_leyenda.render(texto, True, (60, 60, 60))
            surface.blit(lbl_nombre, (leyenda_x + 32, leyenda_y + i * 32))
            
            # Estadísticas
            stats_text = f"{unidades} und. ({porcentaje:.1f}%)"
            lbl_stats = pygame.font.SysFont("Open Sans", int(0.025 * self.alto)).render(stats_text, True, (100, 100, 100))
            surface.blit(lbl_stats, (leyenda_x + 32, leyenda_y + i * 32 + 15))

    def dibujar_grafica_lineas_mejorada(self, surface):
        """Dibuja una gráfica de líneas mejorada para ventas por hora."""
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        margen_izq = int(0.08 * graf_w)
        margen_inf = int(0.12 * graf_h)
        margen_sup = int(0.08 * graf_h)

        # Fondo elegante
        pygame.draw.rect(surface, (248, 250, 252), (graf_x, graf_y, graf_w, graf_h), border_radius=15)
        pygame.draw.rect(surface, (200, 210, 220), (graf_x, graf_y, graf_w, graf_h), 3, border_radius=15)

        # Título
        titulo_font = pygame.font.SysFont("Arial Black", int(0.04 * self.alto))
        titulo = titulo_font.render("VENTAS POR HORA DEL DÍA", True, (50, 70, 120))
        titulo_rect = titulo.get_rect(center=(graf_x + graf_w//2, graf_y + margen_sup//2))
        surface.blit(titulo, titulo_rect)

        # Ejes
        eje_color = (100, 120, 140)
        pygame.draw.line(surface, eje_color, 
                        (graf_x + margen_izq, graf_y + graf_h - margen_inf), 
                        (graf_x + graf_w - 30, graf_y + graf_h - margen_inf), 4)
        pygame.draw.line(surface, eje_color, 
                        (graf_x + margen_izq, graf_y + margen_sup), 
                        (graf_x + margen_izq, graf_y + graf_h - margen_inf), 4)

        if not hasattr(self, 'ventas_por_hora') or not any(self.ventas_por_hora):
            font = pygame.font.SysFont("Open Sans", int(0.04 * self.alto))
            msg = font.render("No hay datos de ventas por hora disponibles", True, (180, 60, 60))
            msg_rect = msg.get_rect(center=(graf_x + graf_w//2, graf_y + graf_h//2))
            surface.blit(msg, msg_rect)
            return

        # Cuadrícula
        area_grafica_w = graf_w - margen_izq - 40
        area_grafica_h = graf_h - margen_inf - margen_sup
        
        # Líneas horizontales
        for i in range(1, 6):
            y_grid = graf_y + margen_sup + area_grafica_h * i / 5
            pygame.draw.line(surface, (220, 230, 240), 
                           (graf_x + margen_izq, int(y_grid)), 
                           (graf_x + graf_w - 30, int(y_grid)), 1)

        # Líneas verticales cada 4 horas
        for i in range(0, 25, 4):
            x_grid = graf_x + margen_izq + (area_grafica_w * i) / 24
            pygame.draw.line(surface, (220, 230, 240), 
                           (int(x_grid), graf_y + margen_sup), 
                           (int(x_grid), graf_y + graf_h - margen_inf), 1)

        # Escalas
        escala_x = area_grafica_w / 23
        escala_y = area_grafica_h / self.max_ventas_hora if self.max_ventas_hora > 0 else 1

        # Puntos de la línea
        puntos = []
        for hora in range(24):
            x = graf_x + margen_izq + hora * escala_x
            y = graf_y + graf_h - margen_inf - self.ventas_por_hora[hora] * escala_y
            puntos.append((x, y))

        # Área bajo la curva (relleno)
        if len(puntos) > 1:
            puntos_relleno = puntos + [(graf_x + graf_w - 40, graf_y + graf_h - margen_inf), 
                                     (graf_x + margen_izq, graf_y + graf_h - margen_inf)]
            # Crear superficie temporal para el gradiente
            temp_surface = pygame.Surface((graf_w, graf_h), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surface, (100, 180, 255, 80), puntos_relleno)
            surface.blit(temp_surface, (graf_x, graf_y))

        # Línea principal
        if len(puntos) > 1:
            pygame.draw.lines(surface, (220, 50, 50), False, puntos, 4)

        # Puntos de datos
        for hora, (x, y) in enumerate(puntos):
            # Círculo de fondo
            pygame.draw.circle(surface, (255, 255, 255), (int(x), int(y)), 8)
            pygame.draw.circle(surface, (220, 50, 50), (int(x), int(y)), 6)
            pygame.draw.circle(surface, (150, 30, 30), (int(x), int(y)), 6, 2)
            
            # Etiquetas cada 2 horas
            if hora % 2 == 0:
                fuente_eje = pygame.font.SysFont("Open Sans", int(0.025 * self.alto))
                lbl = fuente_eje.render(f"{hora}:00", True, (80, 80, 80))
                lbl_rect = lbl.get_rect(center=(x, graf_y + graf_h - margen_inf + 25))
                surface.blit(lbl, lbl_rect)
            
            # Valores sobre puntos altos
            if self.ventas_por_hora[hora] > self.max_ventas_hora * 0.7:
                fuente_val = pygame.font.SysFont("Open Sans", int(0.022 * self.alto), bold=True)
                val_lbl = fuente_val.render(str(self.ventas_por_hora[hora]), True, (150, 30, 30))
                val_rect = val_lbl.get_rect(center=(x, y - 20))
                # Fondo para el texto
                bg_rect = pygame.Rect(val_rect.x - 3, val_rect.y - 1, val_rect.width + 6, val_rect.height + 2)
                pygame.draw.rect(surface, (255, 255, 255), bg_rect, border_radius=3)
                surface.blit(val_lbl, val_rect)

        # Etiquetas del eje Y
        fuente_eje_y = pygame.font.SysFont("Open Sans", int(0.023 * self.alto))
        for i in range(6):
            valor = int((self.max_ventas_hora * i) / 5)
            y_pos = graf_y + graf_h - margen_inf - area_grafica_h * i / 5
            lbl = fuente_eje_y.render(str(valor), True, (80, 80, 80))
            surface.blit(lbl, (graf_x + 5, int(y_pos) - 8))

    def _get_grafica_area(self):
        """Calcula la posición y tamaño de la gráfica."""
        boton_y = self.y + int(0.11 * self.alto)
        boton_h = int(0.06 * self.alto)
        margen = int(0.04 * self.alto)
        graf_y = boton_y + boton_h + margen
        graf_w = int(0.85 * self.ancho)
        graf_x = self.x + (self.ancho - graf_w) // 2
        graf_h = self.alto - (graf_y - self.y) - int(0.05 * self.alto)
        return graf_x, graf_y, graf_w, graf_h

    def dibujar_porcion_pastel(self, surface, cx, cy, r, ang_ini, ang_fin, color):
        """Dibuja una porción de pastel mejorada."""
        ang_ini_rad = math.radians(ang_ini)
        ang_fin_rad = math.radians(ang_fin)
        num_puntos = max(3, int((ang_fin - ang_ini) / 2))
        puntos = [(cx, cy)]
        for i in range(num_puntos + 1):
            ang = ang_ini_rad + (ang_fin_rad - ang_ini_rad) * i / num_puntos
            x = cx + r * math.cos(ang)
            y = cy + r * math.sin(ang)
            puntos.append((x, y))
        pygame.draw.polygon(surface, color, puntos)

    def dibujar_reporte(self, surface):
        """Dibuja el informe en la superficie proporcionada."""
        pygame.draw.rect(surface, self.FONDO, (self.x, self.y, self.ancho, self.alto))
        
        # Título
        titulo = self.fuente_titulo.render("Reportes", True, self.color_texto)
        surface.blit(titulo, (self.x + int(0.02 * self.ancho), self.y + int(0.02 * self.alto)))

        # Botones
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

        # Dibujar contenido según la opción seleccionada
        if self.opcion_seleccionada == "VENTAS":
            self.dibujar_grafica_barras_mejorada(surface)
        elif self.opcion_seleccionada == "PRODUCTOS":
            self.dibujar_grafica_pastel_mejorada(surface)
        elif self.opcion_seleccionada == "HORARIOS":
            self.dibujar_grafica_lineas_mejorada(surface)
        elif self.opcion_seleccionada == "CORTE CAJA":
            self.dibujar_selector_fecha(surface)
            self.dibujar_corte_caja(surface)
        elif self.opcion_seleccionada == "INVENTARIO":
            self.dibujar_filtros_inventario(surface)  
            self.dibujar_inventario_con_scroll(surface)
        elif self.opcion_seleccionada == "PEDIDOS":
            self.dibujar_filtros_pedidos(surface)
            self.dibujar_pedidos_con_scroll(surface)

    def descargar_pdf(self):
        """Descarga el informe actual como un archivo PDF mejorado."""
        try:
            # Crear directorio de reportes si no existe
            if not os.path.exists("reportes"):
                os.makedirs("reportes")

            if self.opcion_seleccionada == "VENTAS":
                self.cargar_ventas_por_dia()
                self.crear_pdf_ventas()
            elif self.opcion_seleccionada == "PRODUCTOS":
                self.cargar_productos_mas_vendidos()
                self.crear_pdf_productos()
            elif self.opcion_seleccionada == "HORARIOS":
                self.cargar_ventas_por_hora()
                self.crear_pdf_horarios()
            elif self.opcion_seleccionada == "CORTE CAJA":
                if not self.corte_caja_datos:
                    self.cargar_corte_caja(self.fecha_seleccionada)
                self.crear_pdf_corte_caja()
            elif self.opcion_seleccionada == "INVENTARIO":
                if not self.inventario_datos:
                    self.cargar_inventario()
                self.crear_pdf_inventario()
            elif self.opcion_seleccionada == "PEDIDOS":
                if not self.pedidos_datos:
                    self.cargar_pedidos()
                self.crear_pdf_pedidos()
                
        except Exception as e:
            print(f"Error al generar PDF: {e}")

    def crear_pdf_ventas(self):
        """Crea un PDF completo para el reporte de ventas."""
        # Generar imagen de la gráfica
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        superficie_ancha = max(graf_w, 1700)
        superficie_alta = max(graf_h, 800)
        temp_surface = pygame.Surface((superficie_ancha, superficie_alta))
        temp_surface.fill((255, 255, 255))
        self.dibujar_grafica_barras_mejorada(temp_surface)
        nombre_img = "temp_grafica_ventas.png"
        pygame.image.save(temp_surface, nombre_img)

        # Crear PDF
        fecha_actual = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')
        nombre_pdf = f"reportes/reporte_ventas_{fecha_actual}.pdf"
        
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter, 
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()

        # Estilo personalizado para títulos
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50')
        )

        # Estilo para subtítulos
        subtitulo_style = ParagraphStyle(
            'CustomSubTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#34495E')
        )

        # Encabezado
        elements.append(Paragraph("REPORTE DE VENTAS DIARIAS", titulo_style))
        elements.append(Paragraph(f"Fecha de generación: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Descripción
        descripcion = """
        <b>Descripción del Reporte:</b><br/>
        Este reporte muestra el análisis de las ventas diarias de la empresa, permitiendo identificar 
        tendencias, patrones de comportamiento y períodos de mayor actividad comercial. 
        Los datos se presentan de forma visual para facilitar la toma de decisiones estratégicas.
        """
        elements.append(Paragraph(descripcion, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Gráfica
        if os.path.exists(nombre_img):
            img = Image(nombre_img, width=10*inch, height=7*inch)
            elements.append(img)
            elements.append(Spacer(1, 20))

        # Análisis estadístico
        if self.ventas_por_dia:
            elements.append(Paragraph("Análisis Estadístico", subtitulo_style))
            
            total_ventas = sum([v for _, v in self.ventas_por_dia])
            promedio_ventas = total_ventas / len(self.ventas_por_dia)
            max_venta = max([v for _, v in self.ventas_por_dia])
            min_venta = min([v for _, v in self.ventas_por_dia])
            
            analisis_data = [
                ["Métrica", "Valor"],
                ["Total de Ventas", f"${total_ventas:,.2f}"],
                ["Promedio Diario", f"${promedio_ventas:,.2f}"],
                ["Venta Máxima", f"${max_venta:,.2f}"],
                ["Venta Mínima", f"${min_venta:,.2f}"],
                ["Días Analizados", str(len(self.ventas_por_dia))]
            ]

            tabla_analisis = Table(analisis_data, colWidths=[2.5*inch, 2*inch])
            tabla_analisis.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (1, -1), colors.HexColor('#ECF0F1')),
                ('GRID', (0, 0), (1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ]))
            elements.append(tabla_analisis)
            elements.append(Spacer(1, 20))

        # Tabla detallada
        if self.ventas_por_dia:
            elements.append(Paragraph("Detalle de Ventas por Día", subtitulo_style))
            
            datos_tabla = [["Fecha", "Ventas ($)", "% del Total"]]
            total_ventas = sum([v for _, v in self.ventas_por_dia])
            
            for dia, venta in self.ventas_por_dia:
                porcentaje = (venta / total_ventas) * 100 if total_ventas > 0 else 0
                fecha_formateada = dia.strftime('%d/%m/%Y') if hasattr(dia, 'strftime') else str(dia)
                datos_tabla.append([
                    fecha_formateada,
                    f"${venta:,.2f}",
                    f"{porcentaje:.1f}%"
                ])

            tabla_detalle = Table(datos_tabla, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            tabla_detalle.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#2ECC71')),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (2, 0), 10),
                ('BACKGROUND', (0, 1), (2, -1), colors.beige),
                ('GRID', (0, 0), (2, -1), 1, colors.black),
                ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (2, -1), 'MIDDLE'),
            ]))
            elements.append(tabla_detalle)

        # Recomendaciones
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Recomendaciones", subtitulo_style))
        recomendaciones = """
        • Analizar los días de mayor venta para implementar estrategias similares<br/>
        • Revisar los factores que influyen en los días de menor venta<br/>
        • Considerar promociones especiales en días de baja actividad<br/>
        • Mantener un inventario adecuado para los días de alta demanda
        """
        elements.append(Paragraph(recomendaciones, styles['Normal']))

        # Generar PDF
        doc.build(elements)
        
        # Limpiar archivo temporal
        if os.path.exists(nombre_img):
            os.remove(nombre_img)
            
        print(f"PDF de ventas generado: {nombre_pdf}")

    def crear_pdf_productos(self):
        """Crea un PDF completo para el reporte de productos."""
        # Generar imagen de la gráfica en superficie grande
        superficie_ancha = max(self.ancho, 1700)
        superficie_alta = max(self.alto, 800)
        temp_surface = pygame.Surface((superficie_ancha, superficie_alta))
        temp_surface.fill((255, 255, 255))

        self.dibujar_grafica_pastel_mejorada(temp_surface)
        nombre_img = "temp_grafica_productos.png"
        pygame.image.save(temp_surface, nombre_img)

        # Crear PDF
        fecha_actual = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')
        nombre_pdf = f"reportes/reporte_productos_{fecha_actual}.pdf"
        
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()

        # Estilos personalizados
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#8E44AD')
        )

        subtitulo_style = ParagraphStyle(
            'CustomSubTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#9B59B6')
        )

        # Encabezado
        elements.append(Paragraph("REPORTE DE PRODUCTOS MÁS VENDIDOS", titulo_style))
        elements.append(Paragraph(f"Fecha de generación: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Descripción
        descripcion = """
        <b>Descripción del Reporte:</b><br/>
        Este reporte analiza los productos con mayor rotación en el inventario, identificando 
        los artículos más populares entre los clientes. Esta información es crucial para 
        optimizar el stock, planificar compras y desarrollar estrategias de marketing dirigidas.
        """
        elements.append(Paragraph(descripcion, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Gráfica
        if os.path.exists(nombre_img):
            img = Image(nombre_img, width=10*inch, height=7*inch)
            elements.append(img)
            elements.append(Spacer(1, 20))

        # Análisis estadístico
        if self.productos_mas_vendidos:
            elements.append(Paragraph("Análisis de Productos", subtitulo_style))
            
            total_productos = len(self.productos_mas_vendidos)
            total_unidades = self.total_unidades_vendidas
            producto_top = self.productos_mas_vendidos[0] if self.productos_mas_vendidos else ("N/A", 0)
            
            analisis_data = [
                ["Métrica", "Valor"],
                ["Total de Productos Analizados", str(total_productos)],
                ["Total de Unidades Vendidas", f"{total_unidades:,}"],
                ["Producto Más Vendido", producto_top[0]],
                ["Unidades del Top 1", f"{producto_top[1]:,}"],
                ["% del Top 1", f"{(producto_top[1]/total_unidades*100):.1f}%" if total_unidades > 0 else "0%"]
            ]

            tabla_analisis = Table(analisis_data, colWidths=[3*inch, 2*inch])
            tabla_analisis.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#E74C3C')),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (1, -1), colors.HexColor('#FADBD8')),
                ('GRID', (0, 0), (1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ]))
            elements.append(tabla_analisis)
            elements.append(Spacer(1, 20))

        # Tabla detallada
        if self.productos_mas_vendidos:
            elements.append(Paragraph("Ranking de Productos", subtitulo_style))
            
            datos_tabla = [["Posición", "Producto", "Unidades", "% del Total"]]
            
            for i, (nombre, unidades) in enumerate(self.productos_mas_vendidos, 1):
                porcentaje = (unidades / self.total_unidades_vendidas) * 100 if self.total_unidades_vendidas > 0 else 0
                datos_tabla.append([
                    str(i),
                    nombre,
                    f"{unidades:,}",
                    f"{porcentaje:.1f}%"
                ])

            tabla_detalle = Table(datos_tabla, colWidths=[0.8*inch, 3*inch, 1*inch, 1*inch])
            tabla_detalle.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#F39C12')),
                ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (3, 0), 10),
                ('BACKGROUND', (0, 1), (3, -1), colors.HexColor('#FEF9E7')),
                ('GRID', (0, 0), (3, -1), 1, colors.black),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (3, -1), 'MIDDLE'),
            ]))
            elements.append(tabla_detalle)

        # Recomendaciones
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Recomendaciones Estratégicas", subtitulo_style))
        recomendaciones = """
        • Mantener stock suficiente de los productos más vendidos<br/>
        • Considerar promociones cruzadas con productos complementarios<br/>
        • Analizar la rentabilidad de cada producto top<br/>
        • Investigar por qué ciertos productos tienen mayor demanda<br/>
        • Evaluar la posibilidad de expandir líneas de productos exitosos
        """
        elements.append(Paragraph(recomendaciones, styles['Normal']))

        # Generar PDF
        doc.build(elements)
        
        # Limpiar archivo temporal
        if os.path.exists(nombre_img):
            os.remove(nombre_img)
            
        print(f"PDF de productos generado: {nombre_pdf}")

    def crear_pdf_horarios(self):
        """Crea un PDF completo para el reporte de horarios."""
        # Generar imagen de la gráfica
        # Crear superficie suficientemente grande para la gráfica completa
        superficie_ancha = max(self.ancho, 1700)
        superficie_alta = max(self.alto, 800)
        temp_surface = pygame.Surface((superficie_ancha, superficie_alta))
        temp_surface.fill((255, 255, 255))

        self.dibujar_grafica_lineas_mejorada(temp_surface)
        nombre_img = "temp_grafica_horarios.png"
        pygame.image.save(temp_surface, nombre_img)

        

        # Crear PDF
        fecha_actual = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')
        nombre_pdf = f"reportes/reporte_horarios_{fecha_actual}.pdf"
        
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter,
                            topMargin=0.5*inch, bottomMargin=0.5*inch,
                            leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()

        # Estilos personalizados
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#27AE60')
        )

        subtitulo_style = ParagraphStyle(
            'CustomSubTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#2ECC71')
        )

        # Encabezado
        elements.append(Paragraph("REPORTE DE VENTAS POR HORARIOS", titulo_style))
        elements.append(Paragraph(f"Fecha de generación: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Descripción
        descripcion = """
        <b>Descripción del Reporte:</b><br/>
        Este reporte analiza los patrones de venta durante las diferentes horas del día, 
        permitiendo identificar los períodos de mayor actividad comercial. Esta información 
        es fundamental para optimizar la asignación de personal, horarios de atención y 
        estrategias de marketing por franjas horarias.
        """
        elements.append(Paragraph(descripcion, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Gráfica
        if os.path.exists(nombre_img):
            max_width = letter[0] - (doc.leftMargin + doc.rightMargin)
            max_height = letter[1] - (doc.topMargin + doc.bottomMargin)
            img_width = min(10*inch, max_width)
            img_height = min(7*inch, max_height * 0.5)
            img = Image(nombre_img, width=img_width, height=img_height)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Spacer(1, 20))

        # Análisis por franjas horarias
        if self.ventas_por_hora:
            elements.append(Paragraph("Análisis por Franjas Horarias", subtitulo_style))
            
            # Calcular estadísticas por franjas
            mañana = sum(self.ventas_por_hora[6:12])    # 6-12
            tarde = sum(self.ventas_por_hora[12:18])    # 12-18
            noche = sum(self.ventas_por_hora[18:24])    # 18-24
            madrugada = sum(self.ventas_por_hora[0:6])  # 0-6
            
            hora_pico = self.ventas_por_hora.index(max(self.ventas_por_hora))
            total_dia = sum(self.ventas_por_hora)
            
            analisis_data = [
                ["Franja Horaria", "Unidades Vendidas", "% del Total"],
                ["Mañana (06:00-12:00)", f"{mañana:,}", f"{(mañana/total_dia*100):.1f}%" if total_dia > 0 else "0%"],
                ["Tarde (12:00-18:00)", f"{tarde:,}", f"{(tarde/total_dia*100):.1f}%" if total_dia > 0 else "0%"],
                ["Noche (18:00-24:00)", f"{noche:,}", f"{(noche/total_dia*100):.1f}%" if total_dia > 0 else "0%"],
                ["Madrugada (00:00-06:00)", f"{madrugada:,}", f"{(madrugada/total_dia*100):.1f}%" if total_dia > 0 else "0%"],
                ["", "", ""],
                ["Hora Pico", f"{hora_pico}:00", f"{self.ventas_por_hora[hora_pico]:,} unidades"]
            ]

            tabla_analisis = Table(analisis_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            tabla_analisis.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#16A085')),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (2, 0), 11),
                ('BACKGROUND', (0, 1), (2, 5), colors.HexColor('#D5F4E6')),
                ('BACKGROUND', (0, 6), (2, 6), colors.HexColor('#A3E4D7')),
                ('GRID', (0, 0), (2, -1), 1, colors.black),
                ('ALIGN', (1, 1), (2, -1), 'CENTER'),
                ('VALIGN', (0, 0), (2, -1), 'MIDDLE'),
                ('FONTNAME', (0, 6), (2, 6), 'Helvetica-Bold'),
            ]))
            elements.append(tabla_analisis)
            elements.append(Spacer(1, 20))

        # Tabla detallada por horas
        if self.ventas_por_hora:
            elements.append(Paragraph("Detalle Hora por Hora", subtitulo_style))
            
            # Crear tabla en dos columnas para ahorrar espacio
            datos_tabla = [["Hora", "Unidades", "Hora", "Unidades"]]
            
            for i in range(12):  # 0-11 y 12-23
                hora1 = f"{i:02d}:00"
                unidades1 = f"{self.ventas_por_hora[i]:,}"
                hora2 = f"{i+12:02d}:00"
                unidades2 = f"{self.ventas_por_hora[i+12]:,}"
                datos_tabla.append([hora1, unidades1, hora2, unidades2])

            tabla_detalle = Table(datos_tabla, colWidths=[1*inch, 1*inch, 1*inch, 1*inch])
            tabla_detalle.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#1ABC9C')),
                ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (3, 0), 10),
                ('BACKGROUND', (0, 1), (3, -1), colors.HexColor('#E8F8F5')),
                ('GRID', (0, 0), (3, -1), 1, colors.black),
                ('ALIGN', (0, 1), (3, -1), 'CENTER'),
                ('VALIGN', (0, 0), (3, -1), 'MIDDLE'),
            ]))
            elements.append(tabla_detalle)

        # Recomendaciones
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Recomendaciones Operativas", subtitulo_style))
        recomendaciones = """
        • Ajustar el personal según los horarios de mayor demanda<br/>
        • Considerar horarios extendidos en las horas pico<br/>
        • Implementar promociones en horarios de baja actividad<br/>
        • Optimizar los procesos durante las horas de mayor flujo<br/>
        • Planificar el mantenimiento en horarios de menor actividad
        """
        elements.append(Paragraph(recomendaciones, styles['Normal']))

        # Generar PDF
        doc.build(elements)
        
        # Limpiar archivo temporal
        if os.path.exists(nombre_img):
            os.remove(nombre_img)
            
        print(f"PDF de horarios generado: {nombre_pdf}")

    def crear_pdf_corte_caja(self):
        """Crea un PDF completo para el corte de caja."""
        if not self.corte_caja_datos:
            return

        fecha_actual = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')
        fecha_corte_format = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d').strftime('%d-%m-%Y')
        nombre_pdf = f"reportes/corte_caja_{fecha_corte_format}_{fecha_actual}.pdf"

        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()

        # Estilos personalizados
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#E67E22')
        )

        subtitulo_style = ParagraphStyle(
            'CustomSubTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#D35400')
        )

        # Encabezado
        fecha_formateada = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d').strftime('%d/%m/%Y')
        elements.append(Paragraph(f"CORTE DE CAJA - {fecha_formateada}", titulo_style))
        elements.append(Paragraph(f"Generado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Descripción
        descripcion = """
        <b>Descripción del Reporte:</b><br/>
        El corte de caja es un proceso contable que registra todas las transacciones de venta 
        realizadas en un día específico. Este documento proporciona un resumen detallado de 
        ingresos, métodos de pago utilizados y productos vendidos, facilitando el control 
        financiero y la conciliación diaria.
        """
        elements.append(Paragraph(descripcion, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Resumen Ejecutivo
        elements.append(Paragraph("Resumen Ejecutivo", subtitulo_style))
        
        ventas_data = self.corte_caja_datos['ventas']
        total_ventas = float(ventas_data['total_ventas'] or 0)
        num_ventas = int(ventas_data['num_ventas'] or 0)
        ticket_promedio = total_ventas / num_ventas if num_ventas > 0 else 0

        resumen_data = [
            ["Concepto", "Valor"],
            ["Total de Ventas", f"${total_ventas:,.2f}"],
            ["Número de Transacciones", f"{num_ventas:,}"],
            ["Ticket Promedio", f"${ticket_promedio:.2f}"],
            ["Fecha del Corte", fecha_formateada]
        ]

        tabla_resumen = Table(resumen_data, colWidths=[3*inch, 2*inch])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#E67E22')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.HexColor('#FDF2E9')),
            ('GRID', (0, 0), (1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        elements.append(tabla_resumen)
        elements.append(Spacer(1, 20))

        # Análisis por Estados de Venta
        if self.corte_caja_datos.get('estados'):
            elements.append(Paragraph("Análisis por Estado de Venta", subtitulo_style))
            
            datos_estados = [["Estado", "Cantidad", "Monto", "% del Total"]]
            
            for estado in self.corte_caja_datos['estados']:
                porcentaje = (float(estado['total']) / total_ventas) * 100 if total_ventas > 0 else 0
                datos_estados.append([
                    estado['Estado'],
                    f"{estado['cantidad']}",
                    f"${float(estado['total']):,.2f}",
                    f"{porcentaje:.1f}%"
                ])

            tabla_estados = Table(datos_estados, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
            tabla_estados.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#F39C12')),
                ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (3, 0), 10),
                ('BACKGROUND', (0, 1), (3, -1), colors.HexColor('#FEF9E7')),
                ('GRID', (0, 0), (3, -1), 1, colors.black),
                ('ALIGN', (1, 1), (3, -1), 'CENTER'),
                ('VALIGN', (0, 0), (3, -1), 'MIDDLE'),
            ]))
            elements.append(tabla_estados)
            elements.append(Spacer(1, 20))

        # Top Productos del Día
        if self.corte_caja_datos.get('productos'):
            elements.append(Paragraph("Productos Más Vendidos del Día", subtitulo_style))
            
            datos_productos = [["Producto", "Cantidad", "Total Vendido"]]
            
            for producto in self.corte_caja_datos['productos'][:10]:  # Top 10
                datos_productos.append([
                    producto['Nombre_prod'],
                    f"{producto['cantidad']}",
                    f"${float(producto['total']):,.2f}"
                ])

            tabla_productos = Table(datos_productos, colWidths=[3*inch, 1*inch, 1.5*inch])
            tabla_productos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#E74C3C')),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (2, 0), 10),
                ('BACKGROUND', (0, 1), (2, -1), colors.HexColor('#FADBD8')),
                ('GRID', (0, 0), (2, -1), 1, colors.black),
                ('ALIGN', (1, 1), (2, -1), 'CENTER'),
                ('VALIGN', (0, 0), (2, -1), 'MIDDLE'),
            ]))
            elements.append(tabla_productos)

        # Observaciones y Notas
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Observaciones", subtitulo_style))
        
        if total_ventas == 0:
            observacion = "No se registraron ventas en la fecha seleccionada."
        elif num_ventas < 10:
            observacion = "Día de baja actividad comercial. Revisar factores externos que pudieron influir."
        elif ticket_promedio > 100:
            observacion = "Ticket promedio alto. Excelente trabajo del equipo de ventas."
        else:
            observacion = "Actividad comercial normal para la fecha analizada."
            
        elements.append(Paragraph(observacion, styles['Normal']))
        
        # Espacio para firmas
        elements.append(Spacer(1, 50))
        elements.append(Paragraph("Validación del Corte", subtitulo_style))
        
        firma_data = [
            ["", "", ""],
            ["_" * 25, "_" * 25, "_" * 25],
            ["Cajero(a)", "Supervisor(a)", "Gerente"],
            ["", "", ""],
            ["Fecha: ___________", "Fecha: ___________", "Fecha: ___________"]
        ]
        
        tabla_firmas = Table(firma_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (2, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (2, -1), 10),
            ('FONTNAME', (0, 2), (2, 2), 'Helvetica-Bold'),
        ]))
        elements.append(tabla_firmas)

        # Generar PDF
        doc.build(elements)
        print(f"PDF de corte de caja generado: {nombre_pdf}")

    def crear_pdf_inventario(self):
        """Crea un PDF completo para el reporte de inventario."""
        if not self.inventario_datos:
            return

        fecha_actual = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')
        nombre_pdf = f"reportes/inventario_{self.inventario_filtro.lower()}_{fecha_actual}.pdf"

        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()

        # Estilos personalizados
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#8E44AD')
        )

        subtitulo_style = ParagraphStyle(
            'CustomSubTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#9B59B6')
        )

        # Encabezado
        elements.append(Paragraph(f"REPORTE DE INVENTARIO - {self.inventario_filtro}", titulo_style))
        elements.append(Paragraph(f"Fecha de generación: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Descripción
        descripcion = """
        <b>Descripción del Reporte:</b><br/>
        Este reporte proporciona un análisis detallado del estado actual del inventario de materia prima,
        incluyendo niveles de stock, productos con existencias bajas y artículos agotados. 
        Es una herramienta esencial para la gestión eficiente del almacén y la planificación de compras.
        """
        elements.append(Paragraph(descripcion, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Resumen estadístico
        items_agotados = sum(1 for item in self.inventario_datos if item['Cantidad'] == 0)
        items_bajos = sum(1 for item in self.inventario_datos if 0 < item['Cantidad'] <= 10)
        items_normales = len(self.inventario_datos) - items_agotados - items_bajos

        elements.append(Paragraph("Resumen del Inventario", subtitulo_style))
        
        resumen_data = [
            ["Estado", "Cantidad", "Porcentaje"],
            ["Total de Items", str(len(self.inventario_datos)), "100%"],
            ["Stock Normal", str(items_normales), f"{(items_normales/len(self.inventario_datos)*100):.1f}%" if len(self.inventario_datos) > 0 else "0%"],
            ["Stock Bajo (≤10)", str(items_bajos), f"{(items_bajos/len(self.inventario_datos)*100):.1f}%" if len(self.inventario_datos) > 0 else "0%"],
            ["Agotados", str(items_agotados), f"{(items_agotados/len(self.inventario_datos)*100):.1f}%" if len(self.inventario_datos) > 0 else "0%"]
        ]

        tabla_resumen = Table(resumen_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#8E44AD')),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (2, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (2, 0), 12),
            ('BACKGROUND', (0, 1), (2, 1), colors.HexColor('#D2B4DE')),
            ('BACKGROUND', (0, 2), (2, 2), colors.HexColor('#A9DFBF')),
            ('BACKGROUND', (0, 3), (2, 3), colors.HexColor('#F9E79F')),
            ('BACKGROUND', (0, 4), (2, 4), colors.HexColor('#F1948A')),
            ('GRID', (0, 0), (2, -1), 1, colors.black),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (2, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        elements.append(tabla_resumen)
        elements.append(Spacer(1, 20))

        # Tabla detallada del inventario
        elements.append(Paragraph("Detalle del Inventario", subtitulo_style))
        
        datos_inventario = [["ID", "Nombre", "Stock", "Unidad", "Tipo", "Estado"]]

        for item in self.inventario_datos:
            # Determinar estado del stock
            if item['Cantidad'] == 0:
                estado = "AGOTADO"
            elif item['Cantidad'] <= 10:
                estado = "BAJO"
            else:
                estado = "NORMAL"
                
            datos_inventario.append([
                str(item['id']),
                item['Nombre'][:25] + "..." if len(item['Nombre']) > 25 else item['Nombre'],
                str(item['Cantidad']),
                item['Unidad'],
                item['Tipo'][:15] + "..." if len(item['Tipo']) > 15 else item['Tipo'],
                estado
            ])

        tabla_inventario = Table(datos_inventario, colWidths=[0.5*inch, 2.2*inch, 0.7*inch, 0.8*inch, 1*inch, 0.8*inch])
        tabla_inventario.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (5, 0), colors.HexColor('#9B59B6')),
            ('TEXTCOLOR', (0, 0), (5, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (5, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (5, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (5, 0), 9),
            ('BACKGROUND', (0, 1), (5, -1), colors.HexColor('#F4F6F7')),
            ('GRID', (0, 0), (5, -1), 1, colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),
            ('VALIGN', (0, 0), (5, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (5, -1), 8),
        ]))

        # Colorear filas según estado
        for i, item in enumerate(self.inventario_datos, 1):
            if item['Cantidad'] == 0:  # Agotado - Rojo
                tabla_inventario.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (5, i), colors.HexColor('#F1948A'))
                ]))
            elif item['Cantidad'] <= 10:  # Bajo - Amarillo
                tabla_inventario.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (5, i), colors.HexColor('#F9E79F'))
                ]))

        elements.append(tabla_inventario)

        # Recomendaciones
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Recomendaciones de Gestión", subtitulo_style))
        
        if items_agotados > 0:
            recomendacion_agotados = f"<b>URGENTE:</b> {items_agotados} productos agotados requieren reposición inmediata.<br/>"
        else:
            recomendacion_agotados = ""
            
        if items_bajos > 0:
            recomendacion_bajos = f"<b>ATENCIÓN:</b> {items_bajos} productos con stock bajo necesitan reposición pronto.<br/>"
        else:
            recomendacion_bajos = ""

        recomendaciones = f"""
        {recomendacion_agotados}
        {recomendacion_bajos}
        • Establecer puntos de reorden para evitar desabastecimientos<br/>
        • Revisar la rotación de productos para optimizar el inventario<br/>
        • Considerar proveedores alternativos para productos críticos<br/>
        • Implementar un sistema de alertas automáticas de stock bajo
        """
        elements.append(Paragraph(recomendaciones, styles['Normal']))

        # Generar PDF
        doc.build(elements)
        print(f"PDF de inventario generado: {nombre_pdf}")

    def crear_pdf_pedidos(self):
        """Crea un PDF completo para el reporte de pedidos."""
        if not self.pedidos_datos:
            return

        fecha_actual = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')
        nombre_pdf = f"reportes/pedidos_{self.pedidos_filtro.lower()}_{fecha_actual}.pdf"

        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.5*inch, rightMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()

        # Estilos personalizados
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2980B9')
        )

        subtitulo_style = ParagraphStyle(
            'CustomSubTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#3498DB')
        )

        # Encabezado
        elements.append(Paragraph(f"REPORTE DE PEDIDOS - {self.pedidos_filtro}", titulo_style))
        elements.append(Paragraph(f"Fecha de generación: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Descripción
        descripcion = """
        <b>Descripción del Reporte:</b><br/>
        Este reporte analiza el estado y progreso de los pedidos de venta, proporcionando 
        información crucial para el seguimiento de entregas, gestión de la producción y 
        atención al cliente. Incluye métricas de tiempo de procesamiento y análisis por estados.
        """
        elements.append(Paragraph(descripcion, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Análisis estadístico
        pedidos_pendientes = sum(1 for p in self.pedidos_datos if p['Estado'] in ['Pendiente', 'En proceso'])
        pedidos_listos = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Listo')
        pedidos_entregados = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Entregado')
        
        # Calcular valor total
        valor_total = sum(float(p.get('Total', 0)) for p in self.pedidos_datos)
        promedio_pedido = valor_total / len(self.pedidos_datos) if len(self.pedidos_datos) > 0 else 0

        elements.append(Paragraph("Análisis de Pedidos", subtitulo_style))
        
        resumen_data = [
            ["Métrica", "Valor"],
            ["Total de Pedidos", str(len(self.pedidos_datos))],
            ["Pedidos Pendientes", str(pedidos_pendientes)],
            ["Pedidos Listos", str(pedidos_listos)],
            ["Pedidos Entregados", str(pedidos_entregados)],
            ["Valor Total", f"${valor_total:,.2f}"],
            ["Valor Promedio por Pedido", f"${promedio_pedido:.2f}"]
        ]

        tabla_resumen = Table(resumen_data, colWidths=[3*inch, 2*inch])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#2980B9')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.HexColor('#EBF5FB')),
            ('GRID', (0, 0), (1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        elements.append(tabla_resumen)
        elements.append(Spacer(1, 20))

        # Tabla detallada de pedidos
        elements.append(Paragraph("Estado Detallado de Pedidos", subtitulo_style))
        
        datos_pedidos = [["ID", "Cliente", "F. Pedido", "F. Entrega", "Estado", "Total", "Días"]]

        for pedido in self.pedidos_datos:
            # Formatear fechas
            fecha_pedido = str(pedido['Fecha_pedido'])[:10] if pedido['Fecha_pedido'] else "N/A"
            fecha_entrega = str(pedido['Fecha_entrega'])[:10] if pedido['Fecha_entrega'] else "N/A"
            
            datos_pedidos.append([
                str(pedido['id']),
                pedido['cliente'][:15] + "..." if len(pedido['cliente']) > 15 else pedido['cliente'],
                fecha_pedido,
                fecha_entrega,
                pedido['Estado'],
                f"${float(pedido.get('Total', 0)):,.0f}",
                str(pedido.get('dias_proceso', 'N/A'))
            ])

        tabla_pedidos = Table(datos_pedidos, colWidths=[0.5*inch, 1.5*inch, 0.9*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.6*inch])
        tabla_pedidos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (6, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (6, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (6, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (6, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (6, 0), 9),
            ('BACKGROUND', (0, 1), (6, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (6, -1), 1, colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (5, 1), (6, -1), 'CENTER'),
            ('VALIGN', (0, 0), (6, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (6, -1), 8),
        ]))

        # Colorear filas según estado
        for i, pedido in enumerate(self.pedidos_datos, 1):
            if pedido['Estado'] == 'Pendiente':
                tabla_pedidos.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (6, i), colors.HexColor('#FADBD8'))
                ]))
            elif pedido['Estado'] == 'En proceso':
                tabla_pedidos.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (6, i), colors.HexColor('#FEF9E7'))
                ]))
            elif pedido['Estado'] == 'Listo':
                tabla_pedidos.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (6, i), colors.HexColor('#D5F4E6'))
                ]))
            elif pedido['Estado'] == 'Entregado':
                tabla_pedidos.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (6, i), colors.HexColor('#E8F6F3'))
                ]))

        elements.append(tabla_pedidos)

        # Análisis de tiempos
        if any(p.get('dias_proceso') for p in self.pedidos_datos):
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Análisis de Tiempos de Procesamiento", subtitulo_style))
            
            tiempos_validos = [int(p['dias_proceso']) for p in self.pedidos_datos if p.get('dias_proceso') and str(p['dias_proceso']).isdigit()]
            
            if tiempos_validos:
                tiempo_promedio = sum(tiempos_validos) / len(tiempos_validos)
                tiempo_max = max(tiempos_validos)
                tiempo_min = min(tiempos_validos)
                
                tiempos_data = [
                    ["Métrica de Tiempo", "Días"],
                    ["Tiempo Promedio de Procesamiento", f"{tiempo_promedio:.1f}"],
                    ["Tiempo Máximo", str(tiempo_max)],
                    ["Tiempo Mínimo", str(tiempo_min)],
                    ["Pedidos con Más de 7 Días", str(sum(1 for t in tiempos_validos if t > 7))]
                ]
                
                tabla_tiempos = Table(tiempos_data, colWidths=[3*inch, 1.5*inch])
                tabla_tiempos.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#17A2B8')),
                    ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (1, 0), 11),
                    ('BACKGROUND', (0, 1), (1, -1), colors.HexColor('#D1ECF1')),
                    ('GRID', (0, 0), (1, -1), 1, colors.black),
                    ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ]))
                elements.append(tabla_tiempos)

        # Recomendaciones
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Recomendaciones de Gestión", subtitulo_style))
        
        recomendaciones_base = """
        • Priorizar la atención de pedidos pendientes por más de 5 días<br/>
        • Implementar notificaciones automáticas para pedidos próximos a vencer<br/>
        • Revisar el flujo de trabajo para reducir tiempos de procesamiento<br/>
        • Mantener comunicación constante con clientes sobre el estado de sus pedidos<br/>
        """
        
        if pedidos_pendientes > 10:
            recomendacion_urgente = f"<b>ATENCIÓN:</b> {pedidos_pendientes} pedidos pendientes requieren seguimiento inmediato.<br/>"
        else:
            recomendacion_urgente = ""
            
        recomendaciones_completas = recomendacion_urgente + recomendaciones_base
        elements.append(Paragraph(recomendaciones_completas, styles['Normal']))

        # Generar PDF
        doc.build(elements)
        print(f"PDF de pedidos generado: {nombre_pdf}")

    # [Mantener todos los métodos existentes sin cambios...]
    def cargar_corte_caja(self, fecha=None):
        """Carga los datos para el corte de caja de la fecha especificada."""
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
        """Carga los datos del inventario desde la base de datos."""
        conexion = Conexion()

        # Filtro según la opción seleccionada
        filtro_sql = ""
        if self.inventario_filtro == "BAJO":
            filtro_sql = " WHERE Cantidad <= 10 AND Cantidad > 0"
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
        """Carga los datos de los pedidos desde la base de datos."""
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

    def dibujar_selector_fecha(self, surface):
        """Dibuja el selector de fecha en la superficie proporcionada."""
        # Calcular posición dinámica
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        
        selector_y = graf_y + int(0.02 * graf_h)
        selector_w = int(0.15 * self.ancho)
        selector_h = int(0.06 * self.alto)
        selector_x = graf_x + (graf_w - selector_w) // 2
        
        # Actualizar rectángulos
        self.selector_fecha_rect = pygame.Rect(selector_x, selector_y, selector_w, selector_h)
        
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

        # Botón anterior
        color_btn_anterior = (200, 200, 200)
        if self.boton_fecha_anterior.collidepoint(pygame.mouse.get_pos()):
            color_btn_anterior = (170, 170, 170)
        
        pygame.draw.rect(surface, color_btn_anterior, self.boton_fecha_anterior, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 100), self.boton_fecha_anterior, 2, border_radius=8)

        # Botón siguiente
        color_btn_siguiente = (200, 200, 200)
        if self.boton_fecha_siguiente.collidepoint(pygame.mouse.get_pos()):
            color_btn_siguiente = (170, 170, 170)
            
        pygame.draw.rect(surface, color_btn_siguiente, self.boton_fecha_siguiente, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 100), self.boton_fecha_siguiente, 2, border_radius=8)

        # Flechas
        flecha_font = pygame.font.SysFont("Arial", int(self.alto * 0.04), bold=True)
        flecha_izq = flecha_font.render("<-", True, (0, 0, 0))
        flecha_der = flecha_font.render("->", True, (0, 0, 0))

        rect_izq = flecha_izq.get_rect(center=self.boton_fecha_anterior.center)
        rect_der = flecha_der.get_rect(center=self.boton_fecha_siguiente.center)

        surface.blit(flecha_izq, rect_izq)
        surface.blit(flecha_der, rect_der)

    def dibujar_filtros_inventario(self, surface):
        """Dibuja los botones de filtro para el inventario."""
        for i, rect in enumerate(self.botones_filtro_inventario):
            color = (180, 180, 255) if self.inventario_filtro == self.filtros_inventario[i] else (220, 220, 220)
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto = self.fuente_boton.render(self.filtros_inventario[i], True, (0, 0, 0))
            text_rect = texto.get_rect(center=rect.center)
            surface.blit(texto, text_rect)

    def dibujar_filtros_pedidos(self, surface):
        """Dibuja los botones de filtro para los pedidos."""
        for i, rect in enumerate(self.botones_filtro_pedidos):
            color = (180, 180, 255) if self.pedidos_filtro == self.filtros_pedidos[i] else (220, 220, 220)
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto = self.fuente_boton.render(self.filtros_pedidos[i], True, (0, 0, 0))
            text_rect = texto.get_rect(center=rect.center)
            surface.blit(texto, text_rect)

    def dibujar_inventario_con_scroll(self, surface):
        """Dibuja el reporte de inventario con scroll en la superficie proporcionada."""
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
        rect = resumen_texto.get_rect(center=(graf_x + graf_w // 2, graf_y +  graf_h +10))
        surface.blit(resumen_texto, rect)

        # Pie de página
        pie_inventario = self.fuente_pie_pagina.render("Reporte de Inventario", True, (50, 50, 120))
        pie_rect = pie_inventario.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h +25))
        surface.blit(pie_inventario, pie_rect)

    def dibujar_pedidos_con_scroll(self, surface):
        """Dibuja el reporte de pedidos con scroll en la superficie proporcionada."""
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
        rect = resumen_texto.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h + 10))
        surface.blit(resumen_texto, rect)

        # Pie de página
        pie_pedidos = self.fuente_pie_pagina.render("Reporte de Pedidos", True, (50, 50, 120))
        pie_rect = pie_pedidos.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h + 30))
        surface.blit(pie_pedidos, pie_rect)

    def dibujar_corte_caja(self, surface):
        """Dibuja el informe de corte de caja en la superficie proporcionada."""
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
        if self.corte_caja_datos.get('productos'):
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
        pie_rect = pie_corte.get_rect(center=(graf_x + graf_w // 2, contenido_y + contenido_h + 25))
        surface.blit(pie_corte, pie_rect)

    def dibujar_scroll_bar(self, surface, x, y, height, scroll_y, scroll_max, tipo):
        """Dibuja una barra de scroll vertical."""
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

    def handle_event(self, event):
        """Maneja los eventos de la interfaz."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Verificar clics en botones de opciones
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

            # Eventos específicos por sección
            if self.opcion_seleccionada == "CORTE CAJA":
                if self.selector_fecha_rect and self.selector_fecha_rect.collidepoint(mouse_pos):
                    self.selector_fecha_activo = not self.selector_fecha_activo
                    return

                if self.boton_fecha_anterior and self.boton_fecha_anterior.collidepoint(mouse_pos):
                    try:
                        fecha_actual = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d')
                        dia_anterior = fecha_actual - datetime.timedelta(days=1)
                        self.fecha_seleccionada = dia_anterior.strftime('%Y-%m-%d')
                        self.cargar_corte_caja(self.fecha_seleccionada)
                    except Exception as e:
                        print(f"Error al cambiar fecha anterior: {e}")
                    return

                if self.boton_fecha_siguiente and self.boton_fecha_siguiente.collidepoint(mouse_pos):
                    try:
                        fecha_actual = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d')
                        dia_siguiente = fecha_actual + datetime.timedelta(days=1)
                        if dia_siguiente.date() <= datetime.datetime.now().date():
                            self.fecha_seleccionada = dia_siguiente.strftime('%Y-%m-%d')
                            self.cargar_corte_caja(self.fecha_seleccionada)
                    except Exception as e:
                        print(f"Error al cambiar fecha siguiente: {e}")
                    return

            elif self.opcion_seleccionada == "INVENTARIO":
                for i, rect in enumerate(self.botones_filtro_inventario):
                    if rect.collidepoint(mouse_pos):
                        self.inventario_filtro = self.filtros_inventario[i]
                        self.cargar_inventario()
                        return

            elif self.opcion_seleccionada == "PEDIDOS":
                for i, rect in enumerate(self.botones_filtro_pedidos):
                    if rect.collidepoint(mouse_pos):
                        self.pedidos_filtro = self.filtros_pedidos[i]
                        self.cargar_pedidos()
                        return

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.pdf_hover = self.boton_pdf_rect and self.boton_pdf_rect.collidepoint(mouse_pos)