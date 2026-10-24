from models.departamento_dao import DepartamentoDAO
from models.empleado import Empleado
from models.empleado_dao import EmpleadoDAO
from views.empleado_view import EmpleadoView


class EmpleadoController:
    def __init__(self):
        self.view = EmpleadoView()

    def ejecutar(self) -> None:
        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.agregar_empleado()
            elif opcion == 2:
                self.editar_empleado()
            elif opcion == 3:
                self.eliminar_empleado()
            elif opcion == 4:
                self.imprimir_empleado()
            elif opcion == 5:
                self.imprimir_empleados()
            elif opcion == 0:
                self.view.mostrar_mensaje("Saliendo de la gestión de empleados.")
                break
            else:
                self.view.mostrar_mensaje("Opción no válida.")

    def agregar_empleado(self) -> None:
        departamentos = DepartamentoDAO.obtener_todos()
        datos = self.view.formulario_nuevo_empleado(departamentos)
        try:
            departamento_seleccionado = None
            if datos['id_departamento']:
                departamento_seleccionado = DepartamentoDAO.obtener_por_id(datos['id_departamento'])
                if departamento_seleccionado is None:
                    self.view.mostrar_mensaje("El departamento indicado no existe.")
                    return

            nuevo_empleado = Empleado(
                correo=datos['correo'], password=datos['password'], nombre=datos['nombre'],
                direccion=datos['direccion'], telefono=datos['telefono'], email=datos['email'],
                fecha_contrato=datos['fecha_contrato'], salario=datos['salario'],
                departamento=departamento_seleccionado
            )
            if EmpleadoDAO.crear(nuevo_empleado):
                self.view.mostrar_mensaje(f"Empleado agregado exitosamente con ID {nuevo_empleado.id_empleado}.")
            else:
                self.view.mostrar_mensaje("No se pudo guardar el empleado.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos ingresados: {e}")

    def editar_empleado(self) -> None:
        id_empleado = self.view.solicitar_id()
        empleado = EmpleadoDAO.obtener_por_id(id_empleado)
        if not empleado:
            self.view.mostrar_mensaje("Empleado no encontrado.")
            return

        departamentos = DepartamentoDAO.obtener_todos()
        datos_nuevos = self.view.formulario_editar_empleado(empleado, departamentos)
        try:
            empleado.correo = datos_nuevos['correo']
            empleado.nombre = datos_nuevos['nombre']
            empleado.direccion = datos_nuevos['direccion']
            empleado.telefono = datos_nuevos['telefono']
            empleado.email = datos_nuevos['email']
            empleado.salario = datos_nuevos['salario']

            departamento_seleccionado = None
            if datos_nuevos['id_departamento']:
                departamento_seleccionado = DepartamentoDAO.obtener_por_id(datos_nuevos['id_departamento'])
                if departamento_seleccionado is None:
                    self.view.mostrar_mensaje("El departamento indicado no existe. No se guardaron los cambios.")
                    return
            empleado.departamento = departamento_seleccionado

            if EmpleadoDAO.actualizar(empleado):
                self.view.mostrar_mensaje("Empleado actualizado exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo actualizar el empleado.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos modificados: {e}")

    def eliminar_empleado(self) -> None:
        id_empleado = self.view.solicitar_id()
        empleado = EmpleadoDAO.obtener_por_id(id_empleado)
        if not empleado:
            self.view.mostrar_mensaje("Empleado no encontrado.")
            return

        if self.view.confirmar_eliminacion(empleado.nombre):
            if EmpleadoDAO.eliminar(id_empleado):
                self.view.mostrar_mensaje("Empleado eliminado exitosamente.")
            else:
                self.view.mostrar_mensaje("No se pudo eliminar el empleado.")
        else:
            self.view.mostrar_mensaje("Operación cancelada.")

    def imprimir_empleado(self) -> None:
        id_empleado = self.view.solicitar_id()
        empleado = EmpleadoDAO.obtener_por_id(id_empleado)
        if empleado:
            self.view.mostrar_empleado(empleado)
        else:
            self.view.mostrar_mensaje("Empleado no encontrado.")

    def imprimir_empleados(self) -> None:
        self.view.mostrar_lista_empleados(EmpleadoDAO.obtener_todos())
