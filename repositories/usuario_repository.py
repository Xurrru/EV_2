from __future__ import annotations

from config.excepciones import ErrorBaseDatos
from models.Departamento import Departamento
from models.Usuarios import Administrador, Empleado, Usuario
from repositories.base_repository import RepositorioBase
from repositories.departamento_repository import RepositorioDepartamento

# Una sola consulta sirve para ambos roles: LEFT JOIN trae los datos de empleado (o NULL).
_SELECT_USUARIO = """
    SELECT u.id_usuario, u.correo, u.password_hash, u.rol, u.id_departamento,
           e.id_empleado, e.nombre, e.direccion, e.telefono, e.email,
           e.fecha_contrato, e.salario
    FROM usuario u
    LEFT JOIN empleado e ON e.id_usuario = u.id_usuario
"""


class RepositorioUsuario(RepositorioBase[Usuario]):
    """CRUD de ``usuario`` y su especialización ``empleado`` (herencia del UML)."""

    def __init__(self, repositorio_departamentos: RepositorioDepartamento | None = None) -> None:
        super().__init__()
        self._departamentos = repositorio_departamentos or RepositorioDepartamento()

    # --- Conversión fila -> objeto ---

    def _construir(self, fila, departamentos: dict[int, Departamento]) -> Usuario:
        try:
            if fila["rol"] == "Administrador":
                return Administrador(fila["id_usuario"], fila["correo"], None, password_hash=fila["password_hash"])
            if fila["rol"] == "Empleado":
                empleado = Empleado(
                    fila["id_usuario"], fila["correo"], None, fila["id_empleado"], fila["nombre"],
                    fila["direccion"], fila["telefono"], fila["email"], fila["fecha_contrato"],
                    fila["salario"], password_hash=fila["password_hash"],
                )
                id_departamento = fila["id_departamento"]
                if id_departamento is not None:
                    departamento = departamentos.get(id_departamento) or self._departamentos.obtener_por_id(id_departamento)
                    empleado.asignar_departamento(departamento)
                return empleado
        except ValueError as error:
            raise ErrorBaseDatos(
                f"El usuario {fila['id_usuario']} tiene datos inconsistentes en la base de datos: {error}"
            ) from error
        raise ErrorBaseDatos(f"Rol desconocido en la base de datos: {fila['rol']}")

    def _consultar(self, condicion: str = "", parametros: tuple = ()) -> list[Usuario]:
        # ``condicion`` es siempre texto fijo escrito en este archivo; los valores van en ``parametros``.
        sql = f"{_SELECT_USUARIO} {condicion} ORDER BY u.id_usuario"
        with self._db.transaccion() as conn:
            filas = conn.execute(sql, parametros).fetchall()
        departamentos = {d.id_departamento: d for d in self._departamentos.listar()}
        return [self._construir(fila, departamentos) for fila in filas]

    @staticmethod
    def _id_departamento_de(usuario: Usuario) -> int | None:
        if not isinstance(usuario, Empleado) or usuario.departamento is None:
            return None
        if usuario.departamento.id_departamento is None:
            raise ValueError("El departamento asignado aún no está guardado en la base de datos.")
        return usuario.departamento.id_departamento

    # --- CRUD ---

    def crear(self, usuario: Usuario) -> None:
        self._exigir_nuevo(usuario.id_usuario, "El usuario")
        id_departamento = self._id_departamento_de(usuario)
        es_empleado = isinstance(usuario, Empleado)
        if es_empleado:
            self._exigir_nuevo(usuario.id_empleado, "El empleado")
        id_empleado = None
        # Ambos INSERT van en la misma transacción: o se guardan los dos o ninguno.
        with self._db.transaccion() as conn:
            cursor = conn.execute(
                "INSERT INTO usuario (correo, password_hash, rol, id_departamento) VALUES (?, ?, ?, ?)",
                (usuario.correo, usuario.password_hash, usuario.rol, id_departamento),
            )
            id_usuario = cursor.lastrowid
            if es_empleado:
                cursor = conn.execute(
                    "INSERT INTO empleado (id_usuario, nombre, direccion, telefono, email, fecha_contrato, salario) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (id_usuario, usuario.nombre, usuario.direccion, usuario.telefono,
                     usuario.email, usuario.fecha_contrato, usuario.salario),
                )
                id_empleado = cursor.lastrowid
        usuario.asignar_id_persistido(id_usuario)
        if es_empleado:
            usuario.asignar_id_empleado_persistido(id_empleado)

    def obtener_por_id(self, identificador: int) -> Usuario | None:
        usuarios = self._consultar("WHERE u.id_usuario = ?", (identificador,))
        return usuarios[0] if usuarios else None

    def obtener_por_correo(self, correo: str) -> Usuario | None:
        usuarios = self._consultar("WHERE u.correo = ?", (correo.strip().lower(),))
        return usuarios[0] if usuarios else None

    def obtener_empleado_por_id(self, id_empleado: int) -> Empleado | None:
        usuarios = self._consultar("WHERE e.id_empleado = ?", (id_empleado,))
        return usuarios[0] if usuarios else None

    def listar(self) -> list[Usuario]:
        return self._consultar()

    def listar_empleados(self) -> list[Empleado]:
        return self._consultar("WHERE u.rol = 'Empleado'")

    def listar_administradores(self) -> list[Administrador]:
        return self._consultar("WHERE u.rol = 'Administrador'")

    def buscar_empleados_por_nombre(self, texto: str) -> list[Empleado]:
        return self._consultar(
            r"WHERE u.rol = 'Empleado' AND e.nombre LIKE ? ESCAPE '\'", (self._patron_like(texto),)
        )

    def contar_administradores(self) -> int:
        with self._db.transaccion() as conn:
            return conn.execute("SELECT COUNT(*) FROM usuario WHERE rol = 'Administrador'").fetchone()[0]

    def actualizar(self, usuario: Usuario) -> None:
        id_usuario = self._exigir_persistido(usuario.id_usuario, "El usuario")
        id_departamento = self._id_departamento_de(usuario)
        with self._db.transaccion() as conn:
            cursor = conn.execute(
                "UPDATE usuario SET correo = ?, password_hash = ?, id_departamento = ? WHERE id_usuario = ?",
                (usuario.correo, usuario.password_hash, id_departamento, id_usuario),
            )
            self._exigir_afectadas(cursor, f"el usuario con ID {id_usuario}")
            if isinstance(usuario, Empleado):
                conn.execute(
                    "UPDATE empleado SET nombre = ?, direccion = ?, telefono = ?, email = ?, salario = ? "
                    "WHERE id_usuario = ?",
                    (usuario.nombre, usuario.direccion, usuario.telefono, usuario.email,
                     usuario.salario, id_usuario),
                )

    def eliminar(self, identificador: int) -> None:
        # Borra también la fila de empleado y sus registros de tiempo (ON DELETE CASCADE).
        with self._db.transaccion() as conn:
            cursor = conn.execute("DELETE FROM usuario WHERE id_usuario = ?", (identificador,))
            self._exigir_afectadas(cursor, f"el usuario con ID {identificador}")
