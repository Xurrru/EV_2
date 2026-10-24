import sqlite3
from sqlite3 import Cursor

from config.database import Database
from models.empleado_dao import EmpleadoDAO
from models.proyecto_dao import ProyectoDAO
from models.registro_tiempo import Registro_Tiempo

_SELECT = "SELECT id_registro, fecha, horas, descripcion, id_empleado, id_proyecto FROM registro_tiempo"


class RegistroTiempoDAO:
    """
    Data Access Object para Registro_Tiempo.
    Como un registro necesita su Empleado y su Proyecto como objetos, se cargan con
    EmpleadoDAO y ProyectoDAO (una sola vez por id, usando diccionarios de apoyo).
    """

    @staticmethod
    def _construir_lista(filas) -> list[Registro_Tiempo]:
        empleados = {}
        proyectos = {}
        registros = []
        for fila in filas:
            id_emp, id_proy = fila['id_empleado'], fila['id_proyecto']
            if id_emp not in empleados:
                empleados[id_emp] = EmpleadoDAO.obtener_por_id(id_emp)
            if id_proy not in proyectos:
                proyectos[id_proy] = ProyectoDAO.obtener_por_id(id_proy)
            if empleados[id_emp] is None or proyectos[id_proy] is None:
                continue  # no debería ocurrir: las claves foráneas lo impiden
            registro = Registro_Tiempo(fila['fecha'], fila['horas'], fila['descripcion'],
                                       empleados[id_emp], proyectos[id_proy], fila['id_registro'])
            empleados[id_emp].registrar_horas(registro)
            registros.append(registro)
        return registros

    @staticmethod
    def _consultar(condicion: str = "", parametros: tuple = ()) -> list[Registro_Tiempo]:
        # `condicion` es siempre texto fijo escrito en este archivo; los valores van en `parametros`.
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(f"{_SELECT} {condicion} ORDER BY fecha DESC, id_registro DESC", parametros)
            filas = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener registros de tiempo: {e}")
            return []
        finally:
            if conn:
                conn.close()
        return RegistroTiempoDAO._construir_lista(filas)

    @staticmethod
    def crear(registro: Registro_Tiempo) -> bool:
        if registro.empleado.id_empleado is None or registro.proyecto.id_proyecto is None:
            print("Error: el empleado y el proyecto deben estar guardados en la base de datos.")
            return False
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO registro_tiempo (fecha, horas, descripcion, id_empleado, id_proyecto) "
                "VALUES (?, ?, ?, ?, ?)",
                (registro.fecha, registro.horas, registro.descripcion,
                 registro.empleado.id_empleado, registro.proyecto.id_proyecto)
            )
            conn.commit()
            registro.id_registro = cursor.lastrowid
            return True
        except sqlite3.IntegrityError:
            print("Error: el empleado o el proyecto indicado no existe.")
            return False
        except sqlite3.Error as e:
            print(f"Error al crear registro de tiempo en BD: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_todos() -> list[Registro_Tiempo]:
        return RegistroTiempoDAO._consultar()

    @staticmethod
    def obtener_por_id(id_registro: int) -> Registro_Tiempo | None:
        registros = RegistroTiempoDAO._consultar("WHERE id_registro = ?", (id_registro,))
        return registros[0] if registros else None

    @staticmethod
    def obtener_por_empleado(id_empleado: int) -> list[Registro_Tiempo]:
        return RegistroTiempoDAO._consultar("WHERE id_empleado = ?", (id_empleado,))

    @staticmethod
    def actualizar(registro: Registro_Tiempo) -> bool:
        if registro.id_registro is None:
            return False
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "UPDATE registro_tiempo SET horas = ?, descripcion = ? WHERE id_registro = ?",
                (registro.horas, registro.descripcion, registro.id_registro)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al actualizar registro de tiempo: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def eliminar(id_registro: int) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute("DELETE FROM registro_tiempo WHERE id_registro = ?", (id_registro,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar registro de tiempo: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def horas_por_proyecto() -> list[tuple]:
        """Resumen para el informe: (proyecto, cantidad de registros, horas totales)."""
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "SELECT p.nombre AS proyecto, COUNT(r.id_registro) AS registros, "
                "COALESCE(SUM(r.horas), 0) AS horas "
                "FROM proyecto p LEFT JOIN registro_tiempo r ON r.id_proyecto = p.id_proyecto "
                "GROUP BY p.id_proyecto ORDER BY horas DESC, p.nombre"
            )
            return [(f['proyecto'], f['registros'], f['horas']) for f in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error al generar el resumen de horas: {e}")
            return []
        finally:
            if conn:
                conn.close()
