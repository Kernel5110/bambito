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
        pygame.font.init()
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

        self.FONDO = (241, 236, 227)
        self.color_texto = (0, 0, 0)

        # Escalado proporcional de fuentes y elementos
        def fuente_relativa(base_size):
            scale = min(self.ancho / 1555, self.alto / 710)
            return int(base_size * scale)
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", fuente_relativa(36), bold=True)
        self.fuente_boton = pygame.font.SysFont("Open Sans", fuente_relativa(28), bold=True)
        self.fuente_boton_agregar = pygame.font.SysFont("Open Sans", fuente_relativa(28), bold=True)
        self.fuente_boton_pdf = pygame.font.SysFont("Open Sans", fuente_relativa(28), bold=True)
        self.fuente_pie_pagina = pygame.font.SysFont("Open Sans", fuente_relativa(28), bold=True)

        # Añadir opciones de INVENTARIO y PEDIDOS
        self.botones_opciones = ["VENTAS", "PRODUCTOS", "HORARIOS", "CORTE CAJA", "INVENTARIO", "PEDIDOS"]
        self.opcion_seleccionada = self.botones_opciones[0]

        # Calcula posiciones y tamaños relativos para los botones
        # Ajustamos el ancho para que quepan todos los botones
        self.boton_width = int(self.ancho * 0.09)  # Reducimos un poco el ancho
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

        self.boton_agregar_rect = pygame.Rect(
            self.x + int(0.013 * self.ancho) + len(self.botones_opciones) * (self.boton_width + int(0.01 * self.ancho)) + int(0.012 * self.ancho),
            self.y + int(0.11 * self.alto),
            int(0.09 * self.ancho),
            int(0.06 * self.alto)
        )
        self.color_boton_agregar = (100, 200, 100)
        self.color_boton_agregar_hover = (80, 180, 80)
        self.agregar_hover = False

        self.boton_pdf_rect = pygame.Rect(
            self.x + int(0.013 * self.ancho) + len(self.botones_opciones) * (self.boton_width + int(0.01 * self.ancho)) + int(0.12 * self.ancho),
            self.y + int(0.11 * self.alto),
            int(0.12 * self.ancho),
            int(0.06 * self.alto)
        )
        self.color_boton_pdf = (100, 100, 200)
        self.color_boton_pdf_hover = (80, 80, 180)
        self.pdf_hover = False

        # Datos de ventas por día (VENTAS)
        self.ventas_por_dia = []
        self.max_ventas = 0

        # Datos de productos más vendidos (PRODUCTOS)
        self.productos_mas_vendidos = []
        self.total_unidades_vendidas = 0

        # Datos de ventas por hora (HORARIOS)
        self.ventas_por_hora = [0] * 24
        self.max_ventas_hora = 0
        
        # Datos del corte de caja
        self.fecha_corte = datetime.datetime.now().strftime('%Y-%m-%d')
        self.corte_caja_datos = {}
        self.metodos_pago = []
        
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
        self.inventario_pagina_actual = 0
        self.inventario_items_por_pagina = 10
        
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
        
        # Botones para navegación de páginas de inventario
        self.boton_anterior_pagina = pygame.Rect(
            self.x + int(0.35 * self.ancho),
            self.y + int(0.75 * self.alto),
            int(0.1 * self.ancho),
            int(0.04 * self.alto)
        )
        
        self.boton_siguiente_pagina = pygame.Rect(
            self.x + int(0.55 * self.ancho),
            self.y + int(0.75 * self.alto),
            int(0.1 * self.ancho),
            int(0.04 * self.alto)
        )
        
        # Datos para reporte de pedidos
        self.pedidos_datos = []
        self.pedidos_filtro = "TODOS"  # TODOS, PENDIENTES, COMPLETADOS
        self.filtros_pedidos = ["TODOS", "PENDIENTES", "COMPLETADOS"]
        self.botones_filtro_pedidos = []
        self.pedidos_pagina_actual = 0
        self.pedidos_items_por_pagina = 8
        
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
        
        # Botones para navegación de páginas de pedidos
        self.boton_anterior_pagina_pedidos = pygame.Rect(
            self.x + int(0.35 * self.ancho),
            self.y + int(0.75 * self.alto),
            int(0.1 * self.ancho),
            int(0.04 * self.alto)
        )
        
        self.boton_siguiente_pagina_pedidos = pygame.Rect(
            self.x + int(0.55 * self.ancho),
            self.y + int(0.75 * self.alto),
            int(0.1 * self.ancho),
            int(0.04 * self.alto)
        )

    def cargar_ventas_por_dia(self):
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
        """Cargar datos para el corte de caja de la fecha especificada"""
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
        
        # Ventas por estado (usando el campo estado en lugar de método de pago)
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
        
        # Organizar datos - versión simplificada
        self.corte_caja_datos = {
            'fecha': fecha,
            'ventas': resultado_ventas[0] if resultado_ventas else {'num_ventas': 0, 'total_ventas': 0},
            'estados': resultado_estados,
            'productos': resultado_productos
        }
        
        # Total de ventas
        total_ventas = float(self.corte_caja_datos['ventas']['total_ventas'] or 0)
        self.corte_caja_datos['total'] = total_ventas
        
        # Estados para el gráfico (en lugar de métodos de pago)
        self.metodos_pago = [(e['Estado'], float(e['total'])) for e in resultado_estados] if resultado_estados else []
        
    def cargar_inventario(self):
        """Cargar datos del inventario desde la base de datos"""
        conexion = Conexion()
        
        # Filtro según la opción seleccionada
        filtro_sql = ""
        if self.inventario_filtro == "BAJO":
            filtro_sql = " WHERE Stock <= 10 AND Stock > 0"
        elif self.inventario_filtro == "AGOTADO":
            filtro_sql = " WHERE Stock = 0"
            
        # Consultar materia prima
        query_mp = f"""
            SELECT 
                ID_MateriaPrima as id,
                Nombre,
                Stock,
                Unidad,
                'Materia Prima' as Tipo
            FROM materiaprima
            {filtro_sql}
            ORDER BY Stock ASC
        """
        
        try:
            resultado_mp = conexion.consultar(query_mp)
            self.inventario_datos = resultado_mp
        except Exception as e:
            print(f"Error al cargar inventario: {e}")
            self.inventario_datos = []
    
    def cargar_pedidos(self):
        """Cargar datos de pedidos desde la base de datos"""
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
                c.Nombre as cliente,
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
        except Exception as e:
            print(f"Error al cargar pedidos: {e}")
            self.pedidos_datos = []

    def dibujar_reporte(self, surface):
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
            self.dibujar_inventario(surface)
        elif self.opcion_seleccionada == "PEDIDOS":
            self.dibujar_filtros_pedidos(surface)
            self.dibujar_pedidos(surface)

    def dibujar_selector_fecha(self, surface):
        # Fondo del selector
        color_fondo = (255, 255, 255)
        color_borde = (100, 100, 100) if self.selector_fecha_activo else (180, 180, 180)
        pygame.draw.rect(surface, color_fondo, self.selector_fecha_rect, border_radius=10)
        pygame.draw.rect(surface, color_borde, self.selector_fecha_rect, 2, border_radius=10)
        
        # Texto de la fecha
        fecha_formateada = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d').strftime('%d/%m/%Y')
        texto_fecha = self.fuente_boton.render(fecha_formateada, True, (0, 0, 0))
        text_rect = texto_fecha.get_rect(center=self.selector_fecha_rect.center)
        surface.blit(texto_fecha, text_rect)
        
        # Botones para cambiar fecha
        pygame.draw.rect(surface, (220, 220, 220), self.boton_fecha_anterior, border_radius=5)
        pygame.draw.rect(surface, (220, 220, 220), self.boton_fecha_siguiente, border_radius=5)
        
        # Flechas para los botones
        flecha_font = pygame.font.SysFont("Arial", int(self.alto * 0.04))
        flecha_izq = flecha_font.render("<", True, (0, 0, 0))
        flecha_der = flecha_font.render(">", True, (0, 0, 0))
        
        rect_izq = flecha_izq.get_rect(center=self.boton_fecha_anterior.center)
        rect_der = flecha_der.get_rect(center=self.boton_fecha_siguiente.center)
        
        surface.blit(flecha_izq, rect_izq)
        surface.blit(flecha_der, rect_der)
        
    def dibujar_filtros_inventario(self, surface):
        """Dibuja los botones de filtro para el inventario"""
        for i, rect in enumerate(self.botones_filtro_inventario):
            color = (180, 180, 255) if self.inventario_filtro == self.filtros_inventario[i] else (220, 220, 220)
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto = self.fuente_boton.render(self.filtros_inventario[i], True, (0, 0, 0))
            text_rect = texto.get_rect(center=rect.center)
            surface.blit(texto, text_rect)
            
    def dibujar_filtros_pedidos(self, surface):
        """Dibuja los botones de filtro para los pedidos"""
        for i, rect in enumerate(self.botones_filtro_pedidos):
            color = (180, 180, 255) if self.pedidos_filtro == self.filtros_pedidos[i] else (220, 220, 220)
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto = self.fuente_boton.render(self.filtros_pedidos[i], True, (0, 0, 0))
            text_rect = texto.get_rect(center=rect.center)
            surface.blit(texto, text_rect)

    def _get_grafica_area(self):
        # Calcula la posición y tamaño de la gráfica para que quede debajo de los botones y centrada
        boton_y = self.y + int(0.11 * self.alto)
        boton_h = int(0.06 * self.alto)
        margen = int(0.04 * self.alto)
        graf_y = boton_y + boton_h + margen
        graf_w = int(0.85 * self.ancho)
        graf_x = self.x + (self.ancho - graf_w) // 2
        graf_h = self.alto - (graf_y - self.y) - int(0.05 * self.alto)
        return graf_x, graf_y, graf_w, graf_h

    def dibujar_grafica_barras(self, surface):
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
        # Si no hay datos, cargarlos
        if not self.corte_caja_datos:
            self.cargar_corte_caja(self.fecha_seleccionada)
            
        graf_x, graf_y, graf_w, graf_h = self._get_grafica_area()
        
        # Fondo principal
        pygame.draw.rect(surface, (255, 255, 255), (graf_x, graf_y, graf_w, graf_h), border_radius=12)
        pygame.draw.rect(surface, (200, 200, 200), (graf_x, graf_y, graf_w, graf_h), 2, border_radius=12)
        
        # Si no hay ventas
        if not self.corte_caja_datos or not self.corte_caja_datos['ventas'] or float(self.corte_caja_datos['ventas']['total_ventas'] or 0) == 0:
            font = pygame.font.SysFont("Open Sans", int(0.045 * self.alto))
            msg = font.render(f"No hay datos de ventas para el día {self.fecha_seleccionada}.", True, (180, 0, 0))
            surface.blit(msg, (graf_x + graf_w//4, graf_y + graf_h // 2))
            
            # Pie de página
            pie_corte = self.fuente_pie_pagina.render("Corte de Caja", True, (50, 50, 120))
            pie_rect = pie_corte.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
            surface.blit(pie_corte, pie_rect)
            return
        
        # Título de la sección
        fecha_formateada = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d').strftime('%d/%m/%Y')
        titulo_seccion = self.fuente_titulo.render(f"Corte de Caja - {fecha_formateada}", True, (0, 0, 0))
        titulo_rect = titulo_seccion.get_rect(center=(graf_x + graf_w // 2, graf_y + 30))
        surface.blit(titulo_seccion, titulo_rect)
        
        # División de pantalla: izquierda resumen, derecha gráfico
        mitad_ancho = graf_w // 2
        
        # Resumen de ventas - Lado izquierdo
        y_pos = graf_y + 80
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
            titulo_rect = titulo_estados.get_rect(center=(graf_x + mitad_ancho + mitad_ancho // 2, graf_y + 80))
            surface.blit(titulo_estados, titulo_rect)
            
            # Gráfico pastel para estados
            centro_x = graf_x + mitad_ancho + mitad_ancho // 2
            centro_y = graf_y + 180
            radio = 100
            
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
                pygame.draw.rect(surface, color, (centro_x - 100, leyenda_y + i * 30, 20, 20))
                porcentaje = monto / total_estados * 100
                texto = f"{estado}: ${monto:.2f} ({porcentaje:.1f}%)"
                lbl = font_normal.render(texto, True, (0, 0, 0))
                surface.blit(lbl, (centro_x - 70, leyenda_y + i * 30))
        
        # Productos más vendidos del día
        if self.corte_caja_datos['productos']:
            titulo_productos = font_titulo.render("Productos más vendidos del día", True, (0, 0, 100))
            y_productos = graf_y + graf_h - 220
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
                
                surface.blit(texto_nombre, (x_nombre, y_pos + i * 30))
                surface.blit(texto_cantidad, (x_cantidad, y_pos + i * 30))
                surface.blit(texto_total, (x_total, y_pos + i * 30))
        
        # Pie de página
        pie_corte = self.fuente_pie_pagina.render("Corte de Caja", True, (50, 50, 120))
        pie_rect = pie_corte.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
        surface.blit(pie_corte, pie_rect)
        
    def dibujar_inventario(self, surface):
        """Dibuja el reporte de inventario"""
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
            
            # Pie de página
            pie_inventario = self.fuente_pie_pagina.render("Reporte de Inventario", True, (50, 50, 120))
            pie_rect = pie_inventario.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
            surface.blit(pie_inventario, pie_rect)
            return
        
        # Título de la sección
        titulo_seccion = self.fuente_titulo.render(f"Inventario - {self.inventario_filtro}", True, (0, 0, 0))
        titulo_rect = titulo_seccion.get_rect(center=(graf_x + graf_w // 2, graf_y + 30))
        surface.blit(titulo_seccion, titulo_rect)
        
        # Encabezados de la tabla
        y_pos = graf_y + 80
        font_titulo = pygame.font.SysFont("Open Sans", int(0.04 * self.alto), bold=True)
        font_normal = pygame.font.SysFont("Open Sans", int(0.035 * self.alto))
        
        # Crear columnas
        col_widths = [int(0.1 * graf_w), int(0.35 * graf_w), int(0.15 * graf_w), int(0.15 * graf_w), int(0.25 * graf_w)]
        col_headers = ["ID", "Nombre", "Stock", "Unidad", "Tipo"]
        
        # Dibujar encabezados
        x_pos = graf_x + 20
        for i, header in enumerate(col_headers):
            pygame.draw.rect(surface, (220, 220, 255), (x_pos, y_pos, col_widths[i], 40))
            pygame.draw.rect(surface, (100, 100, 200), (x_pos, y_pos, col_widths[i], 40), 1)
            texto = font_titulo.render(header, True, (0, 0, 0))
            rect = texto.get_rect(center=(x_pos + col_widths[i]//2, y_pos + 20))
            surface.blit(texto, rect)
            x_pos += col_widths[i]
        
        # Calcular elementos a mostrar según paginación
        items_per_page = self.inventario_items_por_pagina
        start_idx = self.inventario_pagina_actual * items_per_page
        end_idx = min(start_idx + items_per_page, len(self.inventario_datos))
        
        # Dibujar filas
        y_pos += 40
        for i, item in enumerate(self.inventario_datos[start_idx:end_idx]):
            # Color de fondo alternado
            if i % 2 == 0:
                pygame.draw.rect(surface, (240, 240, 255), (graf_x + 20, y_pos, sum(col_widths), 40))
            
            # Color rojo para stock bajo o agotado
            stock_color = (0, 0, 0)
            if item['Stock'] == 0:
                stock_color = (255, 0, 0)  # Rojo para agotado
            elif item['Stock'] <= 10:
                stock_color = (255, 150, 0)  # Naranja para bajo
            
            # Dibujar datos
            x_pos = graf_x + 20
            cols = ["id", "Nombre", "Stock", "Unidad", "Tipo"]
            for j, col in enumerate(cols):
                valor = str(item.get(col, ""))
                texto = font_normal.render(valor, True, stock_color if col == "Stock" else (0, 0, 0))
                rect = texto.get_rect(midleft=(x_pos + 10, y_pos + 20))
                surface.blit(texto, rect)
                x_pos += col_widths[j]
            
            y_pos += 40
        
        # Botones de navegación
        if len(self.inventario_datos) > items_per_page:
            # Texto de paginación
            pagina_texto = font_normal.render(
                f"Página {self.inventario_pagina_actual + 1} de {(len(self.inventario_datos) - 1) // items_per_page + 1}", 
                True, (0, 0, 0)
            )
            rect = pagina_texto.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 40))
            surface.blit(pagina_texto, rect)
            
            # Botón anterior
            if self.inventario_pagina_actual > 0:
                pygame.draw.rect(surface, (220, 220, 220), self.boton_anterior_pagina, border_radius=8)
                texto = font_normal.render("Anterior", True, (0, 0, 0))
                rect = texto.get_rect(center=self.boton_anterior_pagina.center)
                surface.blit(texto, rect)
            
            # Botón siguiente
            if end_idx < len(self.inventario_datos):
                pygame.draw.rect(surface, (220, 220, 220), self.boton_siguiente_pagina, border_radius=8)
                texto = font_normal.render("Siguiente", True, (0, 0, 0))
                rect = texto.get_rect(center=self.boton_siguiente_pagina.center)
                surface.blit(texto, rect)
        
        # Estadísticas de inventario - pequeño resumen
        items_agotados = sum(1 for item in self.inventario_datos if item['Stock'] == 0)
        items_bajos = sum(1 for item in self.inventario_datos if 0 < item['Stock'] <= 10) 
        
        resumen_font = pygame.font.SysFont("Open Sans", int(0.03 * self.alto))
        resumen_texto = resumen_font.render(
            f"Total de items: {len(self.inventario_datos)} | Agotados: {items_agotados} | Stock bajo: {items_bajos}",
            True, (50, 50, 120)
        )
        rect = resumen_texto.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 70))
        surface.blit(resumen_texto, rect)
        
        # Pie de página
        pie_inventario = self.fuente_pie_pagina.render("Reporte de Inventario", True, (50, 50, 120))
        pie_rect = pie_inventario.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
        surface.blit(pie_inventario, pie_rect)
        
    def dibujar_pedidos(self, surface):
        """Dibuja el reporte de pedidos"""
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
            
            # Pie de página
            pie_pedidos = self.fuente_pie_pagina.render("Reporte de Pedidos", True, (50, 50, 120))
            pie_rect = pie_pedidos.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
            surface.blit(pie_pedidos, pie_rect)
            return
        
        # Título de la sección
        titulo_seccion = self.fuente_titulo.render(f"Pedidos - {self.pedidos_filtro}", True, (0, 0, 0))
        titulo_rect = titulo_seccion.get_rect(center=(graf_x + graf_w // 2, graf_y + 30))
        surface.blit(titulo_seccion, titulo_rect)
        
        # Encabezados de la tabla
        y_pos = graf_y + 80
        font_titulo = pygame.font.SysFont("Open Sans", int(0.036 * self.alto), bold=True)
        font_normal = pygame.font.SysFont("Open Sans", int(0.03 * self.alto))
        
        # Crear columnas (ajustamos para que quepan todas)
        col_widths = [
            int(0.07 * graf_w),  # ID
            int(0.2 * graf_w),   # Cliente
            int(0.13 * graf_w),  # Fecha Pedido
            int(0.13 * graf_w),  # Fecha Entrega
            int(0.12 * graf_w),  # Estado
            int(0.13 * graf_w),  # Total
            int(0.12 * graf_w),  # Días Proceso
        ]
        col_headers = ["ID", "Cliente", "Fecha Pedido", "Fecha Entrega", "Estado", "Total", "Días Proceso"]
        
        # Dibujar encabezados
        x_pos = graf_x + 20
        for i, header in enumerate(col_headers):
            pygame.draw.rect(surface, (220, 220, 255), (x_pos, y_pos, col_widths[i], 40))
            pygame.draw.rect(surface, (100, 100, 200), (x_pos, y_pos, col_widths[i], 40), 1)
            texto = font_titulo.render(header, True, (0, 0, 0))
            rect = texto.get_rect(center=(x_pos + col_widths[i]//2, y_pos + 20))
            surface.blit(texto, rect)
            x_pos += col_widths[i]
        
        # Calcular elementos a mostrar según paginación
        items_per_page = self.pedidos_items_por_pagina
        start_idx = self.pedidos_pagina_actual * items_per_page
        end_idx = min(start_idx + items_per_page, len(self.pedidos_datos))
        
        # Dibujar filas
        y_pos += 40
        for i, pedido in enumerate(self.pedidos_datos[start_idx:end_idx]):
            # Color de fondo alternado
            if i % 2 == 0:
                pygame.draw.rect(surface, (240, 240, 255), (graf_x + 20, y_pos, sum(col_widths), 40))
            
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
            
            # Formateamos fechas para mostrar
            fecha_pedido = str(pedido['Fecha_pedido'])
            fecha_entrega = str(pedido['Fecha_entrega'])
            if len(fecha_pedido) > 10:
                fecha_pedido = fecha_pedido[:10]  # Solo YYYY-MM-DD
            if len(fecha_entrega) > 10:
                fecha_entrega = fecha_entrega[:10]  # Solo YYYY-MM-DD
            
            # Dibujar datos
            x_pos = graf_x + 20
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
                
                # Color específico según el estado
                color = estado_color if col == "Estado" else (0, 0, 0)
                texto = font_normal.render(valor, True, color)
                rect = texto.get_rect(midleft=(x_pos + 10, y_pos + 20))
                surface.blit(texto, rect)
                x_pos += col_widths[j]
            
            y_pos += 40
        
        # Botones de navegación
        if len(self.pedidos_datos) > items_per_page:
            # Texto de paginación
            pagina_texto = font_normal.render(
                f"Página {self.pedidos_pagina_actual + 1} de {(len(self.pedidos_datos) - 1) // items_per_page + 1}", 
                True, (0, 0, 0)
            )
            rect = pagina_texto.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 40))
            surface.blit(pagina_texto, rect)
            
            # Botón anterior
            if self.pedidos_pagina_actual > 0:
                pygame.draw.rect(surface, (220, 220, 220), self.boton_anterior_pagina_pedidos, border_radius=8)
                texto = font_normal.render("Anterior", True, (0, 0, 0))
                rect = texto.get_rect(center=self.boton_anterior_pagina_pedidos.center)
                surface.blit(texto, rect)
            
            # Botón siguiente
            if end_idx < len(self.pedidos_datos):
                pygame.draw.rect(surface, (220, 220, 220), self.boton_siguiente_pagina_pedidos, border_radius=8)
                texto = font_normal.render("Siguiente", True, (0, 0, 0))
                rect = texto.get_rect(center=self.boton_siguiente_pagina_pedidos.center)
                surface.blit(texto, rect)
        
        # Estadísticas de pedidos - pequeño resumen
        pedidos_pendientes = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Pendiente' or p['Estado'] == 'En proceso')
        pedidos_listos = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Listo')
        pedidos_entregados = sum(1 for p in self.pedidos_datos if p['Estado'] == 'Entregado')
        
        resumen_font = pygame.font.SysFont("Open Sans", int(0.03 * self.alto))
        resumen_texto = resumen_font.render(
            f"Total de pedidos: {len(self.pedidos_datos)} | Pendientes: {pedidos_pendientes} | Listos: {pedidos_listos} | Entregados: {pedidos_entregados}",
            True, (50, 50, 120)
        )
        rect = resumen_texto.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 70))
        surface.blit(resumen_texto, rect)
        
        # Pie de página
        pie_pedidos = self.fuente_pie_pagina.render("Reporte de Pedidos", True, (50, 50, 120))
        pie_rect = pie_pedidos.get_rect(center=(graf_x + graf_w // 2, graf_y + graf_h - 15))
        surface.blit(pie_pedidos, pie_rect)

    def handle_event(self, event):
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
            
            # Verificar clic en botón agregar
            if self.boton_agregar_rect and self.boton_agregar_rect.collidepoint(mouse_pos):
                self.on_agregar_click()
                return
                
            # Verificar clic en botón PDF
            if self.boton_pdf_rect and self.boton_pdf_rect.collidepoint(mouse_pos):
                self.descargar_pdf()
                return
                
            # Verificar clic en selector de fecha o botones de cambio de fecha (solo en CORTE CAJA)
            if self.opcion_seleccionada == "CORTE CAJA":
                if self.selector_fecha_rect.collidepoint(mouse_pos):
                    self.selector_fecha_activo = True
                    return
                    
                if self.boton_fecha_anterior.collidepoint(mouse_pos):
                    # Cambiar a día anterior
                    fecha_actual = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d')
                    dia_anterior = fecha_actual - datetime.timedelta(days=1)
                    self.fecha_seleccionada = dia_anterior.strftime('%Y-%m-%d')
                    self.cargar_corte_caja(self.fecha_seleccionada)
                    return
                    
                if self.boton_fecha_siguiente.collidepoint(mouse_pos):
                    # Cambiar a día siguiente
                    fecha_actual = datetime.datetime.strptime(self.fecha_seleccionada, '%Y-%m-%d')
                    dia_siguiente = fecha_actual + datetime.timedelta(days=1)
                    # No permitir seleccionar fechas futuras
                    if dia_siguiente.date() <= datetime.datetime.now().date():
                        self.fecha_seleccionada = dia_siguiente.strftime('%Y-%m-%d')
                        self.cargar_corte_caja(self.fecha_seleccionada)
                    return
            
            # Verificar clic en filtros de inventario
            elif self.opcion_seleccionada == "INVENTARIO":
                for i, rect in enumerate(self.botones_filtro_inventario):
                    if rect.collidepoint(mouse_pos):
                        self.inventario_filtro = self.filtros_inventario[i]
                        self.inventario_pagina_actual = 0  # Reiniciar paginación
                        self.cargar_inventario()
                        return
                
                # Verificar clic en botones de paginación
                if self.boton_anterior_pagina.collidepoint(mouse_pos) and self.inventario_pagina_actual > 0:
                    self.inventario_pagina_actual -= 1
                    return
                    
                if self.boton_siguiente_pagina.collidepoint(mouse_pos):
                    items_per_page = self.inventario_items_por_pagina
                    if (self.inventario_pagina_actual + 1) * items_per_page < len(self.inventario_datos):
                        self.inventario_pagina_actual += 1
                    return
                        
            # Verificar clic en filtros de pedidos
            elif self.opcion_seleccionada == "PEDIDOS":
                for i, rect in enumerate(self.botones_filtro_pedidos):
                    if rect.collidepoint(mouse_pos):
                        self.pedidos_filtro = self.filtros_pedidos[i]
                        self.pedidos_pagina_actual = 0  # Reiniciar paginación
                        self.cargar_pedidos()
                        return
                
                # Verificar clic en botones de paginación
                if self.boton_anterior_pagina_pedidos.collidepoint(mouse_pos) and self.pedidos_pagina_actual > 0:
                    self.pedidos_pagina_actual -= 1
                    return
                    
                if self.boton_siguiente_pagina_pedidos.collidepoint(mouse_pos):
                    items_per_page = self.pedidos_items_por_pagina
                    if (self.pedidos_pagina_actual + 1) * items_per_page < len(self.pedidos_datos):
                        self.pedidos_pagina_actual += 1
                    return
                        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            self.agregar_hover = self.boton_agregar_rect and self.boton_agregar_rect.collidepoint(mouse_pos)
            self.pdf_hover = self.boton_pdf_rect and self.boton_pdf_rect.collidepoint(mouse_pos)

    def on_agregar_click(self):
        print(f"Botón 'Agregar' presionado en opción: {self.opcion_seleccionada}")

    def descargar_pdf(self):
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
        """Genera un PDF específico para el corte de caja"""
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
            ["Total de Ventas", f"${float(self.corte_caja_datos['ventas']['total_ventas'] or 0):.2f}"],
            ["Saldo Inicial", f"${self.corte_caja_datos['saldo_inicial']:.2f}"],
            ["Saldo Final", f"${self.corte_caja_datos['saldo_final']:.2f}"]
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
        
        # Datos de métodos de pago
        if self.corte_caja_datos['metodos_pago']:
            elements.append(Paragraph("Métodos de Pago:", styles['Heading2']))
            
            datos_metodos = [["Método", "Cantidad", "Total"]]
            for metodo in self.corte_caja_datos['metodos_pago']:
                datos_metodos.append([
                    metodo['MetodoPago'],
                    f"{metodo['cantidad']}",
                    f"${float(metodo['total']):.2f}"
                ])
                
            tabla_metodos = Table(datos_metodos, colWidths=[200, 150, 150])
            tabla_metodos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (2, -1), colors.beige),
                ('GRID', (0, 0), (2, -1), 1, colors.black)
            ]))
            elements.append(tabla_metodos)
            elements.append(Paragraph(" ", styles['Normal']))  # Espacio
            
        # Datos de gastos
        if self.corte_caja_datos['gastos']:
            elements.append(Paragraph("Gastos:", styles['Heading2']))
            
            datos_gastos = [["Concepto", "Monto"]]
            for gasto in self.corte_caja_datos['gastos']:
                datos_gastos.append([
                    gasto['Concepto'],
                    f"${float(gasto['Monto']):.2f}"
                ])
                
            tabla_gastos = Table(datos_gastos, colWidths=[300, 200])
            tabla_gastos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (1, -1), colors.beige),
                ('GRID', (0, 0), (1, -1), 1, colors.black)
            ]))
            elements.append(tabla_gastos)
            elements.append(Paragraph(" ", styles['Normal']))  # Espacio
            
        # Datos de productos vendidos
        if self.corte_caja_datos['productos']:
            elements.append(Paragraph("Productos Vendidos:", styles['Heading2']))
            
            datos_productos = [["Producto", "Cantidad", "Total"]]
            for producto in self.corte_caja_datos['productos']:
                datos_productos.append([
                    producto['Nombre_prod'],
                    f"{producto['cantidad']}",
                    f"${float(producto['total']):.2f}"
                ])
                
            tabla_productos = Table(datos_productos, colWidths=[250, 100, 150])
            tabla_productos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (2, -1), colors.beige),
                ('GRID', (0, 0), (2, -1), 1, colors.black)
            ]))
            elements.append(tabla_productos)
        
        # Generar el PDF
        doc.build(elements)
        
    def generar_pdf_inventario(self, nombre_pdf):
        """Genera un PDF del reporte de inventario"""
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
        items_agotados = sum(1 for item in self.inventario_datos if item['Stock'] == 0)
        items_bajos = sum(1 for item in self.inventario_datos if 0 < item['Stock'] <= 10) 
        
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
                str(item['Stock']),
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
            ('GRID', (0, 0), (4, -1), 1, colors.black),
            # Colores para stock bajo o agotado
            ('TEXTCOLOR', (2, 1), (2, -1), colors.black)  # Por defecto negro
        ]))
        
        # Aplicar colores específicos a filas con stock bajo o agotado
        for i, item in enumerate(self.inventario_datos):
            if item['Stock'] == 0:
                tabla_inventario.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i+1), (2, i+1), colors.red)
                ]))
            elif item['Stock'] <= 10:
                tabla_inventario.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i+1), (2, i+1), colors.orange)
                ]))
        
        elements.append(tabla_inventario)
        
        # Generar el PDF
        doc.build(elements)
        
    def generar_pdf_pedidos(self, nombre_pdf):
        """Genera un PDF del reporte de pedidos"""
        if not self.pedidos_datos:
            return
            
        # Crear documento
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        titulo_style = styles['Title']
        
        # Títuloss
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
                fecha_pedido = fecha_pedido[:10]  # Solo YYYY-MM-DD
            if len(fecha_entrega) > 10:
                fecha_entrega = fecha_entrega[:10]  # Solo YYYY-MM-DD
                
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
            # Tamaño de fuente más pequeño para que quepan todos los datos
            ('FONTSIZE', (0, 0), (6, -1), 9)
        ]))
        
# Aplicar colores específicos a filas según estado
        for i, pedido in enumerate(self.pedidos_datos):
            if pedido['Estado'] == 'Pendiente':
                tabla_pedidos.setStyle(TableStyle([
                    ('TEXTCOLOR', (4, i+1), (4, i+1), colors.orange)
                ]))
            elif pedido['Estado'] == 'En proceso':
                tabla_pedidos.setStyle(TableStyle([
                    ('TEXTCOLOR', (4, i+1), (4, i+1), colors.blue)
                ]))
            elif pedido['Estado'] == 'Listo':
                tabla_pedidos.setStyle(TableStyle([
                    ('TEXTCOLOR', (4, i+1), (4, i+1), colors.green)
                ]))
            elif pedido['Estado'] == 'Entregado':
                tabla_pedidos.setStyle(TableStyle([
                    ('TEXTCOLOR', (4, i+1), (4, i+1), colors.grey)
                ]))
        
        elements.append(tabla_pedidos)
        
        # Generar el PDF
        doc.build(elements)