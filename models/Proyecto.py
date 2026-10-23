from __future__ import annotations

from .validaciones import asignar_id_una_vez, validar_fecha, validar_id_opcional, validar_texto


class Proyecto:
    """Clase Proyecto según el diagrama UML."""

    def __init__(self, id_proyecto: int | None, nombre: str, descripcion: str, fecha_inicio: str) -> None:
        self._id_proyecto = validar_id_opcional(id_proyecto, "proyecto")
        self._nombre = validar_texto(nombre, "nombre del proyecto")
        self._descripcion = validar_texto(descripcion, "descripción del proyecto", maximo=300)
        self._fecha_inicio = validar_fecha(fecha_inicio, "fecha de inicio")

    @property
    def id_proyecto(self) -> int | None:
        return self._id_proyecto

    def asignar_id_persistido(self, id_proyecto: int) -> None:
        self._id_proyecto = asignar_id_una_vez(self._id_proyecto, id_proyecto, "proyecto")

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def fecha_inicio(self) -> str:
        return self._fecha_inicio

    def editar(self, nuevo_nombre: str, nueva_descripcion: str) -> None:
        nombre = validar_texto(nuevo_nombre, "nombre del proyecto")
        descripcion = validar_texto(nueva_descripcion, "descripción del proyecto", maximo=300)
        self._nombre = nombre
        self._descripcion = descripcion
