"""Colección de artículos y exportación a BibTeX."""

from collections.abc import Iterable, Iterator
from pathlib import Path
import re
import unicodedata

from .articulo import Articulo


def _escapar_bibtex(texto: str) -> str:
    reemplazos = {
        "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}",
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(reemplazos.get(caracter, caracter) for caracter in texto)


class Biblioteca:
    """Conserva el orden de inserción y rechaza DOI repetidos.

    Los artículos sin DOI se admiten sin deduplicar.
    """

    def __init__(self, articulos: Iterable[Articulo] = ()) -> None:
        self._articulos: list[Articulo] = []
        self._dois: set[str] = set()
        for articulo in articulos:
            self.agregar(articulo)

    @property
    def articulos(self) -> tuple[Articulo, ...]:
        """Vista inmutable de los artículos en orden de inserción."""
        return tuple(self._articulos)

    def __len__(self) -> int:
        return len(self._articulos)

    def __iter__(self) -> Iterator[Articulo]:
        return iter(self._articulos)

    def agregar(self, articulo: Articulo) -> None:
        """Añade un artículo; lanza ValueError si el DOI ya existe."""
        if not isinstance(articulo, Articulo):
            raise TypeError("Solo se pueden agregar objetos Articulo")
        if articulo.DOI and articulo.DOI in self._dois:
            raise ValueError(f"DOI duplicado: {articulo.DOI}")
        self._articulos.append(articulo)
        if articulo.DOI:
            self._dois.add(articulo.DOI)

    def exportar_bibtex(self, ruta: str | Path | None = None) -> str:
        """Devuelve BibTeX y, opcionalmente, lo guarda como UTF-8.

        El contador de citas se exporta en el campo personalizado «citations».
        Las claves se generan por apellido y año, con sufijos si colisionan.
        """
        entradas: list[str] = []
        claves: set[str] = set()
        for articulo in self:
            apellido = unicodedata.normalize("NFKD", articulo.apellido_primer_autor)
            apellido = apellido.encode("ascii", "ignore").decode("ascii")
            apellido = re.sub(r"[^a-zA-Z0-9]", "", apellido) or "articulo"
            base = f"{apellido}{articulo.año}"
            clave = base
            numero = 2
            while clave in claves:
                clave = f"{base}_{numero}"
                numero += 1
            claves.add(clave)
            campos = {
                "title": _escapar_bibtex(articulo.titulo),
                "author": " and ".join(_escapar_bibtex(a) for a in articulo.autores),
                "year": str(articulo.año),
                "journal": _escapar_bibtex(articulo.revista),
            }
            if articulo.DOI:
                campos["doi"] = _escapar_bibtex(articulo.DOI)
            if articulo.resumen:
                campos["abstract"] = _escapar_bibtex(articulo.resumen)
            campos["citations"] = str(articulo.citas)
            lineas = [f"  {campo} = {{{valor}}}," for campo, valor in campos.items()]
            entradas.append(f"@article{{{clave},\n" + "\n".join(lineas) + "\n}")
        resultado = "\n\n".join(entradas) + ("\n" if entradas else "")
        if ruta is not None:
            Path(ruta).write_text(resultado, encoding="utf-8")
        return resultado
