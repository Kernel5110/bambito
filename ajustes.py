"""
Sistema de Gestión de Ajustes para Panadería
----------------------------------------
Sistema desarrollado en Pygame para gestionar:
- Información general del negocio
- Empleados
- Clientes  
- Proveedores

Permite crear, visualizar y gestionar datos mediante interfaz gráfica
"""

import pygame
import os
import tkinter as tk
from tkinter import filedialog
from receta import Conexion

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
    
    def __init__(self, x, y, w, h, text='', font=None):
        """
        Inicializa un campo de entrada
        
        Args:
            x (int): Posición x
            y (int): Posición y
            w (int): Ancho del campo
            h (int): Alto del campo
            text (str, optional): Texto inicial. Defaults to ''.
            font (pygame.font.Font, optional): Fuente del texto. Defaults to None.
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.font = font or pygame.font.SysFont("Open Sans", 24)
        self.txt_surface = self.font.render(text, True, (0, 0, 0))
        self.active = False

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
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN and self.active:
            # Manejar teclas cuando está activo
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Agregar caracteres imprimibles
                if len(self.text) < 100 and event.unicode.isprintable():
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
            
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", fuente_relativa(36), bold=True)
        self.color_texto = (0, 0, 0)

        # Configuración de navegación
        self.botones_opciones = ["GENERAL", "EMPLEADOS", "CLIENTES", "PROVEEDORES"]
        self.opcion_seleccionada = self.botones_opciones[0]
        self.fuente_boton = pygame.font.SysFont("Open Sans", fuente_relativa(28), bold=True)
        
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

        # --- Configuración de sección GENERAL ---
        self.info_negocio = {
            "nombre": "Panadería Bambi",
            "direccion": "Calle Ejemplo 123, Centro",
            "telefono": "5551234567",
            "email": "contacto@bambi.com",
            "logo_path": "imagenes/log.png"
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
        
        # Tabla de empleados
        tabla_y = self.y + int(0.32 * self.alto)
        self.dibujar_tabla_empleados(surface, y=tabla_y, row_height=32, datos=self.empleados)
        
        # Formulario si está activo
        if self.mostrando_formulario_empleado:
            self.dibujar_formulario_nuevo_empleado(surface)

    def dibujar_tabla_empleados(self, surface, y, row_height, datos):
        """
        Dibuja una tabla con la información de empleados
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            y (int): Posición Y de la tabla
            row_height (int): Altura de cada fila
            datos (list): Lista de diccionarios con datos de empleados
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
        
        # Centrar tabla
        ancho_tabla = sum(col_widths)
        x = self.x + (self.ancho - ancho_tabla) // 2
        col_x = x
        
        # Dibujar encabezados
        font = pygame.font.SysFont("Open Sans", 20, bold=True)
        for i, col in enumerate(columnas):
            pygame.draw.rect(surface, (200, 200, 255), (col_x, y, col_widths[i], row_height))
            pygame.draw.rect(surface, (180, 180, 180), (col_x, y, col_widths[i], row_height), 2)
            texto = font.render(col, True, (0, 0, 0))
            text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, y + row_height // 2))
            surface.blit(texto, text_rect)
            col_x += col_widths[i]
        
        # Dibujar filas de datos
        fila_y = y + row_height
        font_row = pygame.font.SysFont("Open Sans", 18)
        for fila in datos:
            col_x = x
            for i, key in enumerate(col_keys):
                pygame.draw.rect(surface, (255, 255, 255), (col_x, fila_y, col_widths[i], row_height))
                pygame.draw.rect(surface, (180, 180, 180), (col_x, fila_y, col_widths[i], row_height), 1)
                valor = fila[key]
                texto = font_row.render(str(valor), True, (0, 0, 0))
                text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, fila_y + row_height // 2))
                surface.blit(texto, text_rect)
                col_x += col_widths[i]
            fila_y += row_height

    def mostrar_formulario_nuevo_empleado(self):
        """
        Configura y muestra el formulario para agregar un nuevo empleado
        """
        self.mostrando_formulario_empleado = True
        font = pygame.font.SysFont("Open Sans", 18)
        
        # Campos del formulario
        labels = [
            "Nombre", "Apellido Paterno", "Apellido Materno", "CURP", "Sexo (M/F/O)", "RFC",
            "NSS", "Correo", "Teléfono", "Padecimientos", "Calle", "Colonia", "CP", "Puesto", "Contraseña"
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
            box = InputBox(lx + label_width, ly, input_width, 32, font=font)
            self.formulario_empleado_boxes.append(box)
        
        # Botones del formulario
        btn_y = modal_y + 70 + num_rows * row_height + 30
        btn_w = 200
        btn_h = 40
        total_form_w = 2 * (label_width + input_width) + col_gap
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
        modal_w = int(0.87 * self.ancho)
        modal_h = int(0.8 * self.alto)
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        
        # Dibujar fondo del modal
        pygame.draw.rect(surface, (245, 245, 245), modal_rect, border_radius=18)
        pygame.draw.rect(surface, (0, 120, 220), modal_rect, 3, border_radius=18)
        
        # Título del formulario
        font = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        titulo = font.render("Nuevo Empleado", True, (0, 0, 0))
        surface.blit(titulo, (modal_x + 30, modal_y + 20))
        
        # Dibujar labels y campos
        font_label = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
        for (label_text, (lx, ly)), box in zip(self.formulario_empleado_labels, self.formulario_empleado_boxes):
            surface.blit(font_label.render(label_text, True, (0, 0, 0)), (lx, ly))
            box.draw(surface)
        
        # Botón guardar
        pygame.draw.rect(surface, (0, 180, 0), self.formulario_empleado_btn_guardar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.formulario_empleado_btn_guardar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.026 * self.alto), bold=True)
        btn_text = font_btn.render("Guardar", True, (255, 255, 255))
        surface.blit(btn_text, (self.formulario_empleado_btn_guardar.x + (self.formulario_empleado_btn_guardar.w - btn_text.get_width()) // 2,
                                self.formulario_empleado_btn_guardar.y + (self.formulario_empleado_btn_guardar.h - btn_text.get_height()) // 2))
        
        # Botón cancelar
        pygame.draw.rect(surface, (200, 80, 80), self.formulario_proveedor_btn_cancelar, border_radius=8)
        pygame.draw.rect(surface, (120, 0, 0), self.formulario_proveedor_btn_cancelar, 2, border_radius=8)
        btn_text_cancel = font_btn.render("Cancelar", True, (255, 255, 255))
        surface.blit(btn_text_cancel, (self.formulario_proveedor_btn_cancelar.x + (self.formulario_proveedor_btn_cancelar.w - btn_text_cancel.get_width()) // 2,
                                    self.formulario_proveedor_btn_cancelar.y + (self.formulario_proveedor_btn_cancelar.h - btn_text_cancel.get_height()) // 2))
        
        # Mensaje de error/éxito
        if self.formulario_proveedor_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
            msg = font_msg.render(self.formulario_proveedor_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_x + 30, self.formulario_proveedor_btn_guardar.y + 60))

    def guardar_nuevo_empleado(self):
        """
        Valida y guarda un nuevo empleado en la base de datos
        
        Validaciones:
        - Todos los campos son obligatorios
        - NSS, teléfono y CP deben ser números
        - Sexo debe ser M, F u O
        """
        valores = [box.get_value().strip() for box in self.formulario_empleado_boxes]
        if not all(valores):
            self.formulario_empleado_mensaje = "Todos los campos son obligatorios."
            return
            
        (
            nombre, ap_paterno, ap_materno, curp, sexo, rfc, nss, correo, telefono,
            padecimientos, calle, colonia, cp, puesto, contrasena
        ) = valores
        
        # Validaciones básicas
        try:
            nss = int(nss)
            telefono = int(telefono)
            cp = int(cp)
            if sexo.upper() not in ("M", "F", "O"):
                self.formulario_empleado_mensaje = "Sexo debe ser M, F u O."
                return
        except Exception:
            self.formulario_empleado_mensaje = "NSS, Teléfono o CP inválido."
            return
        
        # Insertar en base de datos
        conexion = Conexion()
        insert = """
            INSERT INTO Empleado (
                Nombre_emple, Ap_Paterno_emple, Ap_Materno_emple, CURP_emple, Sexo, RFC_emple, NSS,
                Correo_Electronico, Telefono_emple, Padecimientos, Calle, Colonia, Cod_Postal,
                stoPuesto, Contrasena_emple, Estado_emple
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
        """
        try:
            conexion.conectar()
            conexion.cursor.execute(insert, (
                nombre, ap_paterno, ap_materno, curp, sexo.upper(), rfc, nss, correo, telefono,
                padecimientos, calle, colonia, cp, puesto, contrasena
            ))
            conexion.conn.commit()
            self.formulario_empleado_mensaje = f"Empleado '{nombre}' agregado."
            self.cargar_empleados()
            self.mostrando_formulario_empleado = False
        except Exception as e:
            self.formulario_empleado_mensaje = f"Error: {e}"
        finally:
            conexion.cerrar()

    def cargar_clientes(self):
        """
        Carga la lista de clientes activos desde la base de datos
        """
        conexion = Conexion()
        query = """
            SELECT Id_Cliente AS id, Nombre_Cliente_cliente AS nombre, Ap_Paterno_cliente_cli AS ap_paterno,
                Ap_Materno_cleinte_cli AS ap_materno, Telefono_cli AS telefono, Correo AS correo,
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
        
        # Tabla de clientes
        tabla_y = self.y + int(0.32 * self.alto)
        self.dibujar_tabla_clientes(surface, y=tabla_y, row_height=50, datos=self.clientes)
        
        # Formulario si está activo
        if self.mostrando_formulario_cliente:
            self.dibujar_formulario_nuevo_cliente(surface)

    def dibujar_tabla_clientes(self, surface, y, row_height, datos):
        """
        Dibuja una tabla con la información de clientes
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            y (int): Posición Y de la tabla
            row_height (int): Altura de cada fila
            datos (list): Lista de diccionarios con datos de clientes
        """
        columnas = ["Nombre", "Apellido Paterno", "Apellido Materno", "Teléfono", "Correo", "RFC", "Calle", "Colonia", "CP"]
        col_keys = ["nombre", "ap_paterno", "ap_materno", "telefono", "correo", "rfc", "calle", "colonia", "cod_postal"]
        col_widths = [160, 130, 130, 130, 190, 110, 130, 130, 80]
        
        # Centrar tabla
        ancho_tabla = sum(col_widths)
        x = self.x + (self.ancho - ancho_tabla) // 2
        col_x = x
        
        # Dibujar encabezados
        font = pygame.font.SysFont("Open Sans", 20, bold=True)
        for i, col in enumerate(columnas):
            pygame.draw.rect(surface, (200, 255, 200), (col_x, y, col_widths[i], row_height))
            pygame.draw.rect(surface, (180, 180, 180), (col_x, y, col_widths[i], row_height), 2)
            texto = font.render(col, True, (0, 0, 0))
            text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, y + row_height // 2))
            surface.blit(texto, text_rect)
            col_x += col_widths[i]
        
        # Dibujar filas de datos
        fila_y = y + row_height
        font_row = pygame.font.SysFont("Open Sans", 18)
        for fila in datos:
            col_x = x
            for i, key in enumerate(col_keys):
                pygame.draw.rect(surface, (255, 255, 255), (col_x, fila_y, col_widths[i], row_height))
                pygame.draw.rect(surface, (180, 180, 180), (col_x, fila_y, col_widths[i], row_height), 1)
                valor = fila[key]
                texto = font_row.render(str(valor), True, (0, 0, 0))
                text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, fila_y + row_height // 2))
                surface.blit(texto, text_rect)
                col_x += col_widths[i]
            fila_y += row_height

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
        total_form_w = 2 * (label_width + input_width) + col_gap
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
        font = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        titulo = font.render("Nuevo Cliente", True, (0, 0, 0))
        surface.blit(titulo, (modal_x + 30, modal_y + 20))
        
        # Dibujar labels y campos
        font_label = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
        for (label_text, (lx, ly)), box in zip(self.formulario_cliente_labels, self.formulario_cliente_boxes):
            surface.blit(font_label.render(label_text, True, (0, 0, 0)), (lx, ly))
            box.draw(surface)
        
        # Botón guardar
        pygame.draw.rect(surface, (0, 180, 0), self.formulario_cliente_btn_guardar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.formulario_cliente_btn_guardar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.026 * self.alto), bold=True)
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
        Valida y guarda un nuevo cliente en la base de datos
        
        Validaciones:
        - Todos los campos son obligatorios
        - Teléfono y CP deben ser números
        """
        valores = [box.get_value().strip() for box in self.formulario_cliente_boxes]
        if not all(valores):
            self.formulario_cliente_mensaje = "Todos los campos son obligatorios."
            return
            
        nombre, ap_paterno, ap_materno, telefono, correo, rfc, calle, colonia, cp = valores
        
        try:
            telefono = int(telefono)
            cp = int(cp)
        except Exception:
            self.formulario_cliente_mensaje = "Teléfono o CP inválido."
            return
        
        # Insertar en base de datos
        conexion = Conexion()
        insert = """
            INSERT INTO Cliente (Nombre_Cliente_cliente, Ap_Paterno_cliente_cli, Ap_Materno_cleinte_cli, Telefono_cli, Correo, RFC, Calle, Colonia, Cod_Postal, Estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
        """
        conexion.conectar()
        conexion.cursor.execute(insert, (nombre, ap_paterno, ap_materno, telefono, correo, rfc, calle, colonia, cp))
        conexion.conn.commit()
        conexion.cerrar()
        self.formulario_cliente_mensaje = f"Cliente '{nombre}' agregado."
        self.cargar_clientes()
        self.mostrando_formulario_cliente = False

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
        
        # Tabla de proveedores
        tabla_y = self.y + int(0.32 * self.alto)
        self.dibujar_tabla_proveedores(surface, y=tabla_y, row_height=50, datos=self.proveedores)
        
        # Formulario si está activo
        if self.mostrando_formulario_proveedor:
            self.dibujar_formulario_nuevo_proveedor(surface)

    def dibujar_tabla_proveedores(self, surface, y, row_height, datos):
        """
        Dibuja una tabla con la información de proveedores
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            y (int): Posición Y de la tabla
            row_height (int): Altura de cada fila
            datos (list): Lista de diccionarios con datos de proveedores
        """
        columnas = ["Nombre", "Apellido Paterno", "Apellido Materno", "Razón Social", "RFC", "Correo", "Teléfono"]
        col_keys = ["nombre", "ap_paterno", "ap_materno", "razon_social", "rfc", "correo", "telefono"]
        col_widths = [150, 150, 150, 210, 150, 210, 150]
        
        # Centrar tabla
        ancho_tabla = sum(col_widths)
        x = self.x + (self.ancho - ancho_tabla) // 2
        col_x = x
        
        # Dibujar encabezados
        font = pygame.font.SysFont("Open Sans", 20, bold=True)
        for i, col in enumerate(columnas):
            pygame.draw.rect(surface, (255, 255, 200), (col_x, y, col_widths[i], row_height))
            pygame.draw.rect(surface, (180, 180, 180), (col_x, y, col_widths[i], row_height), 2)
            texto = font.render(col, True, (0, 0, 0))
            text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, y + row_height // 2))
            surface.blit(texto, text_rect)
            col_x += col_widths[i]
        
        # Dibujar filas de datos
        fila_y = y + row_height
        font_row = pygame.font.SysFont("Open Sans", 18)
        for fila in datos:
            col_x = x
            for i, key in enumerate(col_keys):
                pygame.draw.rect(surface, (255, 255, 255), (col_x, fila_y, col_widths[i], row_height))
                pygame.draw.rect(surface, (180, 180, 180), (col_x, fila_y, col_widths[i], row_height), 1)
                valor = fila[key]
                texto = font_row.render(str(valor), True, (0, 0, 0))
                text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, fila_y + row_height // 2))
                surface.blit(texto, text_rect)
                col_x += col_widths[i]
            fila_y += row_height

    def mostrar_formulario_nuevo_proveedor(self):
        """
        Configura y muestra el formulario para agregar un nuevo proveedor
        """
        self.mostrando_formulario_proveedor = True
        font = pygame.font.SysFont("Open Sans", 18)
        
        # Campos del formulario
        labels = [
            "Nombre", "Apellido Paterno", "Apellido Materno", "Razón Social", "RFC",
            "Correo", "Teléfono"
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
        total_form_w = 2 * (label_width + input_width) + col_gap
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
        font = pygame.font.SysFont("Open Sans", int(0.032 * self.alto), bold=True)
        titulo = font.render("Nuevo Proveedor", True, (0, 0, 0))
        surface.blit(titulo, (modal_x + 30, modal_y + 20))

        # Dibujar labels y campos
        font_label = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
        for (label_text, (lx, ly)), box in zip(self.formulario_proveedor_labels, self.formulario_proveedor_boxes):
            surface.blit(font_label.render(label_text, True, (0, 0, 0)), (lx, ly))
            box.draw(surface)

        # Botón guardar
        pygame.draw.rect(surface, (0, 180, 0), self.formulario_proveedor_btn_guardar, border_radius=8)
        pygame.draw.rect(surface, (0, 120, 0), self.formulario_proveedor_btn_guardar, 2, border_radius=8)
        font_btn = pygame.font.SysFont("Open Sans", int(0.026 * self.alto), bold=True)
        btn_text = font_btn.render("Guardar", True, (255, 255, 255))
        surface.blit(btn_text, (self.formulario_proveedor_btn_guardar.x + (self.formulario_proveedor_btn_guardar.w - btn_text.get_width()) // 2,
                                self.formulario_proveedor_btn_guardar.y + (self.formulario_proveedor_btn_guardar.h - btn_text.get_height()) // 2))
        
        # Botón cancelar
        pygame.draw.rect(surface, (200, 80, 80), self.formulario_proveedor_btn_cancelar, border_radius=8)
        pygame.draw.rect(surface, (120, 0, 0), self.formulario_proveedor_btn_cancelar, 2, border_radius=8)
        btn_text_cancel = font_btn.render("Cancelar", True, (255, 255, 255))
        surface.blit(btn_text_cancel, (self.formulario_proveedor_btn_cancelar.x + (self.formulario_proveedor_btn_cancelar.w - btn_text_cancel.get_width()) // 2,
                                    self.formulario_proveedor_btn_cancelar.y + (self.formulario_proveedor_btn_cancelar.h - btn_text_cancel.get_height()) // 2))
        if self.formulario_proveedor_mensaje:
            font_msg = pygame.font.SysFont("Open Sans", int(0.022 * self.alto))
            msg = font_msg.render(self.formulario_proveedor_mensaje, True, (200, 0, 0))
            surface.blit(msg, (modal_x + 30, self.formulario_proveedor_btn_guardar.y + 60))

    def guardar_nuevo_proveedor(self):
        """
        Valida y guarda un nuevo proveedor en la base de datos
        
        Validaciones:
        - Todos los campos son obligatorios
        - Teléfono debe ser un número
        """
        valores = [box.get_value().strip() for box in self.formulario_proveedor_boxes]
        if not all(valores):
            self.formulario_proveedor_mensaje = "Todos los campos son obligatorios."
            return
            
        nombre, ap_paterno, ap_materno, razon_social, rfc, correo, telefono, direccion = valores
        
        try:
            telefono = int(telefono)
        except Exception:
            self.formulario_proveedor_mensaje = "Teléfono inválido."
            return
        
        # Insertar en base de datos
        conexion = Conexion()
        insert = """
            INSERT INTO Proveedor (Nombre_prov_proveedor, Ap_paterno_prov, Ap_materno_prov, Razon_Social, RFC, Correo_prov, Telefono_prov, Direccion, Estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
        """
        try:
            conexion.conectar()
            conexion.cursor.execute(insert, (nombre, ap_paterno, ap_materno, razon_social, rfc, correo, telefono, direccion))
            conexion.conn.commit()
            self.formulario_proveedor_mensaje = f"Proveedor '{nombre}' agregado."
            self.cargar_proveedores()
            self.mostrando_formulario_proveedor = False
        except Exception as e:
            self.formulario_proveedor_mensaje = f"Error: {e}"
        finally:
            conexion.cerrar()

    def handle_event(self, event):
        """
        Maneja todos los eventos del sistema
        
        Args:
            event (pygame.event.Event): Evento a procesar
            
        Eventos manejados:
        - MOUSEBUTTONDOWN: Clics en botones y campos
        - MOUSEMOTION: Efectos de hover
        - KEYDOWN: Entrada de texto en campos
        """
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
            elif self.opcion_seleccionada == "CLIENTES":
                if self.btn_nuevo_cliente.collidepoint(mouse_pos):
                    self.mostrar_formulario_nuevo_cliente()
            elif self.opcion_seleccionada == "PROVEEDORES":
                if self.btn_nuevo_proveedor.collidepoint(mouse_pos):
                    self.mostrar_formulario_nuevo_proveedor()

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
            elif self.opcion_seleccionada == "EMPLEADOS" and self.mostrando_formulario_empleado:
                for box in self.formulario_empleado_boxes:
                    box.handle_event(event)
            elif self.opcion_seleccionada == "CLIENTES" and self.mostrando_formulario_cliente:
                for box in self.formulario_cliente_boxes:
                    box.handle_event(event)
            elif self.opcion_seleccionada == "PROVEEDORES" and self.mostrando_formulario_proveedor:
                for box in self.formulario_proveedor_boxes:
                    box.handle_event(event)

    # --- Métodos de cambiar_logo y cancelar_cambios igual que antes ---
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
 