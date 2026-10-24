import sqlite3
from sqlite3 import Cursor

from config.database import Database
from models.administrador import Administrador


class AdministradorDAO:
    """
    Data Access Object para Administrador.
    Un administrador solo usa la tabla `usuario` (con rol 'Administrador').
    """

    @staticmethod
    def _construir(fila) -> Administrador:
        # password=None y password_hash=... : el hash ya viene cifrado desde la BD
        return Administrador(fila['correo'], None, fila['id_usuario'], fila['password_hash'])

    @staticmethod
    def crear(administrador: Administrador) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuario (correo, password_hash, rol) VALUES (?, ?, ?)",
                (administrador.correo, administrador.password_hash, administrador.rol)
            )
            conn.commit()
            administrador.id_usuario = cursor.lastrowid
            return True
        except sqlite3.IntegrityError:
            print("Error: ya existe un usuario con ese correo.")
            return False
        except sqlite3.Error as e:
            print(f"Error al crear administrador en BD: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_todos() -> list[Administrador]:
        conn = None
        administradores = []
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "SELECT id_usuario, correo, password_hash FROM usuario "
                "WHERE rol = 'Administrador' ORDER BY id_usuario"
            )
            for fila in cursor.fetchall():
                administradores.append(AdministradorDAO._construir(fila))
        except sqlite3.Error as e:
            print(f"Error al obtener administradores: {e}")
        finally:
            if conn:
                conn.close()
        return administradores

    @staticmethod
    def obtener_por_id(id_usuario: int) -> Administrador | None:
        conn = None
        administrador = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "SELECT id_usuario, correo, password_hash FROM usuario "
                "WHERE id_usuario = ? AND rol = 'Administrador'",
                (id_usuario,)
            )
            fila = cursor.fetchone()
            if fila:
                administrador = AdministradorDAO._construir(fila)
        except sqlite3.Error as e:
            print(f"Error al obtener el administrador: {e}")
        finally:
            if conn:
                conn.close()
        return administrador

    @staticmethod
    def obtener_por_correo(correo: str) -> Administrador | None:
        conn = None
        administrador = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "SELECT id_usuario, correo, password_hash FROM usuario "
                "WHERE correo = ? AND rol = 'Administrador'",
                (correo.strip().lower(),)
            )
            fila = cursor.fetchone()
            if fila:
                administrador = AdministradorDAO._construir(fila)
        except sqlite3.Error as e:
            print(f"Error al buscar el administrador: {e}")
        finally:
            if conn:
                conn.close()
        return administrador

    @staticmethod
    def actualizar(administrador: Administrador) -> bool:
        if administrador.id_usuario is None:
            return False
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuario SET correo = ?, password_hash = ? WHERE id_usuario = ?",
                (administrador.correo, administrador.password_hash, administrador.id_usuario)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            print("Error: ya existe un usuario con ese correo.")
            return False
        except sqlite3.Error as e:
            print(f"Error al actualizar administrador: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def eliminar(id_usuario: int) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute("DELETE FROM usuario WHERE id_usuario = ? AND rol = 'Administrador'", (id_usuario,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar administrador: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def contar() -> int:
        """Cantidad de administradores. Retorna -1 si hubo un error con la BD."""
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuario WHERE rol = 'Administrador'")
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error al contar administradores: {e}")
            return -1
        finally:
            if conn:
                conn.close()
