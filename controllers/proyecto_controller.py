from __future__ import annotations

from config.excepciones import OperacionCancelada
from controllers.base_controller import ControladorCRUD
from models.Proyecto import Proyecto
from models.validaciones import validador_fecha, validador_texto
from repositories.proyecto_repository import RepositorioProyecto
from views import consola
from views.menus import Opcion


class ControladorProyecto(ControladorCRUD):
    def __init__(self, repositorio: RepositorioProyecto) -> None:
        self._repo = repositorio

    @staticmethod
    def _mostrar(proyectos: list[Proyecto]) -> None:
        consola.mostrar_tabla(
            ("ID", "Nombre", "Inicio", "Descripción"),
            [(p.id_proyecto, p.nombre, p.fecha_inicio, p.descripcion) for p in proyectos],
        )

    def _seleccionar(self) -> Proyecto:
        return consola.elegir(
            "Proyectos disponibles:", self._repo.listar(), lambda p: f"{p.nombre} (inicio: {p.fecha_inicio})"
        )

    def listar(self) -> None:
        self._mostrar(self._repo.listar())

    def crear(self) -> None:
        consola.mostrar_info("Escriba /cancelar para abortar.")
        nombre = consola.leer_validado("Nombre del proyecto", validador_texto("nombre del proyecto"))
        descripcion = consola.leer_validado(
            "Descripción", validador_texto("descripción del proyecto", maximo=300)
        )
        fecha = consola.leer_validado("Fecha de inicio (AAAA-MM-DD)", validador_fecha("fecha de inicio"))
        proyecto = Proyecto(None, nombre, descripcion, fecha)
        self._repo.crear(proyecto)
        consola.mostrar_exito(f"Proyecto '{proyecto.nombre}' creado con ID {proyecto.id_proyecto}.")

    def actualizar(self) -> None:
        proyecto = self._seleccionar()
        consola.mostrar_info("Presione Enter para conservar el valor actual.")
        nombre = consola.leer_validado("Nuevo nombre", validador_texto("nombre del proyecto"), proyecto.nombre)
        descripcion = consola.leer_validado(
            "Nueva descripción", validador_texto("descripción del proyecto", maximo=300), proyecto.descripcion
        )
        proyecto.editar(nombre, descripcion)
        self._repo.actualizar(proyecto)
        consola.mostrar_exito("Proyecto actualizado.")

    def eliminar(self) -> None:
        proyecto = self._seleccionar()
        cantidad = self._repo.contar_registros(proyecto.id_proyecto)
        aviso = f" Se eliminarán también {cantidad} registro(s) de tiempo asociados." if cantidad else ""
        if not consola.confirmar(f"¿Eliminar el proyecto '{proyecto.nombre}'?{aviso}"):
            raise OperacionCancelada()
        self._repo.eliminar(proyecto.id_proyecto)
        consola.mostrar_exito("Proyecto eliminado.")

    def buscar(self) -> None:
        texto = consola.leer_validado("Texto a buscar en el nombre", validador_texto("texto de búsqueda"))
        self._mostrar(self._repo.buscar_por_nombre(texto))

    def opciones_menu(self) -> dict[str, Opcion]:
        return {**super().opciones_menu(), "5": ("Buscar por nombre", self.buscar)}
