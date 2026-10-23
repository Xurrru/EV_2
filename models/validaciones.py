"""Validaciones reutilizables por todos los modelos y por la capa de vistas.

Centralizarlas evita repetir las mismas reglas en cada clase (principio DRY).
Todas lanzan ``ValueError`` con un mensaje claro para el usuario.
"""
from __future__ import annotations

import math
import re
from datetime import date
from typing import Callable

_PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PATRON_TELEFONO = re.compile(r"^\+?[0-9][0-9 \-]{6,14}$")
_PATRON_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")

LARGO_MINIMO_PASSWORD = 8
LARGO_MAXIMO_PASSWORD = 128
SALARIO_MAXIMO = 1_000_000_000
HORAS_MAXIMAS_POR_REGISTRO = 24


def validar_id_positivo(valor: object, campo: str) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(f"El ID de {campo} debe ser un número entero.")
    if valor <= 0:
        raise ValueError(f"El ID de {campo} debe ser positivo.")
    return valor


def validar_id_opcional(valor: object, campo: str) -> int | None:
    """``None`` significa que el objeto aún no se ha guardado en la base de datos."""
    return None if valor is None else validar_id_positivo(valor, campo)


def asignar_id_una_vez(actual: int | None, nuevo: object, campo: str) -> int:
    """El ID lo asigna la base de datos y no puede cambiarse después."""
    if actual is not None:
        raise ValueError(f"El {campo} ya tiene un ID asignado.")
    return validar_id_positivo(nuevo, campo)


def validar_texto(valor: object, campo: str, maximo: int = 100) -> str:
    if not isinstance(valor, str):
        raise ValueError(f"El {campo} debe ser texto.")
    valor = valor.strip()
    if not valor:
        raise ValueError(f"El {campo} no puede estar vacío.")
    if len(valor) > maximo:
        raise ValueError(f"El {campo} no puede superar los {maximo} caracteres.")
    return valor


def validar_correo(valor: object, campo: str = "correo") -> str:
    texto = validar_texto(valor, campo, maximo=120).lower()
    if not _PATRON_CORREO.match(texto):
        raise ValueError(f"El {campo} no tiene un formato válido (ejemplo: nombre@empresa.com).")
    return texto


def validar_telefono(valor: object) -> str:
    texto = validar_texto(valor, "teléfono", maximo=20)
    if not _PATRON_TELEFONO.match(texto):
        raise ValueError("El teléfono debe tener entre 7 y 15 dígitos (puede iniciar con +).")
    return texto


def validar_fecha(valor: object, campo: str = "fecha", permitir_futuro: bool = True) -> str:
    texto = validar_texto(valor, campo, maximo=10)
    if not _PATRON_FECHA.match(texto):
        raise ValueError(f"La {campo} debe tener formato AAAA-MM-DD.")
    try:
        fecha = date.fromisoformat(texto)
    except ValueError as error:
        raise ValueError(f"La {campo} no es una fecha real del calendario.") from error
    if not permitir_futuro and fecha > date.today():
        raise ValueError(f"La {campo} no puede ser futura.")
    return fecha.isoformat()


def _validar_numero(valor: object, campo: str) -> float:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"El {campo} debe ser un número.")
    if not math.isfinite(valor):
        raise ValueError(f"El {campo} debe ser un número finito.")
    return float(valor)


def validar_salario(valor: object) -> float:
    numero = _validar_numero(valor, "salario")
    if numero <= 0:
        raise ValueError("El salario debe ser mayor a 0.")
    if numero > SALARIO_MAXIMO:
        raise ValueError("El salario ingresado supera el máximo permitido.")
    return numero


def validar_horas(valor: object) -> float:
    numero = _validar_numero(valor, "valor de horas")
    if numero <= 0:
        raise ValueError("Las horas registradas deben ser mayores a 0.")
    if numero > HORAS_MAXIMAS_POR_REGISTRO:
        raise ValueError(f"Un registro no puede superar {HORAS_MAXIMAS_POR_REGISTRO} horas.")
    return numero


def validar_password(valor: object) -> str:
    if not isinstance(valor, str) or not valor:
        raise ValueError("La contraseña no puede estar vacía.")
    if len(valor) < LARGO_MINIMO_PASSWORD:
        raise ValueError(f"La contraseña debe tener al menos {LARGO_MINIMO_PASSWORD} caracteres.")
    if len(valor) > LARGO_MAXIMO_PASSWORD:
        raise ValueError(f"La contraseña no puede superar los {LARGO_MAXIMO_PASSWORD} caracteres.")
    if not any(c.isalpha() for c in valor) or not any(c.isdigit() for c in valor):
        raise ValueError("La contraseña debe combinar letras y números.")
    return valor


# --- Fábricas: devuelven un validador de un solo argumento (útil en la capa de vistas) ---

def validador_texto(campo: str, maximo: int = 100) -> Callable[[str], str]:
    return lambda valor: validar_texto(valor, campo, maximo)


def validador_correo(campo: str = "correo") -> Callable[[str], str]:
    return lambda valor: validar_correo(valor, campo)


def validador_fecha(campo: str = "fecha", permitir_futuro: bool = True) -> Callable[[str], str]:
    return lambda valor: validar_fecha(valor, campo, permitir_futuro)
