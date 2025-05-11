"""
Sistema de Gestión de Recetas para Panadería
-------------------------------------------
Sistema desarrollado en Pygame para administrar recetas de productos:
- Crear nuevas recetas con materias primas
- Editar recetas existentes
- Ver detalles de recetas
- Gestionar ingredientes por receta
- Calcular costos por materias primas

Características principales:
- Interfaz trimodal: CREAR, EDITAR y VER
- Búsqueda de recetas por nombre
- Gestión de materias primas por receta
- Calculadora de porciones y tiempos
- Formularios modales con validación

Versión: 1.0
"""

import pygame
from conexion import Conexion
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
class Receta:    
    """
    Clase principal para la gestión de recetas
    
    Maneja tres vistas principales:
    1. CREAR: Crear nuevas recetas
    2. EDITAR: Modificar recetas existentes
    3. VER: Visualizar detalles de recetas
    
    Attributes:
        x, y (int): Posición de la interfaz
        ancho, alto (int): Dimensiones de la interfaz
        opcion_seleccionada (str): Vista actual ("CREAR", "EDITAR" o "VER")
        datos_tabla (list): Recetas actualmente mostradas
        materias_primas_receta (list): Ingredientes de la receta actual
        receta_seleccionada (int): ID de la receta en edición/visualización
    """
    def __init__(self, x, y, ancho, alto):
        """
        Inicializa el sistema de gestión de recetas
        
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
        self.botones_opciones = ["CREAR", "EDITAR", "VER"]
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

        # Botón principal (crear/guardar/ver)
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
        
        # Estado del formulario principal
        self.mostrando_formulario = False
        self.formulario_boxes = []
        self.formulario_labels = []
        self.formulario_btn_guardar = None
        self.formulario_btn_cancelar = None
        self.formulario_mensaje = ""
        
        # Gestión de materias primas
        self.materias_primas_receta = []
        self.tabla_materias_primas_scroll = 0
        
        # Sistema de alertas
        self.mensaje_alerta = ""
        self.tiempo_alerta = 0
        
        # Estado del formulario de materias primas
        self.mostrando_form_materiaprima = False
        self.form_materiaprima_boxes = []
        self.form_materiaprima_labels = []
        self.form_materiaprima_btn_agregar = None
        self.form_materiaprima_btn_cancelar = None
        
        # Receta actual en edición/visualización
        self.receta_seleccionada = None

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
        Carga las recetas desde la base de datos
        
        Incluye:
        - Nombre de la receta
        - Tiempo de preparación
        - Descripción
        - Número de ingredientes
        """
        conexion = Conexion()
        texto = self.busqueda_texto.strip().lower()
        
        query = """
            SELECT 
                r.ID_Receta AS id,
                r.Nombre_receta AS nombre, 
                r.Tiempo_Preparacion AS tiempo,
                r.Descripcion AS descripcion,
                r.No_Unidades AS porciones,
                (SELECT COUNT(*) FROM receta_materiaprima WHERE ID_Receta = r.ID_Receta) AS num_ingredientes
            FROM receta r
            WHERE 1=1
        """
        params = ()
        if texto:
            query += " AND LOWER(r.Nombre_receta) LIKE %s"
            params = (f"%{texto}%",)
        
        query += " ORDER BY r.Nombre_receta ASC"
                
        try:
            self.datos_tabla = conexion.consultar(query, params)
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            self.datos_tabla = []

    def dibujar_receta(self, surface):
        """
        Dibuja la interfaz completa de gestión de recetas
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Fondo principal
        pygame.draw.rect(surface, self.FONDO, (self.x, self.y, self.ancho, self.alto))
        
        # Título
        titulo = self.fuente_titulo.render("Gestión de Recetas", True, self.color_texto)
        surface.blit(titulo, (self.x + int(self.ancho * 0.02), self.y + int(self.alto * 0.03)))

        # Campo de búsqueda
        busq_x = self.x + int(self.ancho * 0.02)
        busq_y = self.y + int(self.alto * 0.11)
        busq_w = int(self.ancho * 0.35)
        busq_h = self.boton_height
        self.dibujar_campo_busqueda(surface, busq_x, busq_y, busq_w, busq_h)

        # Botones de navegación
        for i, rect in enumerate(self.boton_rects):
            color = self.color_boton_activo if self.opcion_seleccionada == self.botones_opciones[i] else self.color_boton
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto_boton = self.fuente_boton.render(self.botones_opciones[i], True, self.color_texto)
            text_rect = texto_boton.get_rect(center=rect.center)
            surface.blit(texto_boton, text_rect)

        # Botón principal (adapta el texto según la vista)
        color_agregar = self.color_boton_agregar_hover if self.agregar_hover else self.color_boton_agregar
        pygame.draw.rect(surface, color_agregar, self.boton_agregar_rect, border_radius=8)
        
        if self.opcion_seleccionada == "CREAR":
            texto_agregar = "Nueva Receta"
        elif self.opcion_seleccionada == "EDITAR":
            texto_agregar = "Guardar Cambios"
        else:  # VER
            texto_agregar = "Ver Detalles"
            
        texto_agregar_render = self.fuente_boton.render(texto_agregar, True, (255, 255, 255))
        text_rect_agregar = texto_agregar_render.get_rect(center=self.boton_agregar_rect.center)
        surface.blit(texto_agregar_render, text_rect_agregar)

        # Tabla de recetas
        tabla_x = self.x + int(self.ancho * 0.03)
        tabla_y = self.y + int(self.alto * 0.23)
        tabla_width = int(self.ancho * 0.94)
        tabla_row_height = int(self.alto * 0.07)
        self.dibujar_tabla(surface, tabla_x, tabla_y, tabla_width, tabla_row_height, self.datos_tabla)
        
        # Mensaje de alerta temporal
        if self.mensaje_alerta and pygame.time.get_ticks() < self.tiempo_alerta:
            self.dibujar_alerta(surface)
            
        # Formularios si están activos
        if self.mostrando_formulario:
            self.dibujar_formulario(surface)
            
        if self.mostrando_form_materiaprima:
            self.dibujar_form_materiaprima(surface)

    def dibujar_campo_busqueda(self, surface, x, y, w, h):
        """
        Dibuja el campo de búsqueda de recetas
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            x, y (int): Posición del campo
            w, h (int): Dimensiones del campo
        """
        color_fondo = (255, 255, 255)
        color_borde = (100, 100, 100) if self.busqueda_activa else (180, 180, 180)
        pygame.draw.rect(surface, color_fondo, (x, y, w, h), border_radius=10)
        pygame.draw.rect(surface, color_borde, (x, y, w, h), 2, border_radius=10)
        texto = self.busqueda_texto if self.busqueda_texto else "Buscar receta..."
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
        Dibuja la tabla de recetas con formato adaptativo
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            x, y (int): Posición de la tabla
            width (int): Ancho total de la tabla
            row_height (int): Altura de cada fila
            datos (list): Lista de recetas a mostrar
        """
        # Definir columnas
        columnas = ["ID", "Nombre", "Tiempo Prep.", "Descripción", "Porciones", "# Ingredientes"]
        col_widths = [
            int(width*0.05), int(width*0.2), int(width*0.15), 
            int(width*0.35), int(width*0.10), int(width*0.15)
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

        # Dibujar filas de datos
        fila_y = y + row_height
        for fila in datos:
            col_x = x
            keys = ["id", "nombre", "tiempo", "descripcion", "porciones", "num_ingredientes"]
            for i, key in enumerate(keys):
                valor = fila.get(key, "")
                
                # Formatear valores según tipo
                if key == "tiempo" and valor:
                    valor = f"{valor} min"
                
                # Limitar texto largo
                if key == "descripcion" and valor and len(str(valor)) > 35:
                    valor = str(valor)[:35] + "..."
                
                pygame.draw.rect(surface, self.color_tabla_row, (col_x, fila_y, col_widths[i], row_height))
                pygame.draw.rect(surface, self.color_tabla_border, (col_x, fila_y, col_widths[i], row_height), 1)
                texto = self.fuente_tabla.render(str(valor), True, self.NEGRO)
                text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, fila_y + row_height // 2))
                surface.blit(texto, text_rect)
                col_x += col_widths[i]
            fila_y += row_height

    def mostrar_formulario(self, receta=None):
        """
        Configura y muestra el formulario de receta
        
        Permite crear nueva receta o editar una existente
        
        Args:
            receta (dict, optional): Datos de receta para edición. Defaults to None.
        """
        self.mostrando_formulario = True
        font = pygame.font.SysFont("Open Sans", int(self.alto * 0.035))
        
        # Centrar el formulario
        x = self.x + int(self.ancho * 0.25)
        y = self.y + int(self.alto * 0.18)
        
        # Campos del formulario
        labels = [
            "Nombre:", "Tiempo de Preparación (min):", "Porciones:", 
            "Descripción:", "Instrucciones:"
        ]
        
        self.formulario_labels = []
        self.formulario_boxes = []
        
        for i, label in enumerate(labels):
            lbl = font.render(label, True, (0, 0, 0))
            self.formulario_labels.append((lbl, (x, y + i * int(self.alto * 0.07))))
            
            # Dimensiones del campo
            input_width = int(self.ancho * 0.28)
            input_height = int(self.alto * 0.05)
            
            # Configuración específica por campo
            if label == "Tiempo de Preparación (min):" or label == "Porciones:":
                # Campos numéricos
                valor_default = ""
                if receta:
                    if label == "Tiempo de Preparación (min):":
                        valor_default = str(receta.get('tiempo', ''))
                    elif label == "Porciones:":
                        valor_default = str(receta.get('porciones', ''))
                
                box = InputBox(
                    x + int(self.ancho * 0.15),
                    y + i * int(self.alto * 0.07),
                    input_width,
                    input_height,
                    text=valor_default,
                    font=font,
                    numeric=True
                )
            elif label == "Descripción:" or label == "Instrucciones:":
                # Campos expandidos para texto largo
                valor_default = ""
                if receta:
                    if label == "Descripción:":
                        valor_default = receta.get('descripcion', '')
                    elif label == "Instrucciones:":
                        # Buscar instrucciones en la base de datos
                        if receta.get('id'):
                            conexion = Conexion()
                            query = "SELECT Instrucciones FROM receta WHERE ID_Receta = %s"
                            resultado = conexion.consultar(query, (receta.get('id'),))
                            if resultado and 'Instrucciones' in resultado[0]:
                                valor_default = resultado[0]['Instrucciones']
                
                box = InputBox(
                    x + int(self.ancho * 0.15),
                    y + i * int(self.alto * 0.07),
                    input_width + int(self.ancho * 0.1),  # Más ancho
                    input_height + int(self.alto * 0.05),  # Más alto
                    text=valor_default,
                    font=font
                )
            else:
                # Campo estándar
                valor_default = ""
                if receta and label == "Nombre:":
                    valor_default = receta.get('nombre', '')
                
                box = InputBox(
                    x + int(self.ancho * 0.15),
                    y + i * int(self.alto * 0.07),
                    input_width,
                    input_height,
                    text=valor_default,
                    font=font
                )
            self.formulario_boxes.append(box)
        
        # Botón para gestionar materias primas
        button_y_materiasprimas = y + (len(labels) + 0.5) * int(self.alto * 0.07)
        self.formulario_btn_materiasprimas = pygame.Rect(
            x + int(self.ancho * 0.05),
            button_y_materiasprimas,
            int(self.ancho * 0.3),
            int(self.alto * 0.06)
        )
        
        # Botones de acción
        button_y = y + (len(labels) + 1.5) * int(self.alto * 0.07)
        button_width = int(self.ancho * 0.12)
        button_height = int(self.alto * 0.06)
        
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
        
        self.formulario_mensaje = ""
        
        # Cargar materias primas si es edición
        if receta:
            self.receta_seleccionada = receta.get('id')
            self.cargar_materiasprimas_receta(self.receta_seleccionada)
        else:
            self.receta_seleccionada = None
            self.materias_primas_receta = []

    def cargar_materiasprimas_receta(self, id_receta):
        conexion = Conexion()
        query = """
            SELECT 
                rmp.ID_Receta AS id,
                mp.Nombre AS nombre,
            FROM receta_materiaprima rmp
            JOIN materiaprima mp ON rmp.ID_MateriaPrima = mp.ID_MateriaPrima
            WHERE rmp.ID_Receta = %s
        """
        try:
            self.materias_primas_receta = conexion.consultar(query, (id_receta,))
        except Exception as e:
            print(f"Error al cargar materias primas: {e}")
            self.materias_primas_receta = []

    def dibujar_formulario(self, surface):
        """
        Dibuja el formulario de creación/edición de recetas
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Fondo semitransparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (self.x, self.y))

        # Ventana del formulario
        form_w = int(self.ancho * 0.6)
        form_h = int(self.alto * 0.8)
        form_x = self.x + (self.ancho - form_w) // 2
        form_y = self.y + (self.alto - form_h) // 2
        
        # Dibujar el fondo del formulario
        pygame.draw.rect(surface, (255, 255, 255), (form_x, form_y, form_w, form_h), border_radius=12)
        pygame.draw.rect(surface, (100, 100, 200), (form_x, form_y, form_w, form_h), 3, border_radius=12)

        # Título
        font_title = pygame.font.SysFont("Open Sans", int(self.alto * 0.05), bold=True)
        titulo = "Crear Nueva Receta" if not self.receta_seleccionada else "Editar Receta"
        text_title = font_title.render(titulo, True, (0, 0, 0))
        title_x = form_x + (form_w - text_title.get_width()) // 2
        surface.blit(text_title, (title_x, form_y + 20))

        # Labels y cajas de texto
        for i, (lbl, pos) in enumerate(self.formulario_labels):
            surface.blit(lbl, pos)
            self.formulario_boxes[i].draw(surface)
        
        # Tabla de materias primas (si hay)
        if self.materias_primas_receta:
            self.dibujar_tabla_materiasprimas(surface, form_x + 40, form_y + 350, form_w - 80, int(self.alto * 0.15))
        
        # Botón para gestionar materias primas
        pygame.draw.rect(surface, (100, 150, 200), self.formulario_btn_materiasprimas, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(self.alto * 0.035), bold=True)
        text_materiasprimas = font_btn.render("Gestionar Materias Primas", True, (255, 255, 255))
        ingr_x = self.formulario_btn_materiasprimas.x + (self.formulario_btn_materiasprimas.width - text_materiasprimas.get_width()) // 2
        ingr_y = self.formulario_btn_materiasprimas.y + (self.formulario_btn_materiasprimas.height - text_materiasprimas.get_height()) // 2
        surface.blit(text_materiasprimas, (ingr_x, ingr_y))
        
        # Botones guardar y cancelar
        pygame.draw.rect(surface, (100, 200, 100), self.formulario_btn_guardar, border_radius=8)
        text_guardar = font_btn.render("Guardar", True, (255, 255, 255))
        guardar_x = self.formulario_btn_guardar.x + (self.formulario_btn_guardar.width - text_guardar.get_width()) // 2
        guardar_y = self.formulario_btn_guardar.y + (self.formulario_btn_guardar.height - text_guardar.get_height()) // 2
        surface.blit(text_guardar, (guardar_x, guardar_y))
        
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

    def dibujar_tabla_materiasprimas(self, surface, x, y, width, height):
        """
        Dibuja una tabla que muestra las materias primas asociadas a una receta.
        
        Args:
            surface: Superficie de Pygame donde se dibujará la tabla
            x (int): Posición horizontal de la tabla
            y (int): Posición vertical de la tabla  
            width (int): Ancho de la tabla
            height (int): Alto de la tabla
        
        Features:
            - Tabla con scroll vertical
            - Alternancia de colores en filas
            - Columnas: Nombre, Cantidad, Unidad, Tipo
            - Flechas de navegación para scroll
        """
        # Encabezado de la sección
        font_header = pygame.font.SysFont("Open Sans", int(self.alto * 0.04), bold=True)
        header = font_header.render("Materias Primas", True, (50, 50, 120))
        surface.blit(header, (x, y - 30))
        
        # Fondo de la tabla
        pygame.draw.rect(surface, (240, 240, 255), (x, y, width, height), border_radius=8)
        pygame.draw.rect(surface, (180, 180, 200), (x, y, width, height), 2, border_radius=8)
        
        # Encabezados de columnas
        col_names = ["Nombre", "Cantidad", "Unidad", "Tipo"]
        col_widths = [int(width*0.4), int(width*0.2), int(width*0.2), int(width*0.2)]
        
        font_col = pygame.font.SysFont("Open Sans", int(self.alto * 0.03), bold=True)
        col_x = x + 10
        for i, col in enumerate(col_names):
            col_text = font_col.render(col, True, (0, 0, 80))
            surface.blit(col_text, (col_x, y + 10))
            col_x += col_widths[i]
        
        # Datos de materias primas
        font_data = pygame.font.SysFont("Open Sans", int(self.alto * 0.025))
        row_height = int(self.alto * 0.04)
        max_rows = int(height / row_height) - 1  # -1 para el encabezado
        
        # Aplicar scroll a los datos
        start_idx = min(self.tabla_materias_primas_scroll, len(self.materias_primas_receta) - max_rows) if len(self.materias_primas_receta) > max_rows else 0
        end_idx = min(start_idx + max_rows, len(self.materias_primas_receta))
        
        # Dibujar filas de datos
        for i, materiaprima in enumerate(self.materias_primas_receta[start_idx:end_idx]):
            row_y = y + row_height + i * row_height
            col_x = x + 10
            
            # Dibujar fila alternando colores
            if i % 2 == 0:
                pygame.draw.rect(surface, (230, 230, 245), (x, row_y, width, row_height))
            
            # Nombre
            text = font_data.render(materiaprima['nombre'], True, (0, 0, 0))
            surface.blit(text, (col_x, row_y + 5))
            col_x += col_widths[0]
            
            # Cantidad
            text = font_data.render(str(materiaprima['cantidad']), True, (0, 0, 0))
            surface.blit(text, (col_x, row_y + 5))
            col_x += col_widths[1]
            
            # Unidad
            text = font_data.render(materiaprima['unidad'], True, (0, 0, 0))
            surface.blit(text, (col_x, row_y + 5))
            col_x += col_widths[2]
            
            # Tipo
            text = font_data.render(materiaprima['tipo'], True, (0, 0, 0))
            surface.blit(text, (col_x, row_y + 5))
        
        # Indicadores de scroll si hay más elementos
        if len(self.materias_primas_receta) > max_rows:
            if self.tabla_materias_primas_scroll > 0:
                # Flecha arriba
                pygame.draw.polygon(surface, (100, 100, 200), [
                    (x + width - 20, y + 15),
                    (x + width - 30, y + 25),
                    (x + width - 10, y + 25)
                ])
            
            if end_idx < len(self.materias_primas_receta):
                # Flecha abajo
                pygame.draw.polygon(surface, (100, 100, 200), [
                    (x + width - 20, y + height - 15),
                    (x + width - 30, y + height - 25),
                    (x + width - 10, y + height - 25)
                ])

    def mostrar_form_materiaprima(self):
        """
        Configura y muestra el formulario para agregar una materia prima a la receta.
        
        Features:
            - Campos: Materia Prima, Cantidad (numérico), Unidad
            - Validación numérica en campo de cantidad
            - Botones: Agregar y Cancelar
            - Posicionamiento centrado sobre el formulario principal
        """
        self.mostrando_form_materiaprima = True
        font = pygame.font.SysFont("Open Sans", int(self.alto * 0.035))
        
        # Posición centrada sobre el formulario principal
        x = self.x + int(self.ancho * 0.35)
        y = self.y + int(self.alto * 0.3)
        
        # Definir campos para materia prima
        labels = ["Materia Prima:", "Cantidad:", "Unidad:"]
        
        self.form_materiaprima_labels = []
        self.form_materiaprima_boxes = []
        
        for i, label in enumerate(labels):
            lbl = font.render(label, True, (0, 0, 0))
            self.form_materiaprima_labels.append((lbl, (x, y + i * int(self.alto * 0.07))))
            
            # Tamaño de los campos
            input_width = int(self.ancho * 0.2)
            input_height = int(self.alto * 0.05)
            
            # Configuración específica según el tipo de campo
            if label == "Cantidad:":
                # Campo numérico para cantidad
                box = InputBox(
                    x + int(self.ancho * 0.12),
                    y + i * int(self.alto * 0.07),
                    input_width,
                    input_height,
                    text="",
                    font=font,
                    numeric=True
                )
            else:
                # Campo de texto normal
                box = InputBox(
                    x + int(self.ancho * 0.12),
                    y + i * int(self.alto * 0.07),
                    input_width,
                    input_height,
                    text="",
                    font=font
                )
            self.form_materiaprima_boxes.append(box)
        
        # Botones agregar y cancelar
        button_y = y + len(labels) * int(self.alto * 0.07) + int(self.alto * 0.03)
        button_width = int(self.ancho * 0.1)
        button_height = int(self.alto * 0.05)
        
        self.form_materiaprima_btn_agregar = pygame.Rect(
            x + int(self.ancho * 0.05),
            button_y,
            button_width,
            button_height
        )
        
        self.form_materiaprima_btn_cancelar = pygame.Rect(
            x + int(self.ancho * 0.18),
            button_y,
            button_width,
            button_height
        )

    def dibujar_form_materiaprima(self, surface):
        """
        Dibuja el formulario para agregar materia prima en pantalla.
        
        Args:
            surface: Superficie de Pygame donde se dibuja el formulario
        
        Features:
            - Fondo semitransparente (overlay)
            - Ventana modal centrada
            - Campos de entrada dinámicos
            - Botones estilizados con bordes redondeados
        """
        # Fondo semitransparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (self.x, self.y))
        
        # Ventana del formulario
        form_w = int(self.ancho * 0.35)
        form_h = int(self.alto * 0.4)
        form_x = self.x + (self.ancho - form_w) // 2
        form_y = self.y + (self.alto - form_h) // 2
        
        # Dibujar el fondo
        pygame.draw.rect(surface, (255, 255, 255), (form_x, form_y, form_w, form_h), border_radius=12)
        pygame.draw.rect(surface, (100, 150, 200), (form_x, form_y, form_w, form_h), 3, border_radius=12)
        
        # Título
        font_title = pygame.font.SysFont("Open Sans", int(self.alto * 0.04), bold=True)
        titulo = "Agregar Materia Prima"
        text_title = font_title.render(titulo, True, (0, 0, 0))
        title_x = form_x + (form_w - text_title.get_width()) // 2
        surface.blit(text_title, (title_x, form_y + 15))
        
        # Campos
        for i, (lbl, pos) in enumerate(self.form_materiaprima_labels):
            adjusted_pos = (form_x + 20, form_y + 60 + i * int(self.alto * 0.07))
            surface.blit(lbl, adjusted_pos)
            
            # Ajustar posición de las cajas
            self.form_materiaprima_boxes[i].rect.x = form_x + int(form_w * 0.4)
            self.form_materiaprima_boxes[i].rect.y = form_y + 55 + i * int(self.alto * 0.07)
            self.form_materiaprima_boxes[i].draw(surface)
        
        # Botones
        # Ajustar botones
        self.form_materiaprima_btn_agregar.x = form_x + int(form_w * 0.2) - 30
        self.form_materiaprima_btn_agregar.y = form_y + form_h - 60
        
        self.form_materiaprima_btn_cancelar.x = form_x + int(form_w * 0.6) - 30
        self.form_materiaprima_btn_cancelar.y = form_y + form_h - 60
        
        # Dibujar botones
        pygame.draw.rect(surface, (100, 200, 100), self.form_materiaprima_btn_agregar, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(self.alto * 0.035), bold=True)
        text_agregar = font_btn.render("Agregar", True, (255, 255, 255))
        agregar_x = self.form_materiaprima_btn_agregar.x + (self.form_materiaprima_btn_agregar.width - text_agregar.get_width()) // 2
        agregar_y = self.form_materiaprima_btn_agregar.y + (self.form_materiaprima_btn_agregar.height - text_agregar.get_height()) // 2
        surface.blit(text_agregar, (agregar_x, agregar_y))
        
        pygame.draw.rect(surface, (200, 100, 100), self.form_materiaprima_btn_cancelar, border_radius=8)
        text_cancelar = font_btn.render("Cancelar", True, (255, 255, 255))
        cancelar_x = self.form_materiaprima_btn_cancelar.x + (self.form_materiaprima_btn_cancelar.width - text_cancelar.get_width()) // 2
        cancelar_y = self.form_materiaprima_btn_cancelar.y + (self.form_materiaprima_btn_cancelar.height - text_cancelar.get_height()) // 2
        surface.blit(text_cancelar, (cancelar_x, cancelar_y))

    def agregar_materiaprima(self):
        """
        Agrega una nueva materia prima a la receta actual.
        
        Returns:
            bool: True si la materia prima fue agregada exitosamente, False en caso contrario
        
        Features:
            - Validación de campos obligatorios
            - Validación numérica para cantidad
            - Búsqueda de materia prima existente en BD
            - Creación de nueva materia prima si no existe
            - Actualización de la tabla de materias primas
        
        Validaciones:
            - Nombre de materia prima requerido
            - Cantidad requerida y debe ser numérica
            - Unidad requerida
        """
        nombre = self.form_materiaprima_boxes[0].get_value().strip()
        cantidad_str = self.form_materiaprima_boxes[1].get_value().strip()
        unidad = self.form_materiaprima_boxes[2].get_value().strip()
        
        # Validaciones
        if not nombre:
            self.mostrar_alerta("Error: Nombre de materia prima es obligatorio")
            return False
            
        if not cantidad_str:
            self.mostrar_alerta("Error: Cantidad es obligatoria")
            return False
            
        if not unidad:
            self.mostrar_alerta("Error: Unidad es obligatoria")
            return False
        
        try:
            cantidad = float(cantidad_str)
            
            # Verificar que tengamos una receta creada o seleccionada
            if not self.receta_seleccionada:
                # Si no hay receta aún, guardar primero y obtener el ID
                if not self.guardar_receta():
                    return False
            
            # Buscar o crear la materia prima en la base de datos
            conexion = Conexion()
            query_materiaprima = "SELECT ID_MateriaPrima FROM materiaprima WHERE Nombre = %s"
            resultado = conexion.consultar(query_materiaprima, (nombre,))
            
            if resultado:
                # Si existe la materia prima, usar su ID
                id_materiaprima = resultado[0]['ID_MateriaPrima']
            else:
                # Si no existe, crear una nueva
                query_insert = """
                    INSERT INTO materiaprima (Nombre, Unidad, Stock, Tipo)
                    VALUES (%s, %s, %s, %s)
                """
                conexion.update(query_insert, (nombre, unidad, 0, "Materia Prima"))  # Stock inicial 0
                
                # Obtener el ID de la nueva materia prima
                query_id = "SELECT LAST_INSERT_ID() AS id"
                resultado = conexion.consultar(query_id)
                id_materiaprima = resultado[0]['id']
            
            # Relacionar la materia prima con la receta
            query_relacion = """
                INSERT INTO receta_materiaprima 
                (ID_Receta, ID_MateriaPrima, cantidad)
                VALUES (%s, %s, %s)
            """
            conexion.update(query_relacion, (
                self.receta_seleccionada, id_materiaprima, cantidad
            ))
            
            # Actualizar la lista de materias primas
            self.cargar_materiasprimas_receta(self.receta_seleccionada)
            self.mostrando_form_materiaprima = False
            self.mostrar_alerta(f"Materia prima '{nombre}' agregada")
            return True
            
        except ValueError:
            self.mostrar_alerta("Error: Formato de cantidad inválido")
            return False
        except Exception as e:
            print(f"Error al agregar materia prima: {e}")
            self.mostrar_alerta("Error: No se pudo agregar la materia prima")
            return False

    def guardar_receta(self):
        """
        Guarda la receta actual en la base de datos.
        
        Returns:
            bool: True si la receta fue guardada exitosamente, False en caso contrario
        
        Features:
            - Crear nueva receta o actualizar existente
            - Validación de campos obligatorios
            - Validación numérica para tiempo y porciones
            - Actualización de la tabla de recetas
        
        Validaciones:
            - Nombre de receta requerido
            - Tiempo de preparación y porciones deben ser numéricos
        """
        nombre = self.formulario_boxes[0].get_value().strip()
        tiempo_str = self.formulario_boxes[1].get_value().strip()
        porciones_str = self.formulario_boxes[2].get_value().strip()
        descripcion = self.formulario_boxes[3].get_value().strip()
        instrucciones = self.formulario_boxes[4].get_value().strip()
        
        # Validaciones
        if not nombre:
            self.formulario_mensaje = "Error: El nombre es obligatorio"
            return False
        
        try:
            tiempo = int(tiempo_str) if tiempo_str else 0
            porciones = int(porciones_str) if porciones_str else 1
            
            conexion = Conexion()
            
            if self.receta_seleccionada:  # Editar existente
                query = """
                    UPDATE receta
                    SET Nombre_receta = %s, Tiempo_Preparacion = %s, No_Unidades = %s,
                        Descripcion = %s, Instrucciones = %s
                    WHERE ID_Receta = %s
                """
                conexion.update(query, (
                    nombre, tiempo, porciones, descripcion, instrucciones,
                    self.receta_seleccionada
                ))
                self.mostrar_alerta(f"Receta '{nombre}' actualizada")
            else:  # Crear nueva
                query = """
                    INSERT INTO receta 
                    (Nombre_receta, Tiempo_Preparacion, No_Unidades, Descripcion, Instrucciones)
                    VALUES (%s, %s, %s, %s, %s)
                """
                conexion.update(query, (
                    nombre, tiempo, porciones, descripcion, instrucciones
                ))
                
                # Obtener el ID de la receta creada
                query_id = "SELECT LAST_INSERT_ID() AS id"
                resultado = conexion.consultar(query_id)
                self.receta_seleccionada = resultado[0]['id']
                self.mostrar_alerta(f"Receta '{nombre}' creada")
            
            # Recargar datos
            self.cargar_datos_tabla()
            return True
            
        except Exception as e:
            print(f"Error al guardar receta: {e}")
            self.formulario_mensaje = f"Error: No se pudo guardar la receta"
            return False

    def handle_event(self, event):
        """
        Maneja los eventos de teclado y mouse para la interfaz.
        
        Args:
            event: Evento de Pygame a procesar
        
        Features:
            - Eventos del formulario de materias primas (prioridad alta)
            - Eventos del formulario principal
            - Eventos de búsqueda y navegación
            - Scroll con mouse y flechas
            - Selección de recetas
        
        Gestiona:
            - Clics en botones (agregar, cancelar, guardar)
            - Entrada de texto en formularios
            - Scroll de tablas con rueda del mouse
            - Búsqueda de recetas
            - Selección de opciones (CREAR, EDITAR, VER)
        """
        # Manejar eventos en el formulario de materias primas (tiene prioridad)
        if self.mostrando_form_materiaprima:
            for box in self.form_materiaprima_boxes:
                box.handle_event(event)
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.form_materiaprima_btn_agregar.collidepoint(event.pos):
                    self.agregar_materiaprima()
                elif self.form_materiaprima_btn_cancelar.collidepoint(event.pos):
                    self.mostrando_form_materiaprima = False
            return
            
        # Manejar eventos en el formulario principal
        if self.mostrando_formulario:
            for box in self.formulario_boxes:
                box.handle_event(event)
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.formulario_btn_guardar.collidepoint(event.pos):
                    if self.guardar_receta():
                        # Si es solo para ver, cerrar después de guardar
                        if self.opcion_seleccionada == "VER":
                            self.mostrando_formulario = False
                elif self.formulario_btn_cancelar.collidepoint(event.pos):
                    self.mostrando_formulario = False
                elif self.formulario_btn_materiasprimas.collidepoint(event.pos):
                    # Si aún no hay receta, guardar primero
                    if not self.receta_seleccionada:
                        if self.guardar_receta():
                            self.mostrar_form_materiaprima()
                    else:
                        self.mostrar_form_materiaprima()
                        
                # Manejo de scroll en tabla de materias primas
                tabla_x = self.x + int(self.ancho * 0.25) + 40
                tabla_y = self.y + int(self.alto * 0.18) + 350
                tabla_width = int(self.ancho * 0.28)
                tabla_height = int(self.alto * 0.15)
                
                if (event.pos[0] > tabla_x and event.pos[0] < tabla_x + tabla_width and
                    event.pos[1] > tabla_y and event.pos[1] < tabla_y + tabla_height):
                    
                    # Clic en flecha arriba
                    if (event.pos[0] > tabla_x + tabla_width - 30 and 
                        event.pos[1] < tabla_y + 30 and 
                        self.tabla_materias_primas_scroll > 0):
                        self.tabla_materias_primas_scroll -= 1
                    
                    # Clic en flecha abajo
                    if (event.pos[0] > tabla_x + tabla_width - 30 and 
                        event.pos[1] > tabla_y + tabla_height - 30 and
                        self.tabla_materias_primas_scroll < len(self.materias_primas_receta) - 5):
                        self.tabla_materias_primas_scroll += 1
            
            # Manejo de rueda del mouse para scroll
            elif event.type == pygame.MOUSEWHEEL:
                tabla_x = self.x + int(self.ancho * 0.25) + 40
                tabla_y = self.y + int(self.alto * 0.18) + 350
                tabla_width = int(self.ancho * 0.28)
                tabla_height = int(self.alto * 0.15)
                
                mouse_pos = pygame.mouse.get_pos()
                if (mouse_pos[0] > tabla_x and mouse_pos[0] < tabla_x + tabla_width and
                    mouse_pos[1] > tabla_y and mouse_pos[1] < tabla_y + tabla_height):
                    
                    if event.y > 0 and self.tabla_materias_primas_scroll > 0:
                        self.tabla_materias_primas_scroll -= 1
                    elif event.y < 0 and self.tabla_materias_primas_scroll < len(self.materias_primas_receta) - 5:
                        self.tabla_materias_primas_scroll += 1
                        
            return

        # Eventos generales cuando no hay formularios abiertos
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.agregar_hover = self.boton_agregar_rect.collidepoint(mouse_pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Verificar si se hizo clic en los botones de opción
            for i, rect in enumerate(self.boton_rects):
                if rect.collidepoint(mouse_pos):
                    self.opcion_seleccionada = self.botones_opciones[i]
                    self.cargar_datos_tabla()
                    return
            
            # Verificar si se hizo clic en el botón agregar
            if self.boton_agregar_rect.collidepoint(mouse_pos):
                if self.opcion_seleccionada == "CREAR":
                    # Mostrar formulario para crear receta
                    self.mostrar_formulario()
                elif self.opcion_seleccionada == "EDITAR":
                    # Verificar si hay receta seleccionada
                    if hasattr(self, 'receta_seleccionada_data') and self.receta_seleccionada_data:
                        self.mostrar_formulario(self.receta_seleccionada_data)
                    else:
                        self.mostrar_alerta("Seleccione una receta para editar")
                elif self.opcion_seleccionada == "VER":
                    # Verificar si hay receta seleccionada
                    if hasattr(self, 'receta_seleccionada_data') and self.receta_seleccionada_data:
                        self.mostrar_formulario(self.receta_seleccionada_data)
                    else:
                        self.mostrar_alerta("Seleccione una receta para ver")
                return
                
            # Verificar clic en el campo de búsqueda
            busq_x = self.x + int(self.ancho * 0.02)
            busq_y = self.y + int(self.alto * 0.11)
            busq_w = int(self.ancho * 0.35)
            busq_h = self.boton_height
            busq_rect = pygame.Rect(busq_x, busq_y, busq_w, busq_h)
            if busq_rect.collidepoint(mouse_pos):
                self.busqueda_activa = True
            else:
                self.busqueda_activa = False
                
            # Verificar clic en la tabla para seleccionar una receta
            tabla_x = self.x + int(self.ancho * 0.03)
            tabla_y = self.y + int(self.alto * 0.23) + int(self.alto * 0.07)  # Saltamos el encabezado
            tabla_width = int(self.ancho * 0.94)
            row_height = int(self.alto * 0.07)
            
            for i, fila in enumerate(self.datos_tabla):
                row_rect = pygame.Rect(tabla_x, tabla_y + i * row_height, tabla_width, row_height)
                if row_rect.collidepoint(mouse_pos):
                    # Seleccionar esta receta
                    self.receta_seleccionada_data = self.datos_tabla[i]
                    self.mostrar_alerta(f"Receta '{self.receta_seleccionada_data['nombre']}' seleccionada")
                    break
        
        # Manejo de teclado para búsqueda
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