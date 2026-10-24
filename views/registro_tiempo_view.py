from datetime import date

from views.utils import leer_numero, leer_decimal, leer_decimal_o_mantener, leer_o_mantener, confirmar
from models.empleado import Empleado
from models.proyecto import Proyecto
from models.registro_tiempo import Registro_Tiempo


class RegistroTiempoView:
    @staticmethod
    def mostrar_menu() -> int:
        print("\n" + "-" * 30)
        print("  GESTIÓN DE REGISTROS DE TIEMPO")
        print("-" * 30)
        print("1.- Agregar registro de tiempo")
        print("2.- Editar registro de tiempo")
        print("3.- Eliminar registro de tiempo")
        print("4.- Imprimir un registro")
        print("5.- Imprimir todos los registros")
        print("6.- Imprimir los registros de un empleado")
        print("0.- Volver al menú principal")
        print("-" * 30)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def formulario_nuevo_registro(empleados: list[Empleado], proyectos: list[Proyecto]) -> dict:
        print("\n--- Agregar Registro de Tiempo ---")
        print("\nEmpleados disponibles:")
        for e in empleados:
            print(f"{e.id_empleado}.- {e.nombre}")
        id_empleado = leer_numero("Seleccione el ID del empleado: ")
        print("\nProyectos disponibles:")
        for p in proyectos:
            print(f"{p.id_proyecto}.- {p.nombre}")
        id_proyecto = leer_numero("Seleccione el ID del proyecto: ")
        hoy = date.today().isoformat()
        fecha = leer_o_mantener(f"Fecha (AAAA-MM-DD, Enter = hoy {hoy}): ", hoy)
        horas = leer_decimal("Horas trabajadas (ej: 7.5): ")
        descripcion = input("Descripción de la tarea: ")
        return {"id_empleado": id_empleado, "id_proyecto": id_proyecto, "fecha": fecha,
                "horas": horas, "descripcion": descripcion}

    @staticmethod
    def solicitar_id() -> int:
        return leer_numero("Ingrese el ID del registro: ")

    @staticmethod
    def solicitar_id_empleado() -> int:
        return leer_numero("Ingrese el ID del empleado: ")

    @staticmethod
    def mostrar_registro(registro: Registro_Tiempo) -> None:
        print("\n--- Datos del Registro ---")
        print(registro)
        print("-" * 30)

    @staticmethod
    def mostrar_lista_registros(registros: list[Registro_Tiempo]) -> None:
        print("\n--- Lista de Registros de Tiempo ---")
        if not registros:
            print("No hay registros de tiempo.")
        else:
            for r in registros:
                print(r)
            print(f"Total de horas listadas: {sum(r.horas for r in registros):g}")
        print("-" * 30)

    @staticmethod
    def formulario_editar_registro(registro: Registro_Tiempo) -> dict:
        print(f"\n--- Editando Registro [ID: {registro.id_registro}] ---")
        print("Deje en blanco si no desea modificar el campo.")
        horas = leer_decimal_o_mantener(f"Horas actuales ({registro.horas:g}): ", registro.horas)
        descripcion = leer_o_mantener(f"Descripción actual ({registro.descripcion}): ", registro.descripcion)
        return {"horas": horas, "descripcion": descripcion}

    @staticmethod
    def confirmar_eliminacion(registro: Registro_Tiempo) -> bool:
        return confirmar(f"¿Está seguro que desea eliminar el registro del {registro.fecha} "
                         f"({registro.horas:g} h)?")

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"[REGISTROS] {mensaje}")
