from __future__ import annotations

from models.Departamento import Departamento
from repositories.base_repository import RepositorioBase

_COLUMNAS = "id_departamento, nombre, gerente"


class RepositorioDepartamento(RepositorioBase[Departamento]):
    """CRUD de la tabla ``departamento``. Todas las consultas son parametrizadas (?)."""

    @staticmethod
    def _construir(fila) -> Departamento:
        return Departamento(fila["id_departamento"], fila["nombre"], fila["gerente"])

    def crear(self, departamento: Departamento) -> None:
        self._exigir_nuevo(departamento.id_departamento, "El departamento")
        with self._db.transaccion() as conn:
            cursor = conn.execute(
                "INSERT INTO departamento (nombre, gerente) VALUES (?, ?)",
                (departamento.nombre, departamento.gerente),
            )
            nuevo_id = cursor.lastrowid
        departamento.asignar_id_persistido(nuevo_id)

    def obtener_por_id(self, identificador: int) -> Departamento | None:
        with self._db.transaccion() as conn:
            fila = conn.execute(
                f"SELECT {_COLUMNAS} FROM departamento WHERE id_departamento = ?", (identificador,)
            ).fetchone()
        return self._construir(fila) if fila else None

    def listar(self) -> list[Departamento]:
        with self._db.transaccion() as conn:
            filas = conn.execute(f"SELECT {_COLUMNAS} FROM departamento ORDER BY nombre").fetchall()
        return [self._construir(fila) for fila in filas]

    def buscar_por_nombre(self, texto: str) -> list[Departamento]:
        with self._db.transaccion() as conn:
            filas = conn.execute(
                rf"SELECT {_COLUMNAS} FROM departamento WHERE nombre LIKE ? ESCAPE '\' ORDER BY nombre",
                (self._patron_like(texto),),
            ).fetchall()
        return [self._construir(fila) for fila in filas]

    def actualizar(self, departamento: Departamento) -> None:
        id_departamento = self._exigir_persistido(departamento.id_departamento, "El departamento")
        with self._db.transaccion() as conn:
            cursor = conn.execute(
                "UPDATE departamento SET nombre = ?, gerente = ? WHERE id_departamento = ?",
                (departamento.nombre, departamento.gerente, id_departamento),
            )
            self._exigir_afectadas(cursor, f"el departamento con ID {id_departamento}")

    def eliminar(self, identificador: int) -> None:
        # Los usuarios del departamento quedan sin departamento (ON DELETE SET NULL).
        with self._db.transaccion() as conn:
            cursor = conn.execute("DELETE FROM departamento WHERE id_departamento = ?", (identificador,))
            self._exigir_afectadas(cursor, f"el departamento con ID {identificador}")

    def contar_empleados(self, identificador: int) -> int:
        with self._db.transaccion() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM usuario WHERE id_departamento = ?", (identificador,)
            ).fetchone()[0]
