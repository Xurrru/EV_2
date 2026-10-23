from __future__ import annotations

from models.Usuarios import Empleado, Usuario
from models.validaciones import validador_correo, validar_password
from repositories.usuario_repository import RepositorioUsuario
from views import consola


class ControladorCuenta:
    """Autenticación y gestión de la cuenta de quien tiene la sesión abierta."""

    MAX_INTENTOS = 3

    def __init__(self, repositorio: RepositorioUsuario) -> None:
        self._repo = repositorio

    def iniciar_sesion(self) -> Usuario | None:
        """Devuelve el usuario autenticado o ``None`` tras agotar los intentos.

        El mensaje de error es el mismo si falla el correo o la contraseña,
        para no revelar qué correos existen.
        """
        consola.mostrar_titulo("INICIO DE SESIÓN")
        for intento in range(1, self.MAX_INTENTOS + 1):
            correo = consola.leer_validado("Correo", validador_correo("correo"))
            clave = consola.leer_password("Contraseña")
            usuario = self._repo.obtener_por_correo(correo)
            if usuario is not None and usuario.verificar_contrasena(clave):
                consola.mostrar_exito(f"Bienvenido/a, {usuario.describir()}.")
                return usuario
            restantes = self.MAX_INTENTOS - intento
            consola.mostrar_error(f"Credenciales incorrectas. Intentos restantes: {restantes}.")
        return None

    def cambiar_contrasena(self, usuario: Usuario) -> None:
        actual = consola.leer_password("Contraseña actual")
        nueva = consola.leer_password("Nueva contraseña (mín. 8, letras y números)", validar_password, confirmar=True)
        usuario.cambiar_contrasena(actual, nueva)
        self._repo.actualizar(usuario)
        consola.mostrar_exito("Contraseña actualizada.")

    @staticmethod
    def ver_perfil(usuario: Usuario) -> None:
        consola.mostrar_titulo("MI PERFIL")
        print(f"  Rol: {usuario.rol}\n  Correo de acceso: {usuario.correo}")
        if isinstance(usuario, Empleado):
            departamento = usuario.departamento.nombre if usuario.departamento else "Sin asignar"
            print(
                f"  Nombre: {usuario.nombre}\n  Dirección: {usuario.direccion}\n  Teléfono: {usuario.telefono}\n"
                f"  Email de contacto: {usuario.email}\n  Fecha de contrato: {usuario.fecha_contrato}\n"
                f"  Departamento: {departamento}"
            )
