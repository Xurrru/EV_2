from models.administrador import Administrador
from models.administrador_dao import AdministradorDAO
from views.administrador_view import AdministradorView


class AdministradorController:
    def __init__(self, admin_actual: Administrador | None = None):
        self.view = AdministradorView()
        self.admin_actual = admin_actual  # quien tiene la sesión abierta (None en la primera ejecución)

    def ejecutar(self) -> None:
        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.agregar_administrador()
            elif opcion == 2:
                self.editar_administrador()
            elif opcion == 3:
                self.eliminar_administrador()
            elif opcion == 4:
                self.imprimir_administrador()
            elif opcion == 5:
                self.imprimir_administradores()
            elif opcion == 6:
                self.cambiar_password()
            elif opcion == 0:
                self.view.mostrar_mensaje("Saliendo de la gestión de administradores.")
                break
            else:
                self.view.mostrar_mensaje("Opción no válida.")

    def agregar_administrador(self) -> bool:
        datos = self.view.formulario_nuevo_administrador()
        try:
            nuevo_admin = Administrador(datos['correo'], datos['password'])
            if AdministradorDAO.crear(nuevo_admin):
                self.view.mostrar_mensaje(f"Administrador agregado exitosamente con ID {nuevo_admin.id_usuario}.")
                return True
            self.view.mostrar_mensaje("No se pudo guardar el administrador.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos ingresados: {e}")
        return False

    def editar_administrador(self) -> None:
        id_usuario = self.view.solicitar_id()
        administrador = AdministradorDAO.obtener_por_id(id_usuario)
        if not administrador:
            self.view.mostrar_mensaje("Administrador no encontrado.")
            return

        datos_nuevos = self.view.formulario_editar_administrador(administrador)
        try:
            administrador.correo = datos_nuevos['correo']
            if AdministradorDAO.actualizar(administrador):
                self.view.mostrar_mensaje("Administrador actualizado exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo actualizar el administrador.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos modificados: {e}")

    def eliminar_administrador(self) -> None:
        id_usuario = self.view.solicitar_id()
        administrador = AdministradorDAO.obtener_por_id(id_usuario)
        if not administrador:
            self.view.mostrar_mensaje("Administrador no encontrado.")
            return

        # Reglas para no quedarse sin acceso al sistema
        if self.admin_actual is not None and administrador.id_usuario == self.admin_actual.id_usuario:
            self.view.mostrar_mensaje("No puede eliminar su propia cuenta mientras tiene la sesión abierta.")
            return
        if AdministradorDAO.contar() <= 1:
            self.view.mostrar_mensaje("Debe existir al menos un administrador en el sistema.")
            return

        if self.view.confirmar_eliminacion(administrador.correo):
            if AdministradorDAO.eliminar(id_usuario):
                self.view.mostrar_mensaje("Administrador eliminado exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo eliminar el administrador.")
        else:
            self.view.mostrar_mensaje("Operación cancelada.")

    def imprimir_administrador(self) -> None:
        id_usuario = self.view.solicitar_id()
        administrador = AdministradorDAO.obtener_por_id(id_usuario)
        if administrador:
            self.view.mostrar_administrador(administrador)
        else:
            self.view.mostrar_mensaje("Administrador no encontrado.")

    def imprimir_administradores(self) -> None:
        self.view.mostrar_lista_administradores(AdministradorDAO.obtener_todos())

    def cambiar_password(self) -> None:
        if self.admin_actual is None:
            self.view.mostrar_mensaje("No hay una sesión abierta.")
            return
        datos = self.view.formulario_cambiar_password()
        try:
            self.admin_actual.cambiar_password(datos['actual'], datos['nueva'])
            if AdministradorDAO.actualizar(self.admin_actual):
                self.view.mostrar_mensaje("Contraseña actualizada exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo guardar la nueva contraseña.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error: {e}")
