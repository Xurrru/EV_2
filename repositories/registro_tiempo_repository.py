from __future__ import annotations

from config.excepciones import ErrorBaseDatos
from models.Proyecto import Proyecto
from models.Registro_Tiempo import Registro_Tiempo
from models.Usuarios import Empleado
from repositories.base_repository import RepositorioBase
from repositories.proyecto_repository import RepositorioProyecto
from repositories.usuario_repository import RepositorioUsuario

_SELECT = "SELECT id_registro, fecha, horas, descripcion, id_empleado, id_proyecto FROM registro_tiempo"


class RepositorioRegistroTiempo(RepositorioBase[Registro_Tiempo]):
    """CRUD de ``registro_tiempo`` (asociación entre Empleado y Proyecto)."""

    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuario | None = None,
        repositorio_proyectos: RepositorioProyecto | None = None,
    ) -> None:
        super().__init__()
        self._usuarios = repositorio_usuarios or RepositorioUsuario()
        self._proyectos = repositorio_proyectos or RepositorioProyecto()

    def _construir_lista(self, filas, empleados: dict[int, Empleado], proyectos: dict[int, Proyecto]) -> list[Registro_Tiempo]:
        registros = []
        for fila in filas:
            empleado = empleados.get(fila["id_empleado"])
            proyecto = proyectos.get(fila["id_proyecto"])
            if empleado is None or proyecto is None:
                raise ErrorBaseDatos(f"El registro {fila['id_registro']} referencia datos inexistentes.")
            try:
                registro = Registro_Tiempo(
                    fila["id_registro"], fila["fecha"], fila["horas"], fila["descripcion"], empleado, proyecto
                )
            except ValueError as error:
                raise ErrorBaseDatos(f"El registro {fila['id_registro']} tiene datos inconsistentes: {error}") from error
            empleado.registrar_horas(registro)  # mantiene la asociación Empleado -> registros
            registros.append(registro)
        return registros

    def _filas(self, condicion: str = "", parametros: tuple = ()):
        # ``condicion`` es texto fijo de este archivo; los valores siempre van en ``parametros``.
        with self._db.transaccion() as conn:
            return conn.execute(f"{_SELECT} {condicion} ORDER BY fecha DESC, id_registro DESC", parametros).fetchall()

    def crear(self, registro: Registro_Tiempo) -> None:
        self._exigir_nuevo(registro.id_registro, "El registro")
        id_empleado = self._exigir_persistido(registro.empleado.id_empleado, "El empleado")
        id_proyecto = self._exigir_persistido(registro.proyecto.id_proyecto, "El proyecto")
        with self._db.transaccion() as conn:
            cursor = conn.execute(
                "INSERT INTO registro_tiempo (fecha, horas, descripcion, id_empleado, id_proyecto) "
                "VALUES (?, ?, ?, ?, ?)",
                (registro.fecha, registro.horas, registro.descripcion, id_empleado, id_proyecto),
            )
            nuevo_id = cursor.lastrowid
        registro.asignar_id_persistido(nuevo_id)

    def obtener_por_id(self, identificador: int) -> Registro_Tiempo | None:
        filas = self._filas("WHERE id_registro = ?", (identificador,))
        if not filas:
            return None
        empleado = self._usuarios.obtener_empleado_por_id(filas[0]["id_empleado"])
        proyecto = self._proyectos.obtener_por_id(filas[0]["id_proyecto"])
        if empleado is None or proyecto is None:
            raise ErrorBaseDatos(f"El registro {identificador} referencia datos inexistentes.")
        return self._construir_lista(filas, {empleado.id_empleado: empleado}, {proyecto.id_proyecto: proyecto})[0]

    def listar(self) -> list[Registro_Tiempo]:
        empleados = {e.id_empleado: e for e in self._usuarios.listar_empleados()}
        proyectos = {p.id_proyecto: p for p in self._proyectos.listar()}
        return self._construir_lista(self._filas(), empleados, proyectos)

    def listar_por_empleado(self, empleado: Empleado) -> list[Registro_Tiempo]:
        id_empleado = self._exigir_persistido(empleado.id_empleado, "El empleado")
        proyectos = {p.id_proyecto: p for p in self._proyectos.listar()}
        filas = self._filas("WHERE id_empleado = ?", (id_empleado,))
        return self._construir_lista(filas, {id_empleado: empleado}, proyectos)

    def listar_por_proyecto(self, proyecto: Proyecto) -> list[Registro_Tiempo]:
        id_proyecto = self._exigir_persistido(proyecto.id_proyecto, "El proyecto")
        empleados = {e.id_empleado: e for e in self._usuarios.listar_empleados()}
        filas = self._filas("WHERE id_proyecto = ?", (id_proyecto,))
        return self._construir_lista(filas, empleados, {id_proyecto: proyecto})

    def actualizar(self, registro: Registro_Tiempo) -> None:
        id_registro = self._exigir_persistido(registro.id_registro, "El registro")
        with self._db.transaccion() as conn:
            cursor = conn.execute(
                "UPDATE registro_tiempo SET horas = ?, descripcion = ? WHERE id_registro = ?",
                (registro.horas, registro.descripcion, id_registro),
            )
            self._exigir_afectadas(cursor, f"el registro con ID {id_registro}")

    def eliminar(self, identificador: int) -> None:
        with self._db.transaccion() as conn:
            cursor = conn.execute("DELETE FROM registro_tiempo WHERE id_registro = ?", (identificador,))
            self._exigir_afectadas(cursor, f"el registro con ID {identificador}")

    def horas_por_proyecto(self) -> list[tuple[str, int, float]]:
        """Resumen para el informe: (proyecto, cantidad de registros, horas totales)."""
        with self._db.transaccion() as conn:
            filas = conn.execute(
                "SELECT p.nombre AS proyecto, COUNT(r.id_registro) AS registros, "
                "COALESCE(SUM(r.horas), 0) AS horas "
                "FROM proyecto p LEFT JOIN registro_tiempo r ON r.id_proyecto = p.id_proyecto "
                "GROUP BY p.id_proyecto ORDER BY horas DESC, p.nombre"
            ).fetchall()
        return [(f["proyecto"], f["registros"], f["horas"]) for f in filas]
