import sqlite3
from sqlite3 import Cursor

from config.database import Database
from models.departamento_dao import DepartamentoDAO
from models.empleado import Empleado

# Un Empleado se guarda en DOS tablas: usuario (datos del padre) y empleado (datos propios).
_SELECT = """
    SELECT e.id_empleado, e.id_usuario, e.nombre, e.direccion, e.telefono, e.email,
           e.fecha_contrato, e.salario, e.id_departamento, u.correo, u.password_hash
    FROM empleado e
    JOIN usuario u ON u.id_usuario = e.id_usuario
"""


class EmpleadoDAO:
    """
    Data Access Object para la entidad Empleado.
    Maneja todas las operaciones CRUD en la base de datos.
    """

    @staticmethod
    def _construir(fila) -> Empleado:
        departamento = None
        if fila['id_departamento'] is not None:
            departamento = DepartamentoDAO.obtener_por_id(fila['id_departamento'])
        return Empleado(
            correo=fila['correo'], password=None, nombre=fila['nombre'], direccion=fila['direccion'],
            telefono=fila['telefono'], email=fila['email'], fecha_contrato=fila['fecha_contrato'],
            salario=fila['salario'], departamento=departamento, id_usuario=fila['id_usuario'],
            id_empleado=fila['id_empleado'], password_hash=fila['password_hash']
        )

    @staticmethod
    def crear(empleado: Empleado) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            # Los dos INSERT se confirman juntos con un solo commit: se guardan ambos o ninguno.
            cursor.execute(
                "INSERT INTO usuario (correo, password_hash, rol) VALUES (?, ?, ?)",
                (empleado.correo, empleado.password_hash, empleado.rol)
            )
            id_usuario = cursor.lastrowid
            id_depto = empleado.departamento.id_departamento if empleado.departamento else None
            cursor.execute(
                "INSERT INTO empleado (id_usuario, nombre, direccion, telefono, email, fecha_contrato, "
                "salario, id_departamento) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (id_usuario, empleado.nombre, empleado.direccion, empleado.telefono, empleado.email,
                 empleado.fecha_contrato, empleado.salario, id_depto)
            )
            id_empleado = cursor.lastrowid
            conn.commit()
            empleado.id_usuario = id_usuario
            empleado.id_empleado = id_empleado
            return True
        except sqlite3.IntegrityError:
            print("Error: el correo ya está registrado o el departamento indicado no existe.")
            return False
        except sqlite3.Error as e:
            print(f"Error al crear empleado en BD: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_todos() -> list[Empleado]:
        conn = None
        empleados = []
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(f"{_SELECT} ORDER BY e.id_empleado")
            for fila in cursor.fetchall():
                empleados.append(EmpleadoDAO._construir(fila))
        except sqlite3.Error as e:
            print(f"Error al obtener empleados: {e}")
        finally:
            if conn:
                conn.close()
        return empleados

    @staticmethod
    def obtener_por_id(id_empleado: int) -> Empleado | None:
        conn = None
        empleado = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(f"{_SELECT} WHERE e.id_empleado = ?", (id_empleado,))
            fila = cursor.fetchone()
            if fila:
                empleado = EmpleadoDAO._construir(fila)
        except sqlite3.Error as e:
            print(f"Error al obtener el empleado: {e}")
        finally:
            if conn:
                conn.close()
        return empleado

    @staticmethod
    def actualizar(empleado: Empleado) -> bool:
        if empleado.id_empleado is None or empleado.id_usuario is None:
            return False
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            id_depto = empleado.departamento.id_departamento if empleado.departamento else None
            cursor.execute(
                "UPDATE usuario SET correo = ?, password_hash = ? WHERE id_usuario = ?",
                (empleado.correo, empleado.password_hash, empleado.id_usuario)
            )
            cursor.execute(
                "UPDATE empleado SET nombre = ?, direccion = ?, telefono = ?, email = ?, salario = ?, "
                "id_departamento = ? WHERE id_empleado = ?",
                (empleado.nombre, empleado.direccion, empleado.telefono, empleado.email,
                 empleado.salario, id_depto, empleado.id_empleado)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            print("Error: el correo ya está registrado o el departamento indicado no existe.")
            return False
        except sqlite3.Error as e:
            print(f"Error al actualizar empleado: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def eliminar(id_empleado: int) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            # Se borra el usuario; la fila de empleado y sus registros de tiempo se borran en cascada.
            cursor.execute(
                "DELETE FROM usuario WHERE id_usuario = (SELECT id_usuario FROM empleado WHERE id_empleado = ?)",
                (id_empleado,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar empleado: {e}")
            return False
        finally:
            if conn:
                conn.close()
