"""
Sistema de Login para Panadería Bambi
------------------------------------
Sistema de autenticación desarrollado en Pygame con:
- Interfaz gráfica adaptativa
- Autenticación contra base de datos
- Validación de credenciales
- Registro de sesiones (logs)
- Restablecimiento de contraseña
- Integración con menú principal

Características:
- Pantalla completa adaptativa
- Campos de entrada con validación
- Manejo de intentos fallidos
- Sistema de logs para seguridad
- Navegación con botones estilizados

Versión: 1.0
"""

import pygame  # Importa la biblioteca pygame para crear la interfaz gráfica.
import sys  # Importa el módulo sys para manejar operaciones del sistema.
import os  # Importa el módulo os para manejar rutas de archivos y directorios.
import datetime  # Importa el módulo datetime para manejar fechas y horas.
from password_reset import mostrar_formulario_cambio_contrasena
from icecream import ic

# Importa la conexión MySQL desde el archivo 'conexion.py' en el directorio 'db'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'db')))
from receta import Conexion  # Importa la clase Conexion desde el módulo conexion.

# Importa el menú principal desde el archivo 'menu.py'
import menu 
con_intentos = 0
# Inicializar pygame
pygame.init()  # Inicializa todos los módulos de pygame. 

# Obtener tamaño de pantalla del usuario
info = pygame.display.Info()  # Obtiene información sobre el entorno de visualización actual.
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h  # Asigna el ancho y alto de la pantalla.

# Configuración de la ventana (pantalla completa)
ventana = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)  # Configura la ventana en pantalla completa.
pygame.display.set_caption("Panadería Bambi")  # Establece el título de la ventana.

# Colores (en formato RGB)
color_fondo = (218, 179, 166)  # Color de fondo.
color_marco = (204, 208, 216)  # Color del marco principal.
color_marco2 = (203, 108, 230)  # Color del segundo marco.
color_marco3 = (246, 140, 224)  # Color del tercer marco.
color_marco4 = (74, 206, 209)  # Color del cuarto marco.
color_marco_titulo = (80, 70, 70)  # Color del marco del título.
color_titulo = (204, 208, 210)  # Color del texto del título.
color_texto = (152, 114, 114)  # Color del texto.
color_boton = (159, 212, 199)  # Color del botón.
color_texto_boton = (74, 155, 135)  # Color del texto del botón.
color_fondo_entry = (241, 236, 227)  # Color de fondo de los campos de entrada.
color_fondo_contraseña = (51, 51, 51)  # Color de fondo del campo de contraseña.
color_boton_salir = (220, 80, 80)  # Color del botón de salir.
color_boton_salir_hover = (255, 120, 120)  # Color del botón de salir cuando el mouse está sobre él.
color_texto_salir = (255, 255, 255)  # Color del texto del botón de salir.
color_x = (220, 80, 80)  # Color del botón "X".
color_x_hover = (255, 80, 80)  # Color del botón "X" cuando el mouse está sobre él.

# Fuentes (tamaño relativo a la altura de pantalla)+++++
def fuente_titulo():
    return pygame.font.SysFont("Times New Roman", int(SCREEN_HEIGHT * 0.080), bold=True)  # Fuente para el título.

def fuente_entrada():
    return pygame.font.SysFont("Open Sans", int(SCREEN_HEIGHT * 0.036))  # Fuente para los campos de entrada.

def fuente_boton():
    return pygame.font.SysFont("Open Sans", int(SCREEN_HEIGHT * 0.08), bold=True)  # Fuente para el botón.

def fuente_salir():
    return pygame.font.SysFont("Open Sans", int(SCREEN_HEIGHT * 0.045), bold=True)  # Fuente para el botón de salir.

def fuente_x():
    return pygame.font.SysFont("Arial", int(SCREEN_HEIGHT * 0.035), bold=True)  # Fuente para el botón "X".

# Cargar logo
try:
    logo = pygame.image.load("imagenes/log.png")  # Intenta cargar la imagen del logo.
    logo_size = int(SCREEN_HEIGHT * 0.20)  # Tamaño del logo en relación a la altura de la pantalla.
    logo = pygame.transform.scale(logo, (logo_size, logo_size))  # Redimensiona el logo.
except:
    logo = None  # Si falla la carga del logo, asigna None.

# Variables para campos de entrada
usuario_activo = False  # Indica si el campo de usuario está activo.
contraseña_activa = False  # Indica si el campo de contraseña está activo.
usuario_texto = "CORREO ELECTRÓNICO"  # Texto predeterminado del campo de usuario.
contraseña_texto = "CONTRASEÑA"  # Texto predeterminado del campo de contraseña.
mensaje_login = ""  # Mensaje de login.
color_mensaje = (255, 0, 0)  # Color del mensaje de login.
salir_hover = False  # Indica si el mouse está sobre el botón de salir.
x_hover = False  # Indica si el mouse está sobre el botón "X".

def dibujar_interfaz():
    global usuario_activo, contraseña_activa, usuario_texto, contraseña_texto, mensaje_login, color_mensaje, salir_hover, x_hover

    ventana.fill(color_fondo)  # Rellena la ventana con el color de fondo.

    # Proporciones para el marco principal
    marco_x = int(SCREEN_WIDTH * 0.23)  # Coordenada x del marco.
    marco_y = int(SCREEN_HEIGHT * 0.13)  # Coordenada y del marco.
    marco_w = int(SCREEN_WIDTH * 0.55)  # Ancho del marco.
    marco_h = int(SCREEN_HEIGHT * 0.74)  # Alto del marco.

    pygame.draw.rect(ventana, color_marco2, (marco_x, marco_y, marco_w, marco_h), border_radius=30)  # Dibuja el marco exterior.
    pygame.draw.rect(ventana, color_marco, (marco_x + 20, marco_y + 20, marco_w - 40, marco_h - 40), border_radius=30)  # Dibuja el marco interior.

    # Logo
    if logo:
        logo_x = marco_x + int(marco_w * 0.17)  # Coordenada x del logo.
        logo_y = marco_y + int(marco_h * 0.11)  # Coordenada y del logo.
        ventana.blit(logo, (logo_x, logo_y))  # Dibuja el logo en la ventana.

    # Marco título
    marco_titulo_x = marco_x + int(marco_w * 0.35)  # Coordenada x del marco del título.
    marco_titulo_y = marco_y + int(marco_h * 0.09)  # Coordenada y del marco del título.
    marco_titulo_w = int(marco_w * 0.49)  # Ancho del marco del título.
    marco_titulo_h = int(marco_h * 0.27)  # Alto del marco del título.
    pygame.draw.rect(ventana, color_marco_titulo, (marco_titulo_x, marco_titulo_y, marco_titulo_w, marco_titulo_h), border_radius=20)  # Dibuja el marco del título.

    # Títulos
    titulo1 = fuente_titulo().render("PANADERÍA", True, color_titulo)  # Renderiza el primer título.
    ventana.blit(titulo1, (marco_titulo_x + 5, marco_titulo_y + 10))  # Dibuja el primer título.
    titulo2 = fuente_titulo().render("BAMBI", True, color_titulo)  # Renderiza el segundo título.
    ventana.blit(titulo2, (marco_titulo_x + 110, marco_titulo_y + int(marco_titulo_h * 0.55)))  # Dibuja el segundo título.

    # Campo de usuario
    entry_w = int(marco_w * 0.69)  # Ancho del campo de usuario.
    entry_h = int(marco_h * 0.13)  # Alto del campo de usuario.
    entry_x = marco_x + int(marco_w * 0.15)  # Coordenada x del campo de usuario.
    entry_y = marco_y + int(marco_h * 0.41)  # Coordenada y del campo de usuario.
    pygame.draw.rect(ventana, color_marco3, (entry_x - 10, entry_y - 10, entry_w + 20, entry_h + 20), border_radius=20)  # Dibuja el borde del campo de usuario.
    pygame.draw.rect(ventana, color_fondo_entry, (entry_x, entry_y, entry_w, entry_h), border_radius=20)  # Dibuja el fondo del campo de usuario.
    if usuario_activo:
        pygame.draw.rect(ventana, color_texto, (entry_x, entry_y, entry_w, entry_h), 2)  # Dibuja el borde activo del campo de usuario.
    usuario_surface = fuente_entrada().render(usuario_texto, True, color_texto)  # Renderiza el texto del campo de usuario.
    ventana.blit(usuario_surface, (entry_x + 10, entry_y + entry_h // 3))  # Dibuja el texto del campo de usuario.

    # Campo de contraseña
    entry2_y = entry_y + entry_h + int(marco_h * 0.03)  # Coordenada y del campo de contraseña.
    pygame.draw.rect(ventana, color_marco4, (entry_x - 10, entry2_y - 10, entry_w + 20, entry_h + 20), border_radius=20)  # Dibuja el borde del campo de contraseña.
    pygame.draw.rect(ventana, color_fondo_entry, (entry_x, entry2_y, entry_w, entry_h), border_radius=20)  # Dibuja el fondo del campo de contraseña.
    if contraseña_activa:
        pygame.draw.rect(ventana, color_texto, (entry_x, entry2_y, entry_w, entry_h), 2)  # Dibuja el borde activo del campo de contraseña.
    display_contra = "*" * len(contraseña_texto) if contraseña_texto and contraseña_texto != "CONTRASEÑA" else contraseña_texto  # Muestra asteriscos si hay texto en el campo de contraseña.
    contraseña_surface = fuente_entrada().render(display_contra, True, color_texto)  # Renderiza el texto del campo de contraseña.
    ventana.blit(contraseña_surface, (entry_x + 10, entry2_y + entry_h // 3))  # Dibuja el texto del campo de contraseña.

    # Botón de login
    boton_y = entry2_y + entry_h + int(marco_h * 0.03)  # Coordenada y del botón de login.
    pygame.draw.rect(ventana, color_boton, (entry_x, boton_y, entry_w, entry_h), border_radius=20)  # Dibuja el botón de login.
    boton_login_surface = fuente_boton().render("SIGN IN", True, color_texto_boton)  # Renderiza el texto del botón de login.
    ventana.blit(boton_login_surface, (entry_x + entry_w // 3, boton_y + entry_h // 6))  # Dibuja el texto del botón de login.

    # Mensaje de login
    if mensaje_login:
        fuente_mensaje = pygame.font.SysFont("Open Sans", int(SCREEN_HEIGHT * 0.032), bold=True)  # Fuente para el mensaje de login.
        mensaje_surface = fuente_mensaje.render(mensaje_login, True, color_mensaje)  # Renderiza el mensaje de login.
        ventana.blit(mensaje_surface, (entry_x, boton_y + entry_h + int(marco_h * 0.04)))  # Dibuja el mensaje de login.

    # --- Botón Salir ---
    salir_w = int(SCREEN_WIDTH * 0.12)  # Ancho del botón de salir.
    salir_h = int(SCREEN_HEIGHT * 0.06)  # Alto del botón de salir.
    salir_x = SCREEN_WIDTH - salir_w - int(SCREEN_WIDTH * 0.025)  # Coordenada x del botón de salir.
    salir_y = SCREEN_HEIGHT - salir_h - int(SCREEN_HEIGHT * 0.025)  # Coordenada y del botón de salir.
    color_salir = color_boton_salir_hover if salir_hover else color_boton_salir  # Color del botón de salir dependiendo del estado de hover.
    pygame.draw.rect(ventana, color_salir, (salir_x, salir_y, salir_w, salir_h), border_radius=18)  # Dibuja el botón de salir.
    pygame.draw.rect(ventana, (120, 0, 0), (salir_x, salir_y, salir_w, salir_h), 2, border_radius=18)  # Dibuja el borde del botón de salir.
    salir_text = fuente_salir().render("Salir", True, color_texto_salir)  # Renderiza el texto del botón de salir.
    ventana.blit(salir_text, (salir_x + (salir_w - salir_text.get_width()) // 2, salir_y + (salir_h - salir_text.get_height()) // 2))  # Dibuja el texto del botón de salir.

    # --- Botón X en la esquina superior derecha ---
    x_size = int(SCREEN_HEIGHT * 0.045)  # Tamaño del botón "X".
    x_pad = int(SCREEN_WIDTH * 0.012)  # Espaciado del botón "X".
    x_rect = pygame.Rect(SCREEN_WIDTH - x_size - x_pad, x_pad, x_size, x_size)  # Rectángulo del botón "X".
    color_x_btn = color_x_hover if x_hover else color_x  # Color del botón "X" dependiendo del estado de hover.
    pygame.draw.rect(ventana, color_x_btn, x_rect, border_radius=10)  # Dibuja el botón "X".
    pygame.draw.rect(ventana, (120, 0, 0), x_rect, 2, border_radius=10)  # Dibuja el borde del botón "X".
    # Dibuja la X
    x_font = fuente_x()  # Fuente para el botón "X".
    x_text = x_font.render("X", True, (255, 255, 255))  # Renderiza el texto del botón "X".
    ventana.blit(x_text, (x_rect.x + (x_size - x_text.get_width()) // 2, x_rect.y + (x_size - x_text.get_height()) // 2))  # Dibuja el texto del botón "X".

def verificar_login():
    global usuario_texto, contraseña_texto, mensaje_login, color_mensaje, con_intentos

    correo = usuario_texto.strip()
    contrasena = contraseña_texto.strip()

    if not correo or correo == "CORREO ELECTRÓNICO" or not contrasena or contrasena == "CONTRASEÑA":
        mensaje_login = "Por favor, ingresa tu correo y contraseña."
        color_mensaje = (255, 0, 0)
        return None

    conexion = Conexion()
    try:
        # encontrar al empleado 
        query = """
            SELECT Id_Empleado, Nombre_emple FROM Empleado
            WHERE Correo_Electronico = %s AND Estado_emple = 'Activo'
        """
        encontrado = conexion.consultar(query, (correo,))
        if encontrado:
            # verificar la contrasena
            query = """
            SELECT Id_Empleado, Nombre_emple, stoPuesto FROM Empleado
            WHERE Correo_Electronico = %s AND Contrasena_emple = %s AND Estado_emple = 'Activo'
            """
            resultados = conexion.consultar(query, (correo, contrasena))
            user = resultados[0] if resultados else None

            if user is None: con_intentos += 1

        if user:
            descripcion = f"Inicio de sesión exitoso para {correo}"
            tipo = "Seguridad"
            id_empleado = user["Id_Empleado"]
            conexion.conectar()
            insert_log = """
                INSERT INTO Log (Descripcion, Tipo, FK_ID_Usuario)
                VALUES (%s, %s, %s)
            """
            conexion.cursor.execute(insert_log, (descripcion, tipo, id_empleado))
            conexion.conn.commit()
            conexion.cerrar()
            mensaje_login = f"¡Bienvenido, {user['Nombre_emple']}!"
            color_mensaje = (0, 180, 0)
            primer_nombre = user['Nombre_emple'].split()[0]
            puesto = user['stoPuesto'].split()[0]
            return (primer_nombre, puesto)  # <--- Devuelve el nombre
        else:
            if con_intentos <= 3:
                mensaje_login = "Usuario o contraseña incorrectos."
            else:
                mensaje_login = "Considere cambiar la contraseña."
                pygame.init()
                screen = pygame.display.set_mode((500, 450))
                pygame.display.set_caption("Restablecer contraseña")
                mostrar_formulario_cambio_contrasena(screen)
            color_mensaje = (255, 0, 0)
            return (None, None)
    except Exception as e:
        mensaje_login = f"Error: {str(e)}"
        color_mensaje = (255, 0, 0)
        return (None, None)
    finally:
        conexion.cerrar()

def main():
    global usuario_activo, contraseña_activa, usuario_texto, contraseña_texto, salir_hover, x_hover

    # Proporciones para los campos
    marco_x = int(SCREEN_WIDTH * 0.23)  # Coordenada x del marco.
    marco_y = int(SCREEN_HEIGHT * 0.13)  # Coordenada y del marco.
    marco_w = int(SCREEN_WIDTH * 0.55)  # Ancho del marco.
    marco_h = int(SCREEN_HEIGHT * 0.74)  # Alto del marco.
    entry_w = int(marco_w * 0.69)  # Ancho del campo de entrada.
    entry_h = int(marco_h * 0.13)  # Alto del campo de entrada.
    entry_x = marco_x + int(marco_w * 0.15)  # Coordenada x del campo de entrada.
    entry_y = marco_y + int(marco_h * 0.41)  # Coordenada y del campo de entrada.
    entry2_y = entry_y + entry_h + int(marco_h * 0.03)  # Coordenada y del segundo campo de entrada.
    boton_y = entry2_y + entry_h + int(marco_h * 0.03)  # Coordenada y del botón de login.

    salir_w = int(SCREEN_WIDTH * 0.12)  # Ancho del botón de salir.
    salir_h = int(SCREEN_HEIGHT * 0.06)  # Alto del botón de salir.
    salir_x = SCREEN_WIDTH - salir_w - int(SCREEN_WIDTH * 0.025)  # Coordenada x del botón de salir.
    salir_y = SCREEN_HEIGHT - salir_h - int(SCREEN_HEIGHT * 0.025)  # Coordenada y del botón de salir.

    x_size = int(SCREEN_HEIGHT * 0.045)  # Tamaño del botón "X".
    x_pad = int(SCREEN_WIDTH * 0.012)  # Espaciado del botón "X".
    x_rect = pygame.Rect(SCREEN_WIDTH - x_size - x_pad, x_pad, x_size, x_size)  # Rectángulo del botón "X".

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos  # Obtiene las coordenadas del mouse.
                # Campo de usuario
                if entry_x <= mouse_x <= entry_x + entry_w and entry_y <= mouse_y <= entry_y + entry_h:
                    usuario_activo = True  # Activa el campo de usuario.
                    contraseña_activa = False  # Desactiva el campo de contraseña.
                    if usuario_texto == "CORREO ELECTRÓNICO":
                        usuario_texto = ""  # Limpia el texto del campo de usuario.
                # Campo de contraseña
                elif entry_x <= mouse_x <= entry_x + entry_w and entry2_y <= mouse_y <= entry2_y + entry_h:
                    usuario_activo = False  # Desactiva el campo de usuario.
                    contraseña_activa = True  # Activa el campo de contraseña.
                    if contraseña_texto == "CONTRASEÑA":
                        contraseña_texto = ""  # Limpia el texto del campo de contraseña.
                # Botón de login
                elif entry_x <= mouse_x <= entry_x + entry_w and boton_y <= mouse_y <= boton_y + entry_h:
                    nombre_usuario, puesto = verificar_login()
                    if nombre_usuario:
                        return (nombre_usuario, puesto)  # <--- SOLO return, NO pygame.display.quit()
                # Botón salir
                elif salir_x <= mouse_x <= salir_x + salir_w and salir_y <= mouse_y <= salir_y + salir_h:
                    pygame.quit()
                    sys.exit()
                # Botón X
                elif x_rect.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.KEYDOWN:
                if usuario_activo: 
                    if event.key == pygame.K_BACKSPACE:
                        usuario_texto = usuario_texto[:-1]  # Elimina el último carácter del campo de usuario.
                    else:
                        usuario_texto += event.unicode  # Añade el carácter al campo de usuario.
                elif contraseña_activa:
                    if event.key == pygame.K_BACKSPACE:
                        contraseña_texto = contraseña_texto[:-1]  # Elimina el último carácter del campo de contraseña.
                    else:
                        contraseña_texto += event.unicode  # Añade el carácter al campo de contraseña.
                # Permitir salir con ESC
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos  # Obtiene las coordenadas del mouse.
                salir_hover = salir_x <= mouse_x <= salir_x + salir_w and salir_y <= mouse_y <= salir_y + salir_h  # Actualiza el estado de hover del botón de salir.
                x_hover = x_rect.collidepoint(mouse_x, mouse_y)  # Actualiza el estado de hover del botón "X".
            

        dibujar_interfaz()  # Dibuja la interfaz.
        pygame.display.flip()  # Actualiza la pantalla.

if __name__ == "__main__":
    nombre_usuario, puesto = ic(main())  # Ejecuta la función principal.
    menu.main(nombre_usuario, puesto) # Ejecuta el menú principal.
