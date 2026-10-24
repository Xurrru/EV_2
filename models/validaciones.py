import re
from datetime import date

"""
Funciones de validación que usan varias clases del modelo.
Se escriben una sola vez para no repetir el mismo código en cada setter.
Lanzan TypeError si el tipo es incorrecto y ValueError si el valor no es válido.
"""


def validar_texto(valor, campo: str, minimo: int = 2, maximo: int = 100) -> str:
    if not isinstance(valor, str):
        raise TypeError(f"El {campo} debe ser texto.")
    valor = valor.strip()
    if len(valor) < minimo:
        raise ValueError(f"El {campo} debe tener al menos {minimo} caracteres.")
    if len(valor) > maximo:
        raise ValueError(f"El {campo} no puede superar los {maximo} caracteres.")
    return valor


def validar_correo(valor, campo: str = "correo") -> str:
    valor = validar_texto(valor, campo, 5, 120).lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", valor):
        raise ValueError(f"El {campo} no tiene un formato válido (ejemplo: nombre@empresa.com).")
    return valor


def validar_telefono(valor) -> str:
    valor = validar_texto(valor, "teléfono", 7, 20)
    if not re.match(r"^\+?[0-9][0-9 \-]{6,14}$", valor):
        raise ValueError("El teléfono debe tener entre 7 y 15 dígitos (puede iniciar con +).")
    return valor


def validar_fecha(valor, campo: str = "fecha", permitir_futuro: bool = True) -> str:
    valor = validar_texto(valor, campo, 1, 10)
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", valor):
        raise ValueError(f"La {campo} debe tener formato AAAA-MM-DD.")
    try:
        fecha = date.fromisoformat(valor)
    except ValueError:
        raise ValueError(f"La {campo} no es una fecha real del calendario.")
    if not permitir_futuro and fecha > date.today():
        raise ValueError(f"La {campo} no puede ser futura.")
    return fecha.isoformat()
