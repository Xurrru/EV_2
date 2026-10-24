from views.utils import leer_numero, leer_password


class MainView:
    @staticmethod
    def mostrar_menu() -> int:
        print("\n" + "=" * 36)
        print("  SISTEMA DE GESTIÓN - MENÚ PRINCIPAL")
        print("=" * 36)
        print("1.- Gestión de Empleados")
        print("2.- Gestión de Departamentos")
        print("3.- Gestión de Proyectos")
        print("4.- Gestión de Registros de Tiempo")
        print("5.- Gestión de Administradores")
        print("6.- Informe de horas por proyecto")
        print("0.- Salir")
        print("=" * 36)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def formulario_login() -> dict:
        print("\n--- Inicio de sesión (solo administradores) ---")
        correo = input("Correo: ")
        password = leer_password("Contraseña: ")
        return {"correo": correo, "password": password}

    @staticmethod
    def mostrar_informe(encabezado: str, resumen: list[tuple]) -> None:
        print("\n" + encabezado)
        if not resumen:
            print("No hay proyectos registrados.")
        else:
            print(f"{'Proyecto':<30} {'Registros':>10} {'Horas':>10}")
            for proyecto, cantidad, horas in resumen:
                print(f"{proyecto:<30} {cantidad:>10} {horas:>10g}")
        print("-" * 52)

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"\n[SISTEMA] {mensaje}")
