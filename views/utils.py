import getpass


def leer_numero(mensaje: str) -> int:
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Error: Debe ingresar un número entero válido.")


def leer_decimal(mensaje: str) -> float:
    while True:
        texto = input(mensaje).strip()
        if "," in texto:
            print("Error: use punto como separador decimal y no use separadores de miles (ej: 7.5 o 900000).")
            continue
        try:
            return float(texto)
        except ValueError:
            print("Error: Debe ingresar un número válido.")


def leer_o_mantener(mensaje: str, valor_actual: str) -> str:
    """Si el usuario presiona Enter sin escribir nada, se conserva el valor actual."""
    texto = input(mensaje)
    return texto if texto.strip() else valor_actual


def leer_decimal_o_mantener(mensaje: str, valor_actual: float) -> float:
    while True:
        texto = input(mensaje).strip()
        if not texto:
            return valor_actual
        if "," in texto:
            print("Error: use punto como separador decimal y no use separadores de miles.")
            continue
        try:
            return float(texto)
        except ValueError:
            print("Error: Debe ingresar un número válido.")


def leer_password(mensaje: str) -> str:
    """Lee la contraseña sin mostrarla en pantalla."""
    return getpass.getpass(mensaje)


def leer_password_confirmada(mensaje: str) -> str:
    while True:
        password = getpass.getpass(mensaje)
        if password == getpass.getpass("Repita la contraseña: "):
            return password
        print("Error: las contraseñas no coinciden.")


def confirmar(mensaje: str) -> bool:
    while True:
        resp = input(f"{mensaje} (si/no): ").strip().lower()
        if resp in ("si", "no"):
            return resp == "si"
        print("Respuesta no válida. Por favor, ingrese 'si' o 'no'.")
