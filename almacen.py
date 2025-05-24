
"""
Sistema de Gestión de Almacén para Panadería
-------------------------------------------
Sistema desarrollado en Pygame para gestionar el inventario completo de:
- Insumos (productos terminados, empaques, etc.)
- Materias primas (harina, azúcar, levadura, etc.)

Características principales:
- Visualización tabular de inventario
- Búsqueda instantánea
- Agregar nuevos elementos al inventario
- Control de stock mínimo
- Administración de fechas de entrada y caducidad
- Precios y cálculo de IVA

Versión: 1.0
"""

import pygame
from receta import Conexion

class InputBox:
    """
    Clase para campos de entrada de texto con validación opcional
    
    Permite crear inputs con validación numérica y manejo completo
    de eventos de mouse y teclado.
    
    Attributes:
        rect (pygame.Rect): Dimensiones y posición del campo
        text (str): Texto actual en el campo
        numeric (bool): Si True, solo acepta números y punto decimal
        active (bool): Estado de activación del campo
        color (pygame.Color): Color actual del borde
    """
    
    def __init__(self, x, y, w, h, text='', font=None, numeric=False):
        """
        Inicializa un campo de entrada
        
        Args:
            x, y (int): Posición del campo
            w, h (int): Dimensiones del campo
            text (str, optional): Texto inicial. Defaults to ''.
            font (pygame.font.Font, optional): Fuente personalizada. Defaults to None.
            numeric (bool, optional): Solo permite números. Defaults to False.
        """
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
        """
        Maneja eventos de mouse y teclado
        
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
            str: Texto actual
        """
        return self.text

class almacen:
    """
    Clase principal del sistema de gestión de almacén
    
    Maneja la interfaz completa para:
    - Visualizar inventario de insumos y materias primas
    - Buscar elementos en el inventario
    - Agregar nuevos elementos
    - Controlar stock y fechas de caducidad
    
    Attributes:
        x, y (int): Posición de la interfaz
        ancho, alto (int): Dimensiones de la interfaz
        opcion_seleccionada (str): Categoría actualmente mostrada
        datos_tabla (list): Datos actuales mostrados en la tabla
        busqueda_texto (str): Texto de búsqueda actual
        mostrando_formulario (bool): Estado del formulario de agregar
    """
    
    def __init__(self, x, y, ancho, alto):
        """
        Inicializa el sistema de almacén
        
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

        # Configuración de fuentes escaladas
        self.fuente_titulo = pygame.font.SysFont("Times New Roman", int(self.alto * 0.08), bold=True)
        self.color_texto = (0, 0, 0)

        # Configuración de navegación
        self.botones_opciones = ["INSUMOS", "MATERIA PRIMA"]
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

        # Botón agregar
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

        # Carga inicial de datos
        self.datos_tabla = []
        self.cargar_datos_tabla()

        # Configuración del formulario
        self.mostrando_formulario = False
        self.formulario_boxes = []
        self.formulario_labels = []
        self.formulario_btn_guardar = None
        self.formulario_btn_cancelar = None
        self.formulario_mensaje = ""

    def cargar_datos_tabla(self):
        """
        Carga los datos de la tabla según la categoría seleccionada y búsqueda
        
        Consulta la base de datos filtrando por:
        - Categoría (INSUMOS o MATERIA PRIMA)
        - Texto de búsqueda
        - Estados válidos (Disponible, Agotado, Descontinuado)
        """
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
        """
        Dibuja la interfaz completa del almacén
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
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

        # Botones de navegación
        for i, rect in enumerate(self.boton_rects):
            color = self.color_boton_activo if self.opcion_seleccionada == self.botones_opciones[i] else self.color_boton
            pygame.draw.rect(surface, color, rect, border_radius=8)
            texto_boton = self.fuente_boton.render(self.botones_opciones[i], True, self.color_texto)
            text_rect = texto_boton.get_rect(center=rect.center)
            surface.blit(texto_boton, text_rect)

        # Botón agregar
        color_agregar = self.color_boton_agregar_hover if self.agregar_hover else self.color_boton_agregar
        pygame.draw.rect(surface, color_agregar, self.boton_agregar_rect, border_radius=8)
        texto_agregar = self.fuente_boton_agregar.render("Agregar", True, (255, 255, 255))
        text_rect_agregar = texto_agregar.get_rect(center=self.boton_agregar_rect.center)
        surface.blit(texto_agregar, text_rect_agregar)

        # Tabla de inventario
        tabla_x = self.x + int(self.ancho * 0.03)
        tabla_y = self.y + int(self.alto * 0.23)
        tabla_width = int(self.ancho * 0.94)
        tabla_row_height = int(self.alto * 0.07)
        self.dibujar_tabla(surface, tabla_x, tabla_y, tabla_width, tabla_row_height, self.datos_tabla)

        # Formulario si está activo
        if self.mostrando_formulario:
            self.dibujar_formulario_agregar(surface)

    def dibujar_tabla(self, surface, x, y, width, row_height, datos):
        """
        Dibuja la tabla de inventario con los datos actuales (versión editable)
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            x, y (int): Posición de la tabla
            width (int): Ancho total de la tabla
            row_height (int): Altura de cada fila
            datos (list): Lista de diccionarios con los datos
        """
        # Definir columnas y anchos
        columnas = ["Nombre", "Categoría", "Precio", "Cantidad", "Estado"]
        col_widths = [
            int(width*0.28), int(width*0.21), int(width*0.16), int(width*0.16), int(width*0.16)
        ]
        
        # Almacenar referencias a las celdas para manejo de clics
        self.celdas_tabla = []
        
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
        for fila_idx, fila in enumerate(datos):
            col_x = x
            for i, key in enumerate(["nombre", "categoria", "precio", "cantidad", "estado"]):
                # Crear rectángulo para la celda
                celda_rect = pygame.Rect(col_x, fila_y, col_widths[i], row_height)
                
                # Dibujar celda
                color_celda = self.color_tabla_row
                
                # Si esta celda está siendo editada, usar un color diferente
                if hasattr(self, 'celda_editando') and self.celda_editando == (fila_idx, i):
                    color_celda = (220, 240, 255)  # Azul claro para celda en edición
                
                pygame.draw.rect(surface, color_celda, celda_rect)
                pygame.draw.rect(surface, self.color_tabla_border, celda_rect, 1)
                
                # Mostrar el valor correspondiente
                valor = fila[key]
                if key == "precio":
                    valor = f"${valor:.2f}"
                    
                # Si esta celda se está editando, mostrar el InputBox
                if hasattr(self, 'celda_editando') and self.celda_editando == (fila_idx, i) and hasattr(self, 'input_edicion'):
                    self.input_edicion.rect.x = col_x + 5
                    self.input_edicion.rect.y = fila_y + (row_height - self.input_edicion.rect.height) // 2
                    self.input_edicion.rect.width = col_widths[i] - 10
                    self.input_edicion.draw(surface)
                else:
                    texto = self.fuente_tabla.render(str(valor), True, self.NEGRO)
                    text_rect = texto.get_rect(center=(col_x + col_widths[i] // 2, fila_y + row_height // 2))
                    surface.blit(texto, text_rect)
                
                # Almacenar referencia a esta celda si es editable
                if key != "categoria":  # La categoría no es editable
                    self.celdas_tabla.append((celda_rect, fila_idx, i, key))
                    
                col_x += col_widths[i]
            fila_y += row_height

        # Si estamos mostrando el mensaje de edición
        if hasattr(self, 'mensaje_edicion') and self.mensaje_edicion:
            mensaje_y = y + row_height * (len(datos) + 1) + 10
            font_msg = pygame.font.SysFont("Open Sans", int(self.alto * 0.035))
            color = (0, 120, 0) if "exitosamente" in self.mensaje_edicion else (200, 0, 0)
            msg = font_msg.render(self.mensaje_edicion, True, color)
            surface.blit(msg, (x + (width - msg.get_width()) // 2, mensaje_y))

    def iniciar_edicion_celda(self, fila_idx, col_idx, key):
        """
        Inicia la edición de una celda
        
        Args:
            fila_idx (int): Índice de la fila
            col_idx (int): Índice de la columna
            key (str): Clave del dato en el diccionario
        """
        # Solo permitir editar si hay datos
        if not self.datos_tabla or fila_idx >= len(self.datos_tabla):
            return
        
        # Obtener el valor actual
        valor_actual = self.datos_tabla[fila_idx][key]
        
        # Convertir a string si es necesario
        if key == "precio":
            valor_actual = str(valor_actual)
        else:
            valor_actual = str(valor_actual)
        
        # Configurar InputBox para edición
        font = pygame.font.SysFont("Open Sans", int(self.alto * 0.04))
        numeric = key in ["precio", "cantidad"]
        self.input_edicion = InputBox(0, 0, 100, int(self.alto * 0.05), 
                                    text=valor_actual, font=font, numeric=numeric)
        
        # Marcar esta celda como en edición
        self.celda_editando = (fila_idx, col_idx)
        
        # Mensaje de edición
        self.mensaje_edicion = "Presiona ENTER para guardar o ESC para cancelar"
   
    def finalizar_edicion(self, guardar=True):
        """
        Finaliza la edición de una celda
        
        Args:
            guardar (bool): Si True, guarda los cambios
        """
        if not hasattr(self, 'celda_editando') or not hasattr(self, 'input_edicion'):
            return
        
        if guardar:
            # Obtener la fila y columna que se está editando
            fila_idx, col_idx = self.celda_editando
            
            # Obtener la clave correspondiente
            for rect, f_idx, c_idx, key in self.celdas_tabla:
                if f_idx == fila_idx and c_idx == col_idx:
                    # Obtener el nuevo valor
                    nuevo_valor = self.input_edicion.get_value()
                    
                    # Validar y convertir según el tipo de dato
                    try:
                        if key == "precio":
                            nuevo_valor = float(nuevo_valor)
                        elif key == "cantidad":
                            nuevo_valor = int(nuevo_valor)
                        elif key == "estado" and nuevo_valor not in ["Disponible", "Agotado", "Descontinuado"]:
                            self.mensaje_edicion = "Estado inválido. Use: Disponible, Agotado, Descontinuado"
                            return
                        
                        # Guardar el cambio en la base de datos
                        self.actualizar_dato(fila_idx, key, nuevo_valor)
                        
                        # Actualizar el valor en la vista
                        self.datos_tabla[fila_idx][key] = nuevo_valor
                        
                        self.mensaje_edicion = "Dato actualizado exitosamente"
                    except ValueError:
                        self.mensaje_edicion = "Valor inválido para este campo"
                        return
                    break
        
        # Limpiar variables de edición
        delattr(self, 'celda_editando')
        delattr(self, 'input_edicion')
        
        # Programar que el mensaje desaparezca después de 3 segundos
        if hasattr(self, 'mensaje_edicion') and self.mensaje_edicion:
            pygame.time.set_timer(pygame.USEREVENT + 1, 3000)  # 3 segundos

    def actualizar_dato(self, fila_idx, key, nuevo_valor):
        """
        Actualiza un dato en la base de datos
        
        Args:
            fila_idx (int): Índice de la fila
            key (str): Clave del dato (nombre, precio, cantidad, estado)
            nuevo_valor: Nuevo valor a guardar
        """
        # Obtener el elemento que se está modificando
        if fila_idx >= len(self.datos_tabla):
            return False
        
        elemento = self.datos_tabla[fila_idx]
        nombre = elemento["nombre"]  # Usaremos el nombre para identificar el registro
        
        # Conectar a la base de datos
        conexion = Conexion()
        conexion.conectar()
        
        # La tabla depende de la categoría seleccionada
        tabla = "Insumo" if self.opcion_seleccionada == "INSUMOS" else "MateriaPrima"
        
        # Mapear key a nombre de columna en la base de datos
        # El mapeo puede variar según tu esquema de base de datos
        columnas = {
            "nombre": "Nombre",
            "precio": "Precio",
            "cantidad": "Cantidad",
            "estado": "Estado"
        }
        
        # Columna a actualizar
        columna = columnas.get(key, key)
        
        # Query de actualización
        query = f"""
            UPDATE {tabla}
            SET {columna} = %s
            WHERE Nombre = %s
        """
        
        try:
            # Ejecutar la actualización
            conexion.cursor.execute(query, (nuevo_valor, nombre))
            conexion.conn.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar dato: {e}")
            self.mensaje_edicion = f"Error: {str(e)}"
            return False
        finally:
            conexion.cerrar()

    def dibujar_campo_busqueda(self, surface, x, y, w, h):
        """
        Dibuja el campo de búsqueda de productos
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
            x, y (int): Posición del campo
            w, h (int): Dimensiones del campo
        """
        color_fondo = (255, 255, 255)
        color_borde = (100, 100, 100) if self.busqueda_activa else (180, 180, 180)
        pygame.draw.rect(surface, color_fondo, (x, y, w, h), border_radius=10)
        pygame.draw.rect(surface, color_borde, (x, y, w, h), 2, border_radius=10)
        texto = self.busqueda_texto if self.busqueda_texto else "Buscar producto..."
        color_texto = self.NEGRO if self.busqueda_texto else (150, 150, 150)
        render = self.fuente_busqueda.render(texto, True, color_texto)
        surface.blit(render, (x + 10, y + (h - render.get_height()) // 2))

    def handle_event(self, event):
        """
        Maneja todos los eventos del sistema
        
        Args:
            event (pygame.event.Event): Evento de Pygame
        """
        # Eventos de edición de tabla
        if hasattr(self, 'celda_editando') and hasattr(self, 'input_edicion'):
            # Si estamos editando, dar prioridad a eventos del InputBox
            self.input_edicion.handle_event(event)
            
            # Teclas para confirmar o cancelar edición
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.finalizar_edicion(guardar=True)
                elif event.key == pygame.K_ESCAPE:
                    self.finalizar_edicion(guardar=False)
                    self.mensaje_edicion = "Edición cancelada"
            return

        # Eventos del formulario
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
         # Temporizador para ocultar mensajes
        if event.type == pygame.USEREVENT + 1:
            if hasattr(self, 'mensaje_edicion'):
                self.mensaje_edicion = ""
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Detener el temporizador


        # Eventos de navegación y búsqueda
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Detección de doble clic en celdas de la tabla
            if event.button == 1 and hasattr(self, 'celdas_tabla'):  # Botón izquierdo
                for rect, fila_idx, col_idx, key in self.celdas_tabla:
                    if rect.collidepoint(mouse_pos):
                        # Verificar si es doble clic (menos de 500ms entre clics)
                        tiempo_actual = pygame.time.get_ticks()
                        if (hasattr(self, 'ultimo_clic_tiempo') and 
                            tiempo_actual - self.ultimo_clic_tiempo < 500 and
                            hasattr(self, 'ultima_celda_clic') and 
                            self.ultima_celda_clic == (fila_idx, col_idx)):
                            # Es un doble clic, iniciar edición
                            self.iniciar_edicion_celda(fila_idx, col_idx, key)
                        
                        # Registrar este clic para detectar doble clic
                        self.ultimo_clic_tiempo = tiempo_actual
                        self.ultima_celda_clic = (fila_idx, col_idx)
                        break

            # Botones de navegación
            for i, rect in enumerate(self.boton_rects):
                if rect.collidepoint(mouse_pos):
                    self.opcion_seleccionada = self.botones_opciones[i]
                    self.cargar_datos_tabla()
                    return
            
            # Botón agregar
            if self.boton_agregar_rect.collidepoint(mouse_pos):
                self.mostrar_formulario_agregar()
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
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.agregar_hover = self.boton_agregar_rect.collidepoint(mouse_pos)
            
        elif event.type == pygame.KEYDOWN and self.busqueda_activa:
            # Manejo de teclas en búsqueda
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
        """
        Dibuja el formulario modal para agregar elementos al inventario
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
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
        titulo = "Agregar Materia Prima" if self.opcion_seleccionada == "MATERIA PRIMA" else "Agregar Insumo"
        text_title = font_title.render(titulo, True, (0, 0, 0))
        title_x = form_x + (form_w - text_title.get_width()) // 2  # Título centrado
        surface.blit(text_title, (title_x, form_y + 20))

        # Espaciado y posicionamiento
        label_x = form_x + 30
        input_x = form_x + int(form_w * 0.45)  # Posición fija para inputs
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
            surface.blit(msg, (form_x + (form_w - msg.get_width()) // 2, form_y + form_h - 50))  # Mensaje centrado

    def mostrar_formulario_agregar(self):
        """
        Configura y muestra el formulario para agregar nuevos elementos
        
        Diferencia entre insumos y materias primas:
        - Insumos: requieren fechas de entrada y caducidad
        - Materias primas: solo requieren información básica
        """
        self.mostrando_formulario = True
        font = pygame.font.SysFont("Open Sans", int(self.alto * 0.045))
        x = self.x + int(self.ancho * 0.22)
        y = self.y + int(self.alto * 0.20)
        
        # Definir campos según el tipo
        if self.opcion_seleccionada == "MATERIA PRIMA":
            labels = [
                "Nombre", "Precio", "stock_minimo", "Descripción", "Cantidad",
                "Entrada (YYYY-MM-DD)", "Caducidad (YYYY-MM-DD)"
            ]
        else:
            labels = ["Nombre", "Precio", "stock_minimo", "Descripción", "Cantidad"]
        
        # Crear labels y campos de entrada
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
        
        # Botones del formulario
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
        """
        Valida y guarda un nuevo elemento en el inventario
        
        Proceso:
        1. Valida campos obligatorios
        2. Convierte tipos de datos
        3. Valida fechas (para materia prima)
        4. Inserta en la base de datos
        
        Returns:
            None: Muestra mensajes de error en la interfaz
        """
        valores = [box.get_value().strip() for box in self.formulario_boxes]

        if self.opcion_seleccionada == "MATERIA PRIMA":
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
                INSERT INTO MateriaPrima
                (Nombre, Precio, stock_minimo, Descripcion, Cantidad, IVA, Estado, FK_ID_MedidaCantidad, FK_ID_TipoMateriaPrima, fecha_entrada, fecha_caducidad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1, 1, %s, %s)
            """#"Nombre", "Precio", "stock_minimo", "Descripción", "Cantidad",
                #"Entrada (YYYY-MM-DD)", "Caducidad (YYYY-MM-DD)"
            conexion.conectar()
            conexion.cursor.execute(insert, (
                nombre, precio, stock_minimo, descripcion, cantidad, iva, estado, fecha_entrada, fecha_caducidad
            ))

            conexion.conn.commit()
            conexion.cerrar()
            self.formulario_mensaje = f"Materia Prima '{nombre}' agregado."
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
                INSERT INTO Insumo (Nombre, Precio, stock_minimo, Descripcion, Cantidad, Estado, FK_ID_TipoInsumo)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
            """

            conexion.conectar()
            conexion.cursor.execute(insert, (nombre, precio, stock_minimo, descripcion, cantidad, estado))
            conexion.conn.commit()
            conexion.cerrar()
            self.formulario_mensaje = f"Insumo '{nombre}' agregada."
            self.cargar_datos_tabla()
            self.mostrando_formulario = False
            self.formulario_mensaje = ""