from __future__ import annotations

from .Proyecto import Proyecto
from .Usuarios import Empleado
from .validaciones import (
    asignar_id_una_vez,
    validar_fecha,
    validar_horas,
    validar_id_opcional,
    validar_texto,
)


class Registro_Tiempo:
    """Asocia las horas trabajadas con un empleado y un proyecto."""

    def __init__(
        self,
        id_registro: int | None,
        fecha: str,
        horas: float,
        descripcion: str,
        empleado: Empleado,
        proyecto: Proyecto,
    ) -> None:
        if not isinstance(empleado, Empleado):
            raise ValueError("El registro debe estar asociado a un empleado válido.")
        if not isinstance(proyecto, Proyecto):
            raise ValueError("El registro debe estar asociado a un proyecto válido.")
        self._id_registro = validar_id_opcional(id_registro, "registro")
        self._fecha = validar_fecha(fecha, "fecha del registro", permitir_futuro=False)
        self._horas = validar_horas(horas)
        self._descripcion = validar_texto(descripcion, "descripción del registro", maximo=200)
        self._empleado = empleado
        self._proyecto = proyecto

    @property
    def id_registro(self) -> int | None:
        return self._id_registro

    def asignar_id_persistido(self, id_registro: int) -> None:
        self._id_registro = asignar_id_una_vez(self._id_registro, id_registro, "registro")

    @property
    def fecha(self) -> str:
        return self._fecha

    @property
    def horas(self) -> float:
        return self._horas

    @horas.setter
    def horas(self, cantidad: float) -> None:
        self._horas = validar_horas(cantidad)

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def empleado(self) -> Empleado:
        return self._empleado

    @property
    def proyecto(self) -> Proyecto:
        return self._proyecto

    def modificar(self, nuevas_horas: float, nueva_descripcion: str) -> None:
        horas = validar_horas(nuevas_horas)
        descripcion = validar_texto(nueva_descripcion, "descripción del registro", maximo=200)
        self._horas = horas
        self._descripcion = descripcion
