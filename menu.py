"""
Menú Principal del Sistema de Panadería Bambi - OPTIMIZADO
---------------------------------------------------------
Sistema de navegación principal con carga perezosa (lazy loading)
Características mejoradas:
- Carga módulos solo cuando se necesitan
- Instanciación bajo demanda
- Cache de instancias para reutilización
- Mejor rendimiento de inicio
- Menor uso de memoria inicial

Versión: 1.1 Optimizada
"""

import pygame  # Biblioteca para crear la interfaz gráfica
import sys  # Módulo para operaciones del sistema
import login  # Módulo de login para autenticación
import datetime  # Módulo para timestamps en capturas de pantalla

# Inicialización de Pygame
pygame.init()

# Configuración de pantalla adaptativa
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

# Configuración de la ventana
ventana = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Panadería Bambi")

# Definición de colores utilizados en la interfaz
color_fondo = (241, 236, 227)
color_titulo = (205, 153, 194)
color_texto_titulo = (77, 68, 64)
color_texto = (204, 208, 216)
color_menu = (219, 237, 232)
color_menu2 = (126, 205, 185)
color_marco = (147, 123, 105)
color_usuario = (176, 240, 255)
color_usuario2 = (65, 184, 213)
color_texto_usuario = (65, 184, 213)
color_boton = (219, 237, 232)
color_texto_boton = (74, 155, 135)

# Función para escalado proporcional de fuentes
def fuente_relativa(base_size):
    """
    Calcula el tamaño de fuente escalado según la resolución actual
    
    Args:
        base_size (int): Tamaño base para resolución 1900x1000
        
    Returns:
        int: Tamaño de fuente escalado
    """
    scale = min(SCREEN_WIDTH / 1900, SCREEN_HEIGHT / 1000)
    return int(base_size * scale)

fuente_titulo = pygame.font.SysFont("Times New Roman", fuente_relativa(70), bold=True)
fuente_usuario = pygame.font.SysFont("Open Sans", fuente_relativa(40), bold=True)
fuente_boton = pygame.font.SysFont("Open Sans", fuente_relativa(40), bold=True)

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

# Cargar solo las imágenes necesarias para la interfaz principal
imagen_logo = cargar_imagen("imagenes/log.png", (110, 110))
imagen_usuario = cargar_imagen("imagenes/usuario.png", (50, 50))
imagen_venta = cargar_imagen("imagenes/venta.png", (50, 50))
imagen_almacen = cargar_imagen("imagenes/almacen.png", (50, 50))
imagen_reporte = cargar_imagen("imagenes/reporte.png", (50, 50))
imagen_ajuste = cargar_imagen("imagenes/ajuste.png", (50, 50))
imagen_salir = cargar_imagen("imagenes/salir.png", (50, 50))
imagen_pedido = cargar_imagen("imagenes/pedido.png", (50, 50))
imagen_receta = cargar_imagen("imagenes/receta.png", (50, 50))

class ModuleLoader:
    """
    Clase para manejar la carga perezosa de módulos
    Implementa el patrón Singleton para cache de instancias
    """
    
    def __init__(self):
        self._modules = {}  # Cache de módulos importados
        self._instances = {}  # Cache de instancias creadas
    
    def get_area_trabajo_params(self):
        """Calcula parámetros del área de trabajo"""
        return {
            'x': int(0.155 * SCREEN_WIDTH),
            'y': int(0.15 * SCREEN_HEIGHT),
            'ancho': SCREEN_WIDTH - int(0.15 * SCREEN_WIDTH),
            'alto': SCREEN_HEIGHT - int(0.15 * SCREEN_WIDTH)
        }
    
    def load_punto_venta(self):
        """Carga perezosa del módulo PuntoVenta"""
        if 'PuntoVenta' not in self._instances:
            if 'puntoventa' not in self._modules:
                from puntoventa import PuntoVenta
                self._modules['puntoventa'] = PuntoVenta
            
            params = self.get_area_trabajo_params()
            self._instances['PuntoVenta'] = self._modules['puntoventa'](**params)
        
        return self._instances['PuntoVenta']
    
    def load_almacen(self):
        """Carga perezosa del módulo Almacén"""
        if 'almacen' not in self._instances:
            if 'almacen_module' not in self._modules:
                from almacen import almacen
                self._modules['almacen_module'] = almacen
            
            params = self.get_area_trabajo_params()
            self._instances['almacen'] = self._modules['almacen_module'](**params)
        
        return self._instances['almacen']
    
    def load_pedido(self):
        """Carga perezosa del módulo Pedido"""
        if 'Pedido' not in self._instances:
            if 'pedido' not in self._modules:
                from pedido import Pedido
                self._modules['pedido'] = Pedido
            
            params = self.get_area_trabajo_params()
            self._instances['Pedido'] = self._modules['pedido'](**params)
        
        return self._instances['Pedido']
    
    def load_receta(self):
        """Carga perezosa del módulo Receta"""
        if 'Receta' not in self._instances:
            if 'receta' not in self._modules:
                from receta import Receta
                self._modules['receta'] = Receta
            
            params = self.get_area_trabajo_params()
            self._instances['Receta'] = self._modules['receta'](**params)
        
        return self._instances['Receta']
    
    def load_reporte(self):
        """Carga perezosa del módulo Reporte"""
        if 'reporte' not in self._instances:
            if 'reporte_module' not in self._modules:
                from reporte import reporte
                self._modules['reporte_module'] = reporte
            
            params = self.get_area_trabajo_params()
            self._instances['reporte'] = self._modules['reporte_module'](**params)
        
        return self._instances['reporte']
    
    def load_ajustes(self):
        """Carga perezosa del módulo Ajustes"""
        if 'ajustes' not in self._instances:
            if 'ajustes_module' not in self._modules:
                from ajustes import ajustes
                self._modules['ajustes_module'] = ajustes
            
            params = self.get_area_trabajo_params()
            self._instances['ajustes'] = self._modules['ajustes_module'](**params)
        
        return self._instances['ajustes']
    
    def clear_cache(self):
        """Limpia el cache de instancias (útil para liberar memoria)"""
        self._instances.clear()
    
    def get_memory_usage(self):
        """Retorna información sobre módulos cargados"""
        return {
            'modules_loaded': len(self._modules),
            'instances_created': len(self._instances),
            'module_names': list(self._modules.keys()),
            'instance_names': list(self._instances.keys())
        }

# Instancia global del cargador de módulos
module_loader = ModuleLoader()

def dibujar_interfaz(nombre_usuario):
    """
    Dibuja la interfaz completa del menú principal
    """
    w, h = SCREEN_WIDTH, SCREEN_HEIGHT

    # Dibujar el fondo
    ventana.fill(color_fondo)

    # Dibujar el marco del título
    pygame.draw.rect(ventana, color_titulo, (0, 0, w, int(0.15 * h)))

    # Dibujar la imagen del logo
    ventana.blit(imagen_logo, (int(0.026 * w), int(0.03 * h)))

    # Dibujar contorno del título
    pygame.draw.rect(ventana, color_marco, (int(0.31 * w), int(0.03 * h), int(0.36 * w), int(0.11 * h)), border_radius=20)

    # Dibujar el título
    texto_titulo = fuente_titulo.render("PANADERÍA BAMBI", True, color_texto)
    ventana.blit(texto_titulo, (int(0.316 * w), int(0.045 * h)))

    # Dibujar contorno del usuario
    pygame.draw.rect(ventana, color_usuario2, (int(0.866 * w), int(0.04 * h), int(0.13 * w), int(0.08 * h)), border_radius=30)
    pygame.draw.rect(ventana, color_usuario, (int(0.868 * w), int(0.045 * h), int(0.126 * w), int(0.07 * h)), border_radius=30)

    # Dibujar el nombre del usuario
    texto_usuario = fuente_usuario.render(nombre_usuario, True, color_texto_usuario)
    ventana.blit(texto_usuario, (int(0.915 * w), int(0.065 * h)))

    # Dibujar la imagen del usuario
    ventana.blit(imagen_usuario, (int(0.874 * w), int(0.055 * h)))

    # Dibujar el marco del menú
    pygame.draw.rect(ventana, color_menu, (0, int(0.15 * h), int(0.15 * w), int(0.85 * h)))
    pygame.draw.rect(ventana, color_menu2, (int(0.15 * w), int(0.15 * h), int(0.005 * w), int(0.85 * h)))

    # Dibujar los botones del menú
    botones = [
        ("VENTA", imagen_venta),
        ("ALMACEN", imagen_almacen),
        ("PEDIDO", imagen_pedido), 
        ("RECETA", imagen_receta),
        ("REPORTES", imagen_reporte),
        ("AJUSTES", imagen_ajuste),
        ("SALIR", imagen_salir)
    ]

    # Posiciones relativas para los botones
    posiciones_y = [
        int(0.17 * h), int(0.27 * h), int(0.37 * h), int(0.47 * h), 
        int(0.57 * h), int(0.67 * h), int(0.87 * h)
    ] 

    boton_height = int(0.06 * h)
    boton_width = int(0.14 * w)
    for i, (texto, imagen) in enumerate(botones):
        pygame.draw.rect(ventana, color_boton, (int(0.005 * w), posiciones_y[i], boton_width, boton_height))
        ventana.blit(imagen, (int(0.011 * w), posiciones_y[i] + int(0.008 * h)))
        texto_boton = fuente_boton.render(texto, True, color_texto_boton)
        ventana.blit(texto_boton, (int(0.042 * w), posiciones_y[i] + int(0.025 * h)))

    # Dibujar la sección activa (solo se carga cuando se necesita)
    if mostrar_punto_venta:
        punto_venta_instance = module_loader.load_punto_venta()
        punto_venta_instance.dibujar_punto_venta(ventana)
    elif mostrar_almacen:
        almacen_instance = module_loader.load_almacen()
        almacen_instance.dibujar_punto_venta(ventana)
    elif mostrar_pedidos:
        pedido_instance = module_loader.load_pedido()
        pedido_instance.dibujar_pedido(ventana)
    elif mostrar_recetas:
        receta_instance = module_loader.load_receta()
        receta_instance.dibujar_receta(ventana)
    elif mostrar_reportes:
        reporte_instance = module_loader.load_reporte()
        reporte_instance.dibujar_reporte(ventana)
    elif mostrar_ajustes:
        ajustes_instance = module_loader.load_ajustes()
        ajustes_instance.dibujar(ventana)

# Variables globales para controlar la visualización de módulos
mostrar_punto_venta = False
mostrar_almacen = False
mostrar_reportes = False
mostrar_ajustes = False
mostrar_pedidos = False
mostrar_recetas = False

def main(nombre_usuario, puesto):
    """
    Función principal del menú optimizada
    
    Args:
        nombre_usuario (str): Nombre del usuario logueado
        puesto (str): Rol del usuario (VENDEDOR, ALMACENISTA, GERENTE)
    """
    global mostrar_punto_venta, mostrar_almacen, mostrar_pedidos
    global mostrar_reportes, mostrar_ajustes, mostrar_recetas

    # Definir permisos según el rol
    permisos = {
        "VENDEDOR": ["VENTA", "PEDIDO"],  
        "ALMACENISTA": ["ALMACEN", "RECETA"],
        "GERENTE": ["VENTA", "ALMACEN", "PEDIDO", "RECETA", "REPORTES", "AJUSTES"]
    }

    # Obtener permisos del usuario actual
    permisos_usuario = permisos.get(puesto, [])

    en_menu = True
    current_module_instance = None  # Para mantener referencia al módulo activo
    
    print(f"Sistema iniciado para {nombre_usuario} ({puesto})")
    print("Módulos se cargarán bajo demanda...")

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
                    # Limpiar cache al redimensionar para recalcular posiciones
                    module_loader.clear_cache()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # Detectar clicks en los botones y cargar módulos bajo demanda
                    if int(0.005 * SCREEN_WIDTH) <= mouse_x <= int(0.145 * SCREEN_WIDTH):
                        # Reset todas las variables
                        mostrar_punto_venta = mostrar_almacen = mostrar_pedidos = False
                        mostrar_reportes = mostrar_ajustes = mostrar_recetas = False
                        current_module_instance = None

                        if int(0.17 * SCREEN_HEIGHT) <= mouse_y <= int(0.23 * SCREEN_HEIGHT) and "VENTA" in permisos_usuario:
                            mostrar_punto_venta = True
                            print("Cargando módulo Punto de Venta...")
                            current_module_instance = module_loader.load_punto_venta()
                        elif int(0.27 * SCREEN_HEIGHT) <= mouse_y <= int(0.33 * SCREEN_HEIGHT) and "ALMACEN" in permisos_usuario:
                            mostrar_almacen = True
                            print("Cargando módulo Almacén...")
                            current_module_instance = module_loader.load_almacen()
                        elif int(0.37 * SCREEN_HEIGHT) <= mouse_y <= int(0.43 * SCREEN_HEIGHT) and "PEDIDO" in permisos_usuario:
                            mostrar_pedidos = True
                            print("Cargando módulo Pedidos...")
                            current_module_instance = module_loader.load_pedido()
                        elif int(0.47 * SCREEN_HEIGHT) <= mouse_y <= int(0.53 * SCREEN_HEIGHT) and "RECETA" in permisos_usuario:
                            mostrar_recetas = True
                            print("Cargando módulo Recetas...")
                            current_module_instance = module_loader.load_receta()
                        elif int(0.57 * SCREEN_HEIGHT) <= mouse_y <= int(0.63 * SCREEN_HEIGHT) and "REPORTES" in permisos_usuario:
                            mostrar_reportes = True
                            print("Cargando módulo Reportes...")
                            current_module_instance = module_loader.load_reporte()
                        elif int(0.67 * SCREEN_HEIGHT) <= mouse_y <= int(0.73 * SCREEN_HEIGHT) and "AJUSTES" in permisos_usuario:
                            mostrar_ajustes = True
                            print("Cargando módulo Ajustes...")
                            current_module_instance = module_loader.load_ajustes()
                        elif int(0.87 * SCREEN_HEIGHT) <= mouse_y <= int(0.93 * SCREEN_HEIGHT):
                            en_menu = False  # Salir del menú

                # Manejo de eventos de teclado
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F12:
                        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"screenshot_{now}.png"
                        pygame.image.save(ventana, filename)
                        print(f"Captura de pantalla guardada como {filename}")
                    elif event.key == pygame.K_ESCAPE:
                        en_menu = False
                    elif event.key == pygame.K_F1:
                        # Debug: Mostrar información de memoria
                        memory_info = module_loader.get_memory_usage()
                        print("=== Estado de Memoria ===")
                        print(f"Módulos cargados: {memory_info['modules_loaded']}")
                        print(f"Instancias creadas: {memory_info['instances_created']}")
                        print(f"Módulos: {memory_info['module_names']}")
                        print(f"Instancias: {memory_info['instance_names']}")
                
                # Pasar eventos solo al módulo activo
                if current_module_instance and hasattr(current_module_instance, 'handle_event'):
                    current_module_instance.handle_event(event)

            dibujar_interfaz(nombre_usuario)
            pygame.display.flip()
            
        except Exception as e:
            print("Ocurrió un error:", e)
            pygame.quit()
            sys.exit()

    # Limpiar memoria antes de salir
    module_loader.clear_cache()
    print("Cache de módulos limpiado. Regresando al login...")
    
    # Al salir del menú, regresa al login
    login.main()


if __name__ == '__main__':
    # Modo debug - iniciar directamente como gerente
    main('Bernardo', 'GERENTE')