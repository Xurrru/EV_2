from views.utils import (leer_numero, leer_decimal, leer_decimal_o_mantener, leer_o_mantener,
                         leer_password_confirmada, confirmar)
from models.departamento import Departamento
from models.empleado import Empleado


class EmpleadoView:
    @staticmethod
    def mostrar_menu() -> int:
        print("\n" + "-" * 30)
        print("   GESTIÓN DE EMPLEADOS")
        print("-" * 30)
        print("1.- Agregar empleado")
        print("2.- Editar empleado")
        print("3.- Eliminar empleado")
        print("4.- Imprimir un empleado")
        print("5.- Imprimir todos los empleados")
        print("0.- Volver al menú principal")
        print("-" * 30)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def _mostrar_departamentos(departamentos: list[Departamento]) -> None:
        print("\nDepartamentos disponibles:")
        if departamentos:
            for d in departamentos:
                print(f"{d.id_departamento}.- {d.nombre}")
        else:
            print("No hay departamentos registrados.")

    @staticmethod
    def formulario_nuevo_empleado(departamentos: list[Departamento]) -> dict:
        print("\n--- Agregar Nuevo Empleado ---")
        correo = input("Correo de acceso (login): ")
        password = leer_password_confirmada("Contraseña (mínimo 8 caracteres, letras y números): ")
        nombre = input("Nombre completo: ")
        direccion = input("Dirección: ")
        telefono = input("Teléfono: ")
        email = input("Email de contacto: ")
        fecha_contrato = input("Fecha de contrato (AAAA-MM-DD): ")
        salario = leer_decimal("Salario mensual (solo números, ej: 900000): ")
        EmpleadoView._mostrar_departamentos(departamentos)
        opcion = leer_numero("Seleccione el ID del departamento (o 0 para ninguno): ")
        return {
            "correo": correo, "password": password, "nombre": nombre, "direccion": direccion,
            "telefono": telefono, "email": email, "fecha_contrato": fecha_contrato, "salario": salario,
            "id_departamento": opcion if opcion > 0 else None
        }

    @staticmethod
    def solicitar_id() -> int:
        return leer_numero("Ingrese el ID del empleado: ")

    @staticmethod
    def mostrar_empleado(empleado: Empleado) -> None:
        print("\n--- Datos del Empleado ---")
        print(empleado)
        print(f"Dirección: {empleado.direccion} | Teléfono: {empleado.telefono} "
              f"| Email: {empleado.email} | Contrato: {empleado.fecha_contrato}")
        print("-" * 30)

    @staticmethod
    def mostrar_lista_empleados(empleados: list[Empleado]) -> None:
        print("\n--- Lista de Empleados ---")
        if not empleados:
            print("No hay empleados registrados.")
        else:
            for e in empleados:
                print(e)
        print("-" * 30)

    @staticmethod
    def formulario_editar_empleado(empleado: Empleado, departamentos: list[Departamento]) -> dict:
        print(f"\n--- Editando Empleado {empleado.nombre} ---")
        print("Deje en blanco si no desea modificar el campo.")
        correo = leer_o_mantener(f"Correo de acceso actual ({empleado.correo}): ", empleado.correo)
        nombre = leer_o_mantener(f"Nombre actual ({empleado.nombre}): ", empleado.nombre)
        direccion = leer_o_mantener(f"Dirección actual ({empleado.direccion}): ", empleado.direccion)
        telefono = leer_o_mantener(f"Teléfono actual ({empleado.telefono}): ", empleado.telefono)
        email = leer_o_mantener(f"Email actual ({empleado.email}): ", empleado.email)
        salario = leer_decimal_o_mantener(f"Salario actual ({empleado.salario:g}): ", empleado.salario)
        EmpleadoView._mostrar_departamentos(departamentos)
        actual = empleado.departamento.id_departamento if empleado.departamento else 0
        opcion = leer_o_mantener(
            f"Nuevo ID de departamento (actual: {actual or 'ninguno'}, Enter = mantener, 0 = quitar): ", str(actual)
        )
        try:
            id_departamento = int(opcion)
        except ValueError:
            print("ID de departamento no válido; se mantiene el actual.")
            id_departamento = actual
        return {
            "correo": correo, "nombre": nombre, "direccion": direccion, "telefono": telefono,
            "email": email, "salario": salario,
            "id_departamento": id_departamento if id_departamento > 0 else None
        }

    @staticmethod
    def confirmar_eliminacion(nombre: str) -> bool:
        return confirmar(f"¿Está seguro que desea eliminar al empleado {nombre}? "
                         f"Se borrarán también sus registros de tiempo.")

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"[EMPLEADOS] {mensaje}")
