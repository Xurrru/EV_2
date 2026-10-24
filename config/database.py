import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor


class Database:
    """
    Clase que gestiona la conexión a la base de datos SQLite implementando
    el patrón Singleton para evitar múltiples instancias innecesarias.
    """
    _instance = None
    _db_path = str(Path(__file__).resolve().parent.parent / "sistema_gestion.db")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def get_connection(self) -> Connection:
        """
        Retorna una conexión a la base de datos SQLite.
        - timeout: segundos que espera si la base está bloqueada.
        - row_factory: permite acceder a las columnas por nombre.
        - foreign_keys: SQLite no valida las claves foráneas si no se activa.
        """
        conn = sqlite3.connect(self._db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self) -> bool:
        """
        Crea las tablas del diagrama UML si no existen.
        Retorna True si todo salió bien y False si hubo un error.
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor: Cursor = conn.cursor()

            # Tabla Departamento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departamento (
                    id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    gerente TEXT NOT NULL
                )
            """)
            # Tabla Proyecto
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proyecto (
                    id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    descripcion TEXT NOT NULL,
                    fecha_inicio TEXT NOT NULL
                )
            """)
            # Tabla Usuario (clase padre: guarda lo que comparten Administrador y Empleado)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuario (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    correo TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    rol TEXT NOT NULL CHECK (rol IN ('Administrador', 'Empleado'))
                )
            """)
            # Tabla Empleado (clase hija: datos propios del empleado)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS empleado (
                    id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_usuario INTEGER NOT NULL UNIQUE,
                    nombre TEXT NOT NULL,
                    direccion TEXT NOT NULL,
                    telefono TEXT NOT NULL,
                    email TEXT NOT NULL,
                    fecha_contrato TEXT NOT NULL,
                    salario REAL NOT NULL CHECK (salario > 0),
                    id_departamento INTEGER,
                    FOREIGN KEY(id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
                    FOREIGN KEY(id_departamento) REFERENCES departamento(id_departamento) ON DELETE SET NULL
                )
            """)
            # Tabla Registro_Tiempo (une un Empleado con un Proyecto)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registro_tiempo (
                    id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    horas REAL NOT NULL CHECK (horas > 0 AND horas <= 24),
                    descripcion TEXT NOT NULL,
                    id_empleado INTEGER NOT NULL,
                    id_proyecto INTEGER NOT NULL,
                    FOREIGN KEY(id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE,
                    FOREIGN KEY(id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
                )
            """)

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {e}")
            return False
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    db = Database()
    if db.init_db():
        print("Base de datos inicializada correctamente.")
