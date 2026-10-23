"""Entrada y salida por consola. Es la única capa que usa ``input`` y ``print``.

Todas las lecturas se repiten hasta que el dato sea válido, y el usuario puede
escribir ``/cancelar`` en cualquier momento para abortar la operación actual.
"""
from __future__ import annotations

import getpass
from typing import Callable, Sequence, TypeVar

from config.excepciones import OperacionCancelada

T = TypeVar("T")
COMANDO_CANCELAR = "/cancelar"


# Funciones de bajo nivel separadas para poder sustituirlas en las pruebas automáticas.
def _entrada(mensaje: str) -> str:
    return input(mensaje)


def _entrada_secreta(mensaje: str) -> str:
    return getpass.getpass(mensaje)


def _revisar_cancelacion(texto: str) -> None:
    if texto.strip().lower() == COMANDO_CANCELAR:
        raise OperacionCancelada()


# --- Salida ---

def mostrar_titulo(texto: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {texto}")
    print("=" * 60)


def mostrar_exito(texto: str) -> None:
    print(f"[OK] {texto}")


def mostrar_error(texto: str) -> None:
    print(f"[ERROR] {texto}")


def mostrar_info(texto: str) -> None:
    print(f"[i] {texto}")


def mostrar_tabla(encabezados: Sequence[str], filas: Sequence[Sequence[object]]) -> None:
    celdas = [tuple(str(valor) for valor in fila) for fila in filas]
    if not celdas:
        mostrar_info("No hay registros para mostrar.")
        return
    anchos = [max(len(encabezado), *(len(fila[i]) for fila in celdas)) for i, encabezado in enumerate(encabezados)]
    linea = " | ".join(encabezado.ljust(anchos[i]) for i, encabezado in enumerate(encabezados))
    print("\n" + linea)
    print("-+-".join("-" * ancho for ancho in anchos))
    for fila in celdas:
        print(" | ".join(valor.ljust(anchos[i]) for i, valor in enumerate(fila)))


# --- Entrada ---

def leer_validado(mensaje: str, validador: Callable[[str], T], defecto: T | None = None) -> T:
    """Pide un dato hasta que ``validador`` lo acepte (``ValueError`` = dato inválido).

    Si se indica ``defecto``, presionar Enter conserva el valor actual.
    """
    sufijo = f" [{defecto}]" if defecto is not None else ""
    while True:
        texto = _entrada(f"{mensaje}{sufijo}: ")
        _revisar_cancelacion(texto)
        if texto.strip() == "" and defecto is not None:
            return defecto
        try:
            return validador(texto)
        except ValueError as error:
            mostrar_error(str(error))


def leer_entero(mensaje: str, minimo: int | None = None, maximo: int | None = None) -> int:
    def convertir(texto: str) -> int:
        try:
            numero = int(texto.strip())
        except ValueError:
            raise ValueError("Debe ingresar un número entero.") from None
        if minimo is not None and numero < minimo:
            raise ValueError(f"El valor mínimo permitido es {minimo}.")
        if maximo is not None and numero > maximo:
            raise ValueError(f"El valor máximo permitido es {maximo}.")
        return numero

    return leer_validado(mensaje, convertir)


def leer_decimal(mensaje: str, validador: Callable[[float], float] | None = None, defecto: float | None = None) -> float:
    def convertir(texto: str) -> float:
        texto = texto.strip()
        if "," in texto:
            raise ValueError("Use punto como separador decimal y no use separadores de miles (ej: 7.5 o 900000).")
        try:
            numero = float(texto)
        except ValueError:
            raise ValueError("Debe ingresar un número válido.") from None
        return validador(numero) if validador else numero

    return leer_validado(mensaje, convertir, defecto)


def leer_password(mensaje: str, validador: Callable[[str], str] | None = None, confirmar: bool = False) -> str:
    """Lee una contraseña sin mostrarla. No se recorta ni se registra en ningún lado."""
    while True:
        clave = _entrada_secreta(f"{mensaje}: ")
        _revisar_cancelacion(clave)
        if validador is not None:
            try:
                validador(clave)
            except ValueError as error:
                mostrar_error(str(error))
                continue
        if confirmar and _entrada_secreta("Repita la contraseña: ") != clave:
            mostrar_error("Las contraseñas no coinciden.")
            continue
        return clave


def leer_opcion(mensaje: str, validas: Sequence[str]) -> str:
    while True:
        eleccion = _entrada(f"{mensaje}: ").strip()
        if eleccion in validas:
            return eleccion
        mostrar_error(f"Opción no válida. Elija una de: {', '.join(validas)}.")


def confirmar(mensaje: str) -> bool:
    while True:
        respuesta = _entrada(f"{mensaje} (s/n): ").strip().lower()
        _revisar_cancelacion(respuesta)
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("n", "no"):
            return False
        mostrar_error("Responda 's' o 'n'.")


def elegir(titulo: str, elementos: Sequence[T], formatear: Callable[[T], str]) -> T:
    """Muestra una lista numerada y devuelve el elemento elegido."""
    if not elementos:
        raise OperacionCancelada("No hay registros disponibles para seleccionar.")
    print(f"\n{titulo}")
    for posicion, elemento in enumerate(elementos, 1):
        print(f"  {posicion}. {formatear(elemento)}")
    return elementos[leer_entero("Número de la lista", 1, len(elementos)) - 1]
