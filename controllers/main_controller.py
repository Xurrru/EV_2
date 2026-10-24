from controllers.administrador_controller import AdministradorController
from controllers.departamento_controller import DepartamentoController
from controllers.empleado_controller import EmpleadoController
from controllers.proyecto_controller import ProyectoController
from controllers.registro_tiempo_controller import RegistroTiempoController
from models.administrador import Administrador
from models.administrador_dao import AdministradorDAO
from models.registro_tiempo_dao import RegistroTiempoDAO
from views.main_view import MainView


class MainController:
    MAX_INTENTOS = 3

    def __init__(self):
        self.view = MainView()
        self.admin = None  # administrador con la sesión abierta

    def preparar_primer_administrador(self) -> bool:
        """Si no existe ningún administrador, obliga a crear el primero antes del login."""
        total = AdministradorDAO.contar()
        if total < 0:
            return False
        if total == 0:
            self.view.mostrar_mensaje("Primera ejecución: no hay administradores. Cree el primero.")
        while total == 0:
            AdministradorController().agregar_administrador()
            total = AdministradorDAO.contar()
            if total < 0:
                return False
        return True

    def iniciar_sesion(self) -> Administrador | None:
        for intento in range(1, self.MAX_INTENTOS + 1):
            datos = self.view.formulario_login()
            administrador = AdministradorDAO.obtener_por_correo(datos['correo'])
            if administrador is not None and administrador.verificar_password(datos['password']):
                return administrador
            # Mismo mensaje si falla el correo o la contraseña: no revela qué correos existen.
            restantes = self.MAX_INTENTOS - intento
            self.view.mostrar_mensaje(f"Credenciales incorrectas. Intentos restantes: {restantes}.")
        return None

    def informe_horas(self) -> None:
        self.view.mostrar_informe(self.admin.generar_informe(), RegistroTiempoDAO.horas_por_proyecto())

    def ejecutar(self) -> None:
        if not self.preparar_primer_administrador():
            self.view.mostrar_mensaje("No se pudo acceder a la base de datos. El programa se cerrará.")
            return

        self.admin = self.iniciar_sesion()
        if self.admin is None:
            self.view.mostrar_mensaje("Demasiados intentos fallidos. El programa se cerrará.")
            return
        self.view.mostrar_mensaje(f"Bienvenido/a, {self.admin}")

        empleado_controller = EmpleadoController()
        departamento_controller = DepartamentoController()
        proyecto_controller = ProyectoController()
        registro_controller = RegistroTiempoController()
        administrador_controller = AdministradorController(self.admin)

        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.view.mostrar_mensaje(self.admin.gestionar("empleados"))
                empleado_controller.ejecutar()
            elif opcion == 2:
                self.view.mostrar_mensaje(self.admin.gestionar("departamentos"))
                departamento_controller.ejecutar()
            elif opcion == 3:
                self.view.mostrar_mensaje(self.admin.gestionar("proyectos"))
                proyecto_controller.ejecutar()
            elif opcion == 4:
                self.view.mostrar_mensaje(self.admin.gestionar("registros de tiempo"))
                registro_controller.ejecutar()
            elif opcion == 5:
                self.view.mostrar_mensaje(self.admin.gestionar("administradores"))
                administrador_controller.ejecutar()
            elif opcion == 6:
                self.informe_horas()
            elif opcion == 0:
                self.view.mostrar_mensaje("Gracias por usar el sistema. ¡Hasta luego!")
                break
            else:
                self.view.mostrar_mensaje("Opción no válida. Por favor, intente nuevamente.")
