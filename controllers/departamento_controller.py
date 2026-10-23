from __future__ import annotations

from config.excepciones import OperacionCancelada
from controllers.base_controller import ControladorCRUD
from models.Departamento import Departamento
from models.validaciones import validador_texto
from repositories.departamento_repository import RepositorioDepartamento
from views import consola
from views.menus import Opcion


class ControladorDepartamento(ControladorCRUD):
    def __init__(self, repositorio: RepositorioDepartamento) -> None:
        self._repo = repositorio

    @staticmethod
    def _mostrar(departamentos: list[Departamento]) -> None:
        consola.mostrar_tabla(
            ("ID", "Nombre", "Gerente"),
            [(d.id_departamento, d.nombre, d.gerente) for d in departamentos],
        )

    def _seleccionar(self) -> Departamento:
        return consola.elegir(
            "Departamentos disponibles:", self._repo.listar(), lambda d: f"{d.nombre} (gerente: {d.gerente})"
        )

    def listar(self) -> None:
        self._mostrar(self._repo.listar())

    def crear(self) -> None:
        consola.mostrar_info("Escriba /cancelar para abortar.")
        nombre = consola.leer_validado("Nombre del departamento", validador_texto("nombre del departamento"))
        gerente = consola.leer_validado("Nombre del gerente", validador_texto("gerente"))
        departamento = Departamento(None, nombre, gerente)
        self._repo.crear(departamento)
        consola.mostrar_exito(f"Departamento '{departamento.nombre}' creado con ID {departamento.id_departamento}.")

    def actualizar(self) -> None:
        departamento = self._seleccionar()
        consola.mostrar_info("Presione Enter para conservar el valor actual.")
        nombre = consola.leer_validado("Nuevo nombre", validador_texto("nombre del departamento"), departamento.nombre)
        gerente = consola.leer_validado("Nuevo gerente", validador_texto("gerente"), departamento.gerente)
        departamento.editar(nombre, gerente)
        self._repo.actualizar(departamento)
        consola.mostrar_exito("Departamento actualizado.")

    def eliminar(self) -> None:
        departamento = self._seleccionar()
        cantidad = self._repo.contar_empleados(departamento.id_departamento)
        aviso = f" Tiene {cantidad} empleado(s) que quedarán sin departamento." if cantidad else ""
        if not consola.confirmar(f"¿Eliminar el departamento '{departamento.nombre}'?{aviso}"):
            raise OperacionCancelada()
        departamento.eliminar()
        self._repo.eliminar(departamento.id_departamento)
        consola.mostrar_exito("Departamento eliminado.")

    def buscar(self) -> None:
        texto = consola.leer_validado("Texto a buscar en el nombre", validador_texto("texto de búsqueda"))
        self._mostrar(self._repo.buscar_por_nombre(texto))

    def opciones_menu(self) -> dict[str, Opcion]:
        return {**super().opciones_menu(), "5": ("Buscar por nombre", self.buscar)}
