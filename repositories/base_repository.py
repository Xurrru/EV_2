from __future__ import annotations

from abc import ABC, abstractmethod
from sqlite3 import Cursor
from typing import Generic, TypeVar

from config.Base_Datos import Database
from config.excepciones import RegistroNoEncontrado

T = TypeVar("T")


class RepositorioBase(ABC, Generic[T]):
    """Contrato común de todos los repositorios (CRUD) y utilidades compartidas.

    Cada repositorio concreto implementa las cinco operaciones para su entidad;
    lo que se repite en todos vive aquí (reutilización por herencia).
    """

    def __init__(self) -> None:
        self._db = Database()

    @abstractmethod
    def crear(self, entidad: T) -> None:
        """INSERT: guarda la entidad y le asigna el ID generado."""

    @abstractmethod
    def obtener_por_id(self, identificador: int) -> T | None:
        """SELECT por clave primaria. Devuelve ``None`` si no existe."""

    @abstractmethod
    def listar(self) -> list[T]:
        """SELECT de todos los registros."""

    @abstractmethod
    def actualizar(self, entidad: T) -> None:
        """UPDATE de una entidad ya guardada."""

    @abstractmethod
    def eliminar(self, identificador: int) -> None:
        """DELETE por clave primaria."""

    # --- Utilidades compartidas ---

    @staticmethod
    def _exigir_nuevo(identificador: int | None, descripcion: str) -> None:
        if identificador is not None:
            raise ValueError(f"{descripcion} ya está guardado en la base de datos.")

    @staticmethod
    def _exigir_persistido(identificador: int | None, descripcion: str) -> int:
        if identificador is None:
            raise ValueError(f"{descripcion} aún no está guardado en la base de datos.")
        return identificador

    @staticmethod
    def _exigir_afectadas(cursor: Cursor, descripcion: str) -> None:
        if cursor.rowcount == 0:
            raise RegistroNoEncontrado(f"No existe {descripcion}.")

    @staticmethod
    def _patron_like(texto: str) -> str:
        """Escapa % y _ para que el texto buscado se trate como literal."""
        escapado = texto.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        return f"%{escapado}%"
