"""
Sistema de Gestión de Pedidos para Panadería
------------------------------------------
Sistema desarrollado en Pygame para administrar pedidos personalizados:
- Crear nuevos pedidos por adelantado
- Gestionar pedidos pendientes
- Procesar entregas de pedidos listos
- Seguimiento de fechas de entrega
- Registro automático de fechas

Características principales:
- Interfaz dual: NUEVO (crear) y RECOGER (entregar)
- Búsqueda de pedidos por cliente
- Creación de productos sobre la marcha
- Validación de datos completa
- Integración con sistema de clientes y productos

Versión: 1.0
"""

import pygame
from receta import Conexion
from datetime import datetime

class InputBox:
    """
    Campo de entrada de texto personalizado para Pygame
    
    Permite crear campos con validación numérica opcional
    y manejo completo de eventos.
    
    Attributes:
        rect (pygame.Rect): Posición y dimensiones del campo
        text (str): Texto actual del campo
        numeric (bool): Si True, solo acepta números y punto decimal
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
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.font = font or pygame.font.SysFont("Open Sans", 24)
        self.txt_surface = self.font.render(text, True, (0, 0, 0))
        self.active = False
        self.numeric = numeric
        

    def handle_event(self, event):
        """
        Maneja eventos de mouse y teclado para el campo
        
        Args:
            event (pygame.event.Event): Evento de Pygame
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Activar/desactivar campo según clic
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
                    # Validar entrada según tipo de campo
                    if self.numeric:
                        if event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.text):
                            self.text += event.unicode
                    else:
                        if len(self.text) < 50 and event.unicode.isprintable():
                            self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, (0, 0, 0))

    def draw(self, screen):
        """
        Dibuja el campo en la pantalla
        
        Args:
            screen (pygame.Surface): Superficie donde dibujar
        """
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_value(self):
        """
        Obtiene el valor actual del campo
        
        Returns:
            str: Texto actual del campo
        """
        return self.text

class Pedido:    
    """
    Clase principal para la gestión de pedidos
    
    Maneja dos vistas principales:
    1. NUEVO: Crear nuevos pedidos
    2. RECOGER: Gestionar entregas
    
    Attributes:
        x, y (int): Posición de la interfaz
        ancho, alto (int): Dimensiones de la interfaz
        opcion_seleccionada (str): Vista actual ("NUEVO" o "RECOGER")
        datos_tabla (list): Pedidos actualmente mostrados
        mostrando_formulario (bool): Estado del formulario de creación
        mensaje_alerta (str): Mensaje temporal para el usuario
    """

    def __init__(self, x, y, ancho, alto):
        """
        Inicializa el sistema de gestión de pedidos
        
        Args:
            x, y (int): Posición de la interfaz
            ancho, alto (int): Dimensiones de la interfaz
        """
        pygame.font.init()
        self.FONDO = (241, 236, 227)
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

        # Fuentes escaladas
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", int(self.alto * 0.08), bold=True)
        self.color_texto = (0, 0, 0)

        # Configuración de navegación
        self.botones_opciones = ["NUEVO", "RECOGER"]
        self.opcion_seleccionada = self.botones_opciones[0]
        self.fuente_boton = pygame.font.SysFont("Open Sans", int(self.alto * 0.045), bold=True)

        # Configuración de botones
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

        # Botón principal (crear/entregar)
        self.boton_agregar_rect = pygame.Rect(
            self.x + self.ancho - self.boton_width - self.boton_margin,
            self.y + int(self.alto * 0.11),
            self.boton_width, self.boton_height
        )
        self.color_boton_agregar = (100, 200, 100)
        self.color_boton_agregar_hover = (80, 180, 80)
        self.fuente_boton_agregar = pygame.font.SysFont("Open Sans", int(self.alto * 0.045), bold=True)
        self.agregar_hover = False

        # Configuración de búsqueda
        self.busqueda_activa = False
        self.busqueda_texto = ""
        self.NEGRO = (0, 0, 0)
        self.fuente_busqueda = pygame.font.SysFont("Open Sans", int(self.alto * 0.045))

        # Configuración de tabla
        self.fuente_tabla = pygame.font.SysFont("Open Sans", int(self.alto * 0.04))
        self.color_tabla_header = (200, 200, 255)
        self.color_tabla_row = (255, 255, 255)
        self.color_tabla_border = (180, 180, 180)
        
        # Datos y formularios
        self.datos_tabla = []
        self.cargar_datos_tabla()
        
        # Estado del formulario
        self.mostrando_formulario = False
        self.formulario_boxes = []
        self.formulario_labels = []
        self.formulario_btn_guardar = None
        self.formulario_btn_cancelar = None
        self.formulario_mensaje = ""
        
        # Estado temporal
        self.productos_pedido = []
        
        # Sistema de alertas
        self.mensaje_alerta = ""
        self.tiempo_alerta = 0
        
        # Evitar errores de referencia
        self.formulario_btn_agregar_producto = None

        # Nuevo botón para editar fecha en vista NUEVO
        self.boton_editar_fecha_rect = pygame.Rect(
            self.x + self.ancho - 2 * (self.boton_width + self.boton_margin),
            self.y + int(self.alto * 0.11),
            self.boton_width, self.boton_height
        )
        self.color_boton_editar_fecha = (100, 150, 200)
        self.color_boton_editar_fecha_hover = (80, 130, 180)
        self.editar_fecha_hover = False
        self.mostrando_formulario_editar = False  # Estado para formulario de edición
        self.pedido_seleccionado = None  # Almacena ID del pedido seleccionado
        self.formulario_editar_box = None  # Campo para edición de fecha
        self.formulario_editar_btn_guardar = None
        self.formulario_editar_btn_cancelar = None
        self.formulario_editar_mensaje = ""

    def mostrar_alerta(self, mensaje, duracion=3000):
        """
        Muestra un mensaje temporal en la interfaz
        
        Args:
            mensaje (str): Mensaje a mostrar
            duracion (int, optional): Duración en milisegundos. Defaults to 3000.
        """
        self.mensaje_alerta = mensaje
        self.tiempo_alerta = pygame.time.get_ticks() + duracion

    def cargar_datos_tabla(self):
        """
        Carga los pedidos desde la base de datos según la vista actual
        
        Vista NUEVO: Muestra pedidos pendientes
        Vista RECOGER: Muestra pedidos listos para entregar
        """
        conexion = Conexion()
        texto = self.busqueda_texto.strip().lower()
        
        if self.opcion_seleccionada == "NUEVO":
            # Pedidos pendientes
            query = """
                SELECT 
                    p.ID_PedidoVenta AS id,
                    c.Nombre_Cliente AS cliente, 
                    p.Fecha_pedido AS fecha,
                    p.Fecha_entrega AS entrega,
                    p.Estado AS estado,
                    p.Total AS total
                FROM pedidoventa p
                JOIN Cliente c ON p.FK_ID_Cliente = c.ID_Cliente
                WHERE p.Estado = 'Pendiente'
            """
            params = ()
            if texto:
                query += " AND LOWER(c.Nombre_Cliente) LIKE %s"
                params = (f"%{texto}%",)
        else:  # RECOGER
            # Pedidos listos para recoger
            query = """
                SELECT 
                    p.ID_PedidoVenta AS id,
                    c.Nombre_Cliente AS cliente, 
                    p.Fecha_pedido AS fecha,
                    p.Fecha_entrega AS entrega,
                    p.Estado AS estado,
                    p.Total AS total
                FROM pedidoventa p
                JOIN Cliente c ON p.FK_ID_Cliente = c.ID_Cliente
                WHERE p.Estado = 'Listo'
            """
            params = ()
            if texto:
                query += " AND LOWER(c.Nombre) LIKE %s"
                params = (f"%{texto}%",)
                
        try:
            self.datos_tabla = conexion.consultar(query, params)
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            self.datos_tabla = []

    def dibujar_pedido(self, surface):
        """
        Dibuja la interfaz completa, incluyendo el botón de editar fecha.
        """
        # Fondo y título (sin cambios)
        pygame.draw.rect(surface, self.FONDO, (self.x, self.y, self.ancho, self.alto))
        titulo = self.fuente_titulo.render("Gestión de Pedidos", True, self.color_texto)
        surface.blit(titulo, (self.x + int(self.ancho * 0.02), self.y + int(self.alto * 0.03)))

        # Campo de búsqueda y botones de navegación (sin cambios)
        busq_x = self.x + int(self.ancho * 0.02)
        busq_y = self.y + int(self.alto * 0.11)
        busq_w = int(self.ancho * 0.35)
        busq_h = self.boton_height
        self.dibujar_campo_busqueda(surface, busq_x, busq_y, busq_w, busq_h)

        for i, rect in enumerate(self.boton_rects):
            color = self.color_boton_activo if self.opcion_seleccionada == self.botones_opciones[i] else self.color_boton
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto_boton = self.fuente_boton.render(self.botones_opciones[i], True, self.color_texto)
            text_rect = texto_boton.get_rect(center=rect.center)
            surface.blit(texto_boton, text_rect)

        # Botón principal (crear/entregar)
        color_agregar = self.color_boton_agregar_hover if self.agregar_hover else self.color_boton_agregar
        pygame.draw.rect(surface, color_agregar, self.boton_agregar_rect, border_radius=8)
        texto_agregar = "Crear Pedido" if self.opcion_seleccionada == "NUEVO" else "Entregar"
        texto_agregar_render = self.fuente_boton.render(texto_agregar, True, (255, 255, 255))
        text_rect_agregar = texto_agregar_render.get_rect(center=self.boton_agregar_rect.center)
        surface.blit(texto_agregar_render, text_rect_agregar)

        # Botón de editar fecha (solo en vista NUEVO)
        if self.opcion_seleccionada == "NUEVO":
            color_editar = self.color_boton_editar_fecha_hover if self.editar_fecha_hover else self.color_boton_editar_fecha
            pygame.draw.rect(surface, color_editar, self.boton_editar_fecha_rect, border_radius=8)
            texto_editar = self.fuente_boton.render("Editar Fecha", True, (255, 255, 255))
            text_rect_editar = texto_editar.get_rect(center=self.boton_editar_fecha_rect.center)
            surface.blit(texto_editar, text_rect_editar)

        # Tabla de pedidos
        tabla_x = self.x + int(self.ancho * 0.03)
        tabla_y = self.y + int(self.alto * 0.23)
        tabla_width = int(self.ancho * 0.94)
        tabla_row_height = int(self.alto * 0.07)
        self.dibujar_tabla(surface, tabla_x, tabla_y, tabla_width, tabla_row_height, self.datos_tabla)

        # Mensaje de alerta
        if self.mensaje_alerta and pygame.time.get_ticks() < self.tiempo_alerta:
            self.dibujar_alerta(surface)

        # Formularios
        if self.mostrando_formulario:
            self.dibujar_formulario(surface)
        elif self.mostrando_formulario_editar:
            self.dibujar_formulario_editar(surface)

    def dibujar_campo_busqueda(self, surface, x, y, w, h):
        """
        Dibuja el campo de búsqueda de clientes
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            x, y (int): Posición del campo
            w, h (int): Dimensiones del campo
        """
        color_fondo = (255, 255, 255)
        color_borde = (100, 100, 100) if self.busqueda_activa else (180, 180, 180)
        pygame.draw.rect(surface, color_fondo, (x, y, w, h), border_radius=10)
        pygame.draw.rect(surface, color_borde, (x, y, w, h), 2, border_radius=10)
        texto = self.busqueda_texto if self.busqueda_texto else "Buscar cliente..."
        color_texto = self.NEGRO if self.busqueda_texto else (150, 150, 150)
        render = self.fuente_busqueda.render(texto, True, color_texto)
        surface.blit(render, (x + 10, y + (h - render.get_height()) // 2))
        
    def dibujar_alerta(self, surface):
        """
        Dibuja un mensaje de alerta temporal
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        alerta_w = int(self.ancho * 0.4)
        alerta_h = int(self.alto * 0.08)
        alerta_x = self.x + (self.ancho - alerta_w) // 2
        alerta_y = self.y + int(self.alto * 0.15)
        
        pygame.draw.rect(surface, (255, 240, 210), (alerta_x, alerta_y, alerta_w, alerta_h), border_radius=10)
        pygame.draw.rect(surface, (200, 150, 100), (alerta_x, alerta_y, alerta_w, alerta_h), 2, border_radius=10)
        
        font_alerta = pygame.font.SysFont("Open Sans", int(self.alto * 0.03))
        texto = font_alerta.render(self.mensaje_alerta, True, (100, 80, 0))
        surface.blit(texto, (alerta_x + (alerta_w - texto.get_width()) // 2, alerta_y + (alerta_h - texto.get_height()) // 2))

    def dibujar_tabla(self, surface, x, y, width, row_height, datos):
        """
        Dibuja la tabla de pedidos con formato adaptativo
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            x, y (int): Posición de la tabla
            width (int): Ancho total de la tabla
            row_height (int): Altura de cada fila
            datos (list): Lista de pedidos a mostrar
        """
        # Definir columnas según la vista
        if self.opcion_seleccionada == "NUEVO":
            columnas = ["ID", "Cliente", "Fecha pedido", "Fecha entrega", "Estado", "Total"]
            col_widths = [
                int(width*0.1), int(width*0.25), int(width*0.20), 
                int(width*0.20), int(width*0.10), int(width*0.15)
            ]
        else:  # RECOGER
            columnas = ["ID", "Cliente", "Fecha pedido", "Fecha entrega", "Estado", "Total"]
            col_widths = [
                int(width*0.1), int(width*0.25), int(width*0.20), 
                int(width*0.20), int(width*0.10), int(width*0.15)
            ]

        # Dibujar encabezados
        col_x = x
        for i, col in enumerate(columnas):
            pygame.draw.rect(surface, self.color_tabla_header, (col_x, y, col_widths[i], row_height))
            pygame.draw.rect(surface, self.color_tabla_border, (col_x, y, col_widths[i], row_height), 2)
            texto = self.fuente_tabla.render(col, True, self.NEGRO)
            text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, y + row_height // 2))
            surface.blit(texto, text_rect)
            col_x += col_widths[i]

        # Dibujar filas
        fila_y = y + row_height
        for fila in datos:
            col_x = x
            keys = ["id", "cliente", "fecha", "entrega", "estado", "total"]
            for i, key in enumerate(keys):
                valor = fila.get(key, "")
                if key == "total":
                    valor = f"${float(valor):.2f}" if valor else ""
                elif key in ["fecha", "entrega"] and valor:
                    # Convertir formato de fecha si es necesario
                    if isinstance(valor, datetime):
                        valor = valor.strftime("%d/%m/%Y")
                    elif isinstance(valor, str) and len(valor) > 10:
                        try:
                            valor = datetime.strptime(valor, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                        except:
                            pass
                
                pygame.draw.rect(surface, self.color_tabla_row, (col_x, fila_y, col_widths[i], row_height))
                pygame.draw.rect(surface, self.color_tabla_border, (col_x, fila_y, col_widths[i], row_height), 1)
                texto = self.fuente_tabla.render(str(valor), True, self.NEGRO)
                text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, fila_y + row_height // 2))
                surface.blit(texto, text_rect)
                col_x += col_widths[i]
            fila_y += row_height

    def mostrar_formulario(self):
        """
        Configura y muestra el formulario para crear un nuevo pedido
        
        Campos del formulario:
        1. Correo del cliente
        2. Fecha de entrega
        3. Nombre del producto
        4. Cantidad
        5. Precio unitario
        6. Observaciones
        """
        self.mostrando_formulario = True
        font = pygame.font.SysFont("Open Sans", int(self.alto * 0.035))
        
        # Centrar el formulario
        x = self.x + int(self.ancho * 0.25)
        y = self.y + int(self.alto * 0.18)
        
        # Definir campos del formulario
        labels = [
            "Correo Cliente:", "Fecha Entrega:", "Nombre Producto:", 
            "Cantidad:", "Precio Unitario:", "Observaciones:"
        ]
        
        self.formulario_labels = []
        self.formulario_boxes = []
        for i, label in enumerate(labels):
            lbl = font.render(label, True, (0, 0, 0))
            self.formulario_labels.append((lbl, (x, y + i * int(self.alto * 0.07))))
            
            # Tamaño de los campos de entrada
            input_width = int(self.ancho * 0.28)
            input_height = int(self.alto * 0.05)
            
            # Configuración específica para cada campo
            if label == "Fecha Entrega:":
                from datetime import datetime, timedelta
                fecha_default = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                box = InputBox(
                    x + int(self.ancho * 0.15),
                    y + i * int(self.alto * 0.07),
                    input_width,
                    input_height,
                    text=fecha_default,
                    font=font
                )
            elif label == "Cantidad:":
                # Campo numérico para la cantidad
                box = InputBox(
                    x + int(self.ancho * 0.15),
                    y + i * int(self.alto * 0.07),
                    input_width,
                    input_height,
                    text="1",  # Valor predeterminado
                    font=font,
                    numeric=True  # Solo permite números
                )
            elif label == "Precio Unitario:":
                # Campo numérico para el precio
                box = InputBox(
                    x + int(self.ancho * 0.15),
                    y + i * int(self.alto * 0.07),
                    input_width,
                    input_height,
                    text="",
                    font=font,
                    numeric=True  # Solo permite números
                )
            else:
                box = InputBox(
                    x + int(self.ancho * 0.15),
                    y + i * int(self.alto * 0.07),
                    input_width,
                    input_height,
                    text="",
                    font=font
                )
            self.formulario_boxes.append(box)
        
        # Posición de los botones
        button_y = y + (len(labels) + 1) * int(self.alto * 0.07)
        button_width = int(self.ancho * 0.12)
        button_height = int(self.alto * 0.06)
        
        # Botones de guardar y cancelar
        self.formulario_btn_guardar = pygame.Rect(
            x + int(self.ancho * 0.05),
            button_y,
            button_width, 
            button_height
        )
        
        self.formulario_btn_cancelar = pygame.Rect(
            x + int(self.ancho * 0.22),
            button_y,
            button_width, 
            button_height
        )
        
        # Para evitar errores si alguna parte del código aún intenta acceder a este atributo
        self.formulario_btn_agregar_producto = None
        
        self.formulario_mensaje = ""

    def dibujar_formulario(self, surface):
        """
        Dibuja el formulario de creación de pedidos
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Fondo semitransparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (self.x, self.y))

        # Ventana del formulario - tamaño ajustado
        form_w = int(self.ancho * 0.5)
        form_h = int(self.alto * 0.8)  # Más alto para acomodar todos los campos
        form_x = self.x + (self.ancho - form_w) // 2
        form_y = self.y + (self.alto - form_h) // 2
        
        # Dibujar el fondo del formulario
        pygame.draw.rect(surface, (255, 255, 255), (form_x, form_y, form_w, form_h), border_radius=12)
        pygame.draw.rect(surface, (100, 100, 200), (form_x, form_y, form_w, form_h), 3, border_radius=12)

        # Título
        font_title = pygame.font.SysFont("Open Sans", int(self.alto * 0.05), bold=True)
        titulo = "Crear Nuevo Pedido"
        text_title = font_title.render(titulo, True, (0, 0, 0))
        title_x = form_x + (form_w - text_title.get_width()) // 2
        surface.blit(text_title, (title_x, form_y + 20))
        
        # Mostrar fecha de registro (automática)
        font_date = pygame.font.SysFont("Open Sans", int(self.alto * 0.03))
        fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
        fecha_text = font_date.render(f"Fecha de registro: {fecha_actual}", True, (100, 100, 100))
        surface.blit(fecha_text, (form_x + 40, form_y + 60))

        # Labels y cajas de texto
        label_x = form_x + 40
        input_x = form_x + int(form_w * 0.35)
        start_y = form_y + 90  # Ajustado para dejar espacio para la fecha de registro
        field_spacing = int(self.alto * 0.07)  # Espacio entre campos

        # Dibujar campos de formulario
        for i, (lbl, _) in enumerate(self.formulario_labels):
            current_y = start_y + i * field_spacing
            
            # Dibujar etiqueta
            surface.blit(lbl, (label_x, current_y + 5))
            
            # Dibujar campo de entrada
            self.formulario_boxes[i].rect.x = input_x
            self.formulario_boxes[i].rect.y = current_y
            self.formulario_boxes[i].draw(surface)
        
        # Dibujar botones
        # Botón guardar
        pygame.draw.rect(surface, (100, 200, 100), self.formulario_btn_guardar, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(self.alto * 0.035), bold=True)
        text_guardar = font_btn.render("Guardar", True, (255, 255, 255))
        guardar_x = self.formulario_btn_guardar.x + (self.formulario_btn_guardar.width - text_guardar.get_width()) // 2
        guardar_y = self.formulario_btn_guardar.y + (self.formulario_btn_guardar.height - text_guardar.get_height()) // 2
        surface.blit(text_guardar, (guardar_x, guardar_y))
        
        # Botón cancelar
        pygame.draw.rect(surface, (200, 100, 100), self.formulario_btn_cancelar, border_radius=8)
        text_cancelar = font_btn.render("Cancelar", True, (255, 255, 255))
        cancelar_x = self.formulario_btn_cancelar.x + (self.formulario_btn_cancelar.width - text_cancelar.get_width()) // 2
        cancelar_y = self.formulario_btn_cancelar.y + (self.formulario_btn_cancelar.height - text_cancelar.get_height()) // 2
        surface.blit(text_cancelar, (cancelar_x, cancelar_y))
        
        # Mensaje de error o éxito
        if self.formulario_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(self.alto * 0.03))
            color = (200, 0, 0) if "Error" in self.formulario_mensaje else (0, 150, 0)
            msg = font_msg.render(self.formulario_mensaje, True, color)
            msg_x = form_x + (form_w - msg.get_width()) // 2
            surface.blit(msg, (msg_x, form_y + form_h - 40))

    def dibujar_formulario_editar(self, surface):
        """
        Dibuja el formulario para editar la fecha de entrega.
        """
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (self.x, self.y))

        form_w = int(self.ancho * 0.4)
        form_h = int(self.alto * 0.25)
        form_x = self.x + (self.ancho - form_w) // 2
        form_y = self.y + (self.alto - form_h) // 2

        pygame.draw.rect(surface, (255, 255, 255), (form_x, form_y, form_w, form_h), border_radius=12)
        pygame.draw.rect(surface, (100, 100, 200), (form_x, form_y, form_w, form_h), 3, border_radius=12)

        font_title = pygame.font.SysFont("Open Sans", int(self.alto * 0.05), bold=True)
        titulo = f"Editar Fecha Pedido #{self.pedido_seleccionado}"
        text_title = font_title.render(titulo, True, (0, 0, 0))
        title_x = form_x + (form_w - text_title.get_width()) // 2
        surface.blit(text_title, (title_x, form_y + 20))

        font = pygame.font.SysFont("Open Sans", int(self.alto * 0.035))
        label = font.render("Nueva Fecha (YYYY-MM-DD):", True, (0, 0, 0))
        surface.blit(label, (form_x + 40, form_y + 70))
        self.formulario_editar_box.draw(surface)

        pygame.draw.rect(surface, (100, 200, 100), self.formulario_editar_btn_guardar, border_radius=8)
        text_guardar = font.render("Guardar", True, (255, 255, 255))
        guardar_x = self.formulario_editar_btn_guardar.x + (self.formulario_editar_btn_guardar.width - text_guardar.get_width()) // 2
        guardar_y = self.formulario_editar_btn_guardar.y + (self.formulario_editar_btn_guardar.height - text_guardar.get_height()) // 2
        surface.blit(text_guardar, (guardar_x, guardar_y))

        pygame.draw.rect(surface, (200, 100, 100), self.formulario_editar_btn_cancelar, border_radius=8)
        text_cancelar = font.render("Cancelar", True, (255, 255, 255))
        cancelar_x = self.formulario_editar_btn_cancelar.x + (self.formulario_editar_btn_cancelar.width - text_cancelar.get_width()) // 2
        cancelar_y = self.formulario_editar_btn_cancelar.y + (self.formulario_editar_btn_cancelar.height - text_cancelar.get_height()) // 2
        surface.blit(text_cancelar, (cancelar_x, cancelar_y))

        if self.formulario_editar_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(self.alto * 0.03))
            color = (200, 0, 0) if "Error" in self.formulario_editar_mensaje else (0, 150, 0)
            msg = font_msg.render(self.formulario_editar_mensaje, True, color)
            msg_x = form_x + (form_w - msg.get_width()) // 2
            surface.blit(msg, (msg_x, form_y + form_h - 40))

    def validar_fecha(self, fecha_str):
        """
        Valida que la fecha sea en formato YYYY-MM-DD y posterior a la fecha actual.
        
        Args:
            fecha_str (str): Fecha en formato string
        
        Returns:
            tuple: (bool, str) - (Éxito, Mensaje de error si aplica)
        """
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            fecha_actual = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if fecha <= fecha_actual:
                return False, "Error: La fecha de entrega debe ser posterior a hoy"
            return True, ""
        except ValueError:
            return False, "Error: Formato de fecha inválido (use YYYY-MM-DD)"

    def guardar_pedido(self):
        """
        Guarda un nuevo pedido con validación de fecha.
        """
        correo_cliente = self.formulario_boxes[0].get_value()
        fecha_entrega = self.formulario_boxes[1].get_value()
        nombre_producto = self.formulario_boxes[2].get_value()
        cantidad_str = self.formulario_boxes[3].get_value()
        precio_str = self.formulario_boxes[4].get_value()
        observaciones = self.formulario_boxes[5].get_value()

        # Validar fecha de entrega
        fecha_valida, mensaje_fecha = self.validar_fecha(fecha_entrega)
        if not fecha_valida:
            self.formulario_mensaje = mensaje_fecha
            return False

        # Validaciones existentes
        if not correo_cliente or not nombre_producto:
            self.formulario_mensaje = "Error: Correo y nombre de producto son obligatorios"
            return False

        try:
            cantidad = int(cantidad_str) if cantidad_str else 1
            precio = float(precio_str) if precio_str else 0

            if cantidad <= 0:
                self.formulario_mensaje = "Error: La cantidad debe ser mayor a cero"
                return False
            if precio <= 0:
                self.formulario_mensaje = "Error: El precio debe ser mayor a cero"
                return False

            # Código existente para guardar cliente, producto y pedido
            conexion = Conexion()
            query_cliente = "SELECT Id_Cliente FROM Cliente WHERE Correo = %s"
            resultado_cliente = conexion.consultar(query_cliente, (correo_cliente,))
            if not resultado_cliente:
                self.formulario_mensaje = "Error: No existe un cliente con ese correo"
                return False
            cliente_id = resultado_cliente[0]['Id_Cliente']

            query_producto = "SELECT ID_CatProducto FROM CatProducto WHERE Nombre_prod = %s"
            resultado_producto = conexion.consultar(query_producto, (nombre_producto,))
            if resultado_producto:
                producto_id = resultado_producto[0]['ID_CatProducto']
            else:
                query_insertar_producto = """
                    INSERT INTO CatProducto (Nombre_prod, Precio, Stock, Estado)
                    VALUES (%s, %s, %s, %s)
                """
                conexion.update(query_insertar_producto, (nombre_producto, precio, 10, "Disponible"))
                id_producto_query = "SELECT LAST_INSERT_ID() AS id_producto"
                resultado = conexion.consultar(id_producto_query)
                producto_id = resultado[0]['id_producto']

            subtotal = cantidad * precio
            fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query_pedido = """
                INSERT INTO pedidoventa 
                (Fecha_pedido, Fecha_entrega, Total, Estado, Observaciones, FK_ID_Cliente)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            conexion.update(query_pedido, (
                fecha_registro, fecha_entrega, subtotal, "Pendiente", 
                observaciones, cliente_id
            ))

            id_pedido_query = "SELECT LAST_INSERT_ID() AS id_pedido"
            resultado = conexion.consultar(id_pedido_query)
            id_pedido = resultado[0]['id_pedido']

            query_detalle = """
                INSERT INTO detallepedidoventa 
                (Cantidad, PrecioUnitario, Subtotal, FK_ID_PedidoVenta, FK_ID_CatProducto)
                VALUES (%s, %s, %s, %s, %s)
            """
            conexion.update(query_detalle, (cantidad, precio, subtotal, id_pedido, producto_id))

            self.mostrar_alerta(f"Pedido guardado. Registro: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Entrega: {fecha_entrega}")
            self.mostrando_formulario = False
            self.cargar_datos_tabla()
            return True
        except Exception as e:
            print(f"Error al guardar pedido: {e}")
            self.formulario_mensaje = f"Error: No se pudo guardar el pedido"
            return False
        
    def handle_event(self, event):
        """
        Maneja eventos, incluyendo clics en el botón de editar fecha y el formulario de edición.
        """
        # Manejo del formulario de edición de fecha
        if self.mostrando_formulario_editar:
            self.formulario_editar_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.formulario_editar_btn_guardar.collidepoint(event.pos):
                    self.guardar_nueva_fecha()
                    return
                elif self.formulario_editar_btn_cancelar.collidepoint(event.pos):
                    self.mostrando_formulario_editar = False
                    return
            return

        # Manejo del formulario de creación (sin cambios)
        if self.mostrando_formulario:
            for box in self.formulario_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.formulario_btn_guardar.collidepoint(event.pos):
                    self.guardar_pedido()
                    return
                elif self.formulario_btn_cancelar.collidepoint(event.pos):
                    self.mostrando_formulario = False
                    return
            return

        # Eventos generales
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.agregar_hover = self.boton_agregar_rect.collidepoint(mouse_pos)
            self.editar_fecha_hover = self.boton_editar_fecha_rect.collidepoint(mouse_pos) if self.opcion_seleccionada == "NUEVO" else False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Botones de navegación
            for i, rect in enumerate(self.boton_rects):
                if rect.collidepoint(mouse_pos):
                    self.opcion_seleccionada = self.botones_opciones[i]
                    self.pedido_seleccionado = None  # Resetear selección
                    self.cargar_datos_tabla()
                    return

            # Botón crear/entregar
            if self.boton_agregar_rect.collidepoint(mouse_pos):
                if self.opcion_seleccionada == "NUEVO":
                    self.mostrar_formulario()
                else:  # RECOGER
                    if self.pedido_seleccionado:
                        self.entregar_pedido(self.pedido_seleccionado)
                    else:
                        self.mostrar_alerta("No hay pedido seleccionado")
                return

            # Botón editar fecha
            if self.opcion_seleccionada == "NUEVO" and self.boton_editar_fecha_rect.collidepoint(mouse_pos):
                if self.pedido_seleccionado:
                    self.mostrar_formulario_editar_fecha()
                else:
                    self.mostrar_alerta("Seleccione un pedido primero")
                return

            # Campo de búsqueda
            busq_x = self.x + int(self.ancho * 0.02)
            busq_y = self.y + int(self.alto * 0.11)
            busq_w = int(self.ancho * 0.35)
            busq_h = self.boton_height
            busq_rect = pygame.Rect(busq_x, busq_y, busq_w, busq_h)
            if busq_rect.collidepoint(mouse_pos):
                self.busqueda_activa = True
            else:
                self.busqueda_activa = False

            # Selección en la tabla
            tabla_x = self.x + int(self.ancho * 0.03)
            tabla_y = self.y + int(self.alto * 0.23) + int(self.alto * 0.07)
            tabla_width = int(self.ancho * 0.94)
            row_height = int(self.alto * 0.07)
            for i, fila in enumerate(self.datos_tabla):
                row_rect = pygame.Rect(tabla_x, tabla_y + i * row_height, tabla_width, row_height)
                if row_rect.collidepoint(mouse_pos):
                    self.pedido_seleccionado = self.datos_tabla[i]["id"]
                    if self.opcion_seleccionada == "RECOGER":
                        self.entregar_pedido(self.pedido_seleccionado)
                    break

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
                    
    def entregar_pedido(self, id_pedido):
        try:
            conexion = Conexion()
            query = "UPDATE pedidoventa SET Estado = 'Entregado' WHERE ID_PedidoVenta = %s"
            conexion.update(query, (id_pedido,))
            self.mostrar_alerta(f"Pedido #{id_pedido} entregado correctamente")
            self.cargar_datos_tabla()
            return True
        except Exception as e:
            print(f"Error al entregar pedido: {e}")
            self.mostrar_alerta(f"Error al entregar pedido #{id_pedido}")
            return False
        
    def mostrar_formulario_editar_fecha(self):
        """
        Configura el formulario para editar la fecha de entrega de un pedido.
        """
        if not self.pedido_seleccionado:
            self.mostrar_alerta("Seleccione un pedido primero")
            return

        self.mostrando_formulario_editar = True
        font = pygame.font.SysFont("Open Sans", int(self.alto * 0.035))

        # Obtener la fecha actual del pedido
        conexion = Conexion()
        query = "SELECT Fecha_entrega FROM pedidoventa WHERE ID_PedidoVenta = %s"
        resultado = conexion.consultar(query, (self.pedido_seleccionado,))
        fecha_actual = resultado[0]['Fecha_entrega'] if resultado else datetime.now().strftime("%Y-%m-%d")

        # Configurar campo de entrada
        x = self.x + int(self.ancho * 0.35)
        y = self.y + int(self.alto * 0.35)
        input_width = int(self.ancho * 0.28)
        input_height = int(self.alto * 0.05)
        self.formulario_editar_box = InputBox(x, y, input_width, input_height, text=str(fecha_actual), font=font)

        # Botones de guardar y cancelar
        button_y = y + int(self.alto * 0.07)
        button_width = int(self.ancho * 0.12)
        button_height = int(self.alto * 0.06)
        self.formulario_editar_btn_guardar = pygame.Rect(
            x + int(self.ancho * 0.05), button_y, button_width, button_height
        )
        self.formulario_editar_btn_cancelar = pygame.Rect(
            x + int(self.ancho * 0.22), button_y, button_width, button_height
        )
        self.formulario_editar_mensaje = ""

    def guardar_nueva_fecha(self):
        """
        Guarda la nueva fecha de entrega en la base de datos.
        """
        if not self.pedido_seleccionado:
            self.formulario_editar_mensaje = "Error: No hay pedido seleccionado"
            return False

        nueva_fecha = self.formulario_editar_box.get_value()
        fecha_valida, mensaje_fecha = self.validar_fecha(nueva_fecha)
        if not fecha_valida:
            self.formulario_editar_mensaje = mensaje_fecha
            return False

        try:
            conexion = Conexion()
            query = "UPDATE pedidoventa SET Fecha_entrega = %s WHERE ID_PedidoVenta = %s"
            conexion.update(query, (nueva_fecha, self.pedido_seleccionado))
            self.mostrar_alerta(f"Fecha de entrega actualizada para pedido #{self.pedido_seleccionado}")
            self.mostrando_formulario_editar = False
            self.cargar_datos_tabla()
            return True
        except Exception as e:
            print(f"Error al actualizar fecha: {e}")
            self.formulario_editar_mensaje = "Error: No se pudo actualizar la fecha"
            return False