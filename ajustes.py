
import os
import tkinter as tk
from tkinter import filedialog
from receta import Conexion
from conexion import resource_path
import datetime
import re
import pygame
class InputBox:
    """
    Clase para crear campos de entrada de texto personalizados en Pygame

    Attributes:
        rect (pygame.Rect): Posición y tamaño del campo
        color_inactive (pygame.Color): Color cuando no está seleccionado
        color_active (pygame.Color): Color cuando está seleccionado
        text (str): Texto actual en el campo
        font (pygame.font.Font): Fuente utilizada para el texto
        active (bool): Estado de activación del campo
    """

    def __init__(self, x, y, w, h, text='', font=None, allowed_options=None):
        """
        Inicializa un campo de entrada

        Args:
            x (int): Posición x
            y (int): Posición y
            w (int): Ancho del campo
            h (int): Alto del campo
            text (str, optional): Texto inicial. Defaults to ''.
            font (pygame.font.Font, optional): Fuente del texto. Defaults to None.
            allowed_options (list, optional): Opciones permitidas para validación. Defaults to None.
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.font = font or pygame.font.SysFont("Open Sans", 24)
        self.txt_surface = self.font.render(text, True, (0, 0, 0))
        self.active = False
        self.allowed_options = allowed_options

    def handle_event(self, event):
        """
        Maneja eventos de mouse y teclado para el campo

        Args:
            event (pygame.event.Event): Evento de Pygame
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Activar/desactivar campo según clic
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
                self.validate_text()  # Validar texto al perder el enfoque
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            # Manejar teclas cuando está activo
            if event.key == pygame.K_RETURN:
                self.active = False
                self.validate_text()  # Validar texto al presionar Enter
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Agregar caracteres imprimibles
                if len(self.text) < 100 and event.unicode.isprintable():
                    self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, (0, 0, 0))

    def validate_text(self):
        """
        Valida que el texto ingresado sea una de las opciones permitidas
        """
        if self.allowed_options and self.text not in self.allowed_options:
            self.text = ""
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
            str: Texto actual
        """
        return self.text

    def set_value(self, value):
        """
        Establece un nuevo valor en el campo

        Args:
            value (str): Nuevo valor
        """
        self.text = value
        self.txt_surface = self.font.render(self.text, True, (0, 0, 0))

class ajustes:
    def __init__(self, x=320, y=250, ancho=1555, alto=710):
        """
        Inicializa el sistema de ajustes

        Args:
            x (int): Posición x. Defaults to 320.
            y (int): Posición y. Defaults to 250.
            ancho (int): Ancho de la interfaz. Defaults to 1555.
            alto (int): Alto de la interfaz. Defaults to 710.
        """
        pygame.font.init()
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

        # Configuración visual
        self.FONDO = (241, 236, 227)

        def fuente_relativa(base_size):
            """Calcula tamaño de fuente relativo a las dimensiones"""
            scale = min(self.ancho / 1555, self.alto / 710)
            return int(base_size * scale)

        self.fuente_titulo = pygame.font.SysFont("Times New Roman", int(self.alto * 0.08), bold=True)
        self.color_texto = (0, 0, 0)

        # Configuración de navegación
        self.botones_opciones = ["GENERAL", "EMPLEADOS", "CLIENTES", "PROVEEDORES"]
        self.opcion_seleccionada = self.botones_opciones[0]
        self.fuente_boton = pygame.font.SysFont("Open Sans", int(self.alto * 0.045), bold=True)

        # Crear rectángulos para botones de navegación
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

        # Variables de scroll para cada tabla
        self.scroll_empleados = 0
        self.scroll_clientes = 0
        self.scroll_proveedores = 0
        self.scroll_speed = 30

        # --- Configuración de sección GENERAL ---
        self.info_negocio = {
            "nombre": "Panadería Bambi",
            "direccion": "Calle Ejemplo 123, Centro",
            "telefono": "5551234567",
            "email": "contacto@bambi.com",
            "logo_path": resource_path("imagenes/log.png")
        }

        # Cargar logo
        self.logo_img = pygame.image.load(self.info_negocio["logo_path"])
        self.logo_img = pygame.transform.scale(self.logo_img, (int(0.08*self.ancho), int(0.17*self.alto)))

        # Crear campos de entrada para información general
        font = pygame.font.SysFont("Open Sans", fuente_relativa(24))
        self.input_nombre = InputBox(self.x + int(0.25*self.ancho), self.y + int(0.10*self.alto), int(0.26*self.ancho), int(0.06*self.alto), self.info_negocio["nombre"], font)
        self.input_direccion = InputBox(self.x + int(0.25*self.ancho), self.y + int(0.18*self.alto), int(0.26*self.ancho), int(0.06*self.alto), self.info_negocio["direccion"], font)
        self.input_telefono = InputBox(self.x + int(0.25*self.ancho), self.y + int(0.26*self.alto), int(0.26*self.ancho), int(0.06*self.alto), self.info_negocio["telefono"], font)
        self.input_email = InputBox(self.x + int(0.25*self.ancho), self.y + int(0.34*self.alto), int(0.26*self.ancho), int(0.06*self.alto), self.info_negocio["email"], font)

        # Botones de sección general
        self.btn_cambiar_logo = pygame.Rect(self.x + int(0.36*self.ancho), self.y + int(0.44*self.alto), int(0.13*self.ancho), int(0.07*self.alto))
        self.btn_cancelar = pygame.Rect(self.x + int(0.52*self.ancho), self.y + int(0.60*self.alto), int(0.12*self.ancho), int(0.07*self.alto))
        self.cambiar_logo_hover = False
        self.cancelar_hover = False

        # --- Configuración de sección EMPLEADOS ---
        self.btn_nuevo_empleado = pygame.Rect(self.x + int(0.60*self.ancho), self.y + int(0.08*self.alto), int(0.14*self.ancho), int(0.07*self.alto))
        self.nuevo_empleado_hover = False
        self.mostrando_formulario_empleado = False
        self.formulario_empleado_boxes = []
        self.formulario_empleado_labels = []
        self.formulario_empleado_btn_guardar = None
        self.formulario_empleado_btn_cancelar = None
        self.formulario_empleado_mensaje = ""
        self.empleados = []
        self.cargar_empleados()

        # --- Configuración de sección CLIENTES ---
        self.btn_nuevo_cliente = pygame.Rect(self.x + int(0.60*self.ancho), self.y + int(0.08*self.alto), int(0.14*self.ancho), int(0.07*self.alto))
        self.nuevo_cliente_hover = False
        self.mostrando_formulario_cliente = False
        self.formulario_cliente_boxes = []
        self.formulario_cliente_labels = []
        self.formulario_cliente_btn_guardar = None
        self.formulario_cliente_btn_cancelar = None
        self.formulario_cliente_mensaje = ""
        self.clientes = []
        self.cargar_clientes()

        # --- Configuración de sección PROVEEDORES ---
        self.btn_nuevo_proveedor = pygame.Rect(self.x + int(0.60*self.ancho), self.y + int(0.08*self.alto), int(0.14*self.ancho), int(0.07*self.alto))
        self.nuevo_proveedor_hover = False
        self.mostrando_formulario_proveedor = False
        self.formulario_proveedor_boxes = []
        self.formulario_proveedor_labels = []
        self.formulario_proveedor_btn_guardar = None
        self.formulario_proveedor_btn_cancelar = None
        self.formulario_proveedor_mensaje = ""
        self.proveedores = []
        self.cargar_proveedores()

        # Variables para edición de tablas
        self.celda_editando = None  # (seccion, fila_idx, col_idx, key)
        self.input_edicion = None
        self.mensaje_edicion = ""
        self.celdas_empleados = []
        self.celdas_clientes = []
        self.celdas_proveedores = []
        self.ultimo_clic_tiempo = 0
        self.ultima_celda_clic = None

    def calcular_x_centrada(self, col_widths):
        """
        Calcula la posición X para centrar una tabla

        Args:
            col_widths (list): Anchos de las columnas

        Returns:
            int: Posición X centrada
        """
        ancho_tabla = sum(col_widths)
        return self.x + (self.ancho - ancho_tabla) // 2

    def dibujar(self, surface):
        """
        Dibuja la interfaz principal y delega a la sección activa

        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Dibujar fondo y título
        pygame.draw.rect(surface, self.FONDO, (self.x, self.y, self.ancho, self.alto))
        titulo = self.fuente_titulo.render("Ajustes", True, self.color_texto)
        surface.blit(titulo, (self.x + int(0.02*self.ancho), self.y + int(0.02*self.alto)))

        # Dibujar botones de navegación
        for i, rect in enumerate(self.boton_rects):
            color = self.color_boton_activo if self.opcion_seleccionada == self.botones_opciones[i] else self.color_boton
            pygame.draw.rect(surface, color, rect, border_radius=10)
            texto_boton = self.fuente_boton.render(self.botones_opciones[i], True, self.color_texto)
            text_rect = texto_boton.get_rect(center=rect.center)
            surface.blit(texto_boton, text_rect)

        # Dibujar sección activa
        if self.opcion_seleccionada == "GENERAL":
            self.dibujar_formulario_general(surface)
        elif self.opcion_seleccionada == "EMPLEADOS":
            self.dibujar_empleados(surface)
        elif self.opcion_seleccionada == "CLIENTES":
            self.dibujar_clientes(surface)
        elif self.opcion_seleccionada == "PROVEEDORES":
            self.dibujar_proveedores(surface)

    def dibujar_formulario_general(self, surface):
        """
        Dibuja la sección de información general del negocio

        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        font_titulo = pygame.font.SysFont("Open Sans", int(0.045*self.alto), bold=True)
        font_label = pygame.font.SysFont("Open Sans", int(0.032*self.alto))

        # Título y subtítulo
        surface.blit(font_titulo.render("Información del Negocio", True, (0, 0, 0)), (self.x + int(0.20*self.ancho), self.y + int(0.18*self.alto)))
        surface.blit(font_label.render("Modifica la información general de tu panadería", True, (80, 80, 80)), (self.x + int(0.20*self.ancho), self.y + int(0.22*self.alto)))

        # Calcular posiciones para labels e inputs
        y_base = self.y + int(0.28*self.alto)
        y_step = int(0.08*self.alto)

        # Nombre del negocio
        surface.blit(font_label.render("Nombre del Negocio:", True, (0, 0, 0)), (self.x + int(0.10*self.ancho), y_base))
        self.input_nombre.rect.y = y_base
        self.input_nombre.draw(surface)

        # Dirección
        surface.blit(font_label.render("Dirección:", True, (0, 0, 0)), (self.x + int(0.10*self.ancho), y_base + y_step))
        self.input_direccion.rect.y = y_base + y_step
        self.input_direccion.draw(surface)

        # Teléfono
        surface.blit(font_label.render("Teléfono:", True, (0, 0, 0)), (self.x + int(0.10*self.ancho), y_base + 2*y_step))
        self.input_telefono.rect.y = y_base + 2*y_step
        self.input_telefono.draw(surface)

        # Email
        surface.blit(font_label.render("Email de Contacto:", True, (0, 0, 0)), (self.x + int(0.10*self.ancho), y_base + 3*y_step))
        self.input_email.rect.y = y_base + 3*y_step
        self.input_email.draw(surface)

        # Logo del negocio
        surface.blit(font_label.render("Logo del Negocio:", True, (0, 0, 0)), (self.x + int(0.10*self.ancho), y_base + 4*y_step))
        surface.blit(self.logo_img, (self.x + int(0.25*self.ancho), y_base + 4*y_step))

        # Botón cambiar logo
        color_logo = (0, 120, 220) if self.cambiar_logo_hover else (0, 180, 255)
        self.btn_cambiar_logo.y = y_base + 4*y_step
        pygame.draw.rect(surface, color_logo, self.btn_cambiar_logo, border_radius=8)
        pygame.draw.rect(surface, (0, 80, 180), self.btn_cambiar_logo, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.032*self.alto), bold=True)
        btn_text = font_btn.render("Cambiar Logo", True, (255, 255, 255))
        surface.blit(btn_text, (self.btn_cambiar_logo.x + (self.btn_cambiar_logo.w - btn_text.get_width()) // 2,
                                self.btn_cambiar_logo.y + (self.btn_cambiar_logo.h - btn_text.get_height()) // 2))

        # Botón cancelar
        color_cancel = (200, 80, 80) if self.cancelar_hover else (255, 100, 100)
        self.btn_cancelar.y = y_base + 6*y_step
        pygame.draw.rect(surface, color_cancel, self.btn_cancelar, border_radius=8)
        pygame.draw.rect(surface, (120, 0, 0), self.btn_cancelar, 2, border_radius=8)
        btn_text_cancel = font_btn.render("Cancelar", True, (255, 255, 255))
        surface.blit(btn_text_cancel, (self.btn_cancelar.x + (self.btn_cancelar.w - btn_text_cancel.get_width()) // 2,
                                    self.btn_cancelar.y + (self.btn_cancelar.h - btn_text_cancel.get_height()) // 2))

    def cargar_empleados(self):
        """
        Carga la lista de empleados activos desde la base de datos
        """
        conexion = Conexion()
        query = """
            SELECT
                Id_Empleado AS id,
                Nombre_emple AS nombre,
                Ap_Paterno_emple AS ap_paterno,
                Ap_Materno_emple AS ap_materno,
                CURP_emple AS curp,
                Sexo AS sexo,
                RFC_emple AS rfc,
                NSS AS nss,
                Correo_Electronico AS correo,
                Telefono_emple AS telefono,
                Padecimientos AS padecimientos,
                Calle AS calle,
                Colonia AS colonia,
                Cod_Postal AS cp,
                stoPuesto AS puesto,
                Fecha_Contratacion AS fecha_contratacion,
                Estado_emple AS estado
            FROM Empleado
            WHERE Estado_emple = 'Activo'
        """
        self.empleados = conexion.consultar(query)

    def dibujar_empleados(self, surface):
        """
        Dibuja la sección de gestión de empleados

        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        font_titulo = pygame.font.SysFont("Open Sans", int(0.045 * self.alto), bold=True)
        font_label = pygame.font.SysFont("Open Sans", int(0.032 * self.alto))

        # Título y subtítulo
        surface.blit(font_titulo.render("Gestión de Empleados", True, (0, 0, 0)), (self.x + int(0.20 * self.ancho), self.y + int(0.18 * self.alto)))
        surface.blit(font_label.render("Administra los empleados de tu panadería", True, (80, 80, 80)), (self.x + int(0.20 * self.ancho), self.y + int(0.22 * self.alto)))

        # Botón nuevo empleado
        btn_y = self.y + int(0.18 * self.alto)
        self.btn_nuevo_empleado.y = btn_y
        color_nuevo = (0, 120, 220) if self.nuevo_empleado_hover else (0, 180, 255)
        pygame.draw.rect(surface, color_nuevo, self.btn_nuevo_empleado, border_radius=8)
        pygame.draw.rect(surface, (0, 80, 180), self.btn_nuevo_empleado, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        btn_text = font_btn.render("Nuevo Empleado", True, (255, 255, 255))
        surface.blit(btn_text, (self.btn_nuevo_empleado.x + (self.btn_nuevo_empleado.w - btn_text.get_width()) // 2,
                                self.btn_nuevo_empleado.y + (self.btn_nuevo_empleado.h - btn_text.get_height()) // 2))

        # Tabla de empleados con scroll
        tabla_y = self.y + int(0.32 * self.alto)
        self.dibujar_tabla_empleados_con_scroll(surface, y=tabla_y, row_height=32, datos=self.empleados)

        # Formulario si está activo
        if self.mostrando_formulario_empleado:
            self.dibujar_formulario_nuevo_empleado(surface)

    def dibujar_tabla_empleados_con_scroll(self, surface, y, row_height, datos):
        """
        Dibuja una tabla editable con scroll para empleados
        """
        columnas = [
            "Nombre", "Ap. Paterno", "Ap. Materno", "CURP", "Sexo", "RFC", "NSS",
            "Correo", "Teléfono"
        ]
        col_keys = [
            "nombre", "ap_paterno", "ap_materno", "curp", "sexo", "rfc", "nss",
            "correo", "telefono"
        ]
        col_widths = [170, 150, 150, 170, 100, 150, 140, 150, 130]

        # Área visible de la tabla
        tabla_rect = pygame.Rect(self.x + 50, y, self.ancho - 100, self.alto - (y - self.y) - 50)
        max_filas_visibles = (tabla_rect.height - row_height) // row_height
        
        # Calcular scroll máximo
        max_scroll = max(0, len(datos) - max_filas_visibles)
        self.scroll_empleados = max(0, min(self.scroll_empleados, max_scroll))

        # Crear superficie para la tabla con scroll
        tabla_surface = pygame.Surface((tabla_rect.width, tabla_rect.height))
        tabla_surface.fill((255, 255, 255))

        # Centrar tabla en la superficie
        ancho_tabla = sum(col_widths)
        x_tabla = (tabla_rect.width - ancho_tabla) // 2

        # Limpiar referencias de celdas
        self.celdas_empleados = []

        # Dibujar encabezados
        font = pygame.font.SysFont("Open Sans", 20, bold=True)
        col_x = x_tabla
        for i, col in enumerate(columnas):
            pygame.draw.rect(tabla_surface, (200, 200, 255), (col_x, 0, col_widths[i], row_height))
            pygame.draw.rect(tabla_surface, (180, 180, 180), (col_x, 0, col_widths[i], row_height), 2)
            texto = font.render(col, True, (0, 0, 0))
            text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, row_height // 2))
            tabla_surface.blit(texto, text_rect)
            col_x += col_widths[i]

        # Dibujar filas visibles de datos
        font_row = pygame.font.SysFont("Open Sans", 18)
        inicio_fila = self.scroll_empleados
        fin_fila = min(inicio_fila + max_filas_visibles, len(datos))

        for idx in range(inicio_fila, fin_fila):
            fila = datos[idx]
            fila_y = row_height + (idx - inicio_fila) * row_height
            col_x = x_tabla
            
            for i, key in enumerate(col_keys):
                # Crear rectángulo para la celda (ajustado por scroll)
                celda_rect = pygame.Rect(tabla_rect.x + col_x, tabla_rect.y + fila_y, col_widths[i], row_height)
                
                # Color de la celda
                color_celda = (255, 255, 255)
                if (self.celda_editando and self.celda_editando[0] == "empleados" and 
                    self.celda_editando[1] == idx and self.celda_editando[2] == i):
                    color_celda = (220, 240, 255)
                
                pygame.draw.rect(tabla_surface, color_celda, (col_x, fila_y, col_widths[i], row_height))
                pygame.draw.rect(tabla_surface, (180, 180, 180), (col_x, fila_y, col_widths[i], row_height), 1)
                
                # Contenido de la celda
                if (self.celda_editando and self.celda_editando[0] == "empleados" and 
                    self.celda_editando[1] == idx and self.celda_editando[2] == i and 
                    self.input_edicion):
                    # Dibujar input de edición
                    self.input_edicion.rect.x = tabla_rect.x + col_x + 5
                    self.input_edicion.rect.y = tabla_rect.y + fila_y + (row_height - self.input_edicion.rect.height) // 2
                    self.input_edicion.rect.width = col_widths[i] - 10
                else:
                    # Mostrar valor normal
                    valor = str(fila[key])
                    if len(valor) > 15:  # Truncar texto largo
                        valor = valor[:12] + "..."
                    texto = font_row.render(valor, True, (0, 0, 0))
                    text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, fila_y + row_height // 2))
                    tabla_surface.blit(texto, text_rect)
                
                # Guardar referencia a la celda
                if key != "id":
                    self.celdas_empleados.append((celda_rect, idx, i, key, fila["id"]))
                    
                col_x += col_widths[i]

        # Dibujar tabla en la superficie principal
        surface.blit(tabla_surface, tabla_rect)

        # Dibujar scrollbar si es necesario
        if len(datos) > max_filas_visibles:
            self.dibujar_scrollbar(surface, tabla_rect, self.scroll_empleados, max_scroll)

        # Dibujar input de edición si está activo
        if self.input_edicion and self.celda_editando and self.celda_editando[0] == "empleados":
            self.input_edicion.draw(surface)

    def dibujar_scrollbar(self, surface, tabla_rect, scroll_actual, scroll_max):
        """
        Dibuja una barra de scroll vertical
        """
        if scroll_max <= 0:
            return
            
        scrollbar_width = 15
        scrollbar_x = tabla_rect.right - scrollbar_width
        scrollbar_rect = pygame.Rect(scrollbar_x, tabla_rect.y, scrollbar_width, tabla_rect.height)
        
        # Fondo del scrollbar
        pygame.draw.rect(surface, (200, 200, 200), scrollbar_rect)
        pygame.draw.rect(surface, (150, 150, 150), scrollbar_rect, 2)
        
        # Calcular posición del thumb
        thumb_height = max(20, tabla_rect.height * tabla_rect.height // (tabla_rect.height + scroll_max * 32))
        thumb_y = tabla_rect.y + (scroll_actual / scroll_max) * (tabla_rect.height - thumb_height)
        thumb_rect = pygame.Rect(scrollbar_x + 2, thumb_y, scrollbar_width - 4, thumb_height)
        
        # Dibujar thumb
        pygame.draw.rect(surface, (100, 100, 100), thumb_rect, border_radius=5)

    def cargar_clientes(self):
        """
        Carga la lista de clientes activos desde la base de datos
        """
        conexion = Conexion()
        query = """
            SELECT Id_Cliente AS id, Nombre_Cliente AS nombre, Ap_Paterno_cliente AS ap_paterno,
                Ap_Materno_cliente AS ap_materno, Telefono_cli AS telefono, Correo AS correo,
                RFC AS rfc, Calle AS calle, Colonia AS colonia, Cod_Postal AS cod_postal, Estado
            FROM Cliente
            WHERE Estado = 'Activo'
        """
        self.clientes = conexion.consultar(query)

    def dibujar_clientes(self, surface):
        """
        Dibuja la sección de gestión de clientes

        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        font_titulo = pygame.font.SysFont("Open Sans", int(0.045 * self.alto), bold=True)
        font_label = pygame.font.SysFont("Open Sans", int(0.032 * self.alto))

        # Título y subtítulo
        surface.blit(font_titulo.render("Gestión de Clientes", True, (0, 0, 0)), (self.x + int(0.20 * self.ancho), self.y + int(0.18 * self.alto)))
        surface.blit(font_label.render("Administra los clientes de tu panadería", True, (80, 80, 80)), (self.x + int(0.20 * self.ancho), self.y + int(0.22 * self.alto)))

        # Botón nuevo cliente
        btn_y = self.y + int(0.18 * self.alto)
        self.btn_nuevo_cliente.y = btn_y
        color_nuevo = (0, 120, 220) if self.nuevo_cliente_hover else (0, 180, 255)
        pygame.draw.rect(surface, color_nuevo, self.btn_nuevo_cliente, border_radius=8)
        pygame.draw.rect(surface, (0, 80, 180), self.btn_nuevo_cliente, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        btn_text = font_btn.render("Nuevo Cliente", True, (255, 255, 255))
        surface.blit(btn_text, (self.btn_nuevo_cliente.x + (self.btn_nuevo_cliente.w - btn_text.get_width()) // 2,
                                self.btn_nuevo_cliente.y + (self.btn_nuevo_cliente.h - btn_text.get_height()) // 2))

        # Tabla de clientes con scroll
        tabla_y = self.y + int(0.32 * self.alto)
        self.dibujar_tabla_clientes_con_scroll(surface, y=tabla_y, row_height=50, datos=self.clientes)

        # Formulario si está activo
        if self.mostrando_formulario_cliente:
            self.dibujar_formulario_nuevo_cliente(surface)

    def dibujar_tabla_clientes_con_scroll(self, surface, y, row_height, datos):
        """
        Dibuja una tabla editable con scroll para clientes
        """
        columnas = ["Nombre", "Apellido Paterno", "Apellido Materno", "Teléfono", "Correo", "RFC", "Calle", "Colonia", "CP"]
        col_keys = ["nombre", "ap_paterno", "ap_materno", "telefono", "correo", "rfc", "calle", "colonia", "cod_postal"]
        col_widths = [160, 130, 130, 130, 190, 110, 130, 130, 80]

        # Área visible de la tabla
        tabla_rect = pygame.Rect(self.x + 50, y, self.ancho - 100, self.alto - (y - self.y) - 50)
        max_filas_visibles = (tabla_rect.height - row_height) // row_height
        
        # Calcular scroll máximo
        max_scroll = max(0, len(datos) - max_filas_visibles)
        self.scroll_clientes = max(0, min(self.scroll_clientes, max_scroll))

        # Crear superficie para la tabla con scroll
        tabla_surface = pygame.Surface((tabla_rect.width, tabla_rect.height))
        tabla_surface.fill((255, 255, 255))

        # Centrar tabla en la superficie
        ancho_tabla = sum(col_widths)
        x_tabla = (tabla_rect.width - ancho_tabla) // 2

        # Limpiar referencias de celdas
        self.celdas_clientes = []

        # Dibujar encabezados
        font = pygame.font.SysFont("Open Sans", 20, bold=True)
        col_x = x_tabla
        for i, col in enumerate(columnas):
            pygame.draw.rect(tabla_surface, (200, 255, 200), (col_x, 0, col_widths[i], row_height))
            pygame.draw.rect(tabla_surface, (180, 180, 180), (col_x, 0, col_widths[i], row_height), 2)
            texto = font.render(col, True, (0, 0, 0))
            text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, row_height // 2))
            tabla_surface.blit(texto, text_rect)
            col_x += col_widths[i]

        # Dibujar filas visibles de datos
        font_row = pygame.font.SysFont("Open Sans", 18)
        inicio_fila = self.scroll_clientes
        fin_fila = min(inicio_fila + max_filas_visibles, len(datos))

        for idx in range(inicio_fila, fin_fila):
            fila = datos[idx]
            fila_y = row_height + (idx - inicio_fila) * row_height
            col_x = x_tabla
            
            for i, key in enumerate(col_keys):
                # Crear rectángulo para la celda
                celda_rect = pygame.Rect(tabla_rect.x + col_x, tabla_rect.y + fila_y, col_widths[i], row_height)
                
                # Color de la celda
                color_celda = (255, 255, 255)
                if (self.celda_editando and self.celda_editando[0] == "clientes" and 
                    self.celda_editando[1] == idx and self.celda_editando[2] == i):
                    color_celda = (220, 240, 255)
                
                pygame.draw.rect(tabla_surface, color_celda, (col_x, fila_y, col_widths[i], row_height))
                pygame.draw.rect(tabla_surface, (180, 180, 180), (col_x, fila_y, col_widths[i], row_height), 1)
                
                # Contenido de la celda
                if (self.celda_editando and self.celda_editando[0] == "clientes" and 
                    self.celda_editando[1] == idx and self.celda_editando[2] == i and 
                    self.input_edicion):
                    self.input_edicion.rect.x = tabla_rect.x + col_x + 5
                    self.input_edicion.rect.y = tabla_rect.y + fila_y + (row_height - self.input_edicion.rect.height) // 2
                    self.input_edicion.rect.width = col_widths[i] - 10
                else:
                    valor = str(fila[key])
                    if len(valor) > 15:
                        valor = valor[:12] + "..."
                    texto = font_row.render(valor, True, (0, 0, 0))
                    text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, fila_y + row_height // 2))
                    tabla_surface.blit(texto, text_rect)
                
                # Guardar referencia a la celda
                if key != "id":
                    self.celdas_clientes.append((celda_rect, idx, i, key, fila["id"]))
                    
                col_x += col_widths[i]

        # Dibujar tabla en la superficie principal
        surface.blit(tabla_surface, tabla_rect)

        # Dibujar scrollbar si es necesario
        if len(datos) > max_filas_visibles:
            self.dibujar_scrollbar(surface, tabla_rect, self.scroll_clientes, max_scroll)

        # Dibujar input de edición si está activo
        if self.input_edicion and self.celda_editando and self.celda_editando[0] == "clientes":
            self.input_edicion.draw(surface)

    def mostrar_formulario_nuevo_cliente(self):
        """
        Configura y muestra el formulario para agregar un nuevo cliente
        """
        self.mostrando_formulario_cliente = True
        font = pygame.font.SysFont("Open Sans", 18)

        # Campos del formulario
        labels = [
            "Nombre", "Apellido Paterno", "Apellido Materno", "Teléfono", "Correo",
            "RFC", "Calle", "Colonia", "CP"
        ]

        # Configuración de diseño
        num_cols = 2
        num_rows = (len(labels) + 1) // 2
        self.formulario_cliente_labels = []
        self.formulario_cliente_boxes = []

        # Dimensiones del modal
        modal_x = self.x + int(0.15 * self.ancho)
        modal_y = self.y + int(0.18 * self.alto)
        modal_w = int(0.7 * self.ancho)
        modal_h = int(0.6 * self.alto)

        # Dimensiones de campos
        label_width = int(0.18 * modal_w)
        input_width = int(0.28 * modal_w)
        row_height = int(0.09 * modal_h)
        col_gap = int(0.04 * modal_w)

        # Crear campos de entrada
        for i, label in enumerate(labels):
            col = i // num_rows
            row = i % num_rows
            lx = modal_x + 40 + col * (label_width + input_width + col_gap)
            ly = modal_y + 70 + row * row_height
            self.formulario_cliente_labels.append((label + ":", (lx, ly)))
            box = InputBox(lx + label_width, ly, input_width, 32, font=font)
            self.formulario_cliente_boxes.append(box)

        # Botones del formulario
        btn_y = modal_y + 70 + num_rows * row_height + 30
        btn_w = 180
        btn_h = 40
        btn_x = modal_x + (modal_w - 2 * btn_w - 40) // 2
        self.formulario_cliente_btn_guardar = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.formulario_cliente_btn_cancelar = pygame.Rect(btn_x + btn_w + 40, btn_y, btn_w, btn_h)
        self.formulario_cliente_mensaje = ""

    def dibujar_formulario_nuevo_cliente(self, surface):
        """
        Dibuja el formulario para agregar un nuevo cliente

        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Dimensiones del modal
        modal_x = self.x + int(0.15 * self.ancho)
        modal_y = self.y + int(0.18 * self.alto)
        modal_w = int(0.73 * self.ancho)
        modal_h = int(0.6 * self.alto)
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        # Dibujar fondo del modal
        pygame.draw.rect(surface, (245, 245, 245), modal_rect, border_radius=18)
        pygame.draw.rect(surface, (0, 120, 220), modal_rect, 3, border_radius=18)

        # Título del formulario
        font = pygame.font.SysFont("Open Sans", int(0.035 * self.alto), bold=True)
        titulo = font.render("Nuevo Cliente", True, (0, 0, 0))
        surface.blit(titulo, (modal_x + 30, modal_y + 20))

        # Dibujar labels y campos
        font_label = pygame.font.SysFont("Open Sans", int(0.025 * self.alto))
        for (label_text, (lx, ly)), box in zip(self.formulario_cliente_labels, self.formulario_cliente_boxes):
            surface.blit(font_label.render(label_text, True, (0, 0, 0)), (lx, ly))
            box.draw(surface)

        # Botón guardar
        pygame.draw.rect(surface, (0, 180, 0), self.formulario_cliente_btn_guardar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.formulario_cliente_btn_guardar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.027 * self.alto), bold=True)
        btn_text = font_btn.render("Guardar", True, (255, 255, 255))
        surface.blit(btn_text, (self.formulario_cliente_btn_guardar.x + (self.formulario_cliente_btn_guardar.w - btn_text.get_width()) // 2,
                                self.formulario_cliente_btn_guardar.y + (self.formulario_cliente_btn_guardar.h - btn_text.get_height()) // 2))

        # Botón cancelar
        pygame.draw.rect(surface, (200, 80, 80), self.formulario_cliente_btn_cancelar, border_radius=8)
        pygame.draw.rect(surface, (120, 0, 0), self.formulario_cliente_btn_cancelar, 2, border_radius=8)
        btn_text_cancel = font_btn.render("Cancelar", True, (255, 255, 255))
        surface.blit(btn_text_cancel, (self.formulario_cliente_btn_cancelar.x + (self.formulario_cliente_btn_cancelar.w - btn_text_cancel.get_width()) // 2,
                                    self.formulario_cliente_btn_cancelar.y + (self.formulario_cliente_btn_cancelar.h - btn_text_cancel.get_height()) // 2))

        # Mensaje de error/éxito
        if self.formulario_cliente_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
            msg = font_msg.render(self.formulario_cliente_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_x + 30, self.formulario_cliente_btn_guardar.y + 60))

    def guardar_nuevo_cliente(self):
        """
        Valida y guarda un nuevo cliente en la base de datos con validaciones completas
        """
        try:
            valores = [box.get_value().strip() for box in self.formulario_cliente_boxes]
            if not all(valores):
                self.formulario_cliente_mensaje = "Todos los campos son obligatorios."
                return

            nombre, ap_paterno, ap_materno, telefono, correo, rfc, calle, colonia, cp = valores
            
            # 1. Validar que solo contengan letras (nombres y apellidos)
            if not all(c.isalpha() or c.isspace() for c in nombre):
                self.formulario_cliente_mensaje = "El nombre solo debe contener letras."
                return
            if not all(c.isalpha() or c.isspace() for c in ap_paterno):
                self.formulario_cliente_mensaje = "El apellido paterno solo debe contener letras."
                return
            if not all(c.isalpha() or c.isspace() for c in ap_materno):
                self.formulario_cliente_mensaje = "El apellido materno solo debe contener letras."
                return
            
            # 2. Validar teléfono (solo números, 10 dígitos)
            try:
                telefono_num = int(telefono)
                if len(telefono) != 10:
                    self.formulario_cliente_mensaje = "El teléfono debe tener 10 dígitos."
                    return
            except ValueError:
                self.formulario_cliente_mensaje = "El teléfono debe contener solo números."
                return
            
            # 3. Validar correo electrónico
            if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
                self.formulario_cliente_mensaje = "El formato del correo es inválido."
                return
            
            # 4. Validar RFC (12-13 caracteres alfanuméricos)
            if len(rfc) not in (12, 13) or not rfc.isalnum():
                self.formulario_cliente_mensaje = "El RFC debe tener 12 o 13 caracteres alfanuméricos."
                return
            
            # 5. Validar código postal (solo números, 5 dígitos)
            try:
                cp_num = int(cp)
                if len(cp) != 5:
                    self.formulario_cliente_mensaje = "El código postal debe tener 5 dígitos."
                    return
            except ValueError:
                self.formulario_cliente_mensaje = "El código postal debe contener solo números."
                return
            
            # 6. Validar calle y colonia (alfanuméricos y espacios)
            if not all(c.isalnum() or c.isspace() for c in calle):
                self.formulario_cliente_mensaje = "La calle solo debe contener letras, números y espacios."
                return
            if not all(c.isalnum() or c.isspace() for c in colonia):
                self.formulario_cliente_mensaje = "La colonia solo debe contener letras, números y espacios."
                return

            # Insertar en base de datos
            conexion = Conexion()
            insert = """
                INSERT INTO Cliente 
                (Nombre_Cliente, Ap_Paterno_cliente, Ap_Materno_cliente, 
                Telefono_cli, Correo, RFC, Calle, Colonia, Cod_Postal, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
            """
            conexion.conectar()
            conexion.cursor.execute(insert, (nombre, ap_paterno, ap_materno, telefono_num, correo, 
                                            rfc.upper(), calle, colonia, cp_num))
            conexion.conn.commit()
            self.formulario_cliente_mensaje = f"Cliente '{nombre}' agregado correctamente."
            self.cargar_clientes()
            # Cerrar formulario después de 2 segundos
            pygame.time.set_timer(pygame.USEREVENT + 3, 2000)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error detallado al guardar cliente: {error_msg}")
            self.formulario_cliente_mensaje = f"Error al guardar: {error_msg[:50]}..."
        finally:
            try:
                if 'conexion' in locals():
                    conexion.cerrar()
            except:
                pass

    def cargar_proveedores(self):
        """
        Carga la lista de proveedores activos desde la base de datos
        """
        conexion = Conexion()
        query = """
            SELECT Id_Proveedor AS id, Nombre_prov_proveedor AS nombre, Ap_paterno_prov AS ap_paterno,
                Ap_materno_prov AS ap_materno, Razon_Social AS razon_social, RFC AS rfc,
                Correo_prov AS correo, Telefono_prov AS telefono, Direccion AS direccion, Estado
            FROM Proveedor
            WHERE Estado = 'Activo'
        """
        self.proveedores = conexion.consultar(query)

    def dibujar_proveedores(self, surface):
        """
        Dibuja la sección de gestión de proveedores

        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        font_titulo = pygame.font.SysFont("Open Sans", int(0.045 * self.alto), bold=True)
        font_label = pygame.font.SysFont("Open Sans", int(0.032 * self.alto))

        # Título y subtítulo
        surface.blit(font_titulo.render("Gestión de Proveedores", True, (0, 0, 0)), (self.x + int(0.20 * self.ancho), self.y + int(0.18 * self.alto)))
        surface.blit(font_label.render("Administra los proveedores de tu panadería", True, (80, 80, 80)), (self.x + int(0.20 * self.ancho), self.y + int(0.22 * self.alto)))

        # Botón nuevo proveedor
        btn_y = self.y + int(0.18 * self.alto)
        self.btn_nuevo_proveedor.y = btn_y
        color_nuevo = (0, 120, 220) if self.nuevo_proveedor_hover else (0, 180, 255)
        pygame.draw.rect(surface, color_nuevo, self.btn_nuevo_proveedor, border_radius=8)
        pygame.draw.rect(surface, (0, 80, 180), self.btn_nuevo_proveedor, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        btn_text = font_btn.render("Nuevo Proveedor", True, (255, 255, 255))
        surface.blit(btn_text, (self.btn_nuevo_proveedor.x + (self.btn_nuevo_proveedor.w - btn_text.get_width()) // 2,
                                self.btn_nuevo_proveedor.y + (self.btn_nuevo_proveedor.h - btn_text.get_height()) // 2))

        # Tabla de proveedores con scroll
        tabla_y = self.y + int(0.32 * self.alto)
        self.dibujar_tabla_proveedores_con_scroll(surface, y=tabla_y, row_height=50, datos=self.proveedores)

        # Formulario si está activo
        if self.mostrando_formulario_proveedor:
            self.dibujar_formulario_nuevo_proveedor(surface)

    def dibujar_tabla_proveedores_con_scroll(self, surface, y, row_height, datos):
        """
        Dibuja una tabla editable con scroll para proveedores
        """
        columnas = ["Nombre", "Apellido Paterno", "Apellido Materno", "Razón Social", "RFC", "Correo", "Teléfono"]
        col_keys = ["nombre", "ap_paterno", "ap_materno", "razon_social", "rfc", "correo", "telefono"]
        col_widths = [150, 150, 150, 210, 150, 210, 150]

        # Área visible de la tabla
        tabla_rect = pygame.Rect(self.x + 50, y, self.ancho - 100, self.alto - (y - self.y) - 50)
        max_filas_visibles = (tabla_rect.height - row_height) // row_height
        
        # Calcular scroll máximo
        max_scroll = max(0, len(datos) - max_filas_visibles)
        self.scroll_proveedores = max(0, min(self.scroll_proveedores, max_scroll))

        # Crear superficie para la tabla con scroll
        tabla_surface = pygame.Surface((tabla_rect.width, tabla_rect.height))
        tabla_surface.fill((255, 255, 255))

        # Centrar tabla en la superficie
        ancho_tabla = sum(col_widths)
        x_tabla = (tabla_rect.width - ancho_tabla) // 2

        # Limpiar referencias de celdas
        self.celdas_proveedores = []

        # Dibujar encabezados
        font = pygame.font.SysFont("Open Sans", 20, bold=True)
        col_x = x_tabla
        for i, col in enumerate(columnas):
            pygame.draw.rect(tabla_surface, (255, 255, 200), (col_x, 0, col_widths[i], row_height))
            pygame.draw.rect(tabla_surface, (180, 180, 180), (col_x, 0, col_widths[i], row_height), 2)
            texto = font.render(col, True, (0, 0, 0))
            text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, row_height // 2))
            tabla_surface.blit(texto, text_rect)
            col_x += col_widths[i]

        # Dibujar filas visibles de datos
        font_row = pygame.font.SysFont("Open Sans", 18)
        inicio_fila = self.scroll_proveedores
        fin_fila = min(inicio_fila + max_filas_visibles, len(datos))

        for idx in range(inicio_fila, fin_fila):
            fila = datos[idx]
            fila_y = row_height + (idx - inicio_fila) * row_height
            col_x = x_tabla
            
            for i, key in enumerate(col_keys):
                # Crear rectángulo para la celda
                celda_rect = pygame.Rect(tabla_rect.x + col_x, tabla_rect.y + fila_y, col_widths[i], row_height)
                
                # Color de la celda
                color_celda = (255, 255, 255)
                if (self.celda_editando and self.celda_editando[0] == "proveedores" and 
                    self.celda_editando[1] == idx and self.celda_editando[2] == i):
                    color_celda = (220, 240, 255)
                
                pygame.draw.rect(tabla_surface, color_celda, (col_x, fila_y, col_widths[i], row_height))
                pygame.draw.rect(tabla_surface, (180, 180, 180), (col_x, fila_y, col_widths[i], row_height), 1)
                
                # Contenido de la celda
                if (self.celda_editando and self.celda_editando[0] == "proveedores" and 
                    self.celda_editando[1] == idx and self.celda_editando[2] == i and 
                    self.input_edicion):
                    self.input_edicion.rect.x = tabla_rect.x + col_x + 5
                    self.input_edicion.rect.y = tabla_rect.y + fila_y + (row_height - self.input_edicion.rect.height) // 2
                    self.input_edicion.rect.width = col_widths[i] - 10
                else:
                    valor = str(fila[key])
                    if len(valor) > 15:
                        valor = valor[:12] + "..."
                    texto = font_row.render(valor, True, (0, 0, 0))
                    text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, fila_y + row_height // 2))
                    tabla_surface.blit(texto, text_rect)
                
                # Guardar referencia a la celda
                if key != "id":
                    self.celdas_proveedores.append((celda_rect, idx, i, key, fila["id"]))
                    
                col_x += col_widths[i]

        # Dibujar tabla en la superficie principal
        surface.blit(tabla_surface, tabla_rect)

        # Dibujar scrollbar si es necesario
        if len(datos) > max_filas_visibles:
            self.dibujar_scrollbar(surface, tabla_rect, self.scroll_proveedores, max_scroll)

        # Dibujar input de edición si está activo
        if self.input_edicion and self.celda_editando and self.celda_editando[0] == "proveedores":
            self.input_edicion.draw(surface)

    def validar_fecha_nacimiento(self, fecha_str):
        """
        Valida que la fecha de nacimiento tenga el formato correcto y sea una fecha válida.

        Args:
            fecha_str (str): Fecha en formato DD/MM/AAAA

        Returns:
            tuple: (bool, str) - Indica si es válida y mensaje de error
        """
        if not fecha_str:
            return False, "Fecha de nacimiento requerida"

        try:
            if fecha_str.count('/') != 2:
                return False, "Formato debe ser DD/MM/AAAA"

            dia, mes, anio = fecha_str.split('/')

            if not (dia.isdigit() and mes.isdigit() and anio.isdigit()):
                return False, "Día, mes y año deben ser números"

            if len(dia) != 2 or len(mes) != 2 or len(anio) != 4:
                return False, "Formato debe ser DD/MM/AAAA"

            dia_int = int(dia)
            mes_int = int(mes)
            anio_int = int(anio)

            # Validar rangos
            if not (1 <= mes_int <= 12):
                return False, "El mes debe estar entre 1 y 12"

            # Verificar días según el mes
            dias_por_mes = [0, 31, 29 if (anio_int % 4 == 0 and anio_int % 100 != 0) or (anio_int % 400 == 0) else 28, 
                            31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            
            if not (1 <= dia_int <= dias_por_mes[mes_int]):
                return False, f"El día debe estar entre 1 y {dias_por_mes[mes_int]} para el mes {mes_int}"

            fecha = datetime.datetime(anio_int, mes_int, dia_int)

            # Verificar que la fecha no sea futura
            if fecha > datetime.datetime.now():
                return False, "La fecha no puede ser en el futuro"

            return True, ""

        except ValueError as e:
            return False, f"Fecha inválida: {str(e)}"

    def iniciar_edicion_celda(self, seccion, fila_idx, col_idx, key, valor_actual):
        """
        Inicia la edición de una celda específica
        """
        # Configurar InputBox para edición
        font = pygame.font.SysFont("Open Sans", 18)
        self.input_edicion = InputBox(0, 0, 100, 30, text=str(valor_actual), font=font)
        
        # Marcar esta celda como en edición
        self.celda_editando = (seccion, fila_idx, col_idx, key)
        
        # Mensaje de edición
        self.mensaje_edicion = "Presiona ENTER para guardar o ESC para cancelar"

    def finalizar_edicion(self, guardar=True):
        """
        Finaliza la edición de una celda
        """
        if not self.celda_editando or not self.input_edicion:
            return
        
        if guardar:
            seccion, fila_idx, col_idx, key = self.celda_editando
            nuevo_valor = self.input_edicion.get_value().strip()
            
            # Obtener el ID del registro
            if seccion == "empleados" and fila_idx < len(self.empleados):
                id_registro = self.empleados[fila_idx]["id"]
                self.actualizar_empleado(id_registro, key, nuevo_valor)
            elif seccion == "clientes" and fila_idx < len(self.clientes):
                id_registro = self.clientes[fila_idx]["id"]
                self.actualizar_cliente(id_registro, key, nuevo_valor)
            elif seccion == "proveedores" and fila_idx < len(self.proveedores):
                id_registro = self.proveedores[fila_idx]["id"]
                self.actualizar_proveedor(id_registro, key, nuevo_valor)
        else:
            self.mensaje_edicion = "Edición cancelada"
        
        # Limpiar variables de edición
        self.celda_editando = None
        self.input_edicion = None

    def actualizar_empleado(self, id_empleado, campo, nuevo_valor):
        """
        Actualiza un campo específico de un empleado en la base de datos
        """
        # Mapeo de campos a columnas de la base de datos
        columnas_db = {
            "nombre": "Nombre_emple",
            "ap_paterno": "Ap_Paterno_emple",
            "ap_materno": "Ap_Materno_emple",
            "curp": "CURP_emple",
            "sexo": "Sexo",
            "rfc": "RFC_emple",
            "nss": "NSS",
            "correo": "Correo_Electronico",
            "telefono": "Telefono_emple"
        }
        
        if campo not in columnas_db:
            self.mensaje_edicion = "Campo no editable"
            return
        
        columna_db = columnas_db[campo]
        
        # Validaciones específicas
        try:
            if campo in ["nss", "telefono"]:
                nuevo_valor = int(nuevo_valor)
            elif campo == "sexo" and nuevo_valor not in ["M", "F"]:
                self.mensaje_edicion = "Sexo debe ser M o F"
                return
            elif campo == "curp" and len(nuevo_valor) != 18:
                self.mensaje_edicion = "CURP debe tener 18 caracteres"
                return
            elif campo == "rfc" and len(nuevo_valor) not in [12, 13]:
                self.mensaje_edicion = "RFC debe tener 12 o 13 caracteres"
                return
        except ValueError:
            self.mensaje_edicion = f"Valor inválido para {campo}"
            return
        
        # Actualizar en la base de datos
        try:
            conexion = Conexion()
            query = f"UPDATE empleado SET {columna_db} = %s WHERE Id_Empleado = %s"
            conexion.conectar()
            conexion.cursor.execute(query, (nuevo_valor, id_empleado))
            conexion.conn.commit()
            conexion.cerrar()
            
            # Recargar datos
            self.cargar_empleados()
            self.mensaje_edicion = "Empleado actualizado exitosamente"
        except Exception as e:
            self.mensaje_edicion = f"Error al actualizar: {str(e)}"

    def actualizar_cliente(self, id_cliente, campo, nuevo_valor):
        """
        Actualiza un campo específico de un cliente en la base de datos
        """
        columnas_db = {
            "nombre": "Nombre_Cliente",
            "ap_paterno": "Ap_Paterno_cliente",
            "ap_materno": "Ap_Materno_cliente",
            "telefono": "Telefono_cli",
            "correo": "Correo",
            "rfc": "RFC",
            "calle": "Calle",
            "colonia": "Colonia",
            "cod_postal": "Cod_Postal"
        }
        
        if campo not in columnas_db:
            self.mensaje_edicion = "Campo no editable"
            return
        
        columna_db = columnas_db[campo]
        
        # Validaciones específicas
        try:
            if campo in ["telefono", "cod_postal"]:
                nuevo_valor = int(nuevo_valor)
            elif campo == "rfc" and len(nuevo_valor) not in [12, 13]:
                self.mensaje_edicion = "RFC debe tener 12 o 13 caracteres"
                return
        except ValueError:
            self.mensaje_edicion = f"Valor inválido para {campo}"
            return
        
        # Actualizar en la base de datos
        try:
            conexion = Conexion()
            query = f"UPDATE Cliente SET {columna_db} = %s WHERE Id_Cliente = %s"
            conexion.conectar()
            conexion.cursor.execute(query, (nuevo_valor, id_cliente))
            conexion.conn.commit()
            conexion.cerrar()
            
            # Recargar datos
            self.cargar_clientes()
            self.mensaje_edicion = "Cliente actualizado exitosamente"
        except Exception as e:
            self.mensaje_edicion = f"Error al actualizar: {str(e)}"

    def actualizar_proveedor(self, id_proveedor, campo, nuevo_valor):
        """
        Actualiza un campo específico de un proveedor en la base de datos
        """
        columnas_db = {
            "nombre": "Nombre_prov_proveedor",
            "ap_paterno": "Ap_paterno_prov",
            "ap_materno": "Ap_materno_prov",
            "razon_social": "Razon_Social",
            "rfc": "RFC",
            "correo": "Correo_prov",
            "telefono": "Telefono_prov"
        }
        
        if campo not in columnas_db:
            self.mensaje_edicion = "Campo no editable"
            return
        
        columna_db = columnas_db[campo]
        
        # Validaciones específicas
        try:
            if campo == "telefono":
                nuevo_valor = int(nuevo_valor)
            elif campo == "rfc" and len(nuevo_valor) not in [12, 13]:
                self.mensaje_edicion = "RFC debe tener 12 o 13 caracteres"
                return
        except ValueError:
            self.mensaje_edicion = f"Valor inválido para {campo}"
            return
        
        # Actualizar en la base de datos
        try:
            conexion = Conexion()
            query = f"UPDATE Proveedor SET {columna_db} = %s WHERE Id_Proveedor = %s"
            conexion.conectar()
            conexion.cursor.execute(query, (nuevo_valor, id_proveedor))
            conexion.conn.commit()
            conexion.cerrar()
            
            # Recargar datos
            self.cargar_proveedores()
            self.mensaje_edicion = "Proveedor actualizado exitosamente"
        except Exception as e:
            self.mensaje_edicion = f"Error al actualizar: {str(e)}"

    def cambiar_logo(self):
        """
        Abre un diálogo para seleccionar un nuevo logo del negocio

        Formatos soportados: PNG, JPG, JPEG
        """
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Selecciona el logo",
            filetypes=[("Imagen PNG", "*.png"), ("Imagen JPG", "*.jpg;*.jpeg"), ("Todos los archivos", "*.*")]
        )
        root.destroy()

        if file_path and os.path.exists(file_path):
            self.info_negocio["logo_path"] = file_path
            self.logo_img = pygame.image.load(file_path)
            self.logo_img = pygame.transform.scale(self.logo_img, (120, 120))

    def cancelar_cambios(self):
        """
        Restaura los valores originales en la sección de información general
        """
        self.input_nombre.set_value(self.info_negocio["nombre"])
        self.input_direccion.set_value(self.info_negocio["direccion"])
        self.input_telefono.set_value(self.info_negocio["telefono"])
        self.input_email.set_value(self.info_negocio["email"])
        self.logo_img = pygame.image.load(self.info_negocio["logo_path"])
        self.logo_img = pygame.transform.scale(self.logo_img, (120, 120))

    def manejar_clic_tabla_empleados(self, mouse_pos):
        """
        Maneja clics en la tabla de empleados para iniciar edición
        """
        tiempo_actual = pygame.time.get_ticks()
        
        for celda_rect, fila_idx, col_idx, key, id_registro in self.celdas_empleados:
            if celda_rect.collidepoint(mouse_pos):
                # Detectar doble clic
                celda_actual = (fila_idx, col_idx)
                if (self.ultima_celda_clic == celda_actual and 
                    tiempo_actual - self.ultimo_clic_tiempo < 500):
                    # Doble clic detectado - iniciar edición
                    if fila_idx < len(self.empleados):
                        valor_actual = self.empleados[fila_idx][key]
                        self.iniciar_edicion_celda("empleados", fila_idx, col_idx, key, valor_actual)
                else:
                    # Primer clic - guardar información
                    self.ultima_celda_clic = celda_actual
                    self.ultimo_clic_tiempo = tiempo_actual
                break

    def manejar_clic_tabla_clientes(self, mouse_pos):
        """
        Maneja clics en la tabla de clientes para iniciar edición
        """
        tiempo_actual = pygame.time.get_ticks()
        
        for celda_rect, fila_idx, col_idx, key, id_registro in self.celdas_clientes:
            if celda_rect.collidepoint(mouse_pos):
                # Detectar doble clic
                celda_actual = (fila_idx, col_idx)
                if (self.ultima_celda_clic == celda_actual and 
                    tiempo_actual - self.ultimo_clic_tiempo < 500):
                    # Doble clic detectado - iniciar edición
                    if fila_idx < len(self.clientes):
                        valor_actual = self.clientes[fila_idx][key]
                        self.iniciar_edicion_celda("clientes", fila_idx, col_idx, key, valor_actual)
                else:
                    # Primer clic - guardar información
                    self.ultima_celda_clic = celda_actual
                    self.ultimo_clic_tiempo = tiempo_actual
                break

    def manejar_clic_tabla_proveedores(self, mouse_pos):
        """
        Maneja clics en la tabla de proveedores para iniciar edición
        """
        tiempo_actual = pygame.time.get_ticks()
        
        for celda_rect, fila_idx, col_idx, key, id_registro in self.celdas_proveedores:
            if celda_rect.collidepoint(mouse_pos):
                # Detectar doble clic
                celda_actual = (fila_idx, col_idx)
                if (self.ultima_celda_clic == celda_actual and 
                    tiempo_actual - self.ultimo_clic_tiempo < 500):
                    # Doble clic detectado - iniciar edición
                    if fila_idx < len(self.proveedores):
                        valor_actual = self.proveedores[fila_idx][key]
                        self.iniciar_edicion_celda("proveedores", fila_idx, col_idx, key, valor_actual)
                else:
                    # Primer clic - guardar información
                    self.ultima_celda_clic = celda_actual
                    self.ultimo_clic_tiempo = tiempo_actual
                break

    def handle_event(self, event):
        """
        Maneja todos los eventos del sistema con manejo seguro de errores y scroll
        """
        try:
            # Eventos para cerrar formularios automáticamente
            if event.type == pygame.USEREVENT + 2:  # Empleado guardado
                self.mostrando_formulario_empleado = False
                pygame.time.set_timer(pygame.USEREVENT + 2, 0)
            elif event.type == pygame.USEREVENT + 3:  # Cliente guardado
                self.mostrando_formulario_cliente = False
                pygame.time.set_timer(pygame.USEREVENT + 3, 0)
            elif event.type == pygame.USEREVENT + 4:  # Proveedor guardado
                self.mostrando_formulario_proveedor = False
                pygame.time.set_timer(pygame.USEREVENT + 4, 0)
            
            # Manejo de scroll con rueda del mouse
            if event.type == pygame.MOUSEWHEEL:
                if self.opcion_seleccionada == "EMPLEADOS":
                    self.scroll_empleados -= event.y * 2
                    max_scroll = max(0, len(self.empleados) - 10)  # Ajustar según filas visibles
                    self.scroll_empleados = max(0, min(self.scroll_empleados, max_scroll))
                elif self.opcion_seleccionada == "CLIENTES":
                    self.scroll_clientes -= event.y * 2
                    max_scroll = max(0, len(self.clientes) - 8)  # Ajustar según filas visibles
                    self.scroll_clientes = max(0, min(self.scroll_clientes, max_scroll))
                elif self.opcion_seleccionada == "PROVEEDORES":
                    self.scroll_proveedores -= event.y * 2
                    max_scroll = max(0, len(self.proveedores) - 8)  # Ajustar según filas visibles
                    self.scroll_proveedores = max(0, min(self.scroll_proveedores, max_scroll))
            
            # Eventos de edición de tabla
            if self.celda_editando and self.input_edicion:
                # Si estamos editando, dar prioridad a eventos del InputBox
                self.input_edicion.handle_event(event)
                
                # Teclas para confirmar o cancelar edición
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.finalizar_edicion(guardar=True)
                    elif event.key == pygame.K_ESCAPE:
                        self.finalizar_edicion(guardar=False)
                return

            # Temporizador para ocultar mensajes
            if event.type == pygame.USEREVENT + 1:
                self.mensaje_edicion = ""
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                
            # --- Formulario de empleados ---
            if self.mostrando_formulario_empleado:
                for box in self.formulario_empleado_boxes:
                    box.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.formulario_empleado_btn_guardar and self.formulario_empleado_btn_guardar.collidepoint(event.pos):
                        self.guardar_nuevo_empleado()
                    elif self.formulario_empleado_btn_cancelar and self.formulario_empleado_btn_cancelar.collidepoint(event.pos):
                        self.mostrando_formulario_empleado = False
                return

            # --- Formulario de clientes ---
            if self.mostrando_formulario_cliente:
                for box in self.formulario_cliente_boxes:
                    box.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.formulario_cliente_btn_guardar and self.formulario_cliente_btn_guardar.collidepoint(event.pos):
                        self.guardar_nuevo_cliente()
                    elif self.formulario_cliente_btn_cancelar and self.formulario_cliente_btn_cancelar.collidepoint(event.pos):
                        self.mostrando_formulario_cliente = False
                return

            # --- Formulario de proveedores ---
            if self.mostrando_formulario_proveedor:
                for box in self.formulario_proveedor_boxes:
                    box.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.formulario_proveedor_btn_guardar and self.formulario_proveedor_btn_guardar.collidepoint(event.pos):
                        self.guardar_nuevo_proveedor()
                    elif self.formulario_proveedor_btn_cancelar and self.formulario_proveedor_btn_cancelar.collidepoint(event.pos):
                        self.mostrando_formulario_proveedor = False
                return

            # --- Navegación y botones principales ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Botones de navegación
                for i, rect in enumerate(self.boton_rects):
                    if rect.collidepoint(mouse_pos):
                        self.opcion_seleccionada = self.botones_opciones[i]
                        return

                # Eventos específicos por sección
                if self.opcion_seleccionada == "GENERAL":
                    if self.btn_cambiar_logo.collidepoint(mouse_pos):
                        self.cambiar_logo()
                    elif self.btn_cancelar.collidepoint(mouse_pos):
                        self.cancelar_cambios()
                elif self.opcion_seleccionada == "EMPLEADOS":
                    if self.btn_nuevo_empleado.collidepoint(mouse_pos):
                        self.mostrar_formulario_nuevo_empleado()
                    else:
                        # Verificar clics en celdas de tabla de empleados
                        self.manejar_clic_tabla_empleados(mouse_pos)
                elif self.opcion_seleccionada == "CLIENTES":
                    if self.btn_nuevo_cliente.collidepoint(mouse_pos):
                        self.mostrar_formulario_nuevo_cliente()
                    else:
                        # Verificar clics en celdas de tabla de clientes
                        self.manejar_clic_tabla_clientes(mouse_pos)
                elif self.opcion_seleccionada == "PROVEEDORES":
                    if self.btn_nuevo_proveedor.collidepoint(mouse_pos):
                        self.mostrar_formulario_nuevo_proveedor()
                    else:
                        # Verificar clics en celdas de tabla de proveedores
                        self.manejar_clic_tabla_proveedores(mouse_pos)

            elif event.type == pygame.MOUSEMOTION:
                # Efectos hover en botones
                mouse_pos = pygame.mouse.get_pos()
                self.cambiar_logo_hover = self.btn_cambiar_logo.collidepoint(mouse_pos) if self.opcion_seleccionada == "GENERAL" else False
                self.cancelar_hover = self.btn_cancelar.collidepoint(mouse_pos) if self.opcion_seleccionada == "GENERAL" else False
                self.nuevo_empleado_hover = self.btn_nuevo_empleado.collidepoint(mouse_pos) if self.opcion_seleccionada == "EMPLEADOS" else False
                self.nuevo_cliente_hover = self.btn_nuevo_cliente.collidepoint(mouse_pos) if self.opcion_seleccionada == "CLIENTES" else False
                self.nuevo_proveedor_hover = self.btn_nuevo_proveedor.collidepoint(mouse_pos) if self.opcion_seleccionada == "PROVEEDORES" else False

            elif event.type == pygame.KEYDOWN:
                # Manejo de teclas en campos de entrada
                if self.opcion_seleccionada == "GENERAL":
                    self.input_nombre.handle_event(event)
                    self.input_direccion.handle_event(event)
                    self.input_telefono.handle_event(event)
                    self.input_email.handle_event(event)
                    
        except Exception as e:
            # Manejo seguro de errores para evitar que se cierre el programa
            print(f"Error en handle_event: {str(e)}")
            # Resetear estados que puedan causar problemas
            self.celda_editando = None
            self.input_edicion = None    
    
    def mostrar_formulario_nuevo_proveedor(self):
        """
        Configura y muestra el formulario para agregar un nuevo proveedor
        """
        self.mostrando_formulario_proveedor = True
        font = pygame.font.SysFont("Open Sans", 18)

        # Campos del formulario
        labels = [
            "Nombre", "Apellido Paterno", "Apellido Materno", "Razón Social", "RFC",
            "Correo", "Teléfono", "Dirección"
        ]

        # Configuración de diseño
        num_cols = 2
        num_rows = (len(labels) + 1) // 2
        self.formulario_proveedor_labels = []
        self.formulario_proveedor_boxes = []

        # Dimensiones del modal
        modal_x = self.x + int(0.15 * self.ancho)
        modal_y = self.y + int(0.18 * self.alto)
        modal_w = int(0.7 * self.ancho)
        modal_h = int(0.6 * self.alto)

        # Dimensiones de campos
        label_width = int(0.18 * modal_w)
        input_width = int(0.28 * modal_w)
        row_height = int(0.09 * modal_h)
        col_gap = int(0.04 * modal_w)

        # Crear campos de entrada
        for i, label in enumerate(labels):
            col = i // num_rows
            row = i % num_rows
            lx = modal_x + 40 + col * (label_width + input_width + col_gap)
            ly = modal_y + 70 + row * row_height
            self.formulario_proveedor_labels.append((label + ":", (lx, ly)))
            box = InputBox(lx + label_width, ly, input_width, 32, font=font)
            self.formulario_proveedor_boxes.append(box)

        # Botones del formulario
        btn_y = modal_y + 70 + num_rows * row_height + 30
        btn_w = 180
        btn_h = 40
        btn_x = modal_x + (modal_w - 2 * btn_w - 40) // 2
        self.formulario_proveedor_btn_guardar = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.formulario_proveedor_btn_cancelar = pygame.Rect(btn_x + btn_w + 40, btn_y, btn_w, btn_h)
        self.formulario_proveedor_mensaje = ""

    def dibujar_formulario_nuevo_proveedor(self, surface):
        """
        Dibuja el formulario para agregar un nuevo proveedor

        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Dimensiones del modal
        modal_x = self.x + int(0.15 * self.ancho)
        modal_y = self.y + int(0.18 * self.alto)
        modal_w = int(0.73 * self.ancho)
        modal_h = int(0.6 * self.alto)
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        # Dibujar fondo del modal
        pygame.draw.rect(surface, (245, 245, 245), modal_rect, border_radius=18)
        pygame.draw.rect(surface, (0, 120, 220), modal_rect, 3, border_radius=18)

        # Título del formulario
        font = pygame.font.SysFont("Open Sans", int(0.037 * self.alto), bold=True)
        titulo = font.render("Nuevo Proveedor", True, (0, 0, 0))
        surface.blit(titulo, (modal_x + 30, modal_y + 20))

        # Dibujar labels y campos
        font_label = pygame.font.SysFont("Open Sans", int(0.025 * self.alto))
        for (label_text, (lx, ly)), box in zip(self.formulario_proveedor_labels, self.formulario_proveedor_boxes):
            surface.blit(font_label.render(label_text, True, (0, 0, 0)), (lx, ly))
            box.draw(surface)

        # Botón guardar
        pygame.draw.rect(surface, (0, 180, 0), self.formulario_proveedor_btn_guardar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.formulario_proveedor_btn_guardar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.028 * self.alto), bold=True)
        btn_text = font_btn.render("Guardar", True, (255, 255, 255))
        surface.blit(btn_text, (self.formulario_proveedor_btn_guardar.x + (self.formulario_proveedor_btn_guardar.w - btn_text.get_width()) // 2,
                                self.formulario_proveedor_btn_guardar.y + (self.formulario_proveedor_btn_guardar.h - btn_text.get_height()) // 2))

        # Botón cancelar
        pygame.draw.rect(surface, (200, 80, 80), self.formulario_proveedor_btn_cancelar, border_radius=8)
        pygame.draw.rect(surface, (120, 0, 0), self.formulario_proveedor_btn_cancelar, 2, border_radius=8)
        btn_text_cancel = font_btn.render("Cancelar", True, (255, 255, 255))
        surface.blit(btn_text_cancel, (self.formulario_proveedor_btn_cancelar.x + (self.formulario_proveedor_btn_cancelar.w - btn_text_cancel.get_width()) // 2,
                                    self.formulario_proveedor_btn_cancelar.y + (self.formulario_proveedor_btn_cancelar.h - btn_text_cancel.get_height()) // 2))

        # Mensaje de error/éxito
        if self.formulario_proveedor_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(0.025 * self.alto))
            msg = font_msg.render(self.formulario_proveedor_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_x + 30, self.formulario_proveedor_btn_guardar.y + 60))

    def guardar_nuevo_proveedor(self):
        """
        Valida y guarda un nuevo proveedor en la base de datos con validaciones completas
        """
        try:
            valores = [box.get_value().strip() for box in self.formulario_proveedor_boxes]
            if not all(valores):
                self.formulario_proveedor_mensaje = "Todos los campos son obligatorios."
                return

            nombre, ap_paterno, ap_materno, razon_social, rfc, correo, telefono, direccion = valores

            # 1. Validar que solo contengan letras (nombres y apellidos)
            if not all(c.isalpha() or c.isspace() for c in nombre):
                self.formulario_proveedor_mensaje = "El nombre solo debe contener letras."
                return
            if not all(c.isalpha() or c.isspace() for c in ap_paterno):
                self.formulario_proveedor_mensaje = "El apellido paterno solo debe contener letras."
                return
            if not all(c.isalpha() or c.isspace() for c in ap_materno):
                self.formulario_proveedor_mensaje = "El apellido materno solo debe contener letras."
                return

            # 2. Validar razón social (alfanuméricos, espacios y algunos caracteres especiales)
            if not all(c.isalnum() or c.isspace() or c in '.,&-' for c in razon_social):
                self.formulario_proveedor_mensaje = "La razón social solo debe contener letras, números, espacios y .,&-"
                return

            # 3. Validar RFC (12-13 caracteres alfanuméricos)
            if len(rfc) not in (12, 13) or not rfc.isalnum():
                self.formulario_proveedor_mensaje = "El RFC debe tener 12 o 13 caracteres alfanuméricos."
                return

            # 4. Validar correo electrónico
            if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
                self.formulario_proveedor_mensaje = "El formato del correo es inválido."
                return

            # 5. Validar teléfono (solo números, 10 dígitos)
            try:
                telefono_num = int(telefono)
                if len(telefono) != 10:
                    self.formulario_proveedor_mensaje = "El teléfono debe tener 10 dígitos."
                    return
            except ValueError:
                self.formulario_proveedor_mensaje = "El teléfono debe contener solo números."
                return

            # 6. Validar dirección (alfanuméricos, espacios y algunos caracteres especiales)
            if not all(c.isalnum() or c.isspace() or c in '.,#-' for c in direccion):
                self.formulario_proveedor_mensaje = "La dirección solo debe contener letras, números, espacios y .,#-"
                return

            # Insertar en base de datos
            conexion = Conexion()
            insert = """
                INSERT INTO Proveedor (Nombre_prov_proveedor, Ap_paterno_prov, Ap_materno_prov, 
                Razon_Social, RFC, Correo_prov, Telefono_prov, Direccion, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
            """
            conexion.conectar()
            conexion.cursor.execute(insert, (nombre, ap_paterno, ap_materno, razon_social, 
                                            rfc.upper(), correo, telefono_num, direccion))
            conexion.conn.commit()
            self.formulario_proveedor_mensaje = f"Proveedor '{nombre}' agregado correctamente."
            self.cargar_proveedores()
            # Cerrar formulario después de 2 segundos
            pygame.time.set_timer(pygame.USEREVENT + 4, 2000)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error detallado al guardar proveedor: {error_msg}")
            self.formulario_proveedor_mensaje = f"Error al guardar: {error_msg[:50]}..."
        finally:
            try:
                if 'conexion' in locals():
                    conexion.cerrar()
            except:
                pass

    def mostrar_formulario_nuevo_empleado(self):
        """
        Configura y muestra el formulario para agregar un nuevo empleado
        """
        self.mostrando_formulario_empleado = True
        font = pygame.font.SysFont("Open Sans", 22)

        # Campos del formulario EN EL ORDEN CORRECTO
        labels = [
            "Nombre", "Apellido Paterno", "Apellido Materno", "CURP", "Sexo (M/F)", "RFC",
            "NSS", "Correo", "Teléfono", "Padecimientos", "Calle", "Colonia", "CP", "Puesto", 
            "Contraseña", "Fecha de Nacimiento (DD/MM/AAAA)"
        ]

        # Configuración de diseño
        num_cols = 2
        num_rows = (len(labels) + 1) // 2
        self.formulario_empleado_labels = []
        self.formulario_empleado_boxes = []

        # Dimensiones del modal
        modal_x = self.x + int(0.075 * self.ancho)
        modal_y = self.y + int(0.08 * self.alto)
        modal_w = int(0.85 * self.ancho)
        modal_h = int(0.8 * self.alto)

        # Dimensiones de campos
        label_width = int(0.18 * modal_w)
        input_width = int(0.28 * modal_w)
        row_height = int(0.07 * modal_h)
        col_gap = int(0.04 * modal_w)

        # Crear campos de entrada
        for i, label in enumerate(labels):
            col = i // num_rows
            row = i % num_rows
            lx = modal_x + 40 + col * (label_width + input_width + col_gap)
            ly = modal_y + 70 + row * row_height
            self.formulario_empleado_labels.append((label + ":", (lx, ly)))
            if label == "Puesto":
                # Crear un campo de texto con opciones permitidas
                allowed_options = ["VENDEDOR", "ALMACENISTA", "GERENTE"]
                box = InputBox(lx + label_width, ly, input_width, 32, font=font, allowed_options=allowed_options)
            else:
                box = InputBox(lx + label_width, ly, input_width, 32, font=font)
            self.formulario_empleado_boxes.append(box)

        # Botones del formulario
        btn_y = modal_y + 70 + num_rows * row_height + 30
        btn_w = 200
        btn_h = 40
        btn_x = modal_x + (modal_w - 2 * btn_w - 40) // 2
        self.formulario_empleado_btn_guardar = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.formulario_empleado_btn_cancelar = pygame.Rect(btn_x + btn_w + 40, btn_y, btn_w, btn_h)
        self.formulario_empleado_mensaje = ""

    def dibujar_formulario_nuevo_empleado(self, surface):
        """
        Dibuja el formulario para agregar un nuevo empleado

        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Dimensiones del modal
        modal_x = self.x + int(0.075 * self.ancho)
        modal_y = self.y + int(0.08 * self.alto)
        modal_w = int(0.85 * self.ancho)
        modal_h = int(0.8 * self.alto)
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        # Dibujar fondo del modal
        pygame.draw.rect(surface, (245, 245, 245), modal_rect, border_radius=18)
        pygame.draw.rect(surface, (0, 120, 220), modal_rect, 3, border_radius=18)

        # Título del formulario
        font = pygame.font.SysFont("Open Sans", int(0.035 * self.alto), bold=True)
        titulo = font.render("Nuevo Empleado", True, (0, 0, 0))
        surface.blit(titulo, (modal_x + 30, modal_y + 20))

        # Dibujar labels y campos
        font_label = pygame.font.SysFont("Open Sans", int(0.025 * self.alto))
        for (label_text, (lx, ly)), box in zip(self.formulario_empleado_labels, self.formulario_empleado_boxes):
            surface.blit(font_label.render(label_text, True, (0, 0, 0)), (lx, ly))
            box.draw(surface)

        # Botón guardar
        pygame.draw.rect(surface, (0, 180, 0), self.formulario_empleado_btn_guardar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.formulario_empleado_btn_guardar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.028 * self.alto), bold=True)
        btn_text = font_btn.render("Guardar", True, (255, 255, 255))
        surface.blit(btn_text, (self.formulario_empleado_btn_guardar.x + (self.formulario_empleado_btn_guardar.w - btn_text.get_width()) // 2,
                                self.formulario_empleado_btn_guardar.y + (self.formulario_empleado_btn_guardar.h - btn_text.get_height()) // 2))

        # Botón cancelar
        pygame.draw.rect(surface, (200, 80, 80), self.formulario_empleado_btn_cancelar, border_radius=8)
        pygame.draw.rect(surface, (120, 0, 0), self.formulario_empleado_btn_cancelar, 2, border_radius=8)
        btn_text_cancel = font_btn.render("Cancelar", True, (255, 255, 255))
        surface.blit(btn_text_cancel, (self.formulario_empleado_btn_cancelar.x + (self.formulario_empleado_btn_cancelar.w - btn_text_cancel.get_width()) // 2,
                                    self.formulario_empleado_btn_cancelar.y + (self.formulario_empleado_btn_cancelar.h - btn_text_cancel.get_height()) // 2))

        # Mensaje de error/éxito
        if self.formulario_empleado_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
            msg = font_msg.render(self.formulario_empleado_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_x + 30, self.formulario_empleado_btn_guardar.y + 60))

    def guardar_nuevo_empleado(self):
        """
        Valida y guarda un nuevo empleado en la base de datos con validaciones completas
        """
        try:
            # Obtener todos los valores de los campos del formulario
            valores = [box.get_value().strip() for box in self.formulario_empleado_boxes]
            
            # Verificar que todos los campos obligatorios estén llenos
            if not all(valores):
                self.formulario_empleado_mensaje = "Todos los campos son obligatorios."
                return
            
            # Desempaquetar los valores EN EL ORDEN CORRECTO
            nombre, ap_paterno, ap_materno, curp, sexo, rfc, nss, correo, telefono, padecimientos, calle, colonia, cp, puesto, contrasena, fecha_nacimiento = valores
            
            # VALIDACIONES DETALLADAS
            
            # 1. Validar que solo contengan letras (nombres y apellidos)
            if not all(c.isalpha() or c.isspace() for c in nombre):
                self.formulario_empleado_mensaje = "El nombre solo debe contener letras."
                return
            if not all(c.isalpha() or c.isspace() for c in ap_paterno):
                self.formulario_empleado_mensaje = "El apellido paterno solo debe contener letras."
                return
            if not all(c.isalpha() or c.isspace() for c in ap_materno):
                self.formulario_empleado_mensaje = "El apellido materno solo debe contener letras."
                return
            
            # 2. Validar CURP (18 caracteres alfanuméricos)
            if len(curp) != 18 or not curp.isalnum():
                self.formulario_empleado_mensaje = "La CURP debe tener 18 caracteres alfanuméricos."
                return
            
            # 3. Validar sexo
            if sexo.upper() not in ['M', 'F']:
                self.formulario_empleado_mensaje = "El sexo debe ser 'M' o 'F'."
                return
            
            # 4. Validar RFC (12-13 caracteres alfanuméricos)
            if len(rfc) not in (12, 13) or not rfc.isalnum():
                self.formulario_empleado_mensaje = "El RFC debe tener 12 o 13 caracteres alfanuméricos."
                return
            
            # 5. Validar NSS (solo números)
            try:
                nss_num = int(nss)
                if len(nss) < 10:
                    self.formulario_empleado_mensaje = "El NSS debe tener al menos 10 dígitos."
                    return
            except ValueError:
                self.formulario_empleado_mensaje = "El NSS debe contener solo números."
                return
            
            # 6. Validar correo electrónico
            if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
                self.formulario_empleado_mensaje = "El formato del correo es inválido."
                return
            
            # 7. Validar teléfono (solo números, 10 dígitos)
            try:
                telefono_num = int(telefono)
                if len(telefono) != 10:
                    self.formulario_empleado_mensaje = "El teléfono debe tener 10 dígitos."
                    return
            except ValueError:
                self.formulario_empleado_mensaje = "El teléfono debe contener solo números."
                return
            
            # 8. Validar código postal (solo números, 5 dígitos)
            try:
                cp_num = int(cp)
                if len(cp) != 5:
                    self.formulario_empleado_mensaje = "El código postal debe tener 5 dígitos."
                    return
            except ValueError:
                self.formulario_empleado_mensaje = "El código postal debe contener solo números."
                return
            
            # 9. Validar puesto
            if puesto not in ["VENDEDOR", "ALMACENISTA", "GERENTE"]:
                self.formulario_empleado_mensaje = "El puesto debe ser: VENDEDOR, ALMACENISTA o GERENTE."
                return
            
            # 10. Validar contraseña (mínimo 6 caracteres)
            if len(contrasena) < 6:
                self.formulario_empleado_mensaje = "La contraseña debe tener al menos 6 caracteres."
                return
            
            # 11. Validar fecha de nacimiento
            fecha_valida, mensaje = self.validar_fecha_nacimiento(fecha_nacimiento)
            if not fecha_valida:
                self.formulario_empleado_mensaje = f"Error en fecha de nacimiento: {mensaje}"
                return
            
            # 12. Validar que las calles y colonias solo contengan letras, números y espacios
            if not all(c.isalnum() or c.isspace() for c in calle):
                self.formulario_empleado_mensaje = "La calle solo debe contener letras, números y espacios."
                return
            if not all(c.isalnum() or c.isspace() for c in colonia):
                self.formulario_empleado_mensaje = "La colonia solo debe contener letras, números y espacios."
                return
            
            # Insertar en la base de datos
            conexion = Conexion()
            insert = """
                INSERT INTO empleado (
                    Nombre_emple, Ap_Paterno_emple, Ap_Materno_emple, CURP_emple, 
                    Sexo, RFC_emple, NSS, Correo_Electronico, Telefono_emple, 
                    Padecimientos, Calle, Colonia, Cod_Postal, stoPuesto, 
                    Estado_emple, Contrasena_emple
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            conexion.conectar()
            conexion.cursor.execute(insert, (
                nombre, ap_paterno, ap_materno, curp.upper(), sexo.upper(), rfc.upper(), nss_num, 
                correo, telefono_num, padecimientos, calle, colonia, cp_num, 
                puesto, 'Activo', contrasena
            ))
            conexion.conn.commit()
            self.formulario_empleado_mensaje = f"Empleado '{nombre} {ap_paterno}' agregado correctamente."
            
            # Actualizar lista de empleados
            self.cargar_empleados()
            # Cerrar formulario después de 2 segundos
            pygame.time.set_timer(pygame.USEREVENT + 2, 2000)
            
        except Exception as e:
            # Manejo seguro de errores
            error_msg = str(e)
            print(f"Error detallado al guardar empleado: {error_msg}")
            self.formulario_empleado_mensaje = f"Error al guardar: {error_msg[:50]}..."
        finally:
            try:
                if 'conexion' in locals():
                    conexion.cerrar()
            except:
                pass