
import pygame
from conexion import Conexion

class InputBox:
    def __init__(self, x, y, w, h, text='', font=None, numeric=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.font = font or pygame.font.SysFont("Open Sans", 24)
        self.txt_surface = self.font.render(text, True, (0, 0, 0))
        self.active = False
        self.numeric = numeric

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
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
                self.txt_surface = self.font.render(self.text, True, (0, 0, 0))

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_value(self):
        return self.text

class almacen:
    def __init__(self, x, y, ancho, alto):
        pygame.font.init()
        self.FONDO = (241, 236, 227)
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

        # Fuentes escaladas
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", int(self.alto * 0.08), bold=True)
        self.color_texto = (0, 0, 0)

        self.botones_opciones = ["INSUMOS", "MATERIA PRIMA"]
        self.opcion_seleccionada = self.botones_opciones[0]
        self.fuente_boton = pygame.font.SysFont("Open Sans", int(self.alto * 0.045), bold=True)

        # Botones de opciones y agregar
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

        self.boton_agregar_rect = pygame.Rect(
            self.x + self.ancho - self.boton_width - self.boton_margin,
            self.y + int(self.alto * 0.11),
            self.boton_width, self.boton_height
        )
        self.color_boton_agregar = (100, 200, 100)
        self.color_boton_agregar_hover = (80, 180, 80)
        self.fuente_boton_agregar = pygame.font.SysFont("Open Sans", int(self.alto * 0.045), bold=True)
        self.agregar_hover = False

        self.busqueda_activa = False
        self.busqueda_texto = ""
        self.NEGRO = (0, 0, 0)
        self.fuente_busqueda = pygame.font.SysFont("Open Sans", int(self.alto * 0.045))

        self.fuente_tabla = pygame.font.SysFont("Open Sans", int(self.alto * 0.04))
        self.color_tabla_header = (200, 200, 255)
        self.color_tabla_row = (255, 255, 255)
        self.color_tabla_border = (180, 180, 180)

        # Carga inicial de datos
        self.datos_tabla = []
        self.cargar_datos_tabla()

        # Formulario gráfico
        self.mostrando_formulario = False
        self.formulario_boxes = []
        self.formulario_labels = []
        self.formulario_btn_guardar = None
        self.formulario_btn_cancelar = None
        self.formulario_mensaje = ""

    def cargar_datos_tabla(self):
        conexion = Conexion()
        texto = self.busqueda_texto.strip().lower()
        if self.opcion_seleccionada == "INSUMOS":
            query = """
                SELECT Nombre AS nombre, 
                       'Insumo' AS categoria, 
                       Precio AS precio, 
                       Cantidad AS cantidad, 
                       Estado AS estado
                FROM Insumo
                WHERE Estado IN ('Disponible', 'Agotado', 'Descontinuado')
            """
            params = ()
            if texto:
                query += " AND LOWER(Nombre) LIKE %s"
                params = (f"%{texto}%",)
        else:  # MATERIA PRIMA
            query = """
                SELECT Nombre AS nombre, 
                       'Materia Prima' AS categoria, 
                       Precio AS precio, 
                       Cantidad AS cantidad, 
                       Estado AS estado
                FROM MateriaPrima
                WHERE Estado IN ('Disponible', 'Agotado', 'Descontinuado')
            """
            params = ()
            if texto:
                query += " AND LOWER(Nombre) LIKE %s"
                params = (f"%{texto}%",)
        self.datos_tabla = conexion.consultar(query, params)

    def dibujar_punto_venta(self, surface):
        # Fondo principal
        pygame.draw.rect(surface, self.FONDO, (self.x, self.y, self.ancho, self.alto))
        # Título
        titulo = self.fuente_titulo.render("Almacen", True, self.color_texto)
        surface.blit(titulo, (self.x + int(self.ancho * 0.02), self.y + int(self.alto * 0.03)))

        # Campo de búsqueda
        busq_x = self.x + int(self.ancho * 0.02)
        busq_y = self.y + int(self.alto * 0.11)
        busq_w = int(self.ancho * 0.35)
        busq_h = self.boton_height
        self.dibujar_campo_busqueda(surface, busq_x, busq_y, busq_w, busq_h)

        # Botones
        for i, rect in enumerate(self.boton_rects):
            color = self.color_boton_activo if self.opcion_seleccionada == self.botones_opciones[i] else self.color_boton
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto_boton = self.fuente_boton.render(self.botones_opciones[i], True, self.color_texto)
            text_rect = texto_boton.get_rect(center=rect.center)
            surface.blit(texto_boton, text_rect)

        color_agregar = self.color_boton_agregar_hover if self.agregar_hover else self.color_boton_agregar
        pygame.draw.rect(surface, color_agregar, self.boton_agregar_rect, border_radius=8)
        texto_agregar = self.fuente_boton_agregar.render("Agregar", True, (255, 255, 255))
        text_rect_agregar = texto_agregar.get_rect(center=self.boton_agregar_rect.center)
        surface.blit(texto_agregar, text_rect_agregar)

        # Tabla
        tabla_x = self.x + int(self.ancho * 0.03)
        tabla_y = self.y + int(self.alto * 0.23)
        tabla_width = int(self.ancho * 0.94)
        tabla_row_height = int(self.alto * 0.07)
        self.dibujar_tabla(surface, tabla_x, tabla_y, tabla_width, tabla_row_height, self.datos_tabla)

        if self.mostrando_formulario:
            self.dibujar_formulario_agregar(surface)

    def dibujar_tabla(self, surface, x, y, width, row_height, datos):
        columnas = ["Nombre", "Categoría", "Precio", "Cantidad", "Estado"]
        col_widths = [
            int(width*0.28), int(width*0.21), int(width*0.16), int(width*0.16), int(width*0.16)
        ]

        col_x = x
        for i, col in enumerate(columnas):
            pygame.draw.rect(surface, self.color_tabla_header, (col_x, y, col_widths[i], row_height))
            pygame.draw.rect(surface, self.color_tabla_border, (col_x, y, col_widths[i], row_height), 2)
            texto = self.fuente_tabla.render(col, True, self.NEGRO)
            text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, y + row_height // 2))
            surface.blit(texto, text_rect)
            col_x += col_widths[i]

        fila_y = y + row_height
        for fila in datos:
            col_x = x
            for i, key in enumerate(["nombre", "categoria", "precio", "cantidad", "estado"]):
                pygame.draw.rect(surface, self.color_tabla_row, (col_x, fila_y, col_widths[i], row_height))
                pygame.draw.rect(surface, self.color_tabla_border, (col_x, fila_y, col_widths[i], row_height), 1)
                valor = fila[key]
                if key == "precio":
                    valor = f"${valor:.2f}"
                texto = self.fuente_tabla.render(str(valor), True, self.NEGRO)
                text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, fila_y + row_height // 2))
                surface.blit(texto, text_rect)
                col_x += col_widths[i]
            fila_y += row_height

    def dibujar_campo_busqueda(self, surface, x, y, w, h):
        color_fondo = (255, 255, 255)
        color_borde = (100, 100, 100) if self.busqueda_activa else (180, 180, 180)
        pygame.draw.rect(surface, color_fondo, (x, y, w, h), border_radius=10)
        pygame.draw.rect(surface, color_borde, (x, y, w, h), 2, border_radius=10)
        texto = self.busqueda_texto if self.busqueda_texto else "Buscar producto..."
        color_texto = self.NEGRO if self.busqueda_texto else (150, 150, 150)
        render = self.fuente_busqueda.render(texto, True, color_texto)
        surface.blit(render, (x + 10, y + (h - render.get_height()) // 2))

    def handle_event(self, event):
        if self.mostrando_formulario:
            for box in self.formulario_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.formulario_btn_guardar and self.formulario_btn_guardar.collidepoint(event.pos):
                    self.guardar_formulario_agregar()
                elif self.formulario_btn_cancelar and self.formulario_btn_cancelar.collidepoint(event.pos):
                    self.mostrando_formulario = False
                    self.formulario_mensaje = ""
                return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.boton_rects):
                if rect.collidepoint(mouse_pos):
                    self.opcion_seleccionada = self.botones_opciones[i]
                    self.cargar_datos_tabla()
                    return
            if self.boton_agregar_rect.collidepoint(mouse_pos):
                self.mostrar_formulario_agregar()
                return
            busq_x = self.x + int(self.ancho * 0.02)
            busq_y = self.y + int(self.alto * 0.11)
            busq_w = int(self.ancho * 0.35)
            busq_h = self.boton_height
            busq_rect = pygame.Rect(busq_x, busq_y, busq_w, busq_h)
            if busq_rect.collidepoint(mouse_pos):
                self.busqueda_activa = True
            else:
                self.busqueda_activa = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.agregar_hover = self.boton_agregar_rect.collidepoint(mouse_pos)
        elif event.type == pygame.KEYDOWN and self.busqueda_activa:
            if event.key == pygame.K_BACKSPACE:
                self.busqueda_texto = self.busqueda_texto[:-1]
                self.cargar_datos_tabla()
            elif event.key == pygame.K_RETURN:
                self.busqueda_activa = False
            elif event.key == pygame.K_ESCAPE:
                self.busqueda_texto = ""
                self.cargar_datos_tabla()
            else:
                if len(self.busqueda_texto) < 30 and event.unicode.isprintable():
                    self.busqueda_texto += event.unicode
                    self.cargar_datos_tabla()

    def dibujar_formulario_agregar(self, surface):
        # Fondo semitransparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (self.x, self.y))

        # Ventana del formulario
        form_w = int(self.ancho * 0.5)
        form_h = int(self.alto * 0.9)
        form_x = self.x + (self.ancho - form_w) // 2
        form_y = self.y + (self.alto - form_h) // 2
        pygame.draw.rect(surface, (255, 255, 255), (form_x, form_y, form_w, form_h), border_radius=12)
        pygame.draw.rect(surface, (100, 100, 200), (form_x, form_y, form_w, form_h), 3, border_radius=12)

        # Título
        font_title = pygame.font.SysFont("Open Sans", int(self.alto * 0.06), bold=True)
        titulo = "Agregar Insumo" if self.opcion_seleccionada == "INSUMOS" else "Agregar Materia Prima"
        text_title = font_title.render(titulo, True, (0, 0, 0))
        title_x = form_x + (form_w - text_title.get_width()) // 2  # Centered title
        surface.blit(text_title, (title_x, form_y + 20))

        # Espaciado y posicionamiento
        label_x = form_x + 30
        input_x = form_x + int(form_w * 0.45)  # Fixed position for inputs
        start_y = form_y + 80
        field_height = 50

        # Labels y cajas de texto
        for i, (lbl, _) in enumerate(self.formulario_labels):
            # Actualizar la posición vertical para cada par de label/input
            current_y = start_y + i * (field_height + 10)
            
            # Dibujar el label alineado a la izquierda
            surface.blit(lbl, (label_x, current_y + (field_height - lbl.get_height()) // 2))
            
            # Actualizar la posición del cuadro de texto y dibujarlo
            self.formulario_boxes[i].rect.x = input_x
            self.formulario_boxes[i].rect.y = current_y
            self.formulario_boxes[i].draw(surface)

        # Botones - al final del formulario
        buttons_y = start_y + len(self.formulario_labels) * (field_height + 10) + 20
        button_width = int(form_w * 0.2)
        button_height = int(self.alto * 0.06)
        
        # Actualizar posiciones de los botones
        self.formulario_btn_guardar = pygame.Rect(
            form_x + int(form_w * 0.25) - button_width // 2,
            buttons_y,
            button_width,
            button_height
        )
        
        self.formulario_btn_cancelar = pygame.Rect(
            form_x + int(form_w * 0.75) - button_width // 2,
            buttons_y,
            button_width,
            button_height
        )

        # Dibujar botones
        font_btn = pygame.font.SysFont("Open Sans", int(self.alto * 0.045), bold=True)
        pygame.draw.rect(surface, (100, 200, 100), self.formulario_btn_guardar, border_radius=8)
        pygame.draw.rect(surface, (200, 100, 100), self.formulario_btn_cancelar, border_radius=8)
        
        txt_guardar = font_btn.render("Guardar", True, (255, 255, 255))
        txt_cancelar = font_btn.render("Cancelar", True, (255, 255, 255))
        
        # Centrar el texto en los botones
        guardar_text_x = self.formulario_btn_guardar.x + (self.formulario_btn_guardar.width - txt_guardar.get_width()) // 2
        guardar_text_y = self.formulario_btn_guardar.y + (self.formulario_btn_guardar.height - txt_guardar.get_height()) // 2
        
        cancelar_text_x = self.formulario_btn_cancelar.x + (self.formulario_btn_cancelar.width - txt_cancelar.get_width()) // 2
        cancelar_text_y = self.formulario_btn_cancelar.y + (self.formulario_btn_cancelar.height - txt_cancelar.get_height()) // 2
        
        surface.blit(txt_guardar, (guardar_text_x, guardar_text_y))
        surface.blit(txt_cancelar, (cancelar_text_x, cancelar_text_y))

        # Mensaje de error o éxito
        if self.formulario_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(self.alto * 0.035))
            color = (200, 0, 0) if "inválido" in self.formulario_mensaje or "obligatorio" in self.formulario_mensaje else (0, 120, 0)
            msg = font_msg.render(self.formulario_mensaje, True, color)
            surface.blit(msg, (form_x + (form_w - msg.get_width()) // 2, form_y + form_h - 50))  # Centered message

    # --- AJUSTA EL FORMULARIO PARA USAR LOS CAMPOS CORRECTOS ---
    def mostrar_formulario_agregar(self):
        self.mostrando_formulario = True
        font = pygame.font.SysFont("Open Sans", int(self.alto * 0.045))
        x = self.x + int(self.ancho * 0.22)
        y = self.y + int(self.alto * 0.20)
        if self.opcion_seleccionada == "INSUMOS":
            labels = [
                "Nombre", "Precio", "stock_minimo", "Descripción", "Cantidad",
                "Entrada (YYYY-MM-DD)", "Caducidad (YYYY-MM-DD)"
            ]
        else:
            labels = ["Nombre", "Precio", "stock_minimo", "Descripción", "Cantidad"]
        self.formulario_labels = []
        self.formulario_boxes = []
        for i, label in enumerate(labels):
            lbl = font.render(label + ":", True, (0, 0, 0))
            self.formulario_labels.append((lbl, (x, y + 40 + i * int(self.alto * 0.07))))
            numeric = label in ["Precio", "Cantidad", "stock_minimo"]
            box = InputBox(
                x + int(self.ancho * 0.18),
                y + 35 + i * int(self.alto * 0.07),
                int(self.ancho * 0.13),
                int(self.alto * 0.05),
                font=font,
                numeric=numeric
            )
            self.formulario_boxes.append(box)
        # Botones
        self.formulario_btn_guardar = pygame.Rect(
            x, y + 60 + len(labels) * int(self.alto * 0.06),
            int(self.ancho * 0.11), int(self.alto * 0.06)
        )
        self.formulario_btn_cancelar = pygame.Rect(
            x + int(self.ancho * 0.18), y + 60 + len(labels) * int(self.alto * 0.06),
            int(self.ancho * 0.11), int(self.alto * 0.06)
        )
        self.formulario_mensaje = ""

    def guardar_formulario_agregar(self):
        valores = [box.get_value().strip() for box in self.formulario_boxes]
        if self.opcion_seleccionada == "INSUMOS":
            # Esperado: Nombre, Precio, stock_minimo, Descripción, Cantidad, Fecha Entrada, Fecha Caducidad
            if not valores[0] or not valores[1] or not valores[2] or not valores[4] or not valores[5] or not valores[6]:
                self.formulario_mensaje = "Todos los campos son obligatorios."
                return
            nombre, precio, stock_minimo, descripcion, cantidad, fecha_entrada, fecha_caducidad = valores
            try:
                precio = float(precio)
                stock_minimo = int(stock_minimo)
                cantidad = int(cantidad)
                from datetime import datetime
                fecha_entrada = datetime.strptime(fecha_entrada, "%Y-%m-%d").date()
                fecha_caducidad = datetime.strptime(fecha_caducidad, "%Y-%m-%d").date()
            except ValueError:
                self.formulario_mensaje = "Formato de fecha inválido. Usa YYYY-MM-DD."
                return
            except Exception:
                self.formulario_mensaje = "Datos numéricos inválidos."
                return
            estado = "Disponible"
            iva = 0.16
            conexion = Conexion()
            insert = """
                INSERT INTO Insumo
                (Nombre, Precio, stock_minimo, Descripcion, Cantidad, IVA, Estado, FK_ID_TipoInsumo, fecha_entrada, fecha_caducidad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s, %s)
            """
            conexion.conectar()
            conexion.cursor.execute(insert, (
                nombre, precio, stock_minimo, descripcion, cantidad, iva, estado, fecha_entrada, fecha_caducidad
            ))
            conexion.conn.commit()
            conexion.cerrar()
            self.formulario_mensaje = f"Insumo '{nombre}' agregado."
            self.cargar_datos_tabla()
            self.mostrando_formulario = False
            self.formulario_mensaje = ""
        else:
            # Materia Prima igual que antes
            if not valores[0] or not valores[1] or not valores[2]:
                self.formulario_mensaje = "Nombre, precio y stock mínimo son obligatorios."
                return
            nombre, precio, stock_minimo, descripcion, cantidad = valores
            try:
                precio = float(precio)
                stock_minimo = int(stock_minimo)
                cantidad = int(cantidad)
            except Exception:
                self.formulario_mensaje = "Datos numéricos inválidos."
                return
            estado = "Disponible"
            iva = 0.16
            conexion = Conexion()
            insert = """
                INSERT INTO MateriaPrima (Nombre, Precio, stock_minimo, Descripcion, Cantidad, IVA, Estado, FK_ID_MedidaCantidad, FK_ID_TipoMateriaPrima)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1, 1)
            """
            conexion.conectar()
            conexion.cursor.execute(insert, (nombre, precio, stock_minimo, descripcion, cantidad, iva, estado))
            conexion.conn.commit()
            conexion.cerrar()
            self.formulario_mensaje = f"Materia Prima '{nombre}' agregada."
            self.cargar_datos_tabla()
            self.mostrando_formulario = False
            self.formulario_mensaje = ""
