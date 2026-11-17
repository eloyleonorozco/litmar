"""Modelo de un artículo científico."""

from dataclasses import dataclass


def normalizar_doi(doi: str | None) -> str:
    """Unifica DOI desnudos, con prefijo DOI: y con URL del resolutor."""
    valor = (doi or "").strip().casefold()
    for prefijo in (
        "https://doi.org/", "http://doi.org/",
        "https://dx.doi.org/", "http://dx.doi.org/", "doi:",
    ):
        if valor.startswith(prefijo):
            return valor[len(prefijo):].strip()
    return valor


@dataclass(frozen=True, slots=True)
class Articulo:
    """Datos bibliográficos; citas es el número de citas recibidas.

    Los autores se aceptan como lista o tupla y se almacenan como tupla.
    Se recomienda «Apellido(s), Nombre» para conservar apellidos compuestos;
    con «Nombre Apellido» se toma la última palabra como apellido.
    """

    titulo: str
    autores: tuple[str, ...]
    año: int
    DOI: str | None = None
    revista: str = ""
    resumen: str = ""
    citas: int = 0

    def __post_init__(self) -> None:
        if not self.titulo.strip():
            raise ValueError("El título no puede estar vacío")
        if isinstance(self.autores, str):
            raise TypeError("autores debe ser una colección de nombres")
        autores = tuple(autor.strip() for autor in self.autores)
        if not autores or any(not autor for autor in autores):
            raise ValueError("Debe haber al menos un autor con nombre")
        if type(self.año) is not int or self.año < 1:
            raise ValueError("El año debe ser un entero positivo")
        if type(self.citas) is not int or self.citas < 0:
            raise ValueError("Las citas deben ser un entero no negativo")
        object.__setattr__(self, "autores", autores)
        object.__setattr__(self, "DOI", normalizar_doi(self.DOI) or None)

    @property
    def apellido_primer_autor(self) -> str:
        """Apellido usado para la cita corta y la clave BibTeX."""
        autor = self.autores[0]
        return autor.split(",", 1)[0] if "," in autor else autor.split()[-1]

    @property
    def cita_corta(self) -> str:
        """Devuelve, por ejemplo, «García et al. (2021)»."""
        sufijo = " et al." if len(self.autores) > 1 else ""
        return f"{self.apellido_primer_autor}{sufijo} ({self.año})"
