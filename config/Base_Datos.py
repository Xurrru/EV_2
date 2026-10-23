"""Conexión a SQLite mediante la librería oficial ``sqlite3`` (biblioteca estándar)."""
from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Connection
from typing import Iterator

from config.excepciones import ErrorBaseDatos, ErrorIntegridad

_log = logging.getLogger("sistema.bd")


def _traducir_error(error: sqlite3.Error) -> ErrorBaseDatos:
    """Convierte un error técnico de sqlite3 en un mensaje seguro para el usuario.

    El detalle técnico se guarda en el log, no se muestra en pantalla.
    """
    _log.error("Error de SQLite: %s", error)
    detalle = str(error).upper()
    if isinstance(error, sqlite3.IntegrityError):
        if "UNIQUE" in detalle:
            return ErrorIntegridad("Ya existe un registro con esos datos únicos (por ejemplo, correo o nombre repetido).")
        if "FOREIGN KEY" in detalle:
            return ErrorIntegridad("La operación hace referencia a un registro inexistente o que está en uso.")
        if "CHECK" in detalle:
            return ErrorIntegridad("Los datos no cumplen las reglas definidas en la base de datos.")
        return ErrorIntegridad("Se violó una regla de integridad de la base de datos.")
    if isinstance(error, sqlite3.OperationalError):
        return ErrorBaseDatos("La base de datos no está disponible o está bloqueada. Intente nuevamente.")
    return ErrorBaseDatos("Ocurrió un error al operar con la base de datos.")


class Database:
    """Gestiona la conexión a la base de datos (patrón Singleton).

    Parámetros de conexión utilizados con ``sqlite3.connect``:
      * ruta del archivo ``sistema_gestion.db`` (junto al proyecto);
      * ``timeout=10``: segundos de espera si la base está bloqueada;
      * ``row_factory = sqlite3.Row``: acceso a columnas por nombre;
      * ``PRAGMA foreign_keys = ON``: SQLite no valida claves foráneas por defecto.
    """

    _instance = None
    _db_path = str(Path(__file__).resolve().parent.parent / "sistema_gestion.db")
    _TIMEOUT_SEGUNDOS = 10

    def __new__(cls) -> "Database":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def configurar_ruta(cls, ruta: str | Path) -> None:
        """Cambia el archivo de base de datos (se usa en las pruebas)."""
        cls._db_path = str(ruta)

    @property
    def ruta(self) -> str:
        return self._db_path

    def get_connection(self) -> Connection:
        """Abre una conexión nueva. Lanza ``ErrorBaseDatos`` si no es posible."""
        try:
            conn = sqlite3.connect(self._db_path, timeout=self._TIMEOUT_SEGUNDOS)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as error:
            raise _traducir_error(error) from error

    @contextmanager
    def transaccion(self) -> Iterator[Connection]:
        """Entrega una conexión dentro de una transacción.

        * Éxito   -> ``commit``.
        * Error   -> ``rollback`` y se relanza como excepción propia.
        * Siempre -> la conexión se cierra.
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as error:
            conn.rollback()
            raise _traducir_error(error) from error
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        """Crea las tablas del diagrama UML si no existen (operación idempotente)."""
        sentencias = (
            """
            CREATE TABLE IF NOT EXISTS departamento (
                id_departamento INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE,
                gerente TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS proyecto (
                id_proyecto INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT NOT NULL,
                fecha_inicio TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS usuario (
                id_usuario INTEGER PRIMARY KEY,
                correo TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL CHECK (rol IN ('Administrador', 'Empleado')),
                id_departamento INTEGER,
                FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento)
                    ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS empleado (
                id_empleado INTEGER PRIMARY KEY,
                id_usuario INTEGER NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                direccion TEXT NOT NULL,
                telefono TEXT NOT NULL,
                email TEXT NOT NULL,
                fecha_contrato TEXT NOT NULL,
                salario REAL NOT NULL CHECK (salario > 0),
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS registro_tiempo (
                id_registro INTEGER PRIMARY KEY,
                fecha TEXT NOT NULL,
                horas REAL NOT NULL CHECK (horas > 0 AND horas <= 24),
                descripcion TEXT NOT NULL,
                id_empleado INTEGER NOT NULL,
                id_proyecto INTEGER NOT NULL,
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE,
                FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
            )
            """,
            "CREATE INDEX IF NOT EXISTS idx_registro_empleado ON registro_tiempo(id_empleado)",
            "CREATE INDEX IF NOT EXISTS idx_registro_proyecto ON registro_tiempo(id_proyecto)",
        )
        with self.transaccion() as conn:
            for sentencia in sentencias:
                conn.execute(sentencia)


if __name__ == "__main__":
    Database().init_db()
    print(f"Base de datos lista en: {Database().ruta}")
