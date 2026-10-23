from __future__ import annotations

from config.excepciones import OperacionCancelada
from controllers.base_controller import ControladorCRUD
from models.Departamento import Departamento
from models.Usuarios import Empleado, Usuario
from models.validaciones import (
    validador_correo,
    validador_fecha,
    validador_texto,
    validar_password,
    validar_salario,
    validar_telefono,
)
from repositories.departamento_repository import RepositorioDepartamento
from repositories.usuario_repository import RepositorioUsuario
from views import consola
from views.menus import Opcion


class ControladorEmpleado(ControladorCRUD):
    """CRUD de empleados. Solo lo usan administradores."""

    def __init__(self, repo_usuarios: RepositorioUsuario, repo_departamentos: RepositorioDepartamento) -> None:
        self._repo = repo_usuarios
        self._repo_departamentos = repo_departamentos

    @staticmethod
    def _mostrar(empleados: list[Empleado]) -> None:
        consola.mostrar_tabla(
            ("ID", "Nombre", "Correo", "Departamento", "Salario", "Contrato"),
            [
                (e.id_empleado, e.nombre, e.correo, e.departamento.nombre if e.departamento else "Sin asignar",
                 f"${e.salario:,.0f}", e.fecha_contrato)
                for e in empleados
            ],
        )

    def _seleccionar(self) -> Empleado:
        return consola.elegir(
            "Empleados disponibles:", self._repo.listar_empleados(), lambda e: f"{e.nombre} <{e.correo}>"
        )

    def _pedir_departamento(self, actual: Departamento | None = None) -> Departamento | None:
        departamentos = self._repo_departamentos.listar()
        if not departamentos:
            consola.mostrar_info("No hay departamentos creados; el empleado quedará sin departamento.")
            return actual
        print("\nDepartamentos disponibles:")
        for posicion, departamento in enumerate(departamentos, 1):
            print(f"  {posicion}. {departamento.nombre}")
        nombre_actual = actual.nombre if actual else "sin departamento"
        eleccion = consola.leer_entero(f"Número de departamento (0 = sin departamento; actual: {nombre_actual})", 0, len(departamentos))
        return departamentos[eleccion - 1] if eleccion else None

    def listar(self) -> None:
        self._mostrar(self._repo.listar_empleados())

    def crear(self) -> None:
        consola.mostrar_info("Escriba /cancelar para abortar.")
        correo = consola.leer_validado("Correo de acceso (login)", validador_correo("correo de acceso"))
        password = consola.leer_password("Contraseña inicial (mín. 8, letras y números)", validar_password, confirmar=True)
        nombre = consola.leer_validado("Nombre completo", validador_texto("nombre"))
        direccion = consola.leer_validado("Dirección", validador_texto("dirección", maximo=150))
        telefono = consola.leer_validado("Teléfono", validar_telefono)
        email = consola.leer_validado("Email de contacto", validador_correo("email de contacto"))
        fecha = consola.leer_validado("Fecha de contrato (AAAA-MM-DD)", validador_fecha("fecha de contrato"))
        salario = consola.leer_decimal("Salario mensual (solo números, sin separador de miles)", validar_salario)
        empleado = Empleado(None, correo, password, None, nombre, direccion, telefono, email, fecha, salario)
        empleado.asignar_departamento(self._pedir_departamento())
        self._repo.crear(empleado)
        consola.mostrar_exito(f"Empleado '{empleado.nombre}' registrado con ID {empleado.id_empleado}.")

    def actualizar(self) -> None:
        empleado = self._seleccionar()
        consola.mostrar_info("Presione Enter para conservar el valor actual.")
        # Se piden y validan todos los datos antes de modificar el objeto.
        correo = consola.leer_validado("Correo de acceso", validador_correo("correo de acceso"), empleado.correo)
        nombre = consola.leer_validado("Nombre", validador_texto("nombre"), empleado.nombre)
        direccion = consola.leer_validado("Dirección", validador_texto("dirección", maximo=150), empleado.direccion)
        telefono = consola.leer_validado("Teléfono", validar_telefono, empleado.telefono)
        email = consola.leer_validado("Email de contacto", validador_correo("email de contacto"), empleado.email)
        salario = consola.leer_decimal("Salario mensual", validar_salario, empleado.salario)
        departamento = self._pedir_departamento(empleado.departamento)
        empleado.correo, empleado.nombre, empleado.direccion = correo, nombre, direccion
        empleado.telefono, empleado.email, empleado.salario = telefono, email, salario
        empleado.asignar_departamento(departamento)
        self._repo.actualizar(empleado)
        consola.mostrar_exito("Empleado actualizado.")

    def eliminar(self) -> None:
        empleado = self._seleccionar()
        if not consola.confirmar(f"¿Eliminar a '{empleado.nombre}'? Se borrarán también sus registros de tiempo"):
            raise OperacionCancelada()
        self._repo.eliminar(empleado.id_usuario)
        consola.mostrar_exito("Empleado eliminado.")

    def buscar(self) -> None:
        texto = consola.leer_validado("Texto a buscar en el nombre", validador_texto("texto de búsqueda"))
        self._mostrar(self._repo.buscar_empleados_por_nombre(texto))

    def opciones_menu(self) -> dict[str, Opcion]:
        return {**super().opciones_menu(), "5": ("Buscar por nombre", self.buscar)}
