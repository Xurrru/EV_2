from views.utils import leer_numero, leer_o_mantener, confirmar
from models.proyecto import Proyecto


class ProyectoView:
    @staticmethod
    def mostrar_menu() -> int:
        print("\n" + "-" * 30)
        print("   GESTIÓN DE PROYECTOS")
        print("-" * 30)
        print("1.- Agregar proyecto")
        print("2.- Editar proyecto")
        print("3.- Eliminar proyecto")
        print("4.- Imprimir un proyecto")
        print("5.- Imprimir todos los proyectos")
        print("0.- Volver al menú principal")
        print("-" * 30)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def formulario_nuevo_proyecto() -> dict:
        print("\n--- Agregar Nuevo Proyecto ---")
        nombre = input("Ingrese el nombre del proyecto: ")
        descripcion = input("Ingrese la descripción: ")
        fecha_inicio = input("Ingrese la fecha de inicio (AAAA-MM-DD): ")
        return {"nombre": nombre, "descripcion": descripcion, "fecha_inicio": fecha_inicio}

    @staticmethod
    def solicitar_id() -> int:
        return leer_numero("Ingrese el ID del proyecto: ")

    @staticmethod
    def mostrar_proyecto(proyecto: Proyecto) -> None:
        print("\n--- Datos del Proyecto ---")
        print(proyecto)
        print("-" * 30)

    @staticmethod
    def mostrar_lista_proyectos(proyectos: list[Proyecto]) -> None:
        print("\n--- Lista de Proyectos ---")
        if not proyectos:
            print("No hay proyectos registrados.")
        else:
            for p in proyectos:
                print(p)
        print("-" * 30)

    @staticmethod
    def formulario_editar_proyecto(proyecto: Proyecto) -> dict:
        print(f"\n--- Editando Proyecto [ID: {proyecto.id_proyecto}] ---")
        print("Deje en blanco si no desea modificar el campo.")
        nuevo_nombre = leer_o_mantener(f"Nombre actual ({proyecto.nombre}): ", proyecto.nombre)
        nueva_descripcion = leer_o_mantener(f"Descripción actual ({proyecto.descripcion}): ", proyecto.descripcion)
        return {"nombre": nuevo_nombre, "descripcion": nueva_descripcion}

    @staticmethod
    def confirmar_eliminacion(nombre: str, cantidad_registros: int) -> bool:
        aviso = f" Se eliminarán también {cantidad_registros} registro(s) de tiempo." if cantidad_registros else ""
        return confirmar(f"¿Está seguro que desea eliminar el proyecto '{nombre}'?{aviso}")

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"[PROYECTOS] {mensaje}")
