from models.empleado_dao import EmpleadoDAO
from models.proyecto_dao import ProyectoDAO
from models.registro_tiempo import Registro_Tiempo
from models.registro_tiempo_dao import RegistroTiempoDAO
from views.registro_tiempo_view import RegistroTiempoView


class RegistroTiempoController:
    def __init__(self):
        self.view = RegistroTiempoView()

    def ejecutar(self) -> None:
        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.agregar_registro()
            elif opcion == 2:
                self.editar_registro()
            elif opcion == 3:
                self.eliminar_registro()
            elif opcion == 4:
                self.imprimir_registro()
            elif opcion == 5:
                self.imprimir_registros()
            elif opcion == 6:
                self.imprimir_registros_de_empleado()
            elif opcion == 0:
                self.view.mostrar_mensaje("Saliendo de la gestión de registros de tiempo.")
                break
            else:
                self.view.mostrar_mensaje("Opción no válida.")

    def agregar_registro(self) -> None:
        empleados = EmpleadoDAO.obtener_todos()
        proyectos = ProyectoDAO.obtener_todos()
        if not empleados or not proyectos:
            self.view.mostrar_mensaje("Primero debe existir al menos un empleado y un proyecto.")
            return

        datos = self.view.formulario_nuevo_registro(empleados, proyectos)
        try:
            empleado = EmpleadoDAO.obtener_por_id(datos['id_empleado'])
            proyecto = ProyectoDAO.obtener_por_id(datos['id_proyecto'])
            if empleado is None or proyecto is None:
                self.view.mostrar_mensaje("El empleado o el proyecto indicado no existe.")
                return

            nuevo_registro = Registro_Tiempo(datos['fecha'], datos['horas'], datos['descripcion'],
                                             empleado, proyecto)
            if RegistroTiempoDAO.crear(nuevo_registro):
                empleado.registrar_horas(nuevo_registro)
                self.view.mostrar_mensaje(f"Registro agregado exitosamente con ID {nuevo_registro.id_registro}.")
            else:
                self.view.mostrar_mensaje("No se pudo guardar el registro.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos ingresados: {e}")

    def editar_registro(self) -> None:
        id_registro = self.view.solicitar_id()
        registro = RegistroTiempoDAO.obtener_por_id(id_registro)
        if not registro:
            self.view.mostrar_mensaje("Registro no encontrado.")
            return

        datos_nuevos = self.view.formulario_editar_registro(registro)
        try:
            registro.modificar(datos_nuevos['horas'], datos_nuevos['descripcion'])
            if RegistroTiempoDAO.actualizar(registro):
                self.view.mostrar_mensaje("Registro actualizado exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo actualizar el registro.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos modificados: {e}")

    def eliminar_registro(self) -> None:
        id_registro = self.view.solicitar_id()
        registro = RegistroTiempoDAO.obtener_por_id(id_registro)
        if not registro:
            self.view.mostrar_mensaje("Registro no encontrado.")
            return

        if self.view.confirmar_eliminacion(registro):
            if RegistroTiempoDAO.eliminar(id_registro):
                self.view.mostrar_mensaje("Registro eliminado exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo eliminar el registro.")
        else:
            self.view.mostrar_mensaje("Operación cancelada.")

    def imprimir_registro(self) -> None:
        id_registro = self.view.solicitar_id()
        registro = RegistroTiempoDAO.obtener_por_id(id_registro)
        if registro:
            self.view.mostrar_registro(registro)
        else:
            self.view.mostrar_mensaje("Registro no encontrado.")

    def imprimir_registros(self) -> None:
        self.view.mostrar_lista_registros(RegistroTiempoDAO.obtener_todos())

    def imprimir_registros_de_empleado(self) -> None:
        id_empleado = self.view.solicitar_id_empleado()
        if EmpleadoDAO.obtener_por_id(id_empleado) is None:
            self.view.mostrar_mensaje("Empleado no encontrado.")
            return
        self.view.mostrar_lista_registros(RegistroTiempoDAO.obtener_por_empleado(id_empleado))
