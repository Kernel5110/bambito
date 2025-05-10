"""
Menú Principal del Sistema de Panadería Bambi
-------------------------------------------
Sistema de navegación principal desarrollado en Pygame que integra:
- Punto de venta (POS)
- Gestión de almacén
- Gestión de pedidos
- Gestión de recetas
- Reportes de ventas
- Configuración/Ajustes
- Control de roles y permisos

Características principales:
- Interfaz adaptativa a diferentes resoluciones
- Sistema de permisos basado en roles
- Navegación modular entre secciones
- Integración con sistema de login
- Captura de pantalla con F12
- Diseño escalable

Versión: 1.0
"""

import pygame  # Biblioteca para crear la interfaz gráfica
import sys  # Módulo para operaciones del sistema
import login  # Módulo de login para autenticación
from puntoventa import PuntoVenta  # Clase para punto de venta
from almacen import almacen  # Clase para gestión de almacén
from reporte import reporte  # Clase para generación de reportes
from ajustes import ajustes  # Clase para configuración del sistema
import datetime  # Módulo para timestamps en capturas de pantalla
from pedido import Pedido  # Clase para gestión de pedidos
from receta import Receta  # Clase para gestión de recetas

# Inicialización de Pygame
pygame.init()

# Configuración de pantalla adaptativa
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

# Configuración de la ventana
ventana = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)  # Configura la ventana para que sea redimensionable.
pygame.display.set_caption("Panadería Bambi")  # Establece el título de la ventana.

# Definición de colores utilizados en la interfaz
color_fondo = (241, 236, 227)  # Color de fondo.
color_titulo = (205, 153, 194)  # Color del título.
color_texto_titulo = (77, 68, 64)  # Color del texto del título.
color_texto = (204, 208, 216)  # Color del texto.
color_menu = (219, 237, 232)  # Color del menú.
color_menu2 = (126, 205, 185)  # Color secundario del menú.
color_marco = (147, 123, 105)  # Color del marco.
color_usuario = (176, 240, 255)  # Color del usuario.
color_usuario2 = (65, 184, 213)  # Color secundario del usuario.
color_texto_usuario = (65, 184, 213)  # Color del texto del usuario.
color_boton = (219, 237, 232)  # Color del botón.
color_texto_boton = (74, 155, 135)  # Color del texto del botón.

# Escalado proporcional de fuentes
# Función para escalado proporcional de fuentes
def fuente_relativa(base_size):
    """
    Calcula el tamaño de fuente escalado según la resolución actual
    
    Args:
        base_size (int): Tamaño base para resolución 1900x1000
        
    Returns:
        int: Tamaño de fuente escalado
    """
    # Resolución base: 1900x1000
    scale = min(SCREEN_WIDTH / 1900, SCREEN_HEIGHT / 1000)
    return int(base_size * scale)


fuente_titulo = pygame.font.SysFont("Times New Roman", fuente_relativa(70), bold=True)  # Fuente para el título.
fuente_usuario = pygame.font.SysFont("Open Sans", fuente_relativa(40), bold=True)  # Fuente para el usuario.
fuente_boton = pygame.font.SysFont("Open Sans", fuente_relativa(40), bold=True)  # Fuente para el botón.

# Cargar y escalar las imágenes utilizadas en la interfaz
# Función para cargar y escalar imágenes
def cargar_imagen(path, base_size):
    """
    Carga y escala una imagen según la resolución actual
    
    Args:
        path (str): Ruta del archivo de imagen
        base_size (tuple): Tamaño base para resolución 1900x1000
        
    Returns:
        pygame.Surface: Imagen cargada y escalada
    """
    scale = min(SCREEN_WIDTH / 1900, SCREEN_HEIGHT / 1000)
    size = (int(base_size[0] * scale), int(base_size[1] * scale))
    img = pygame.image.load(path)
    return pygame.transform.scale(img, size)

imagen_logo = cargar_imagen("imagenes/log.png", (110, 110))  # Carga y escala la imagen del logo.
imagen_usuario = cargar_imagen("imagenes/usuario.png", (50, 50))  # Carga y escala la imagen del usuario.
imagen_venta = cargar_imagen("imagenes/venta.png", (50, 50))  # Carga y escala la imagen de venta.
imagen_almacen = cargar_imagen("imagenes/almacen.png", (50, 50))  # Carga y escala la imagen del almacén.
imagen_reporte = cargar_imagen("imagenes/reporte.png", (50, 50))  # Carga y escala la imagen del reporte.
imagen_ajuste = cargar_imagen("imagenes/ajuste.png", (50, 50))  # Carga y escala la imagen de ajustes.
imagen_salir = cargar_imagen("imagenes/salir.png", (50, 50))  # Carga y escala la imagen de salir.

# Instanciar módulos del sistema
# Todos los módulos se posicionan en el área de trabajo (85% de pantalla)
area_trabajo_x = int(0.15 * SCREEN_WIDTH)
area_trabajo_y = int(0.15 * SCREEN_HEIGHT)
area_trabajo_ancho = SCREEN_WIDTH - area_trabajo_x
area_trabajo_alto = SCREEN_HEIGHT - area_trabajo_x

# Instancia de las clases PuntoVenta, almacen, reporte y ajustes
punto_venta       = PuntoVenta(x=int(0.15 * SCREEN_WIDTH), y=int(0.15 * SCREEN_HEIGHT), ancho=SCREEN_WIDTH - int(0.15 * SCREEN_WIDTH), alto=SCREEN_HEIGHT - int(0.15 * SCREEN_WIDTH))  # Crea una instancia de la clase PuntoVenta.
almacen_instancia = almacen   (x=int(0.15 * SCREEN_WIDTH), y=int(0.15 * SCREEN_HEIGHT), ancho=SCREEN_WIDTH - int(0.15 * SCREEN_WIDTH), alto=SCREEN_HEIGHT - int(0.15 * SCREEN_WIDTH)) # Crea una instancia de la clase almacen.
reporte_instancia = reporte   (x=int(0.15 * SCREEN_WIDTH), y=int(0.15 * SCREEN_HEIGHT), ancho=SCREEN_WIDTH - int(0.15 * SCREEN_WIDTH), alto=SCREEN_HEIGHT - int(0.15 * SCREEN_WIDTH))  # Crea una instancia de la clase reporte.
ajustes_instancia = ajustes   (x=int(0.15 * SCREEN_WIDTH), y=int(0.15 * SCREEN_HEIGHT), ancho=SCREEN_WIDTH - int(0.15 * SCREEN_WIDTH), alto=SCREEN_HEIGHT - int(0.15 * SCREEN_WIDTH))  # Crea una instancia de la clase ajustes.
pedido_instancia =  Pedido    (x=int(0.15 * SCREEN_WIDTH), y=int(0.15 * SCREEN_HEIGHT), ancho=SCREEN_WIDTH - int(0.15 * SCREEN_WIDTH), alto=SCREEN_HEIGHT - int(0.15 * SCREEN_WIDTH))
receta_instancia =  Receta    (x=int(0.15 * SCREEN_WIDTH), y=int(0.15 * SCREEN_HEIGHT), ancho=SCREEN_WIDTH - int(0.15 * SCREEN_WIDTH), alto=SCREEN_HEIGHT - int(0.15 * SCREEN_WIDTH))

def dibujar_interfaz(nombre_usuario):
    """
    Dibuja la interfaz completa del menú principal
    
    Incluye:
    - Encabezado con título y usuario
    - Menú lateral con botones
    - Área principal para módulos activos
    
    Args:
        nombre_usuario (str): Nombre del usuario logueado
    """
    # Proporciones relativas
    w, h = SCREEN_WIDTH, SCREEN_HEIGHT  # Ancho y alto de la pantalla.

    # Dibujar el fondo
    ventana.fill(color_fondo)  # Rellena la ventana con el color de fondo.

    # Dibujar el marco del título
    pygame.draw.rect(ventana, color_titulo, (0, 0, w, int(0.15 * h)))  # Dibuja el marco del título.

    # Dibujar la imagen del logo
    ventana.blit(imagen_logo, (int(0.026 * w), int(0.03 * h)))  # Dibuja la imagen del logo.

    # Dibujar contorno del título
    pygame.draw.rect(ventana, color_marco, (int(0.31 * w), int(0.03 * h), int(0.36 * w), int(0.11 * h)), border_radius=20)  # Dibuja el contorno del título.

    # Dibujar el título
    texto_titulo = fuente_titulo.render("PANADERÍA BAMBI", True, color_texto)  # Renderiza el texto del título.
    ventana.blit(texto_titulo, (int(0.316 * w), int(0.045 * h)))  # Dibuja el texto del título.

    # Dibujar contorno del usuario
    pygame.draw.rect(ventana, color_usuario2, (int(0.866 * w), int(0.04 * h), int(0.13 * w), int(0.08 * h)), border_radius=30)  # Dibuja el contorno del usuario.
    pygame.draw.rect(ventana, color_usuario, (int(0.868 * w), int(0.045 * h), int(0.126 * w), int(0.07 * h)), border_radius=30)  # Dibuja el contorno interno del usuario.


    texto_usuario = fuente_usuario.render(nombre_usuario, True, color_texto_usuario)
    ventana.blit(texto_usuario, (int(0.915 * w), int(0.065 * h)))


    # Dibujar el nombre del usuario
    #texto_usuario = fuente_usuario.render("ADMIN", True, color_texto_usuario)  # Renderiza el texto del usuario.
    ventana.blit(texto_usuario, (int(0.915 * w), int(0.065 * h)))  # Dibuja el texto del usuario.

    # Dibujar la imagen del usuario
    ventana.blit(imagen_usuario, (int(0.874 * w), int(0.055 * h)))  # Dibuja la imagen del usuario.

    # Dibujar el marco del menú
    pygame.draw.rect(ventana, color_menu, (0, int(0.15 * h), int(0.15 * w), int(0.85 * h)))  # Dibuja el marco del menú.
    pygame.draw.rect(ventana, color_menu2, (int(0.15 * w), int(0.15 * h), int(0.005 * w), int(0.85 * h)))  # Dibuja el marco interno del menú.

    # Dibujar los botones del menú
    botones = [
        ("VENTA", imagen_venta),
        ("ALMACEN", imagen_almacen),
        ("PEDIDO", imagen_reporte), 
        ("RECETA", imagen_almacen),
        ("REPORTES", imagen_reporte),
        ("AJUSTES", imagen_ajuste),
        ("SALIR", imagen_salir)
    ]  # Lista de botones con sus respectivas imágenes.

    # Posiciones relativas para los botones
    posiciones_y = [
        int(0.17 * h), int(0.27 * h), int(0.37 * h), int(0.47 * h), int(0.57 * h), int(0.67 * h), int(0.87 * h)
    ] 

    boton_height = int(0.06 * h)  # Alto de los botones.
    boton_width = int(0.14 * w)  # Ancho de los botones.
    for i, (texto, imagen) in enumerate(botones):
        pygame.draw.rect(ventana, color_boton, (int(0.005 * w), posiciones_y[i], boton_width, boton_height))  # Dibuja el botón.
        ventana.blit(imagen, (int(0.011 * w), posiciones_y[i] + int(0.008 * h)))  # Dibuja la imagen del botón.
        texto_boton = fuente_boton.render(texto, True, color_texto_boton)  # Renderiza el texto del botón.
        ventana.blit(texto_boton, (int(0.042 * w), posiciones_y[i] + int(0.025 * h)))  # Dibuja el texto del botón.

    # Dibujar la sección activa
    if mostrar_punto_venta:
        punto_venta.dibujar_punto_venta(ventana)
    elif mostrar_almacen:
        almacen_instancia.dibujar_punto_venta(ventana)
    elif mostrar_pedidos:
        pedido_instancia.dibujar_pedido(ventana)
    elif mostrar_recetas:  # Añadir esta condición
        receta_instancia.dibujar_receta(ventana)
    elif mostrar_reportes:
        reporte_instancia.dibujar_reporte(ventana)
    elif mostrar_ajustes:
        ajustes_instancia.dibujar(ventana)

def ventas():
    """
    Función temporal para manejar la acción de ventas
    
    Note:
        Esta función se puede usar para acciones adicionales relacionadas con ventas
    """
    print("¡Éxito! Bienvenido")

# Variables globales para controlar la visualización de módulos
mostrar_punto_venta = False
mostrar_almacen = False
mostrar_reportes = False
mostrar_ajustes = False
mostrar_pedidos = False
mostrar_recetas = False

def main(nombre_usuario, puesto):
    """
    Función principal del menú
    
    Maneja:
    - Sistema de permisos basado en roles
    - Navegación entre módulos
    - Eventos de mouse y teclado
    - Redimensionamiento de ventana
    - Capturas de pantalla
    - Transición de regreso al login
    
    Args:
        nombre_usuario (str): Nombre del usuario logueado
        puesto (str): Rol del usuario (VENDEDOR, ALMACENISTA, GERENTE)
    """
    global mostrar_punto_venta, mostrar_almacen, mostrar_pedidos
    global mostrar_reportes, mostrar_ajustes, mostrar_recetas

    # Definir permisos según el rol
    permisos = {
        "VENDEDOR": ["VENTA", "PEDIDO"],  
        "ALMACENISTA": ["ALMACEN", "RECETA"],  # Añadir permiso de receta al almacenista
        "GERENTE": ["VENTA", "ALMACEN", "PEDIDO", "RECETA", "REPORTES", "AJUSTES"]  # Añadir permiso de receta al gerente
    }

    # Obtener permisos del usuario actual
    permisos_usuario = permisos.get(puesto, [])

    en_menu = True
    while en_menu:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    global SCREEN_WIDTH, SCREEN_HEIGHT, ventana
                    SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                    ventana = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # Usar proporciones para detectar clicks en los botones
                    if int(0.005 * SCREEN_WIDTH) <= mouse_x <= int(0.145 * SCREEN_WIDTH):
                        if int(0.17 * SCREEN_HEIGHT) <= mouse_y <= int(0.23 * SCREEN_HEIGHT) and "VENTA" in permisos_usuario:
                            mostrar_punto_venta = True
                            mostrar_almacen = False
                            mostrar_pedidos = False
                            mostrar_reportes = False
                            mostrar_ajustes = False
                        elif int(0.27 * SCREEN_HEIGHT) <= mouse_y <= int(0.33 * SCREEN_HEIGHT) and "ALMACEN" in permisos_usuario:
                            mostrar_almacen = True
                            mostrar_punto_venta = False
                            mostrar_pedidos = False
                            mostrar_reportes = False
                            mostrar_ajustes = False
                        elif int(0.37 * SCREEN_HEIGHT) <= mouse_y <= int(0.43 * SCREEN_HEIGHT) and "PEDIDO" in permisos_usuario:
                            mostrar_pedidos = True
                            mostrar_punto_venta = False
                            mostrar_almacen = False
                            mostrar_recetas = False
                            mostrar_reportes = False
                            mostrar_ajustes = False
                        elif int(0.47 * SCREEN_HEIGHT) <= mouse_y <= int(0.53 * SCREEN_HEIGHT) and "RECETA" in permisos_usuario:
                            # Añadir esta condición para el botón de receta
                            mostrar_recetas = True
                            mostrar_punto_venta = False
                            mostrar_almacen = False
                            mostrar_pedidos = False
                            mostrar_reportes = False
                            mostrar_ajustes = False
                        elif int(0.57 * SCREEN_HEIGHT) <= mouse_y <= int(0.63 * SCREEN_HEIGHT) and "REPORTES" in permisos_usuario:
                            mostrar_reportes = True
                            mostrar_punto_venta = False
                            mostrar_almacen = False
                            mostrar_pedidos = False
                            mostrar_recetas = False
                            mostrar_ajustes = False
                        elif int(0.67 * SCREEN_HEIGHT) <= mouse_y <= int(0.73 * SCREEN_HEIGHT) and "AJUSTES" in permisos_usuario:
                            mostrar_ajustes = True
                            mostrar_punto_venta = False
                            mostrar_almacen = False
                            mostrar_pedidos = False
                            mostrar_recetas = False
                            mostrar_reportes = False
                        elif int(0.87 * SCREEN_HEIGHT) <= mouse_y <= int(0.93 * SCREEN_HEIGHT):
                            en_menu = False  # Salir del menú

                # Pasa eventos a la sección activa
                elif event.type == pygame.KEYDOWN:
                    # --- Captura de pantalla con F12 ---
                    if event.key == pygame.K_F12:
                        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"screenshot_{now}.png"
                        pygame.image.save(ventana, filename)
                        print(f"Captura de pantalla guardada como {filename}")
                
                if mostrar_recetas:
                    receta_instancia.handle_event(event)
                elif mostrar_punto_venta:
                    punto_venta.handle_event(event)
                if mostrar_pedidos:
                    pedido_instancia.handle_event(event)
                elif mostrar_almacen:
                    almacen_instancia.handle_event(event)
                elif mostrar_reportes:
                    reporte_instancia.handle_event(event)
                elif mostrar_ajustes:
                    ajustes_instancia.handle_event(event)
                

            dibujar_interfaz(nombre_usuario)
            pygame.display.flip()
        except Exception as e:
            print("Ocurrió un error:", e)
            pygame.quit()
            sys.exit()

    # Al salir del menú, regresa al login
    login.main()


if __name__ == '__main__':
     # Modo debug - iniciar directamente como gerente
    main('Bernardo', 'GERENTE')