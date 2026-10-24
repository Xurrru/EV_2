import math

from models.departamento import Departamento
from models.usuario import Usuario
from models.validaciones import validar_correo, validar_fecha, validar_telefono, validar_texto


class Empleado(Usuario):
    """
    Clase HIJA de Usuario (herencia). Hereda correo y contraseña, y agrega
    los datos propios del empleado.

    Relaciones del modelo:
    - Empleado pertenece a un Departamento (asociación, atributo `departamento`).
    - Empleado tiene muchos Registro_Tiempo (lista `registros_tiempo`).
    """

    def __init__(self, correo: str, password: str | None, nombre: str, direccion: str, telefono: str,
                 email: str, fecha_contrato: str, salario: float, departamento: Departamento | None = None,
                 id_usuario: int | None = None, id_empleado: int | None = None,
                 password_hash: str | None = None):
        super().__init__(correo, password, id_usuario, password_hash)  # constructor del padre
        self.id_empleado = id_empleado
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.fecha_contrato = fecha_contrato
        self.salario = salario
        self.departamento = departamento
        self._registros_tiempo = []

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "nombre", 2, 100)

    @property
    def direccion(self) -> str:
        return self._direccion

    @direccion.setter
    def direccion(self, valor: str) -> None:
        self._direccion = validar_texto(valor, "dirección", 3, 150)

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        self._telefono = validar_telefono(valor)

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        self._email = validar_correo(valor, "email de contacto")

    @property
    def fecha_contrato(self) -> str:
        return self._fecha_contrato

    @fecha_contrato.setter
    def fecha_contrato(self, valor: str) -> None:
        self._fecha_contrato = validar_fecha(valor, "fecha de contrato")

    @property
    def salario(self) -> float:
        return self._salario

    @salario.setter
    def salario(self, valor: float) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise TypeError("El salario debe ser un número.")
        if not math.isfinite(valor) or valor <= 0 or valor > 1_000_000_000:
            raise ValueError("El salario debe ser mayor a 0 y no superar 1.000.000.000.")
        self._salario = float(valor)

    @property
    def departamento(self) -> Departamento | None:
        return self._departamento

    @departamento.setter
    def departamento(self, valor: Departamento | None) -> None:
        if valor is not None and not isinstance(valor, Departamento):
            raise TypeError("El departamento debe ser una instancia de Departamento o None.")
        self._departamento = valor

    @property
    def registros_tiempo(self) -> tuple:
        return tuple(self._registros_tiempo)  # copia de solo lectura

    @property
    def total_horas(self) -> float:
        return sum(registro.horas for registro in self._registros_tiempo)

    def registrar_horas(self, registro) -> None:
        """Asocia un Registro_Tiempo a este empleado (solo si el registro es suyo)."""
        if registro.empleado is not self:
            raise ValueError("El registro pertenece a otro empleado.")
        if registro not in self._registros_tiempo:
            self._registros_tiempo.append(registro)

    def __str__(self) -> str:
        id_str = self.id_empleado if self.id_empleado is not None else "Sin asignar"
        depto = self.departamento.nombre if self.departamento else "Ninguno"
        return (f"Empleado [ID: {id_str}] | Nombre: {self.nombre} | Correo: {self.correo} "
                f"| Departamento: {depto} | Salario: ${self.salario:,.0f}")

    def __repr__(self) -> str:
        return (f"Empleado(id_empleado={self.id_empleado}, nombre='{self.nombre}', "
                f"correo='{self.correo}', departamento={repr(self.departamento)})")
