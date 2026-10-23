"""Pruebas de la capa de vistas/controladores simulando lo que escribe el usuario."""
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from config.excepciones import OperacionCancelada
from controllers.cuenta_controller import ControladorCuenta
from controllers.departamento_controller import ControladorDepartamento
from controllers.registro_tiempo_controller import ControladorRegistroTiempo
from models.Usuarios import Administrador
from repositories.departamento_repository import RepositorioDepartamento
from repositories.usuario_repository import RepositorioUsuario
from tests.base_prueba import PruebaConBD
from views import consola, menus


def simular(entradas=(), secretas=()):
    """Sustituye input()/getpass() por respuestas predefinidas."""
    it_e, it_s = iter(entradas), iter(secretas)
    return (patch.object(consola, "_entrada", lambda _m: next(it_e)),
            patch.object(consola, "_entrada_secreta", lambda _m: next(it_s)))


class PruebaFlujo(PruebaConBD):
    def ejecutar(self, funcion, entradas=(), secretas=()):
        p1, p2 = simular(entradas, secretas)
        salida = io.StringIO()
        with p1, p2, redirect_stdout(salida):
            resultado = funcion()
        return resultado, salida.getvalue()

    def test_entrada_invalida_se_vuelve_a_pedir(self):
        valor, salida = self.ejecutar(lambda: consola.leer_entero("N", 1, 5), ["abc", "9", "0", "3"])
        self.assertEqual(valor, 3)
        self.assertEqual(salida.count("[ERROR]"), 3)

    def test_decimal_rechaza_coma_y_nan(self):
        valor, salida = self.ejecutar(lambda: consola.leer_decimal("H"), ["7,5", "nan?", "7.5"])
        self.assertEqual(valor, 7.5)
        self.assertEqual(salida.count("[ERROR]"), 2)

    def test_cancelar(self):
        with self.assertRaises(OperacionCancelada):
            self.ejecutar(lambda: consola.leer_validado("x", str), ["/cancelar"])

    def test_crear_departamento_con_datos_malos_primero(self):
        repo = RepositorioDepartamento()
        self.ejecutar(ControladorDepartamento(repo).crear, ["  ", "TI", "", "Carlos"])
        self.assertEqual([(d.nombre, d.gerente) for d in repo.listar()], [("TI", "Carlos")])

    def test_menu_no_se_cae_con_errores(self):
        repo = RepositorioDepartamento()
        ctrl = ControladorDepartamento(repo)
        # eliminar sin departamentos -> aviso; opción inválida -> error; luego salir
        _, salida = self.ejecutar(lambda: menus.ejecutar_menu("T", ctrl.opciones_menu()), ["4", "99", "0"])
        self.assertIn("No hay registros", salida)
        self.assertIn("Opción no válida", salida)

    def test_menu_atrapa_errores_inesperados(self):
        def falla():
            raise RuntimeError("boom")
        _, salida = self.ejecutar(lambda: menus.ejecutar_menu("T", {"1": ("x", falla)}), ["1", "0"])
        self.assertIn("error inesperado", salida)
        self.assertNotIn("boom", salida)  # el detalle técnico no se muestra al usuario

    def test_login_correcto_y_con_bloqueo(self):
        repo = RepositorioUsuario()
        repo.crear(Administrador(None, "admin@empresa.com", "admin12345"))
        cuenta = ControladorCuenta(repo)
        usuario, _ = self.ejecutar(cuenta.iniciar_sesion, ["admin@empresa.com"], ["admin12345"])
        self.assertEqual(usuario.correo, "admin@empresa.com")
        usuario, salida = self.ejecutar(
            cuenta.iniciar_sesion,
            ["admin@empresa.com", "otro@empresa.com", "admin@empresa.com"],
            ["mala1234", "admin12345", "tambien1234"],
        )
        self.assertIsNone(usuario)
        self.assertEqual(salida.count("Credenciales incorrectas"), 3)

    def test_cambiar_contrasena_persiste(self):
        repo = RepositorioUsuario()
        admin = Administrador(None, "admin@empresa.com", "admin12345")
        repo.crear(admin)
        self.ejecutar(lambda: ControladorCuenta(repo).cambiar_contrasena(admin), [],
                      ["admin12345", "nueva12345", "nueva12345"])
        recargado = repo.obtener_por_correo("admin@empresa.com")
        self.assertTrue(recargado.verificar_contrasena("nueva12345"))
        self.assertFalse(recargado.verificar_contrasena("admin12345"))


if __name__ == "__main__":
    unittest.main()
