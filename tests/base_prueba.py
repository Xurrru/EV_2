"""Utilidades comunes: cada prueba trabaja con una base de datos temporal y aislada."""
from __future__ import annotations

import logging
import tempfile
import unittest
from pathlib import Path

from config.Base_Datos import Database


logging.disable(logging.CRITICAL)  # los errores esperados de las pruebas no deben ensuciar la consola


class PruebaConBD(unittest.TestCase):
    def setUp(self) -> None:
        self._ruta_original = Database._db_path
        self._carpeta = tempfile.TemporaryDirectory()
        Database.configurar_ruta(Path(self._carpeta.name) / "prueba.db")
        Database().init_db()

    def tearDown(self) -> None:
        Database.configurar_ruta(self._ruta_original)
        self._carpeta.cleanup()
