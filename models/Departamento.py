from __future__ import annotations

from typing import TYPE_CHECKING

from .validaciones import asignar_id_una_vez, validar_id_opcional, validar_texto

if TYPE_CHECKING:
    from .Usuarios import Empleado


class Departamento:
    """Agrupa empleados y mantiene los datos propios de un departamento."""

    def __init__(self, id_departamento: int | None, nombre: str, gerente: str) -> None:
        self._id_departamento = validar_id_opcional(id_departamento, "departamento")
        self._nombre = validar_texto(nombre, "nombre del departamento")
        self._gerente = validar_texto(gerente, "gerente del departamento")
        self._empleados: list[Empleado] = []

    @property
    def id_departamento(self) -> int | None:
        return self._id_departamento

    def asignar_id_persistido(self, id_departamento: int) -> None:
        self._id_departamento = asignar_id_una_vez(self._id_departamento, id_departamento, "departamento")

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, nuevo_nombre: str) -> None:
        self._nombre = validar_texto(nuevo_nombre, "nombre del departamento")

    @property
    def gerente(self) -> str:
        return self._gerente

    @gerente.setter
    def gerente(self, nuevo_gerente: str) -> None:
        self._gerente = validar_texto(nuevo_gerente, "gerente del departamento")

    @property
    def empleados(self) -> tuple[Empleado, ...]:
        return tuple(self._empleados)

    # Métodos "protegidos": solo los usa Empleado.asignar_departamento para mantener la relación.
    def _agregar_empleado(self, empleado: Empleado) -> None:
        if empleado not in self._empleados:
            self._empleados.append(empleado)

    def _quitar_empleado(self, empleado: Empleado) -> None:
        if empleado in self._empleados:
            self._empleados.remove(empleado)

    def editar(self, nuevo_nombre: str, nuevo_gerente: str) -> None:
        """Actualiza ambos datos o ninguno (valida primero, asigna después)."""
        nombre = validar_texto(nuevo_nombre, "nombre del departamento")
        gerente = validar_texto(nuevo_gerente, "gerente del departamento")
        self._nombre = nombre
        self._gerente = gerente

    def buscar(self, id_dept: int) -> bool:
        return self._id_departamento == id_dept

    def eliminar(self) -> None:
        """Desvincula a sus empleados (en memoria) antes de borrar el departamento."""
        for empleado in list(self._empleados):
            empleado.asignar_departamento(None)
