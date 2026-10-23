from __future__ import annotations

from datetime import date

from config.excepciones import OperacionCancelada
from controllers.base_controller import ControladorCRUD
from models.Registro_Tiempo import Registro_Tiempo
from models.Usuarios import Administrador, Empleado, Usuario
from models.validaciones import validador_fecha, validador_texto, validar_horas
from repositories.proyecto_repository import RepositorioProyecto
from repositories.registro_tiempo_repository import RepositorioRegistroTiempo
from repositories.usuario_repository import RepositorioUsuario
from views import consola


class ControladorRegistroTiempo(ControladorCRUD):
    """Un empleado ve y modifica solo sus registros; un administrador, los de todos."""

    def __init__(
        self,
        repo_registros: RepositorioRegistroTiempo,
        repo_usuarios: RepositorioUsuario,
        repo_proyectos: RepositorioProyecto,
        sesion: Usuario,
    ) -> None:
        self._repo = repo_registros
        self._usuarios = repo_usuarios
        self._proyectos = repo_proyectos
        self._sesion = sesion

    def _registros_visibles(self) -> list[Registro_Tiempo]:
        if isinstance(self._sesion, Empleado):
            return self._repo.listar_por_empleado(self._sesion)
        return self._repo.listar()

    def _empleado_destino(self) -> Empleado:
        if isinstance(self._sesion, Empleado):
            return self._sesion
        return consola.elegir(
            "¿A qué empleado corresponde el registro?",
            self._usuarios.listar_empleados(),
            lambda e: f"{e.nombre} <{e.correo}>",
        )

    def _seleccionar(self) -> Registro_Tiempo:
        return consola.elegir(
            "Registros de tiempo:",
            self._registros_visibles(),
            lambda r: f"{r.fecha} | {r.empleado.nombre} | {r.proyecto.nombre} | {r.horas:g} h",
        )

    def listar(self) -> None:
        registros = self._registros_visibles()
        consola.mostrar_tabla(
            ("ID", "Fecha", "Empleado", "Proyecto", "Horas", "Descripción"),
            [(r.id_registro, r.fecha, r.empleado.nombre, r.proyecto.nombre, f"{r.horas:g}", r.descripcion) for r in registros],
        )
        if registros:
            consola.mostrar_info(f"Total de horas listadas: {sum(r.horas for r in registros):g}")

    def crear(self) -> None:
        consola.mostrar_info("Escriba /cancelar para abortar.")
        empleado = self._empleado_destino()
        proyecto = consola.elegir("Proyecto asociado:", self._proyectos.listar(), lambda p: p.nombre)
        fecha = consola.leer_validado(
            "Fecha (AAAA-MM-DD)", validador_fecha("fecha del registro", permitir_futuro=False), date.today().isoformat()
        )
        horas = consola.leer_decimal("Horas trabajadas (ej: 7.5)", validar_horas)
        descripcion = consola.leer_validado("Descripción de la tarea", validador_texto("descripción", maximo=200))
        registro = Registro_Tiempo(None, fecha, horas, descripcion, empleado, proyecto)
        self._repo.crear(registro)
        empleado.registrar_horas(registro)
        consola.mostrar_exito(f"Registro {registro.id_registro} guardado en el proyecto '{proyecto.nombre}'.")

    def actualizar(self) -> None:
        registro = self._seleccionar()
        consola.mostrar_info("Presione Enter para conservar el valor actual.")
        horas = consola.leer_decimal("Nuevas horas", validar_horas, registro.horas)
        descripcion = consola.leer_validado("Nueva descripción", validador_texto("descripción", maximo=200), registro.descripcion)
        registro.modificar(horas, descripcion)
        self._repo.actualizar(registro)
        consola.mostrar_exito("Registro actualizado.")

    def eliminar(self) -> None:
        registro = self._seleccionar()
        if not consola.confirmar(f"¿Eliminar el registro del {registro.fecha} ({registro.horas:g} h)?"):
            raise OperacionCancelada()
        self._repo.eliminar(registro.id_registro)
        registro.empleado.quitar_registro(registro)
        consola.mostrar_exito("Registro eliminado.")

    def informe(self) -> None:
        if not isinstance(self._sesion, Administrador):
            raise ValueError("Solo un administrador puede generar informes.")
        consola.mostrar_info(self._sesion.generar_informe())
        consola.mostrar_tabla(
            ("Proyecto", "Registros", "Horas totales"),
            [(proyecto, cantidad, f"{horas:g}") for proyecto, cantidad, horas in self._repo.horas_por_proyecto()],
        )
