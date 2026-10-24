import hashlib
import hmac
import os

from models.validaciones import validar_correo


class Usuario:
    """
    Clase PADRE. Administrador y Empleado heredan de ella.
    Guarda los datos que ambos tienen en común: correo y contraseña.
    La contraseña NUNCA se guarda en texto plano: se guarda un hash scrypt con sal.

    Atributos:
    - id_usuario (int | None): Identificador en la BD.
    - correo (str): Correo de acceso al sistema.
    - password_hash (str): Contraseña cifrada (solo lectura).
    """

    def __init__(self, correo: str, password: str | None, id_usuario: int | None = None,
                 password_hash: str | None = None):
        self.id_usuario = id_usuario
        self.correo = correo
        if password_hash is not None:
            # El objeto viene de la BD: la contraseña ya está cifrada.
            self._password_hash = password_hash
        else:
            # Objeto nuevo: se valida y se cifra la contraseña recibida.
            self.establecer_password(password)

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        self._correo = validar_correo(valor, "correo")

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def rol(self) -> str:
        # Devuelve "Administrador" o "Empleado" según la clase hija.
        return self.__class__.__name__

    @staticmethod
    def _cifrar(password: str, sal: bytes) -> bytes:
        return hashlib.scrypt(password.encode("utf-8"), salt=sal, n=2**14, r=8, p=1)

    def establecer_password(self, password: str) -> None:
        if not isinstance(password, str):
            raise TypeError("La contraseña debe ser texto.")
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if len(password) > 128:
            raise ValueError("La contraseña no puede superar los 128 caracteres.")
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            raise ValueError("La contraseña debe combinar letras y números.")
        sal = os.urandom(16)  # sal aleatoria: dos contraseñas iguales dan hashes distintos
        self._password_hash = sal.hex() + "$" + self._cifrar(password, sal).hex()

    def verificar_password(self, password: str) -> bool:
        try:
            sal_hex, hash_hex = self._password_hash.split("$")
            hash_ingresado = self._cifrar(password, bytes.fromhex(sal_hex))
            # compare_digest compara en tiempo constante (evita ataques de temporización)
            return hmac.compare_digest(bytes.fromhex(hash_hex), hash_ingresado)
        except (ValueError, AttributeError):
            return False

    def cambiar_password(self, password_actual: str, password_nueva: str) -> None:
        if not self.verificar_password(password_actual):
            raise ValueError("La contraseña actual es incorrecta.")
        self.establecer_password(password_nueva)

    def __str__(self) -> str:
        id_str = self.id_usuario if self.id_usuario is not None else "Sin asignar"
        return f"Usuario [ID: {id_str}] | Correo: {self.correo}"

    def __repr__(self) -> str:
        return f"Usuario(id_usuario={self.id_usuario}, correo='{self.correo}')"
