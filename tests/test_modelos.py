import unittest

from models.Departamento import Departamento
from models.Proyecto import Proyecto
from models.Registro_Tiempo import Registro_Tiempo
from models.Usuarios import Administrador, Empleado, Usuario
from models import validaciones as v


def crear_empleado(**cambios):
    datos = dict(id_usuario=None, correo="ana@empresa.com", password_plana="clave1234", id_empleado=None,
                 nombre="Ana Gómez", direccion="Calle 1", telefono="912345678", email="ana@empresa.com",
                 fecha_contrato="2026-01-10", salario=900000)
    datos.update(cambios)
    return Empleado(**datos)


class PruebaValidaciones(unittest.TestCase):
    def test_correo(self):
        self.assertEqual(v.validar_correo("  ANA@Empresa.COM "), "ana@empresa.com")
        for malo in ("", "sin-arroba", "@x.com", "a@b", "a b@c.com", None, 5):
            with self.assertRaises(ValueError):
                v.validar_correo(malo)

    def test_fecha(self):
        self.assertEqual(v.validar_fecha("2026-02-28"), "2026-02-28")
        for mala in ("2026-02-30", "20260228", "28-02-2026", "2026-2-8", ""):
            with self.assertRaises(ValueError):
                v.validar_fecha(mala)
        with self.assertRaises(ValueError):
            v.validar_fecha("2999-01-01", permitir_futuro=False)

    def test_numeros(self):
        for malo in (0, -5, float("nan"), float("inf"), True, "10", 25):
            with self.assertRaises(ValueError):
                v.validar_horas(malo)
        self.assertEqual(v.validar_horas(7.5), 7.5)
        for malo in (0, -1, float("inf"), 2_000_000_000, None):
            with self.assertRaises(ValueError):
                v.validar_salario(malo)

    def test_password(self):
        v.validar_password("clave1234")
        for mala in ("", "corta1", "sololetras", "12345678", "x" * 200):
            with self.assertRaises(ValueError):
                v.validar_password(mala)

    def test_telefono(self):
        self.assertEqual(v.validar_telefono(" +56 9 1234 5678 "), "+56 9 1234 5678")
        self.assertEqual(v.validar_telefono("912345678"), "912345678")
        for malo in ("abc", "123", "12345678901234567"):
            with self.assertRaises(ValueError):
                v.validar_telefono(malo)


class PruebaUsuarios(unittest.TestCase):
    def test_usuario_es_abstracto(self):
        with self.assertRaises(TypeError):
            Usuario(1, "a@b.com", "clave1234")

    def test_hash_no_guarda_texto_plano_y_verifica(self):
        emp = crear_empleado()
        self.assertNotIn("clave1234", emp.password_hash)
        self.assertTrue(emp.verificar_contrasena("clave1234"))
        self.assertFalse(emp.verificar_contrasena("otra12345"))
        self.assertFalse(emp.verificar_contrasena(""))
        self.assertFalse(emp.verificar_contrasena(None))

    def test_misma_clave_distinto_hash(self):
        self.assertNotEqual(crear_empleado().password_hash, crear_empleado().password_hash)

    def test_rehidratar_desde_hash(self):
        original = crear_empleado()
        copia = crear_empleado(password_plana=None, password_hash=original.password_hash)
        self.assertTrue(copia.verificar_contrasena("clave1234"))

    def test_hash_corrupto_rechazado(self):
        for malo in ("", "basura", "md5$1$2$3$aa$bb", "scrypt$x$8$1$zz$zz"):
            with self.assertRaises(ValueError):
                crear_empleado(password_plana=None, password_hash=malo)

    def test_exige_clave_o_hash_pero_no_ambos(self):
        with self.assertRaises(ValueError):
            crear_empleado(password_plana=None)
        with self.assertRaises(ValueError):
            crear_empleado(password_hash="scrypt$1$1$1$aa$bb")

    def test_cambiar_contrasena(self):
        emp = crear_empleado()
        with self.assertRaises(ValueError):
            emp.cambiar_contrasena("incorrecta1", "nueva12345")
        with self.assertRaises(ValueError):
            emp.cambiar_contrasena("clave1234", "corta")
        emp.cambiar_contrasena("clave1234", "nueva12345")
        self.assertTrue(emp.verificar_contrasena("nueva12345"))
        self.assertFalse(emp.verificar_contrasena("clave1234"))

    def test_validaciones_del_empleado(self):
        for campo, valor in (("nombre", " "), ("telefono", "abc"), ("email", "mal"),
                             ("fecha_contrato", "2026-99-99"), ("salario", -1), ("correo", "x"), ("id_empleado", -3)):
            with self.assertRaises(ValueError, msg=campo):
                crear_empleado(**{campo: valor})

    def test_setters_validan(self):
        emp = crear_empleado()
        emp.salario = 1_000_000
        self.assertEqual(emp.salario, 1_000_000)
        with self.assertRaises(ValueError):
            emp.salario = -5
        self.assertEqual(emp.salario, 1_000_000)

    def test_id_se_asigna_una_sola_vez(self):
        emp = crear_empleado()
        emp.asignar_id_persistido(7)
        with self.assertRaises(ValueError):
            emp.asignar_id_persistido(8)

    def test_polimorfismo_y_rol(self):
        admin = Administrador(None, "admin@empresa.com", "admin12345")
        emp = crear_empleado()
        self.assertEqual((admin.rol, emp.rol), ("Administrador", "Empleado"))
        self.assertIn("Administrador", str(admin))
        self.assertIn("Ana", str(emp))
        with self.assertRaises(ValueError):
            admin.gestionar("  ")


class PruebaRelaciones(unittest.TestCase):
    def test_asociacion_bidireccional(self):
        dep, otro, emp = Departamento(None, "TI", "Carlos"), Departamento(None, "RRHH", "Marta"), crear_empleado()
        emp.asignar_departamento(dep)
        self.assertIs(emp.departamento, dep)
        self.assertIn(emp, dep.empleados)
        emp.asignar_departamento(otro)
        self.assertNotIn(emp, dep.empleados)
        self.assertIn(emp, otro.empleados)

    def test_eliminar_departamento_desvincula(self):
        dep, emp = Departamento(None, "TI", "Carlos"), crear_empleado()
        emp.asignar_departamento(dep)
        dep.eliminar()
        self.assertIsNone(emp.departamento)

    def test_editar_departamento_es_atomico(self):
        dep = Departamento(None, "TI", "Carlos")
        with self.assertRaises(ValueError):
            dep.editar("Nuevo", "  ")
        self.assertEqual((dep.nombre, dep.gerente), ("TI", "Carlos"))

    def test_registro_tiempo(self):
        emp, proy = crear_empleado(), Proyecto(None, "Sistema", "Desarrollo", "2026-01-10")
        reg = Registro_Tiempo(None, "2026-10-19", 8, "Trabajo", emp, proy)
        emp.registrar_horas(reg)
        emp.registrar_horas(reg)
        self.assertEqual((len(emp.registros_tiempo), emp.total_horas), (1, 8))
        otro = crear_empleado(correo="b@empresa.com")
        with self.assertRaises(ValueError):
            otro.registrar_horas(reg)

    def test_registro_valida_datos(self):
        emp, proy = crear_empleado(), Proyecto(None, "S", "D", "2026-01-10")
        for fecha, horas, desc in (("2999-01-01", 5, "x"), ("2026-10-19", 0, "x"),
                                   ("2026-10-19", 30, "x"), ("2026-10-19", 5, " ")):
            with self.assertRaises(ValueError):
                Registro_Tiempo(None, fecha, horas, desc, emp, proy)
        with self.assertRaises(ValueError):
            Registro_Tiempo(None, "2026-10-19", 5, "x", "no-empleado", proy)

    def test_modificar_registro_es_atomico(self):
        emp, proy = crear_empleado(), Proyecto(None, "S", "D", "2026-01-10")
        reg = Registro_Tiempo(None, "2026-10-19", 5, "x", emp, proy)
        with self.assertRaises(ValueError):
            reg.modificar(6, " ")
        self.assertEqual((reg.horas, reg.descripcion), (5, "x"))


if __name__ == "__main__":
    unittest.main()
