from config.database import Database
from controllers.main_controller import MainController


def main() -> None:
    # 1. Inicializar la base de datos (crear tablas si no existen)
    print("Inicializando sistema...")
    db = Database()
    if not db.init_db():
        print("No fue posible preparar la base de datos. El programa se cerrará.")
        return

    # 2. Iniciar el controlador principal que maneja el flujo de la aplicación
    app = MainController()
    app.ejecutar()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma finalizado por el usuario.")
