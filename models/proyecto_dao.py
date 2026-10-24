import sqlite3
from sqlite3 import Cursor

from config.database import Database
from models.proyecto import Proyecto


class ProyectoDAO:
    """
    Data Access Object para la entidad Proyecto.
    Maneja las operaciones CRUD en la base de datos.
    """

    @staticmethod
    def crear(proyecto: Proyecto) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO proyecto (nombre, descripcion, fecha_inicio) VALUES (?, ?, ?)",
                (proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio)
            )
            conn.commit()
            proyecto.id_proyecto = cursor.lastrowid
            return True
        except sqlite3.IntegrityError:
            print("Error: ya existe un proyecto con ese nombre.")
            return False
        except sqlite3.Error as e:
            print(f"Error al crear proyecto en BD: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_todos() -> list[Proyecto]:
        conn = None
        proyectos = []
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "SELECT id_proyecto, nombre, descripcion, fecha_inicio FROM proyecto ORDER BY id_proyecto"
            )
            for fila in cursor.fetchall():
                proyectos.append(Proyecto(fila['nombre'], fila['descripcion'], fila['fecha_inicio'],
                                          fila['id_proyecto']))
        except sqlite3.Error as e:
            print(f"Error al obtener proyectos: {e}")
        finally:
            if conn:
                conn.close()
        return proyectos

    @staticmethod
    def obtener_por_id(id_proyecto: int) -> Proyecto | None:
        conn = None
        proyecto = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "SELECT id_proyecto, nombre, descripcion, fecha_inicio FROM proyecto WHERE id_proyecto = ?",
                (id_proyecto,)
            )
            fila = cursor.fetchone()
            if fila:
                proyecto = Proyecto(fila['nombre'], fila['descripcion'], fila['fecha_inicio'],
                                    fila['id_proyecto'])
        except sqlite3.Error as e:
            print(f"Error al obtener el proyecto: {e}")
        finally:
            if conn:
                conn.close()
        return proyecto

    @staticmethod
    def actualizar(proyecto: Proyecto) -> bool:
        if proyecto.id_proyecto is None:
            return False
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "UPDATE proyecto SET nombre = ?, descripcion = ? WHERE id_proyecto = ?",
                (proyecto.nombre, proyecto.descripcion, proyecto.id_proyecto)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            print("Error: ya existe otro proyecto con ese nombre.")
            return False
        except sqlite3.Error as e:
            print(f"Error al actualizar proyecto: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def eliminar(id_proyecto: int) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            # Los registros de tiempo del proyecto se eliminan en cascada.
            cursor.execute("DELETE FROM proyecto WHERE id_proyecto = ?", (id_proyecto,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar proyecto: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def contar_registros(id_proyecto: int) -> int:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM registro_tiempo WHERE id_proyecto = ?", (id_proyecto,))
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error al contar registros: {e}")
            return 0
        finally:
            if conn:
                conn.close()
