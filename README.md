# Sistema de Gestión de Empleados – EcoTech Solutions

Aplicación de consola en **Python** con arquitectura **MVC + DAO** y base de datos **SQLite**
(librería oficial `sqlite3`). Asignatura TI3021 – Programación Orientada a Objeto Seguro.

## Cómo ejecutar

```bash
python main.py                                  # iniciar el sistema
python -m unittest discover -s tests -t .       # pruebas automáticas (opcional)
```

Requiere Python 3.10 o superior y no necesita instalar nada.
En la primera ejecución se crea `sistema_gestion.db` y se pide crear el primer administrador.
Solo los administradores inician sesión; ellos gestionan empleados, departamentos, proyectos y horas.

## Estructura

```
main.py                         Arranque: crea las tablas y lanza el MainController
config/database.py              Conexión a SQLite (Singleton) y creación de tablas
models/                         MODELO
  usuario.py                    Clase PADRE (correo, contraseña cifrada)
  administrador.py              HIJA de Usuario
  empleado.py                   HIJA de Usuario (+ Departamento)
  departamento.py  proyecto.py  registro_tiempo.py
  validaciones.py               Validaciones compartidas por los setters
  *_dao.py                      DAO: único lugar con SQL (crear, obtener, actualizar, eliminar)
views/                          VISTA: único lugar con input() y print()
  utils.py                      leer_numero, leer_decimal, confirmar, leer_password...
controllers/                    CONTROLADOR: une vistas, modelos y DAO
tests/test_sistema.py           Pruebas automáticas con BD temporal
```

## Dónde está cada concepto

| Concepto | Dónde |
|---|---|
| Clases del UML, atributos y constructores | `models/*.py` |
| Herencia | `Administrador` y `Empleado` heredan de `Usuario` (`super().__init__`) |
| Polimorfismo | `__str__` / `__repr__` redefinidos en cada clase hija |
| Encapsulamiento | atributos `_privados` + `@property` y setters que validan |
| Asociaciones | `Empleado.departamento`, `Registro_Tiempo.empleado` y `.proyecto` |
| Reutilización | `Usuario` (padre) y `models/validaciones.py` |
| Conexión y CRUD | `config/database.py` y `models/*_dao.py` |
| Errores | `try/except sqlite3.Error` en cada DAO; `ValueError/TypeError` en controladores |
| Seguridad | hash `scrypt` con sal, consultas con `?`, contraseña oculta con `getpass` |

> Si tenías un `sistema_gestion.db` de una versión anterior, bórralo: el esquema cambió.
