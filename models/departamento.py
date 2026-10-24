from models.validaciones import validar_texto


class Departamento:
    """
    Modelo (DTO) para la entidad Departamento.
    Atributos:
    - id_departamento (int | None): Identificador único del departamento en BD.
    - nombre (str): Nombre del departamento (e.g. Tecnología, Finanzas).
    - gerente (str): Nombre del gerente a cargo.
    """

    def __init__(self, nombre: str, gerente: str, id_departamento: int | None = None):
        self.id_departamento = id_departamento
        self.nombre = nombre
        self.gerente = gerente

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "nombre del departamento", 3, 100)

    @property
    def gerente(self) -> str:
        return self._gerente

    @gerente.setter
    def gerente(self, valor: str) -> None:
        self._gerente = validar_texto(valor, "gerente del departamento", 3, 100)

    def editar(self, nuevo_nombre: str, nuevo_gerente: str) -> None:
        self.nombre = nuevo_nombre
        self.gerente = nuevo_gerente

    def __str__(self) -> str:
        id_str = self.id_departamento if self.id_departamento is not None else "Sin asignar"
        return f"Departamento [ID: {id_str}] | Nombre: {self.nombre} | Gerente: {self.gerente}"

    def __repr__(self) -> str:
        return f"Departamento(id_departamento={self.id_departamento}, nombre='{self.nombre}', gerente='{self.gerente}')"
