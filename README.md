# Sistema de Gestión de Empleados – EcoTech Solutions

Aplicación de consola en **Python (POO)** con base de datos **SQLite** (librería oficial `sqlite3`).
Asignatura TI3021 – Programación Orientada a Objeto Seguro – Evaluación Sumativa 2.

## Cómo ejecutar

```bash
python app.py                                   # iniciar el sistema
python -m unittest discover -s tests -t .       # ejecutar las pruebas automáticas
```

Requiere Python 3.10 o superior y **no necesita instalar nada** (solo biblioteca estándar).
En la primera ejecución el sistema crea `sistema_gestion.db` y pide crear el primer administrador.

## Estructura y responsabilidades

```
app.py                      Punto de entrada: ensambla las capas y arranca la sesión
config/
  Base_Datos.py             Conexión (Singleton), transacciones, creación de tablas
  excepciones.py            Excepciones propias (ErrorBaseDatos, RegistroNoEncontrado...)
models/                     CLASES DEL UML (sin print, sin input, sin SQL)
  Usuarios.py               Usuario (abstracta) -> Administrador, Empleado
  Departamento.py  Proyecto.py  Registro_Tiempo.py
  validaciones.py           Reglas de validación reutilizables
repositories/               ACCESO A DATOS: único lugar con SQL (CRUD)
  base_repository.py        Clase abstracta RepositorioBase (contrato CRUD)
  departamento_ / proyecto_ / usuario_ / registro_tiempo_repository.py
controllers/                LÓGICA DE LA APLICACIÓN: une vistas, modelos y repositorios
  base_controller.py        Clase abstracta ControladorCRUD
  departamento_ / proyecto_ / empleado_ / administrador_ / registro_tiempo_ / cuenta_controller.py
views/                      ENTRADA/SALIDA: único lugar con input() y print()
  consola.py                Lectura validada, tablas, confirmaciones
  menus.py                  Motor de menús + captura central de errores
tests/                      Pruebas automáticas (unittest) con BD temporal
```

## Reglas de diseño

* **Modelos**: encapsulamiento (`_atributos` + `@property` con validación), herencia y asociaciones bidireccionales.
* **Contraseñas**: hash `scrypt` con sal aleatoria; nunca se guarda ni se muestra el texto plano.
* **SQL**: todas las consultas son parametrizadas (`?`); no se concatenan datos del usuario.
* **IDs**: los asigna la base de datos (`INTEGER PRIMARY KEY`); el usuario no los digita.
* **Errores**: `try/except` en conexión, en cada operación y en los menús; los detalles técnicos van a `sistema.log`.
* **Roles**: el administrador gestiona todo; el empleado solo ve y modifica sus propios registros de tiempo.

> Si ya tenías un `sistema_gestion.db` de una versión anterior, bórralo: el esquema ahora incluye restricciones nuevas.
