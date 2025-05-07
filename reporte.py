
import pygame
from conexion import Conexion
import math
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

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

        self.botones_opciones = ["VENTAS", "PRODUCTOS", "HORARIOS"]
        self.opcion_seleccionada = self.botones_opciones[0]

        # Calcula posiciones y tamaños relativos para los botones
        self.boton_rects = [
            pygame.Rect(
                self.x + int(0.013 * self.ancho) + i * int(0.11 * self.ancho),
                self.y + int(0.11 * self.alto),
                int(0.10 * self.ancho),
                int(0.06 * self.alto)
            ) for i in range(len(self.botones_opciones))
        ]
        self.color_boton = (220, 220, 220)
        self.color_boton_activo = (180, 180, 255)

        self.boton_agregar_rect = pygame.Rect(
            self.x + int(0.013 * self.ancho) + len(self.botones_opciones) * int(0.11 * self.ancho) + int(0.012 * self.ancho),
            self.y + int(0.11 * self.alto),
            int(0.09 * self.ancho),
            int(0.06 * self.alto)
        )
        self.color_boton_agregar = (100, 200, 100)
        self.color_boton_agregar_hover = (80, 180, 80)
        self.agregar_hover = False

        self.boton_pdf_rect = pygame.Rect(
            self.x + int(0.013 * self.ancho) + len(self.botones_opciones) * int(0.11 * self.ancho) + int(0.18 * self.ancho),
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

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for i, rect in enumerate(self.boton_rects):
                if rect and rect.collidepoint(mouse_pos):
                    self.opcion_seleccionada = self.botones_opciones[i]
                    if self.opcion_seleccionada == "VENTAS":
                        self.cargar_ventas_por_dia()
                    elif self.opcion_seleccionada == "PRODUCTOS":
                        self.cargar_productos_mas_vendidos()
                    elif self.opcion_seleccionada == "HORARIOS":
                        self.cargar_ventas_por_hora()
                    return
            if self.boton_agregar_rect and self.boton_agregar_rect.collidepoint(mouse_pos):
                self.on_agregar_click()
                return
            if self.boton_pdf_rect and self.boton_pdf_rect.collidepoint(mouse_pos):
                self.descargar_pdf()
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
        elif self.opcion_seleccionada == "PRODUCTOS":
            self.cargar_productos_mas_vendidos()
            self.dibujar_grafica_pastel_productos(temp_surface)
            datos = self.productos_mas_vendidos
            encabezado = ["Producto", "Unidades"]
            nombre_pdf = "reporte_productos.pdf"
            nombre_img = "grafica_productos.png"
        elif self.opcion_seleccionada == "HORARIOS":
            self.cargar_ventas_por_hora()
            self.dibujar_grafica_lineas_horarios(temp_surface)
            datos = [(str(h), self.ventas_por_hora[h]) for h in range(24)]
            encabezado = ["Hora", "Unidades"]
            nombre_pdf = "reporte_horarios.pdf"
            nombre_img = "grafica_horarios.png"
        else:
            return

        pygame.image.save(temp_surface, nombre_img)
        self.generar_pdf(nombre_pdf, nombre_img, encabezado, datos)
        os.remove(nombre_img)
        print(f"PDF generado: {nombre_pdf}")

    def generar_pdf(self, nombre_pdf, nombre_img, encabezado, datos):
        c = canvas.Canvas(nombre_pdf, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "Reporte " + self.opcion_seleccionada.title())
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
