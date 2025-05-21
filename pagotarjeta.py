"""
Sistema de Pago con Tarjeta para integración con MercadoPago
--------------------------------------------------------
Clase para manejar pagos con tarjeta usando terminal MercadoPago

Autor: Sistema POS Bambi
Versión: 1.0
"""

import pygame
import time
import requests
import json
from datetime import datetime

class PagoTarjeta:
    """
    Clase para manejar el pago con tarjeta a través de MercadoPago
    
    Atributos:
        x, y (int): Posición de la interfaz
        ancho, alto (int): Dimensiones de la interfaz
        total (float): Monto total a cobrar
        estado (str): Estado actual de la transacción
        resultado (dict): Resultado de la transacción
    """
    
    def __init__(self, x, y, ancho, alto, total):
        """
        Inicializa la interfaz de pago con tarjeta
        
        Args:
            x, y (int): Posición de la interfaz
            ancho, alto (int): Dimensiones de la interfaz
            total (float): Monto total a cobrar
        """
        pygame.font.init()
        
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.total = total
        self.estado = "esperando"  # esperando, procesando, completado, error
        self.resultado = None
        
        # Colores
        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.AZUL = (0, 120, 220)
        self.VERDE = (0, 180, 0)
        self.ROJO = (220, 0, 0)
        self.GRIS = (200, 200, 200)
        
        # Fuentes
        self.fuente_titulo = pygame.font.SysFont("Open Sans", int(alto * 0.05), bold=True)
        self.fuente_normal = pygame.font.SysFont("Open Sans", int(alto * 0.04))
        self.fuente_grande = pygame.font.SysFont("Open Sans", int(alto * 0.06), bold=True)
        
        # Posiciones
        self.modal_w = int(ancho * 0.4)
        self.modal_h = int(alto * 0.6)
        self.modal_x = x + (ancho - self.modal_w) // 2
        self.modal_y = y + (alto - self.modal_h) // 2
        
        # Botones
        self.btn_procesar = None
        self.btn_cancelar = None
        self.inicializar_botones()
        
        # Timer para animación
        self.timer_animacion = 0
        self.puntos_cargando = ""
        
        # Configuración de MercadoPago (ajustar según tu configuración)
        self.MERCADOPAGO_ACCESS_TOKEN = "TU_ACCESS_TOKEN_AQUI"
        self.TERMINAL_ID = "TU_TERMINAL_ID_AQUI"
        
    def inicializar_botones(self):
        """Configura los botones de la interfaz"""
        btn_w, btn_h = 150, 50
        btn_y = self.modal_y + self.modal_h - btn_h - 30
        
        self.btn_procesar = pygame.Rect(
            self.modal_x + 30,
            btn_y,
            btn_w,
            btn_h
        )
        
        self.btn_cancelar = pygame.Rect(
            self.modal_x + self.modal_w - btn_w - 30,
            btn_y,
            btn_w,
            btn_h
        )
    
    def procesar_pago(self):
        """Inicia el proceso de pago con la terminal MercadoPago"""
        self.estado = "procesando"
        
        try:
            # Aquí iría la integración real con MercadoPago
            # Este es un ejemplo simplificado
            
            # Preparar datos del pago
            payment_data = {
                "transaction_amount": self.total,
                "description": f"Venta POS Bambi - {datetime.now().strftime('%Y%m%d%H%M%S')}",
                "payment_method_id": None,  # Se determina automáticamente
                "installments": 1,
                "payer": {
                    "email": "cliente@example.com"
                }
            }
            
            # Simular comunicación con terminal (reemplazar con API real)
            self.simular_proceso_terminal()
            
            # En una implementación real, aquí harías la llamada a la API
            # response = self.enviar_a_terminal(payment_data)
            # self.resultado = response
            
        except Exception as e:
            self.estado = "error"
            self.resultado = {"error": str(e)}
    
    def simular_proceso_terminal(self):
        """Simula el proceso de pago con la terminal (solo para testing)"""
        # Simular tiempo de procesamiento
        pygame.time.wait(2000)
        
        # Simular respuesta exitosa
        self.estado = "completado"
        self.resultado = {
            "status": "approved",
            "transaction_id": "12345678",
            "card_brand": "visa",
            "card_last_digits": "1234",
            "payment_type": "debit",
            "total": self.total,
            "timestamp": datetime.now().isoformat()
        }
    
    def enviar_a_terminal(self, payment_data):
        """
        Envía la información de pago a la terminal MercadoPago
        
        Args:
            payment_data (dict): Datos del pago
            
        Returns:
            dict: Respuesta de la terminal
        """
        headers = {
            "Authorization": f"Bearer {self.MERCADOPAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        url = f"https://api.mercadopago.com/v1/pos/{self.TERMINAL_ID}/payment"
        
        try:
            response = requests.post(url, json=payment_data, headers=headers)
            return response.json()
        except Exception as e:
            raise Exception(f"Error al comunicarse con MercadoPago: {e}")
    
    def dibujar(self, surface):
        """
        Dibuja la interfaz de pago con tarjeta
        
        Args:
            surface (pygame.Surface): Superficie donde dibujar
        """
        # Fondo semitransparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (self.x, self.y))
        
        # Modal principal
        modal_rect = pygame.Rect(self.modal_x, self.modal_y, self.modal_w, self.modal_h)
        pygame.draw.rect(surface, self.BLANCO, modal_rect, border_radius=16)
        pygame.draw.rect(surface, self.AZUL, modal_rect, 3, border_radius=16)
        
        # Título
        titulo = self.fuente_titulo.render("Pago con Tarjeta", True, self.NEGRO)
        titulo_x = self.modal_x + (self.modal_w - titulo.get_width()) // 2
        surface.blit(titulo, (titulo_x, self.modal_y + 30))
        
        # Total
        total_text = self.fuente_grande.render(f"${self.total:.2f}", True, self.NEGRO)
        total_x = self.modal_x + (self.modal_w - total_text.get_width()) // 2
        surface.blit(total_text, (total_x, self.modal_y + 100))
        
        # Contenido según estado
        if self.estado == "esperando":
            self.dibujar_estado_esperando(surface)
        elif self.estado == "procesando":
            self.dibujar_estado_procesando(surface)
        elif self.estado == "completado":
            self.dibujar_estado_completado(surface)
        elif self.estado == "error":
            self.dibujar_estado_error(surface)
        
        # Botones
        self.dibujar_botones(surface)
    
    def dibujar_estado_esperando(self, surface):
        """Dibuja el estado inicial antes de procesar"""
        instrucciones = [
            "1. Presione 'Procesar' para iniciar",
            "2. Presente la tarjeta en la terminal",
            "3. Siga las instrucciones en pantalla",
            "4. Espere la confirmación"
        ]
        
        y_offset = self.modal_y + 200
        for instruccion in instrucciones:
            texto = self.fuente_normal.render(instruccion, True, self.NEGRO)
            surface.blit(texto, (self.modal_x + 40, y_offset))
            y_offset += 40
    
    def dibujar_estado_procesando(self, surface):
        """Dibuja el estado mientras se procesa el pago"""
        # Actualizar animación
        self.timer_animacion += 1
        if self.timer_animacion % 30 == 0:
            self.puntos_cargando = "." * ((self.timer_animacion // 30) % 4)
        
        mensaje = f"Procesando pago{self.puntos_cargando}"
        texto = self.fuente_normal.render(mensaje, True, self.NEGRO)
        texto_x = self.modal_x + (self.modal_w - texto.get_width()) // 2
        surface.blit(texto, (texto_x, self.modal_y + 250))
        
        # Barra de progreso
        barra_w = 300
        barra_h = 20
        barra_x = self.modal_x + (self.modal_w - barra_w) // 2
        barra_y = self.modal_y + 300
        
        pygame.draw.rect(surface, self.GRIS, (barra_x, barra_y, barra_w, barra_h), border_radius=10)
        progreso_w = int((self.timer_animacion % 120) / 120 * barra_w)
        pygame.draw.rect(surface, self.AZUL, (barra_x, barra_y, progreso_w, barra_h), border_radius=10)
    
    def dibujar_estado_completado(self, surface):
        """Dibuja el estado cuando el pago fue completado exitosamente"""
        # Símbolo de éxito
        check_img = self.fuente_grande.render("✓", True, self.VERDE)
        check_x = self.modal_x + (self.modal_w - check_img.get_width()) // 2
        surface.blit(check_img, (check_x, self.modal_y + 200))
        
        # Mensaje de éxito
        mensaje = "¡Pago Aprobado!"
        texto = self.fuente_normal.render(mensaje, True, self.VERDE)
        texto_x = self.modal_x + (self.modal_w - texto.get_width()) // 2
        surface.blit(texto, (texto_x, self.modal_y + 260))
        
        # Detalles de la transacción
        if self.resultado and self.resultado.get("status") == "approved":
            detalles = [
                f"ID: {self.resultado.get('transaction_id', '')}",
                f"Tarjeta: {self.resultado.get('card_brand', '').upper()} ...{self.resultado.get('card_last_digits', '')}",
                f"Tipo: {self.resultado.get('payment_type', '').title()}"
            ]
            
            y_offset = self.modal_y + 320
            for detalle in detalles:
                texto = self.fuente_normal.render(detalle, True, self.NEGRO)
                texto_x = self.modal_x + (self.modal_w - texto.get_width()) // 2
                surface.blit(texto, (texto_x, y_offset))
                y_offset += 35
    
    def dibujar_estado_error(self, surface):
        """Dibuja el estado cuando hay un error en el pago"""
        # Símbolo de error
        error_img = self.fuente_grande.render("✗", True, self.ROJO)
        error_x = self.modal_x + (self.modal_w - error_img.get_width()) // 2
        surface.blit(error_img, (error_x, self.modal_y + 200))
        
        # Mensaje de error
        mensaje = "Error en el Pago"
        texto = self.fuente_normal.render(mensaje, True, self.ROJO)
        texto_x = self.modal_x + (self.modal_w - texto.get_width()) // 2
        surface.blit(texto, (texto_x, self.modal_y + 260))
        
        # Detalles del error
        if self.resultado and "error" in self.resultado:
            error_texto = self.fuente_normal.render(self.resultado["error"], True, self.NEGRO)
            error_x = self.modal_x + (self.modal_w - error_texto.get_width()) // 2
            surface.blit(error_texto, (error_x, self.modal_y + 320))
    
    def dibujar_botones(self, surface):
        """Dibuja los botones de la interfaz"""
        if self.estado != "procesando":
            # Botón Procesar/Aceptar
            if self.estado in ["esperando", "error"]:
                btn_text = "Procesar"
                btn_color = self.VERDE
            else:  # completado
                btn_text = "Aceptar"
                btn_color = self.AZUL
            
            pygame.draw.rect(surface, btn_color, self.btn_procesar, border_radius=8)
            texto = self.fuente_normal.render(btn_text, True, self.BLANCO)
            texto_x = self.btn_procesar.x + (self.btn_procesar.width - texto.get_width()) // 2
            texto_y = self.btn_procesar.y + (self.btn_procesar.height - texto.get_height()) // 2
            surface.blit(texto, (texto_x, texto_y))
        
        # Botón Cancelar
        btn_cancel_color = self.GRIS if self.estado == "procesando" else self.ROJO
        pygame.draw.rect(surface, btn_cancel_color, self.btn_cancelar, border_radius=8)
        texto = self.fuente_normal.render("Cancelar", True, self.BLANCO)
        texto_x = self.btn_cancelar.x + (self.btn_cancelar.width - texto.get_width()) // 2
        texto_y = self.btn_cancelar.y + (self.btn_cancelar.height - texto.get_height()) // 2
        surface.blit(texto, (texto_x, texto_y))
    
    def handle_event(self, event):
        """
        Maneja los eventos de la interfaz
        
        Args:
            event (pygame.event.Event): Evento de Pygame
            
        Returns:
            str: 'procesar', 'completado', 'cancelar', o None
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_procesar.collidepoint(event.pos):
                if self.estado == "esperando" or self.estado == "error":
                    # Iniciar proceso de pago
                    self.procesar_pago()
                    return "procesar"
                elif self.estado == "completado":
                    # Confirmar pago completado
                    return "completado"
            
            elif self.btn_cancelar.collidepoint(event.pos):
                if self.estado != "procesando":
                    return "cancelar"
        
        return None