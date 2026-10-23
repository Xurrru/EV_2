from __future__ import annotations

from abc import ABC, abstractmethod

from views.menus import Opcion


class ControladorCRUD(ABC):
    """Contrato común de los controladores: las cuatro operaciones CRUD.

    ``opciones_menu`` se hereda tal cual, así todos los submenús son iguales
    sin repetir código.
    """

    @abstractmethod
    def listar(self) -> None: ...

    @abstractmethod
    def crear(self) -> None: ...

    @abstractmethod
    def actualizar(self) -> None: ...

    @abstractmethod
    def eliminar(self) -> None: ...

    def opciones_menu(self) -> dict[str, Opcion]:
        return {
            "1": ("Listar", self.listar),
            "2": ("Crear", self.crear),
            "3": ("Actualizar", self.actualizar),
            "4": ("Eliminar", self.eliminar),
        }
