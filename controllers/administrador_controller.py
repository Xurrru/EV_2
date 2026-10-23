from __future__ import annotations

from config.excepciones import OperacionCancelada
from controllers.base_controller import ControladorCRUD
from models.Usuarios import Administrador, Usuario
from models.validaciones import validador_correo, validar_password
from repositories.usuario_repository import RepositorioUsuario
from views import consola


class ControladorAdministrador(ControladorCRUD):
    """CRUD de administradores, con reglas para no dejar el sistema sin acceso."""

    def __init__(self, repositorio: RepositorioUsuario, sesion: Usuario | None) -> None:
        self._repo = repositorio
        self._sesion = sesion

    def _seleccionar(self) -> Administrador:
        return consola.elegir("Administradores:", self._repo.listar_administradores(), lambda a: a.correo)

    def listar(self) -> None:
        consola.mostrar_tabla(
            ("ID", "Correo"), [(a.id_usuario, a.correo) for a in self._repo.listar_administradores()]
        )

    def crear(self) -> None:
        consola.mostrar_info("Escriba /cancelar para abortar.")
        correo = consola.leer_validado("Correo del administrador", validador_correo("correo"))
        password = consola.leer_password("Contraseña (mín. 8, letras y números)", validar_password, confirmar=True)
        administrador = Administrador(None, correo, password)
        self._repo.crear(administrador)
        consola.mostrar_exito(f"Administrador '{administrador.correo}' creado.")
        consola.mostrar_info(administrador.generar_informe())

    def actualizar(self) -> None:
        administrador = self._seleccionar()
        consola.mostrar_info("Presione Enter para conservar el valor actual.")
        administrador.correo = consola.leer_validado("Nuevo correo", validador_correo("correo"), administrador.correo)
        self._repo.actualizar(administrador)
        consola.mostrar_exito("Administrador actualizado.")

    def eliminar(self) -> None:
        administrador = self._seleccionar()
        if self._sesion is not None and administrador.id_usuario == self._sesion.id_usuario:
            raise ValueError("No puede eliminar su propia cuenta mientras tiene la sesión abierta.")
        if self._repo.contar_administradores() <= 1:
            raise ValueError("Debe existir al menos un administrador en el sistema.")
        if not consola.confirmar(f"¿Eliminar al administrador '{administrador.correo}'?"):
            raise OperacionCancelada()
        self._repo.eliminar(administrador.id_usuario)
        consola.mostrar_exito("Administrador eliminado.")
