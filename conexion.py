
import mysql.connector
from mysql.connector import Error

class Conexion:
    def __init__(self, host='localhost', user='root', password='12345', database='panaderia'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    def conectar(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.conn.is_connected():
                self.cursor = self.conn.cursor(dictionary=True)
                print("Conexión exitosa a la base de datos 'panaderia'")
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            self.conn = None

    def cerrar(self):
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("Conexión cerrada.")

    def consultar(self, query, params=None):
        self.conectar()
        if not self.conn:
            return []
        self.cursor.execute(query, params or ())
        resultados = self.cursor.fetchall()
        self.cerrar()
        return resultados

    def update(self, query, params=None):
        self.conectar()
        if not self.conn:
            return False
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            return True
        except Error as e:
            print(f"Error al ejecutar comando: {e}")
            self.conn.rollback()
            return False
        finally:
            self.cerrar()
# Funciones auxiliares para importar fácilmente
def crear_conexion():
    conexion = Conexion()
    conexion.conectar()
    return conexion

def cerrar_conexion(conexion):
    conexion.cerrar()
