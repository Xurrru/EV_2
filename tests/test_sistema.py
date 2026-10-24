"""
Pruebas automáticas del sistema. Cada prueba usa una base de datos temporal.
Ejecutar desde la carpeta del proyecto:  python -m unittest discover -s tests -t .
"""
import os
import tempfile
import unittest

from config.database import Database
from models.administrador import Administrador
from models.administrador_dao import AdministradorDAO
from models.departamento import Departamento
from models.departamento_dao import DepartamentoDAO
from models.empleado import Empleado
from models.empleado_dao import EmpleadoDAO
from models.proyecto import Proyecto
from models.proyecto_dao import ProyectoDAO
from models.registro_tiempo import Registro_Tiempo
from models.registro_tiempo_dao import RegistroTiempoDAO
from models.usuario import Usuario


def nuevo_empleado(**cambios):
    datos = dict(correo="ana@empresa.com", password="clave1234", nombre="Ana Gómez", direccion="Calle 1 123",
                 telefono="912345678", email="ana@mail.com", fecha_contrato="2026-01-10", salario=900000)
    datos.update(cambios)
    return Empleado(**datos)


class PruebaConBD(unittest.TestCase):
    """Clase base: crea una BD temporal antes de cada prueba y la borra después."""

    def setUp(self):
        self.ruta_original = Database._db_path
        self.carpeta = tempfile.TemporaryDirectory()
        Database._db_path = os.path.join(self.carpeta.name, "prueba.db")
        Database().init_db()

    def tearDown(self):
        Database._db_path = self.ruta_original
        self.carpeta.cleanup()


class PruebaModelos(unittest.TestCase):
    def test_departamento_valida(self):
        with self.assertRaises(ValueError):
            Departamento("  ", "Carlos")
        with self.assertRaises(TypeError):
            Departamento(123, "Carlos")
        self.assertEqual(Departamento("  Tecnología ", "Carlos").nombre, "Tecnología")

    def test_departamento_editar(self):
        d = Departamento("Tecnología", "Carlos")
        d.editar("Finanzas", "Marta")
        self.assertEqual((d.nombre, d.gerente), ("Finanzas", "Marta"))

    def test_proyecto_valida_fecha(self):
        for mala in ("2026-02-30", "20260101", "01-01-2026", ""):
            with self.assertRaises(ValueError):
                Proyecto("Sistema", "Desarrollo", mala)

    def test_usuario_hereda_y_es_polimorfico(self):
        admin = Administrador("admin@empresa.com", "admin12345")
        emp = nuevo_empleado()
        self.assertIsInstance(admin, Usuario)
        self.assertIsInstance(emp, Usuario)
        self.assertEqual((admin.rol, emp.rol), ("Administrador", "Empleado"))
        self.assertTrue(str(admin).startswith("Administrador"))
        self.assertTrue(str(emp).startswith("Empleado"))

    def test_password_se_cifra_y_verifica(self):
        emp = nuevo_empleado()
        self.assertNotIn("clave1234", emp.password_hash)
        self.assertTrue(emp.verificar_password("clave1234"))
        self.assertFalse(emp.verificar_password("otra12345"))
        self.assertNotEqual(emp.password_hash, nuevo_empleado().password_hash)  # sal distinta

    def test_password_invalida(self):
        for mala in ("corta1", "sololetras", "12345678", ""):
            with self.assertRaises(ValueError):
                nuevo_empleado(password=mala)
        with self.assertRaises(TypeError):
            nuevo_empleado(password=12345678)

    def test_cambiar_password(self):
        emp = nuevo_empleado()
        with self.assertRaises(ValueError):
            emp.cambiar_password("incorrecta1", "nueva12345")
        emp.cambiar_password("clave1234", "nueva12345")
        self.assertTrue(emp.verificar_password("nueva12345"))

    def test_empleado_valida_campos(self):
        for campo, valor in (("nombre", " "), ("telefono", "abc"), ("email", "mal"), ("correo", "x"),
                             ("fecha_contrato", "2026-99-99"), ("salario", -1), ("salario", float("nan"))):
            with self.assertRaises((ValueError, TypeError), msg=campo):
                nuevo_empleado(**{campo: valor})

    def test_empleado_departamento_tipo(self):
        emp = nuevo_empleado()
        with self.assertRaises(TypeError):
            emp.departamento = "Tecnología"

    def test_registro_valida(self):
        emp, proy = nuevo_empleado(), Proyecto("Sistema", "Desarrollo", "2026-01-10")
        for fecha, horas, desc in (("2999-01-01", 5, "tarea"), ("2026-10-19", 0, "tarea"),
                                   ("2026-10-19", 30, "tarea"), ("2026-10-19", 5, " ")):
            with self.assertRaises(ValueError):
                Registro_Tiempo(fecha, horas, desc, emp, proy)
        with self.assertRaises(TypeError):
            Registro_Tiempo("2026-10-19", 5, "tarea", "no es empleado", proy)

    def test_registrar_horas(self):
        emp, otro = nuevo_empleado(), nuevo_empleado(correo="b@empresa.com")
        proy = Proyecto("Sistema", "Desarrollo", "2026-01-10")
        reg = Registro_Tiempo("2026-10-19", 8, "Código", emp, proy)
        emp.registrar_horas(reg)
        emp.registrar_horas(reg)
        self.assertEqual((len(emp.registros_tiempo), emp.total_horas), (1, 8))
        with self.assertRaises(ValueError):
            otro.registrar_horas(reg)


class PruebaDAO(PruebaConBD):
    def test_crud_departamento(self):
        d = Departamento("Tecnología", "Carlos")
        self.assertTrue(DepartamentoDAO.crear(d))
        self.assertIsNotNone(d.id_departamento)
        d.editar("Tecnología e Innovación", "Carla")
        self.assertTrue(DepartamentoDAO.actualizar(d))
        recargado = DepartamentoDAO.obtener_por_id(d.id_departamento)
        self.assertEqual((recargado.nombre, recargado.gerente), ("Tecnología e Innovación", "Carla"))
        self.assertTrue(DepartamentoDAO.eliminar(d.id_departamento))
        self.assertIsNone(DepartamentoDAO.obtener_por_id(d.id_departamento))
        self.assertFalse(DepartamentoDAO.eliminar(999))

    def test_departamento_duplicado(self):
        self.assertTrue(DepartamentoDAO.crear(Departamento("Tecnología", "Carlos")))
        self.assertFalse(DepartamentoDAO.crear(Departamento("Tecnología", "Otro")))
        self.assertEqual(len(DepartamentoDAO.obtener_todos()), 1)

    def test_crud_proyecto(self):
        p = Proyecto("Sistema", "Desarrollo", "2026-01-10")
        self.assertTrue(ProyectoDAO.crear(p))
        p.editar("Sistema v2", "Nueva versión")
        self.assertTrue(ProyectoDAO.actualizar(p))
        self.assertEqual(ProyectoDAO.obtener_por_id(p.id_proyecto).nombre, "Sistema v2")
        self.assertTrue(ProyectoDAO.eliminar(p.id_proyecto))
        self.assertEqual(ProyectoDAO.obtener_todos(), [])

    def test_crud_empleado_y_login(self):
        d = Departamento("Tecnología", "Carlos")
        DepartamentoDAO.crear(d)
        emp = nuevo_empleado(departamento=d)
        self.assertTrue(EmpleadoDAO.crear(emp))
        cargado = EmpleadoDAO.obtener_por_id(emp.id_empleado)
        self.assertTrue(cargado.verificar_password("clave1234"))   # el hash se guardó bien
        self.assertEqual(cargado.departamento.nombre, "Tecnología")
        cargado.nombre, cargado.salario, cargado.departamento = "Ana Pérez", 1200000, None
        self.assertTrue(EmpleadoDAO.actualizar(cargado))
        de_nuevo = EmpleadoDAO.obtener_por_id(emp.id_empleado)
        self.assertEqual((de_nuevo.nombre, de_nuevo.salario, de_nuevo.departamento), ("Ana Pérez", 1200000, None))
        self.assertTrue(EmpleadoDAO.eliminar(emp.id_empleado))
        self.assertIsNone(EmpleadoDAO.obtener_por_id(emp.id_empleado))

    def test_correo_duplicado_no_deja_datos_a_medias(self):
        self.assertTrue(EmpleadoDAO.crear(nuevo_empleado()))
        self.assertFalse(EmpleadoDAO.crear(nuevo_empleado()))
        self.assertEqual(len(EmpleadoDAO.obtener_todos()), 1)

    def test_eliminar_departamento_deja_empleado_sin_departamento(self):
        d = Departamento("Tecnología", "Carlos")
        DepartamentoDAO.crear(d)
        emp = nuevo_empleado(departamento=d)
        EmpleadoDAO.crear(emp)
        self.assertEqual(DepartamentoDAO.contar_empleados(d.id_departamento), 1)
        DepartamentoDAO.eliminar(d.id_departamento)
        self.assertIsNone(EmpleadoDAO.obtener_por_id(emp.id_empleado).departamento)

    def test_administradores(self):
        self.assertEqual(AdministradorDAO.contar(), 0)
        admin = Administrador("Admin@Empresa.com", "admin12345")
        self.assertTrue(AdministradorDAO.crear(admin))
        self.assertFalse(AdministradorDAO.crear(Administrador("admin@empresa.com", "otra12345")))
        encontrado = AdministradorDAO.obtener_por_correo("  ADMIN@empresa.com ")
        self.assertTrue(encontrado.verificar_password("admin12345"))
        self.assertFalse(encontrado.verificar_password("mala12345"))
        EmpleadoDAO.crear(nuevo_empleado())
        self.assertEqual(AdministradorDAO.contar(), 1)       # los empleados no cuentan
        self.assertEqual(len(AdministradorDAO.obtener_todos()), 1)

    def test_registros_de_tiempo(self):
        emp, proy = nuevo_empleado(), Proyecto("Sistema", "Desarrollo", "2026-01-10")
        EmpleadoDAO.crear(emp)
        ProyectoDAO.crear(proy)
        reg = Registro_Tiempo("2026-10-18", 8, "Código", emp, proy)
        self.assertTrue(RegistroTiempoDAO.crear(reg))
        RegistroTiempoDAO.crear(Registro_Tiempo("2026-10-19", 3.5, "Pruebas", emp, proy))
        cargado = RegistroTiempoDAO.obtener_por_id(reg.id_registro)
        self.assertEqual((cargado.horas, cargado.empleado.nombre, cargado.proyecto.nombre), (8, "Ana Gómez", "Sistema"))
        cargado.modificar(6, "Código y revisión")
        self.assertTrue(RegistroTiempoDAO.actualizar(cargado))
        self.assertEqual(RegistroTiempoDAO.obtener_por_id(reg.id_registro).horas, 6)
        self.assertEqual(len(RegistroTiempoDAO.obtener_por_empleado(emp.id_empleado)), 2)
        self.assertEqual(RegistroTiempoDAO.horas_por_proyecto(), [("Sistema", 2, 9.5)])
        self.assertTrue(RegistroTiempoDAO.eliminar(reg.id_registro))
        self.assertEqual(len(RegistroTiempoDAO.obtener_todos()), 1)

    def test_registro_requiere_entidades_guardadas(self):
        emp, proy = nuevo_empleado(), Proyecto("Sistema", "Desarrollo", "2026-01-10")
        self.assertFalse(RegistroTiempoDAO.crear(Registro_Tiempo("2026-10-18", 8, "Código", emp, proy)))

    def test_cascada_al_eliminar_proyecto(self):
        emp, proy = nuevo_empleado(), Proyecto("Sistema", "Desarrollo", "2026-01-10")
        EmpleadoDAO.crear(emp)
        ProyectoDAO.crear(proy)
        RegistroTiempoDAO.crear(Registro_Tiempo("2026-10-18", 8, "Código", emp, proy))
        self.assertEqual(ProyectoDAO.contar_registros(proy.id_proyecto), 1)
        ProyectoDAO.eliminar(proy.id_proyecto)
        self.assertEqual(RegistroTiempoDAO.obtener_todos(), [])

    def test_sql_injection_es_inofensiva(self):
        DepartamentoDAO.crear(Departamento("Tecnología", "Carlos"))
        self.assertIsNone(AdministradorDAO.obtener_por_correo("x' OR '1'='1"))
        self.assertTrue(DepartamentoDAO.crear(Departamento("'; DROP TABLE departamento; --", "Carlos")))
        self.assertEqual(len(DepartamentoDAO.obtener_todos()), 2)

    def test_error_de_conexion_se_controla(self):
        Database._db_path = os.path.join(self.carpeta.name, "no_existe", "x.db")
        self.assertEqual(DepartamentoDAO.obtener_todos(), [])
        self.assertFalse(DepartamentoDAO.crear(Departamento("Tecnología", "Carlos")))
        self.assertEqual(AdministradorDAO.contar(), -1)
        self.assertFalse(Database().init_db())


if __name__ == "__main__":
    unittest.main()
