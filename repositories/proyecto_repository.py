from __future__ import annotations

from models.Proyecto import Proyecto
from repositories.base_repository import RepositorioBase

_COLUMNAS = "id_proyecto, nombre, descripcion, fecha_inicio"


class RepositorioProyecto(RepositorioBase[Proyecto]):
    """CRUD de la tabla ``proyecto``."""

    @staticmethod
    def _construir(fila) -> Proyecto:
        return Proyecto(fila["id_proyecto"], fila["nombre"], fila["descripcion"], fila["fecha_inicio"])

    def crear(self, proyecto: Proyecto) -> None:
        self._exigir_nuevo(proyecto.id_proyecto, "El proyecto")
        with self._db.transaccion() as conn:
            cursor = conn.execute(
                "INSERT INTO proyecto (nombre, descripcion, fecha_inicio) VALUES (?, ?, ?)",
                (proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio),
            )
            nuevo_id = cursor.lastrowid
        proyecto.asignar_id_persistido(nuevo_id)

    def obtener_por_id(self, identificador: int) -> Proyecto | None:
        with self._db.transaccion() as conn:
            fila = conn.execute(
                f"SELECT {_COLUMNAS} FROM proyecto WHERE id_proyecto = ?", (identificador,)
            ).fetchone()
        return self._construir(fila) if fila else None

    def listar(self) -> list[Proyecto]:
        with self._db.transaccion() as conn:
            filas = conn.execute(f"SELECT {_COLUMNAS} FROM proyecto ORDER BY nombre").fetchall()
        return [self._construir(fila) for fila in filas]

    def buscar_por_nombre(self, texto: str) -> list[Proyecto]:
        with self._db.transaccion() as conn:
            filas = conn.execute(
                rf"SELECT {_COLUMNAS} FROM proyecto WHERE nombre LIKE ? ESCAPE '\' ORDER BY nombre",
                (self._patron_like(texto),),
            ).fetchall()
        return [self._construir(fila) for fila in filas]

    def actualizar(self, proyecto: Proyecto) -> None:
        id_proyecto = self._exigir_persistido(proyecto.id_proyecto, "El proyecto")
        with self._db.transaccion() as conn:
            cursor = conn.execute(
                "UPDATE proyecto SET nombre = ?, descripcion = ? WHERE id_proyecto = ?",
                (proyecto.nombre, proyecto.descripcion, id_proyecto),
            )
            self._exigir_afectadas(cursor, f"el proyecto con ID {id_proyecto}")

    def eliminar(self, identificador: int) -> None:
        # Los registros de tiempo del proyecto se eliminan en cascada.
        with self._db.transaccion() as conn:
            cursor = conn.execute("DELETE FROM proyecto WHERE id_proyecto = ?", (identificador,))
            self._exigir_afectadas(cursor, f"el proyecto con ID {identificador}")

    def contar_registros(self, identificador: int) -> int:
        with self._db.transaccion() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM registro_tiempo WHERE id_proyecto = ?", (identificador,)
            ).fetchone()[0]
