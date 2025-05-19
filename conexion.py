"""
Clase para gestionar conexiones a MySQL
------------------------------------
Proporciona una interfaz simplificada para conectar, consultar y actualizar
la base de datos 'panaderiaBambiDB'.

Incluye métodos para:
- Conectar/desconectar de la base de datos
- Ejecutar consultas SELECT
- Ejecutar comandos UPDATE/INSERT/DELETE
- Manejo automático de conexiones
"""

import os
import sys
import json
import mysql.connector
from mysql.connector import Error

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

JSON_FILE = resource_path("credentials.json")

class Conexion:
    """
    Clase para gestionar conexiones a la base de datos MySQL
    
    Maneja automáticamente la apertura y cierre de conexiones,
    y proporciona métodos simples para ejecutar consultas.
    
    Attributes:
        host (str): Servidor MySQL (default: localhost)
        user (str): Usuario de MySQL (default: root)
        password (str): Contraseña del usuario (default: 12345)
        database (str): Nombre de la base de datos (default: panaderiaBambiDB)
        conn: Objeto de conexión MySQL
        cursor: Cursor para ejecutar comandos SQL
    """
    
    def __init__(self, host='localhost', user='root', password='12345', database='panaderiaBambiDB', port='3036'):
        """
        Inicializa la configuración de conexión
        
        Args:
            host (str, optional): Servidor de base de datos. Defaults to 'localhost'.
            user (str, optional): Usuario MySQL. Defaults to 'root'.
            password (str, optional): Contraseña del usuario. Defaults to '12345'.
            database (str, optional): Nombre de la base de datos. Defaults to 'panaderiaBambiDB'.
        """
        try:
            with open(JSON_FILE, "r") as f:
                d = json.load(f)
                self.host = d['host']
                self.user = d['user']
                self.password = d['password']
                self.database = d['database']
                self.port = d['port']
        except (FileNotFoundError, KeyError):
            self.host = host
            self.user = user
            self.password = password
            self.database = database
            self.port = port

            d = {
                'host': host,
                'user': user,
                'password': password,
                'database': database,
                'port': port
            }
            with open(JSON_FILE, "w") as f:
                json.dump(d, f, indent=4)

        self.conn = None
        self.cursor = None

    def conectar(self):
        """
        Establece la conexión con la base de datos MySQL
        
        Crea la conexión y el cursor. Si la conexión falla,
        establece self.conn como None.
        
        Returns:
            None
            
        Prints:
            Mensaje de éxito o error en la conexión
        """
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            if self.conn.is_connected():
                # Usar cursor con dictionary=True para obtener resultados como diccionarios
                self.cursor = self.conn.cursor(dictionary=True)
                print("Conexión exitosa a la base de datos 'panaderia'")
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            self.conn = None

    def cerrar(self):
        """
        Cierra la conexión con la base de datos
        
        Cierra primero el cursor y luego la conexión,
        validando que existan antes de cerrarlos.
        
        Prints:
            Mensaje de confirmación al cerrar
        """
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("Conexión cerrada.")

    def consultar(self, query, params=None):
        """
        Ejecuta una consulta SELECT en la base de datos
        
        Abre la conexión, ejecuta la consulta y la cierra automáticamente.
        Ideal para operaciones de lectura.
        
        Args:
            query (str): Consulta SQL SELECT a ejecutar
            params (tuple, optional): Parámetros para la consulta parametrizada. 
                                    Defaults to None.
        
        Returns:
            list: Lista de diccionarios con los resultados de la consulta.
                 Lista vacía si hay error o no hay resultados.
        
        Example:
            >>> conexion = Conexion()
            >>> resultados = conexion.consultar("SELECT * FROM Cliente WHERE id = %s", (1,))
            >>> print(resultados[0]['nombre'])
        """
        self.conectar()
        if not self.conn:
            return []
            
        self.cursor.execute(query, params or ())
        resultados = self.cursor.fetchall()
        self.cerrar()
        return resultados

    def update(self, query, params=None):
        """
        Ejecuta comandos INSERT, UPDATE o DELETE en la base de datos
        
        Abre la conexión, ejecuta el comando y hace commit automáticamente.
        En caso de error, hace rollback para mantener consistencia.
        
        Args:
            query (str): Comando SQL (INSERT/UPDATE/DELETE) a ejecutar
            params (tuple, optional): Parámetros para el comando parametrizado. 
                                    Defaults to None.
        
        Returns:
            bool: True si el comando se ejecutó exitosamente, False en caso contrario
        
        Example:
            >>> conexion = Conexion()
            >>> exito = conexion.update(
            ...     "INSERT INTO Cliente (nombre, telefono) VALUES (%s, %s)",
            ...     ("Juan Pérez", "5551234567")
            ... )
            >>> if exito:
            ...     print("Cliente agregado exitosamente")
        """
        self.conectar()
        if not self.conn:
            return False
            
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()  # Confirmar los cambios
            return True
        except Error as e:
            print(f"Error al ejecutar comando: {e}")
            self.conn.rollback()  # Revertir cambios en caso de error
            return False
        finally:
            self.cerrar()  # Siempre cerrar la conexión


# Funciones auxiliares para importar fácilmente
def crear_conexion():
    """
    Función helper para crear y abrir una conexión rápidamente
    
    Returns:
        Conexion: Objeto de conexión ya establecida con la base de datos
        
    Example:
        >>> conexion = crear_conexion()
        >>> resultados = conexion.cursor.execute("SELECT * FROM Empleado")
        >>> cerrar_conexion(conexion)
    """
    conexion = Conexion()
    conexion.conectar()
    return conexion


def cerrar_conexion(conexion):
    """
    Función helper para cerrar una conexión
    
    Args:
        conexion (Conexion): Objeto de conexión a cerrar
        
    Example:
        >>> conexion = crear_conexion()
        >>> # ... operaciones con la base de datos ...
        >>> cerrar_conexion(conexion)
    """
    conexion.cerrar()


if __name__ == '__main__':
    """
    Código de prueba que se ejecuta al correr directamente este archivo
    
    Crea una conexión y la abre para verificar que todo funciona correctamente
    """
    con = Conexion()
    con.conectar()