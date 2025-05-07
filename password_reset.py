
import pygame
import random
import string
import smtplib
from email.mime.text import MIMEText
from conexion import Conexion

def validar_empleado_en_bd(nombre, ap_pat, ap_mat, correo):
    conn = Conexion()
    conn.conectar()
    if not conn.conn:
        return None
    query = """
        SELECT Id_Empleado FROM Empleado
        WHERE Nombre_emple = %s AND Ap_Paterno_emple = %s AND Ap_Materno_emple = %s AND Correo_Electronico = %s
    """
    conn.cursor.execute(query, (nombre, ap_pat, ap_mat, correo))
    resultado = conn.cursor.fetchone()
    conn.cerrar()
    if resultado:
        return resultado['Id_Empleado']
    return None

def actualizar_contrasena_empleado(id_empleado, nueva_contra):
    conn = Conexion()
    conn.conectar()
    if not conn.conn:
        return
    query = "UPDATE Empleado SET Contrasena_emple = %s WHERE Id_Empleado = %s"
    conn.cursor.execute(query, (nueva_contra, id_empleado))
    conn.conn.commit()
    conn.cerrar()

def generar_contrasena_aleatoria(longitud=10):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def enviar_correo(destinatario, nueva_contra):
    remitente = "nado17hernsvas@gmail.com"
    password = "rhkt wtfb cjco swpw"
    asunto = "Restablecimiento de contraseña"
    cuerpo = f"Su nueva contraseña es: {nueva_contra}"

    msg = MIMEText(cuerpo, _charset="utf-8")
    msg['Subject'] = asunto
    msg['From'] = remitente
    msg['To'] = destinatario

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False

def draw_button(screen, rect, text, font, color, text_color):
    pygame.draw.rect(screen, color, rect, border_radius=8)
    txt_surface = font.render(text, True, text_color)
    text_rect = txt_surface.get_rect(center=rect.center)
    screen.blit(txt_surface, text_rect)

def mostrar_formulario_cambio_contrasena(screen):
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 22)
    font_small = pygame.font.SysFont('Arial', 16)
    font_title = pygame.font.SysFont('Arial', 28, bold=True)
    labels = ["Nombre", "Apellido Paterno", "Apellido Materno", "Correo Electrónico"]
    placeholders = ["Ej: Juan", "Ej: Pérez", "Ej: López", "Ej: juan@email.com"]
    datos = ["", "", "", ""]
    active_box = 0
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color_placeholder = pygame.Color('gray70')
    color_success = pygame.Color('green')
    color_error = pygame.Color('red')
    input_rects = [pygame.Rect(60, 80 + i*60, 380, 38) for i in range(4)]
    button_rect = pygame.Rect(150, 340, 200, 45)
    running = True
    mensaje = ""
    mensaje_color = color_error

    while running:
        screen.fill((245, 248, 255))
        # Título
        title_surface = font_title.render("Restablecer Contraseña", True, (30, 30, 80))
        screen.blit(title_surface, (screen.get_width()//2 - title_surface.get_width()//2, 20))

        # Campos de entrada
        for i, label in enumerate(labels):
            label_surface = font_small.render(label, True, (40, 40, 40))
            screen.blit(label_surface, (input_rects[i].x, input_rects[i].y - 18))
            rect = input_rects[i]
            color = color_active if i == active_box else color_inactive
            pygame.draw.rect(screen, color, rect, 2, border_radius=6)
            # Placeholder o texto
            if datos[i]:
                input_text = font.render(datos[i], True, (0, 0, 0))
                screen.blit(input_text, (rect.x+8, rect.y+6))
            else:
                placeholder_surface = font.render(placeholders[i], True, color_placeholder)
                screen.blit(placeholder_surface, (rect.x+8, rect.y+6))

        # Botón
        draw_button(screen, button_rect, "Restablecer y Enviar", font, (30, 120, 200), (255, 255, 255))

        # Mensaje
        if mensaje:
            msg_surface = font_small.render(mensaje, True, mensaje_color)
            screen.blit(msg_surface, (screen.get_width()//2 - msg_surface.get_width()//2, 400))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_box = (active_box + 1) % 4
                elif event.key == pygame.K_RETURN:
                    # Simula click en el botón
                    if all(datos):
                        user_id = validar_empleado_en_bd(*datos)
                        if user_id:
                            nueva_contra = generar_contrasena_aleatoria()
                            actualizar_contrasena_empleado(user_id, nueva_contra)
                            if enviar_correo(datos[3], nueva_contra):
                                mensaje = "¡Contraseña restablecida y enviada por correo!"
                                mensaje_color = color_success
                                datos = ["", "", "", ""]
                            else:
                                mensaje = "Error al enviar el correo."
                                mensaje_color = color_error
                        else:
                            mensaje = "Datos incorrectos o usuario no encontrado."
                            mensaje_color = color_error
                    else:
                        mensaje = "Por favor, completa todos los campos."
                        mensaje_color = color_error
                elif event.key == pygame.K_BACKSPACE:
                    datos[active_box] = datos[active_box][:-1]
                else:
                    # Limita el correo a caracteres válidos
                    if active_box == 3:
                        if len(datos[active_box]) < 50 and (event.unicode.isalnum() or event.unicode in "@._-"):
                            datos[active_box] += event.unicode
                    else:
                        if len(datos[active_box]) < 50 and (event.unicode.isalpha() or event.unicode in " áéíóúÁÉÍÓÚñÑ'-"):
                            datos[active_box] += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Selección de campo
                for i, rect in enumerate(input_rects):
                    if rect.collidepoint(event.pos):
                        active_box = i
                # Click en botón
                if button_rect.collidepoint(event.pos):
                    if all(datos):
                        user_id = validar_empleado_en_bd(*datos)
                        if user_id:
                            nueva_contra = generar_contrasena_aleatoria()
                            actualizar_contrasena_empleado(user_id, nueva_contra)
                            if enviar_correo(datos[3], nueva_contra):
                                mensaje = "¡Contraseña restablecida y enviada por correo!"
                                mensaje_color = color_success
                                datos = ["", "", "", ""]
                                pygame.display.quit()  # Cierra la ventana pequeña
                                from login import main
                                main()
                                return
                            else:
                                mensaje = "Error al enviar el correo."
                                mensaje_color = color_error
                        else:
                            mensaje = "Datos incorrectos o usuario no encontrado."
                            mensaje_color = color_error
                    else:
                        mensaje = "Por favor, completa todos los campos."
                        mensaje_color = color_error

        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((500, 450))
    pygame.display.set_caption("Restablecer contraseña")
    mostrar_formulario_cambio_contrasena(screen)
    pygame.quit()