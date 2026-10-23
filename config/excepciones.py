"""Excepciones propias de la aplicación.

Tener una jerarquía propia permite que cada capa lance errores con significado
y que la capa de menús decida cómo mostrarlos sin exponer detalles internos.
"""


class ErrorSistema(Exception):
    """Base de todas las excepciones controladas de la aplicación."""


class ErrorBaseDatos(ErrorSistema):
    """Fallo al conectar o al operar con la base de datos."""


class ErrorIntegridad(ErrorBaseDatos):
    """Violación de una regla de integridad (UNIQUE, FOREIGN KEY, CHECK...)."""


class RegistroNoEncontrado(ErrorBaseDatos):
    """El registro solicitado no existe en la base de datos."""


class OperacionCancelada(ErrorSistema):
    """El usuario canceló la operación en curso o no hay datos para continuar."""

    def __init__(self, mensaje: str = "Operación cancelada.") -> None:
        super().__init__(mensaje)
