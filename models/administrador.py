from models.usuario import Usuario


class Administrador(Usuario):
    """
    Clase HIJA de Usuario. Hereda correo, contraseña y sus validaciones.
    Agrega los métodos propios del administrador.
    """

    def gestionar(self, entidad: str) -> str:
        if not isinstance(entidad, str) or not entidad.strip():
            raise ValueError("Debe indicar la entidad que se gestionará.")
        return f"El administrador {self.correo} gestiona: {entidad.strip()}"

    def generar_informe(self) -> str:
        return f"--- INFORME ---\nGenerado por administrador: {self.correo}"

    # Polimorfismo: se reemplaza __str__ del padre con una versión propia.
    def __str__(self) -> str:
        id_str = self.id_usuario if self.id_usuario is not None else "Sin asignar"
        return f"Administrador [ID: {id_str}] | Correo: {self.correo}"

    def __repr__(self) -> str:
        return f"Administrador(id_usuario={self.id_usuario}, correo='{self.correo}')"
