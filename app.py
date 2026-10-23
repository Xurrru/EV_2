"""Punto de entrada del Sistema de Gestión de Empleados (EcoTech Solutions).

Ejecutar desde la carpeta del proyecto:  python app.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from config.Base_Datos import Database
from config.excepciones import ErrorBaseDatos, OperacionCancelada
from controllers.administrador_controller import ControladorAdministrador
from controllers.cuenta_controller import ControladorCuenta
from controllers.departamento_controller import ControladorDepartamento
from controllers.empleado_controller import ControladorEmpleado
from controllers.proyecto_controller import ControladorProyecto
from controllers.registro_tiempo_controller import ControladorRegistroTiempo
from models.Usuarios import Administrador, Usuario
from repositories.departamento_repository import RepositorioDepartamento
from repositories.proyecto_repository import RepositorioProyecto
from repositories.registro_tiempo_repository import RepositorioRegistroTiempo
from repositories.usuario_repository import RepositorioUsuario
from views import consola, menus


def configurar_log() -> None:
    """Los errores técnicos van a ``sistema.log``; el usuario solo ve mensajes claros."""
    try:
        logging.basicConfig(
            filename=Path(__file__).resolve().parent / "sistema.log",
            level=logging.ERROR,
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            encoding="utf-8",
        )
    except OSError:
        logging.disable(logging.CRITICAL)  # sin permisos de escritura: la app sigue funcionando


class Aplicacion:
    """Ensambla las capas: repositorios (BD) -> controladores (lógica) -> menús (vista)."""

    def __init__(self) -> None:
        self._db = Database()
        self._repo_departamentos = RepositorioDepartamento()
        self._repo_proyectos = RepositorioProyecto()
        self._repo_usuarios = RepositorioUsuario(self._repo_departamentos)
        self._repo_registros = RepositorioRegistroTiempo(self._repo_usuarios, self._repo_proyectos)
        self._cuenta = ControladorCuenta(self._repo_usuarios)

    # --- Arranque ---

    def _preparar_primer_administrador(self) -> None:
        """Si la base está vacía, obliga a crear el primer administrador antes del login."""
        if self._repo_usuarios.contar_administradores() > 0:
            return
        consola.mostrar_titulo("PRIMERA EJECUCIÓN")
        consola.mostrar_info("No existen administradores. Cree el primero para poder ingresar al sistema.")
        controlador = ControladorAdministrador(self._repo_usuarios, sesion=None)
        while self._repo_usuarios.contar_administradores() == 0:
            try:
                controlador.crear()
            except ValueError as error:  # dato inválido: se vuelve a pedir
                consola.mostrar_error(str(error))

    # --- Menús ---

    def _menu_administrador(self, admin: Administrador) -> None:
        departamentos = ControladorDepartamento(self._repo_departamentos)
        proyectos = ControladorProyecto(self._repo_proyectos)
        empleados = ControladorEmpleado(self._repo_usuarios, self._repo_departamentos)
        administradores = ControladorAdministrador(self._repo_usuarios, admin)
        registros = ControladorRegistroTiempo(self._repo_registros, self._repo_usuarios, self._repo_proyectos, admin)

        def submenu(entidad: str, titulo: str, controlador) -> None:
            consola.mostrar_info(admin.gestionar(entidad))
            menus.ejecutar_menu(titulo, controlador.opciones_menu())

        opciones = {
            "1": ("Departamentos", lambda: submenu("departamentos", "DEPARTAMENTOS", departamentos)),
            "2": ("Proyectos", lambda: submenu("proyectos", "PROYECTOS", proyectos)),
            "3": ("Empleados", lambda: submenu("empleados", "EMPLEADOS", empleados)),
            "4": ("Administradores", lambda: submenu("administradores", "ADMINISTRADORES", administradores)),
            "5": ("Registros de tiempo", lambda: submenu("registros de tiempo", "REGISTROS DE TIEMPO", registros)),
            "6": ("Informe de horas por proyecto", registros.informe),
            "7": ("Mi perfil", lambda: self._cuenta.ver_perfil(admin)),
            "8": ("Cambiar mi contraseña", lambda: self._cuenta.cambiar_contrasena(admin)),
        }
        menus.ejecutar_menu(f"MENÚ ADMINISTRADOR - {admin.correo}", opciones, "Cerrar sesión")

    def _menu_empleado(self, empleado: Usuario) -> None:
        registros = ControladorRegistroTiempo(self._repo_registros, self._repo_usuarios, self._repo_proyectos, empleado)
        opciones = {
            "1": ("Registrar mis horas", registros.crear),
            "2": ("Ver mis registros", registros.listar),
            "3": ("Modificar un registro", registros.actualizar),
            "4": ("Eliminar un registro", registros.eliminar),
            "5": ("Mi perfil", lambda: self._cuenta.ver_perfil(empleado)),
            "6": ("Cambiar mi contraseña", lambda: self._cuenta.cambiar_contrasena(empleado)),
        }
        menus.ejecutar_menu(f"MENÚ EMPLEADO - {empleado.correo}", opciones, "Cerrar sesión")

    # --- Ejecución ---

    def ejecutar(self) -> int:
        try:
            self._db.init_db()
            self._preparar_primer_administrador()
            sesion = self._cuenta.iniciar_sesion()
            if sesion is None:
                consola.mostrar_error("Demasiados intentos fallidos. El programa se cerrará.")
                return 1
            if isinstance(sesion, Administrador):
                self._menu_administrador(sesion)
            else:
                self._menu_empleado(sesion)
        except ErrorBaseDatos as error:
            consola.mostrar_error(f"No fue posible continuar por un problema con la base de datos: {error}")
            return 1
        except (OperacionCancelada, KeyboardInterrupt, EOFError):
            pass
        consola.mostrar_info("Sesión finalizada. ¡Hasta pronto!")
        return 0


def main() -> int:
    configurar_log()
    return Aplicacion().ejecutar()


if __name__ == "__main__":
    sys.exit(main())
