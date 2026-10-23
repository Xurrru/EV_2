import sqlite3
import unittest
from pathlib import Path

from config.Base_Datos import Database
from config.excepciones import ErrorBaseDatos, ErrorIntegridad, RegistroNoEncontrado
from models.Departamento import Departamento
from models.Proyecto import Proyecto
from models.Registro_Tiempo import Registro_Tiempo
from models.Usuarios import Administrador, Empleado
from repositories.departamento_repository import RepositorioDepartamento
from repositories.proyecto_repository import RepositorioProyecto
from repositories.registro_tiempo_repository import RepositorioRegistroTiempo
from repositories.usuario_repository import RepositorioUsuario
from tests.base_prueba import PruebaConBD
from tests.test_modelos import crear_empleado


class PruebaRepositorios(PruebaConBD):
    def setUp(self):
        super().setUp()
        self.deps, self.proys = RepositorioDepartamento(), RepositorioProyecto()
        self.users = RepositorioUsuario(self.deps)
        self.regs = RepositorioRegistroTiempo(self.users, self.proys)

    # --- Conexión ---
    def test_conexion_y_tablas(self):
        with Database().transaccion() as conn:
            tablas = {f[0] for f in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"departamento", "proyecto", "usuario", "empleado", "registro_tiempo"} <= tablas)

    def test_claves_foraneas_activas(self):
        with Database().transaccion() as conn:
            self.assertEqual(conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_error_de_conexion_se_controla(self):
        Database.configurar_ruta(Path(self._carpeta.name) / "no_existe" / "x.db")
        with self.assertRaises(ErrorBaseDatos):
            Database().get_connection()
        with self.assertRaises(ErrorBaseDatos):
            self.deps.listar()

    def test_rollback_si_falla_a_mitad(self):
        with self.assertRaises(ErrorIntegridad):
            with Database().transaccion() as conn:
                conn.execute("INSERT INTO departamento (nombre, gerente) VALUES ('A', 'B')")
                conn.execute("INSERT INTO departamento (nombre, gerente) VALUES ('A', 'C')")  # nombre duplicado
        self.assertEqual(self.deps.listar(), [])

    # --- Departamento ---
    def test_crud_departamento(self):
        d = Departamento(None, "TI", "Carlos")
        self.deps.crear(d)
        self.assertIsNotNone(d.id_departamento)
        self.assertEqual(self.deps.obtener_por_id(d.id_departamento).nombre, "TI")
        d.editar("Tecnología", "Carla")
        self.deps.actualizar(d)
        recargado = self.deps.obtener_por_id(d.id_departamento)
        self.assertEqual((recargado.nombre, recargado.gerente), ("Tecnología", "Carla"))
        self.deps.eliminar(d.id_departamento)
        self.assertIsNone(self.deps.obtener_por_id(d.id_departamento))

    def test_departamento_duplicado_y_no_encontrado(self):
        self.deps.crear(Departamento(None, "TI", "Carlos"))
        with self.assertRaises(ErrorIntegridad):
            self.deps.crear(Departamento(None, "TI", "Otro"))
        with self.assertRaises(RegistroNoEncontrado):
            self.deps.eliminar(999)
        fantasma = Departamento(999, "X", "Y")
        with self.assertRaises(RegistroNoEncontrado):
            self.deps.actualizar(fantasma)
        with self.assertRaises(ValueError):
            self.deps.actualizar(Departamento(None, "X", "Y"))

    def test_no_se_crea_dos_veces_el_mismo_objeto(self):
        d = Departamento(None, "TI", "Carlos")
        self.deps.crear(d)
        with self.assertRaises(ValueError):
            self.deps.crear(d)

    def test_busqueda_trata_comodines_como_texto(self):
        self.deps.crear(Departamento(None, "TI", "A"))
        self.deps.crear(Departamento(None, "Ventas", "B"))
        self.assertEqual([d.nombre for d in self.deps.buscar_por_nombre("ven")], ["Ventas"])
        self.assertEqual(self.deps.buscar_por_nombre("%"), [])
        self.assertEqual(self.deps.buscar_por_nombre("' OR 1=1 --"), [])  # inyección SQL inofensiva

    # --- Proyecto ---
    def test_crud_proyecto(self):
        p = Proyecto(None, "Sistema", "Desarrollo", "2026-01-10")
        self.proys.crear(p)
        p.editar("Sistema v2", "Nueva versión")
        self.proys.actualizar(p)
        self.assertEqual(self.proys.obtener_por_id(p.id_proyecto).nombre, "Sistema v2")
        self.proys.eliminar(p.id_proyecto)
        self.assertEqual(self.proys.listar(), [])

    # --- Usuarios ---
    def test_crud_empleado_con_departamento_y_login(self):
        dep = Departamento(None, "TI", "Carlos")
        self.deps.crear(dep)
        emp = crear_empleado()
        emp.asignar_departamento(dep)
        self.users.crear(emp)
        self.assertIsNotNone(emp.id_usuario)
        self.assertIsNotNone(emp.id_empleado)
        cargado = self.users.obtener_por_correo("ANA@empresa.com")
        self.assertIsInstance(cargado, Empleado)
        self.assertTrue(cargado.verificar_contrasena("clave1234"))
        self.assertFalse(cargado.verificar_contrasena("mala12345"))
        self.assertEqual(cargado.departamento.nombre, "TI")
        cargado.nombre, cargado.salario = "Ana Pérez", 1_200_000
        cargado.asignar_departamento(None)
        self.users.actualizar(cargado)
        de_nuevo = self.users.obtener_empleado_por_id(cargado.id_empleado)
        self.assertEqual((de_nuevo.nombre, de_nuevo.salario, de_nuevo.departamento), ("Ana Pérez", 1_200_000, None))
        self.users.eliminar(de_nuevo.id_usuario)
        self.assertIsNone(self.users.obtener_por_id(de_nuevo.id_usuario))

    def test_polimorfismo_en_listados(self):
        self.users.crear(Administrador(None, "admin@empresa.com", "admin12345"))
        self.users.crear(crear_empleado())
        self.assertEqual({type(u).__name__ for u in self.users.listar()}, {"Administrador", "Empleado"})
        self.assertEqual(len(self.users.listar_empleados()), 1)
        self.assertEqual(self.users.contar_administradores(), 1)

    def test_correo_duplicado(self):
        self.users.crear(crear_empleado())
        with self.assertRaises(ErrorIntegridad):
            self.users.crear(crear_empleado())
        self.assertEqual(len(self.users.listar()), 1)  # el INSERT parcial se revirtió

    def test_departamento_sin_guardar_se_rechaza(self):
        emp = crear_empleado()
        emp.asignar_departamento(Departamento(None, "TI", "C"))
        with self.assertRaises(ValueError):
            self.users.crear(emp)

    def test_eliminar_departamento_deja_empleado_sin_departamento(self):
        dep = Departamento(None, "TI", "C")
        self.deps.crear(dep)
        emp = crear_empleado()
        emp.asignar_departamento(dep)
        self.users.crear(emp)
        self.assertEqual(self.deps.contar_empleados(dep.id_departamento), 1)
        self.deps.eliminar(dep.id_departamento)
        self.assertIsNone(self.users.obtener_empleado_por_id(emp.id_empleado).departamento)

    def test_fila_corrupta_se_informa(self):
        with Database().transaccion() as conn:
            conn.execute("INSERT INTO usuario (correo, password_hash, rol) VALUES ('x@y.com', 'basura', 'Administrador')")
        with self.assertRaises(ErrorBaseDatos):
            self.users.listar()

    def test_reglas_check_de_la_bd(self):
        with self.assertRaises(ErrorIntegridad):
            with Database().transaccion() as conn:
                conn.execute("INSERT INTO usuario (correo, password_hash, rol) VALUES ('x@y.com', 'h', 'Invitado')")

    # --- Registros de tiempo ---
    def _preparar(self):
        emp, proy = crear_empleado(), Proyecto(None, "Sistema", "Desarrollo", "2026-01-10")
        self.users.crear(emp)
        self.proys.crear(proy)
        return emp, proy

    def test_crud_registro(self):
        emp, proy = self._preparar()
        reg = Registro_Tiempo(None, "2026-10-19", 8, "Código", emp, proy)
        self.regs.crear(reg)
        emp.registrar_horas(reg)
        self.assertIsNotNone(reg.id_registro)
        cargado = self.regs.obtener_por_id(reg.id_registro)
        self.assertEqual((cargado.horas, cargado.empleado.nombre, cargado.proyecto.nombre), (8, "Ana Gómez", "Sistema"))
        reg.modificar(6.5, "Código y pruebas")
        self.regs.actualizar(reg)
        self.assertEqual(self.regs.obtener_por_id(reg.id_registro).horas, 6.5)
        self.assertEqual(len(self.regs.listar()), 1)
        self.regs.eliminar(reg.id_registro)
        self.assertEqual(self.regs.listar(), [])

    def test_listar_por_empleado_no_duplica_en_memoria(self):
        emp, proy = self._preparar()
        self.regs.crear(Registro_Tiempo(None, "2026-10-19", 4, "a", emp, proy))
        self.regs.listar_por_empleado(emp)
        self.regs.listar_por_empleado(emp)
        self.assertEqual((len(emp.registros_tiempo), emp.total_horas), (1, 4))

    def test_cascada_al_eliminar_empleado_y_proyecto(self):
        emp, proy = self._preparar()
        self.regs.crear(Registro_Tiempo(None, "2026-10-19", 4, "a", emp, proy))
        self.assertEqual(self.proys.contar_registros(proy.id_proyecto), 1)
        self.users.eliminar(emp.id_usuario)
        self.assertEqual(self.regs.listar(), [])

    def test_registro_requiere_entidades_guardadas(self):
        emp, proy = crear_empleado(), Proyecto(None, "S", "D", "2026-01-10")
        with self.assertRaises(ValueError):
            self.regs.crear(Registro_Tiempo(None, "2026-10-19", 4, "a", emp, proy))

    def test_informe_de_horas(self):
        emp, proy = self._preparar()
        self.regs.crear(Registro_Tiempo(None, "2026-10-18", 4, "a", emp, proy))
        self.regs.crear(Registro_Tiempo(None, "2026-10-19", 3.5, "b", emp, proy))
        self.assertEqual(self.regs.horas_por_proyecto(), [("Sistema", 2, 7.5)])


if __name__ == "__main__":
    unittest.main()
