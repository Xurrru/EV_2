from models.departamento import Departamento
from models.departamento_dao import DepartamentoDAO
from views.departamento_view import DepartamentoView


class DepartamentoController:
    def __init__(self):
        self.view = DepartamentoView()

    def ejecutar(self) -> None:
        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.agregar_departamento()
            elif opcion == 2:
                self.editar_departamento()
            elif opcion == 3:
                self.eliminar_departamento()
            elif opcion == 4:
                self.imprimir_departamento()
            elif opcion == 5:
                self.imprimir_departamentos()
            elif opcion == 0:
                self.view.mostrar_mensaje("Saliendo de la gestión de departamentos.")
                break
            else:
                self.view.mostrar_mensaje("Opción no válida.")

    def agregar_departamento(self) -> None:
        datos = self.view.formulario_nuevo_departamento()
        try:
            nuevo_departamento = Departamento(datos['nombre'], datos['gerente'])
            if DepartamentoDAO.crear(nuevo_departamento):
                self.view.mostrar_mensaje(
                    f"Departamento agregado exitosamente con ID {nuevo_departamento.id_departamento}.")
            else:
                self.view.mostrar_mensaje("No se pudo guardar el departamento.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos ingresados: {e}")

    def editar_departamento(self) -> None:
        id_depto = self.view.solicitar_id()
        departamento = DepartamentoDAO.obtener_por_id(id_depto)
        if not departamento:
            self.view.mostrar_mensaje("Departamento no encontrado.")
            return

        datos_nuevos = self.view.formulario_editar_departamento(departamento)
        try:
            departamento.editar(datos_nuevos['nombre'], datos_nuevos['gerente'])
            if DepartamentoDAO.actualizar(departamento):
                self.view.mostrar_mensaje("Departamento actualizado exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo actualizar el departamento.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos modificados: {e}")

    def eliminar_departamento(self) -> None:
        id_depto = self.view.solicitar_id()
        departamento = DepartamentoDAO.obtener_por_id(id_depto)
        if not departamento:
            self.view.mostrar_mensaje("Departamento no encontrado.")
            return

        cantidad = DepartamentoDAO.contar_empleados(id_depto)
        if self.view.confirmar_eliminacion(departamento.nombre, cantidad):
            if DepartamentoDAO.eliminar(id_depto):
                self.view.mostrar_mensaje("Departamento eliminado exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo eliminar el departamento.")
        else:
            self.view.mostrar_mensaje("Operación cancelada.")

    def imprimir_departamento(self) -> None:
        id_depto = self.view.solicitar_id()
        departamento = DepartamentoDAO.obtener_por_id(id_depto)
        if departamento:
            self.view.mostrar_departamento(departamento)
        else:
            self.view.mostrar_mensaje("Departamento no encontrado.")

    def imprimir_departamentos(self) -> None:
        self.view.mostrar_lista_departamentos(DepartamentoDAO.obtener_todos())
