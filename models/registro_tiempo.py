import math

from models.empleado import Empleado
from models.proyecto import Proyecto
from models.validaciones import validar_fecha, validar_texto


class Registro_Tiempo:
    """
    Modelo (DTO) para Registro_Tiempo: las horas que un Empleado trabajó en un Proyecto.
    Es la clase que RELACIONA a Empleado con Proyecto (asociación).
    """

    def __init__(self, fecha: str, horas: float, descripcion: str, empleado: Empleado,
                 proyecto: Proyecto, id_registro: int | None = None):
        self.id_registro = id_registro
        self.fecha = fecha
        self.horas = horas
        self.descripcion = descripcion
        self.empleado = empleado
        self.proyecto = proyecto

    @property
    def fecha(self) -> str:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: str) -> None:
        self._fecha = validar_fecha(valor, "fecha del registro", permitir_futuro=False)

    @property
    def horas(self) -> float:
        return self._horas

    @horas.setter
    def horas(self, valor: float) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise TypeError("Las horas deben ser un número.")
        if not math.isfinite(valor) or valor <= 0 or valor > 24:
            raise ValueError("Las horas registradas deben ser mayores a 0 y no superar 24.")
        self._horas = float(valor)

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        self._descripcion = validar_texto(valor, "descripción del registro", 3, 200)

    @property
    def empleado(self) -> Empleado:
        return self._empleado

    @empleado.setter
    def empleado(self, valor: Empleado) -> None:
        if not isinstance(valor, Empleado):
            raise TypeError("El registro debe estar asociado a un Empleado.")
        self._empleado = valor

    @property
    def proyecto(self) -> Proyecto:
        return self._proyecto

    @proyecto.setter
    def proyecto(self, valor: Proyecto) -> None:
        if not isinstance(valor, Proyecto):
            raise TypeError("El registro debe estar asociado a un Proyecto.")
        self._proyecto = valor

    def modificar(self, nuevas_horas: float, nueva_descripcion: str) -> None:
        self.horas = nuevas_horas
        self.descripcion = nueva_descripcion

    def __str__(self) -> str:
        id_str = self.id_registro if self.id_registro is not None else "Sin asignar"
        return (f"Registro [ID: {id_str}] | Fecha: {self.fecha} | Empleado: {self.empleado.nombre} "
                f"| Proyecto: {self.proyecto.nombre} | Horas: {self.horas:g} | Tarea: {self.descripcion}")

    def __repr__(self) -> str:
        return (f"Registro_Tiempo(id_registro={self.id_registro}, fecha='{self.fecha}', "
                f"horas={self.horas}, empleado={repr(self.empleado)}, proyecto={repr(self.proyecto)})")
