from models.validaciones import validar_fecha, validar_texto


class Proyecto:
    """
    Modelo (DTO) para la entidad Proyecto.
    Atributos:
    - id_proyecto (int | None): Identificador único en BD.
    - nombre (str): Nombre del proyecto.
    - descripcion (str): Breve descripción.
    - fecha_inicio (str): Fecha de inicio en formato AAAA-MM-DD.
    """

    def __init__(self, nombre: str, descripcion: str, fecha_inicio: str, id_proyecto: int | None = None):
        self.id_proyecto = id_proyecto
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "nombre del proyecto", 3, 100)

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        self._descripcion = validar_texto(valor, "descripción del proyecto", 3, 300)

    @property
    def fecha_inicio(self) -> str:
        return self._fecha_inicio

    @fecha_inicio.setter
    def fecha_inicio(self, valor: str) -> None:
        self._fecha_inicio = validar_fecha(valor, "fecha de inicio")

    def editar(self, nuevo_nombre: str, nueva_descripcion: str) -> None:
        self.nombre = nuevo_nombre
        self.descripcion = nueva_descripcion

    def __str__(self) -> str:
        id_str = self.id_proyecto if self.id_proyecto is not None else "Sin asignar"
        return (f"Proyecto [ID: {id_str}] | Nombre: {self.nombre} | Inicio: {self.fecha_inicio} "
                f"| Descripción: {self.descripcion}")

    def __repr__(self) -> str:
        return (f"Proyecto(id_proyecto={self.id_proyecto}, nombre='{self.nombre}', "
                f"descripcion='{self.descripcion}', fecha_inicio='{self.fecha_inicio}')")
