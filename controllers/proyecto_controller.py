from models.proyecto import Proyecto
from models.proyecto_dao import ProyectoDAO
from views.proyecto_view import ProyectoView


class ProyectoController:
    def __init__(self):
        self.view = ProyectoView()

    def ejecutar(self) -> None:
        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.agregar_proyecto()
            elif opcion == 2:
                self.editar_proyecto()
            elif opcion == 3:
                self.eliminar_proyecto()
            elif opcion == 4:
                self.imprimir_proyecto()
            elif opcion == 5:
                self.imprimir_proyectos()
            elif opcion == 0:
                self.view.mostrar_mensaje("Saliendo de la gestión de proyectos.")
                break
            else:
                self.view.mostrar_mensaje("Opción no válida.")

    def agregar_proyecto(self) -> None:
        datos = self.view.formulario_nuevo_proyecto()
        try:
            nuevo_proyecto = Proyecto(datos['nombre'], datos['descripcion'], datos['fecha_inicio'])
            if ProyectoDAO.crear(nuevo_proyecto):
                self.view.mostrar_mensaje(f"Proyecto agregado exitosamente con ID {nuevo_proyecto.id_proyecto}.")
            else:
                self.view.mostrar_mensaje("No se pudo guardar el proyecto.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos ingresados: {e}")

    def editar_proyecto(self) -> None:
        id_proyecto = self.view.solicitar_id()
        proyecto = ProyectoDAO.obtener_por_id(id_proyecto)
        if not proyecto:
            self.view.mostrar_mensaje("Proyecto no encontrado.")
            return

        datos_nuevos = self.view.formulario_editar_proyecto(proyecto)
        try:
            proyecto.editar(datos_nuevos['nombre'], datos_nuevos['descripcion'])
            if ProyectoDAO.actualizar(proyecto):
                self.view.mostrar_mensaje("Proyecto actualizado exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo actualizar el proyecto.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos modificados: {e}")

    def eliminar_proyecto(self) -> None:
        id_proyecto = self.view.solicitar_id()
        proyecto = ProyectoDAO.obtener_por_id(id_proyecto)
        if not proyecto:
            self.view.mostrar_mensaje("Proyecto no encontrado.")
            return

        cantidad = ProyectoDAO.contar_registros(id_proyecto)
        if self.view.confirmar_eliminacion(proyecto.nombre, cantidad):
            if ProyectoDAO.eliminar(id_proyecto):
                self.view.mostrar_mensaje("Proyecto eliminado exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo eliminar el proyecto.")
        else:
            self.view.mostrar_mensaje("Operación cancelada.")

    def imprimir_proyecto(self) -> None:
        id_proyecto = self.view.solicitar_id()
        proyecto = ProyectoDAO.obtener_por_id(id_proyecto)
        if proyecto:
            self.view.mostrar_proyecto(proyecto)
        else:
            self.view.mostrar_mensaje("Proyecto no encontrado.")

    def imprimir_proyectos(self) -> None:
        self.view.mostrar_lista_proyectos(ProyectoDAO.obtener_todos())
