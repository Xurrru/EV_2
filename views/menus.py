"""Motor de menús reutilizable. Aquí se centraliza el manejo de errores de la sesión."""
from __future__ import annotations

import logging
from typing import Callable

from config.excepciones import ErrorSistema, OperacionCancelada
from views import consola

Opcion = tuple[str, Callable[[], None]]
_log = logging.getLogger("sistema.menu")


def _ejecutar_accion(accion: Callable[[], None]) -> None:
    """Ejecuta una acción del menú sin permitir que un error cierre el programa."""
    try:
        accion()
    except OperacionCancelada as aviso:
        consola.mostrar_info(str(aviso))
    except (ValueError, ErrorSistema) as error:
        consola.mostrar_error(str(error))
    except (KeyboardInterrupt, EOFError):
        raise  # salida voluntaria: la maneja la aplicación principal
    except Exception:
        _log.exception("Error inesperado en una acción del menú")
        consola.mostrar_error("Ocurrió un error inesperado. La operación fue cancelada y quedó registrada en el log.")


def ejecutar_menu(titulo: str, opciones: dict[str, Opcion], texto_salida: str = "Volver") -> None:
    while True:
        consola.mostrar_titulo(titulo)
        for clave, (etiqueta, _) in opciones.items():
            print(f"  {clave}. {etiqueta}")
        print(f"  0. {texto_salida}")
        eleccion = consola.leer_opcion("Seleccione una opción", [*opciones, "0"])
        if eleccion == "0":
            return
        _ejecutar_accion(opciones[eleccion][1])
