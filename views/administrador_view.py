from views.utils import leer_numero, leer_o_mantener, leer_password, leer_password_confirmada, confirmar
from models.administrador import Administrador


class AdministradorView:
    @staticmethod
    def mostrar_menu() -> int:
        print("\n" + "-" * 30)
        print("   GESTIÓN DE ADMINISTRADORES")
        print("-" * 30)
        print("1.- Agregar administrador")
        print("2.- Editar correo de un administrador")
        print("3.- Eliminar administrador")
        print("4.- Imprimir un administrador")
        print("5.- Imprimir todos los administradores")
        print("6.- Cambiar mi contraseña")
        print("0.- Volver al menú principal")
        print("-" * 30)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def formulario_nuevo_administrador() -> dict:
        print("\n--- Agregar Nuevo Administrador ---")
        correo = input("Correo del administrador: ")
        password = leer_password_confirmada("Contraseña (mínimo 8 caracteres, letras y números): ")
        return {"correo": correo, "password": password}

    @staticmethod
    def solicitar_id() -> int:
        return leer_numero("Ingrese el ID del administrador: ")

    @staticmethod
    def mostrar_administrador(administrador: Administrador) -> None:
        print("\n--- Datos del Administrador ---")
        print(administrador)
        print("-" * 30)

    @staticmethod
    def mostrar_lista_administradores(administradores: list[Administrador]) -> None:
        print("\n--- Lista de Administradores ---")
        if not administradores:
            print("No hay administradores registrados.")
        else:
            for a in administradores:
                print(a)
        print("-" * 30)

    @staticmethod
    def formulario_editar_administrador(administrador: Administrador) -> dict:
        print(f"\n--- Editando Administrador [ID: {administrador.id_usuario}] ---")
        correo = leer_o_mantener(f"Correo actual ({administrador.correo}): ", administrador.correo)
        return {"correo": correo}

    @staticmethod
    def formulario_cambiar_password() -> dict:
        print("\n--- Cambiar contraseña ---")
        actual = leer_password("Contraseña actual: ")
        nueva = leer_password_confirmada("Nueva contraseña (mínimo 8 caracteres, letras y números): ")
        return {"actual": actual, "nueva": nueva}

    @staticmethod
    def confirmar_eliminacion(correo: str) -> bool:
        return confirmar(f"¿Está seguro que desea eliminar al administrador {correo}?")

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"[ADMINISTRADORES] {mensaje}")
