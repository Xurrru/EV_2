from __future__ import annotations

import hashlib
import hmac
import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .validaciones import (
    asignar_id_una_vez,
    validar_correo,
    validar_fecha,
    validar_id_opcional,
    validar_password,
    validar_salario,
    validar_telefono,
    validar_texto,
)

if TYPE_CHECKING:
    from .Departamento import Departamento
    from .Registro_Tiempo import Registro_Tiempo


class Usuario(ABC):
    """Clase base ABSTRACTA: identidad, correo y credenciales protegidas.

    No se puede instanciar directamente; obliga a las subclases a implementar
    ``describir`` (polimorfismo). La contraseña nunca se guarda en texto plano:
    se almacena un hash scrypt con sal aleatoria.
    """

    _SCRYPT_N = 2**14
    _SCRYPT_R = 8
    _SCRYPT_P = 1
    _LARGO_SAL = 16
    _LARGO_HASH = 32
    _PREFIJO = "scrypt"

    def __init__(
        self,
        id_usuario: int | None,
        correo: str,
        password_plana: str | None,
        *,
        password_hash: str | None = None,
    ) -> None:
        """Crea un usuario nuevo (``password_plana``) o rehidrata uno guardado (``password_hash``)."""
        self._id_usuario = validar_id_opcional(id_usuario, "usuario")
        self._correo = validar_correo(correo, "correo")
        if (password_plana is None) == (password_hash is None):
            raise ValueError("Debe indicar la contraseña o un hash almacenado (solo uno de los dos).")
        if password_plana is not None:
            self._establecer_password(password_plana)
        else:
            self._cargar_credencial(password_hash)

    # --- Manejo de credenciales (interno) ---

    @staticmethod
    def _derivar(password: str, sal: bytes, n: int, r: int, p: int, largo: int) -> bytes:
        return hashlib.scrypt(password.encode("utf-8"), salt=sal, n=n, r=r, p=p, dklen=largo)

    def _establecer_password(self, password_plana: str) -> None:
        validar_password(password_plana)
        self._parametros = (self._SCRYPT_N, self._SCRYPT_R, self._SCRYPT_P)
        self._sal = os.urandom(self._LARGO_SAL)
        self._hash = self._derivar(password_plana, self._sal, *self._parametros, self._LARGO_HASH)

    def _cargar_credencial(self, almacenada: str) -> None:
        """Lee el formato ``scrypt$n$r$p$sal_hex$hash_hex`` guardado en la base de datos."""
        try:
            prefijo, n, r, p, sal_hex, hash_hex = almacenada.split("$")
            if prefijo != self._PREFIJO:
                raise ValueError
            self._parametros = (int(n), int(r), int(p))
            self._sal = bytes.fromhex(sal_hex)
            self._hash = bytes.fromhex(hash_hex)
        except (ValueError, AttributeError) as error:
            raise ValueError("El hash de contraseña almacenado no tiene un formato válido.") from error

    # --- Interfaz pública ---

    @property
    def id_usuario(self) -> int | None:
        return self._id_usuario

    def asignar_id_persistido(self, id_usuario: int) -> None:
        """Lo invoca el repositorio una vez que la base de datos generó el ID."""
        self._id_usuario = asignar_id_una_vez(self._id_usuario, id_usuario, "usuario")

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, nuevo_correo: str) -> None:
        self._correo = validar_correo(nuevo_correo, "correo")

    @property
    def rol(self) -> str:
        return self.__class__.__name__

    @property
    def password_hash(self) -> str:
        """Representación segura para guardar en la base de datos (nunca la contraseña)."""
        n, r, p = self._parametros
        return f"{self._PREFIJO}${n}${r}${p}${self._sal.hex()}${self._hash.hex()}"

    def verificar_contrasena(self, password: str) -> bool:
        if not isinstance(password, str) or not password:
            return False
        n, r, p = self._parametros
        candidato = self._derivar(password, self._sal, n, r, p, len(self._hash))
        return hmac.compare_digest(self._hash, candidato)

    def cambiar_contrasena(self, password_actual: str, password_nueva: str) -> None:
        if not self.verificar_contrasena(password_actual):
            raise ValueError("La contraseña actual es incorrecta.")
        self._establecer_password(password_nueva)

    @abstractmethod
    def describir(self) -> str:
        """Texto breve que identifica al usuario según su rol."""

    def __str__(self) -> str:
        return self.describir()


class Administrador(Usuario):
    """Usuario con permisos para administrar el sistema."""

    def describir(self) -> str:
        return f"Administrador <{self.correo}>"

    def gestionar(self, entidad: str) -> str:
        entidad = validar_texto(entidad, "nombre de la entidad a gestionar")
        return f"El administrador {self.correo} gestiona: {entidad}"

    def generar_informe(self) -> str:
        return f"--- INFORME ---\nGenerado por administrador: {self.correo}"


class Empleado(Usuario):
    """Usuario que pertenece opcionalmente a un departamento y registra horas."""

    def __init__(
        self,
        id_usuario: int | None,
        correo: str,
        password_plana: str | None,
        id_empleado: int | None,
        nombre: str,
        direccion: str,
        telefono: str,
        email: str,
        fecha_contrato: str,
        salario: float,
        *,
        password_hash: str | None = None,
    ) -> None:
        super().__init__(id_usuario, correo, password_plana, password_hash=password_hash)
        self._id_empleado = validar_id_opcional(id_empleado, "empleado")
        self._nombre = validar_texto(nombre, "nombre")
        self._direccion = validar_texto(direccion, "dirección", maximo=150)
        self._telefono = validar_telefono(telefono)
        self._email = validar_correo(email, "email de contacto")
        self._fecha_contrato = validar_fecha(fecha_contrato, "fecha de contrato")
        self._salario = validar_salario(salario)
        self._departamento: Departamento | None = None
        self._registros_tiempo: list[Registro_Tiempo] = []

    # --- Atributos con encapsulamiento: lectura por property, escritura validada ---

    @property
    def id_empleado(self) -> int | None:
        return self._id_empleado

    def asignar_id_empleado_persistido(self, id_empleado: int) -> None:
        self._id_empleado = asignar_id_una_vez(self._id_empleado, id_empleado, "empleado")

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "nombre")

    @property
    def direccion(self) -> str:
        return self._direccion

    @direccion.setter
    def direccion(self, valor: str) -> None:
        self._direccion = validar_texto(valor, "dirección", maximo=150)

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

    @property
    def salario(self) -> float:
        return self._salario

    @salario.setter
    def salario(self, valor: float) -> None:
        self._salario = validar_salario(valor)

    # --- Relaciones (asociaciones del UML) ---

    @property
    def departamento(self) -> Departamento | None:
        return self._departamento

    @property
    def registros_tiempo(self) -> tuple[Registro_Tiempo, ...]:
        return tuple(self._registros_tiempo)

    @property
    def total_horas(self) -> float:
        return sum(registro.horas for registro in self._registros_tiempo)

    def asignar_departamento(self, departamento: Departamento | None) -> None:
        """Mantiene la asociación bidireccional Empleado <-> Departamento."""
        if self._departamento is departamento:
            return
        if self._departamento is not None:
            self._departamento._quitar_empleado(self)
        self._departamento = departamento
        if departamento is not None:
            departamento._agregar_empleado(self)

    def registrar_horas(self, registro_tiempo: Registro_Tiempo) -> None:
        if registro_tiempo.empleado is not self:
            raise ValueError("El registro pertenece a otro empleado.")
        for posicion, existente in enumerate(self._registros_tiempo):
            if existente is registro_tiempo:
                return
            if registro_tiempo.id_registro is not None and existente.id_registro == registro_tiempo.id_registro:
                self._registros_tiempo[posicion] = registro_tiempo  # versión recargada desde la BD
                return
        self._registros_tiempo.append(registro_tiempo)

    def quitar_registro(self, registro_tiempo: Registro_Tiempo) -> None:
        self._registros_tiempo = [r for r in self._registros_tiempo if r is not registro_tiempo]

    def describir(self) -> str:
        return f"Empleado {self._nombre} <{self.correo}>"
