# litmar

Paquete de Python gestionado con [uv](https://docs.astral.sh/uv/).

## Estructura

```text
litmar/
├── .venv/
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── src/
    └── litmar/
        └── __init__.py
```

## Uso

Instala el paquete y sincroniza el entorno virtual:

```powershell
uv sync
```

Comprueba que el paquete se puede importar:

```powershell
uv run python -c "import litmar; print(litmar.__name__)"
```

Añade los módulos del paquete dentro de `src/litmar/`.

## Artículos y biblioteca

```python
from litmar import Articulo, Biblioteca

articulo = Articulo(
    titulo="Un estudio sobre literatura científica",
    autores=("García, Ana", "Pérez, Luis"),
    año=2021,
    DOI="https://doi.org/10.1234/ejemplo",
    revista="Revista científica",
    resumen="Resumen del estudio.",
    citas=12,
)

print(articulo.cita_corta)  # García et al. (2021)
biblioteca = Biblioteca([articulo])
texto = biblioteca.exportar_bibtex("biblioteca.bib")
```

`Articulo` es una dataclass inmutable. `titulo`, `autores` y `año` son
obligatorios; `DOI`, `revista`, `resumen` y `citas` tienen valores por defecto.
`citas` representa el número de citas recibidas y debe ser un entero no negativo.
Los autores se aceptan como lista o tupla y se conservan como tupla.
Usa `"Apellido(s), Nombre"` para conservar apellidos compuestos; si utilizas
`"Nombre Apellido"`, la cita corta toma la última palabra. Con varios autores
se añade `et al.`; con uno se muestra solo el apellido y el año.

`Biblioteca.agregar(articulo)` lanza `ValueError` si ya existe el DOI, después de
normalizar mayúsculas, espacios exteriores y prefijos `doi:`, `doi.org` o
`dx.doi.org`. Los artículos sin DOI se admiten sin deduplicar. Puedes iterar la
biblioteca, consultar `len(biblioteca)` o leer su tupla `articulos`.

`exportar_bibtex()` devuelve texto; si recibe una ruta también guarda un archivo
UTF-8. Genera entradas `@article` con claves únicas, escapa caracteres de LaTeX y
conserva los acentos en UTF-8. El resumen se exporta como `abstract` y el contador
de citas como `citations`, un campo personalizado que algunos gestores ignoran.

## Tests

```powershell
uv sync
uv run pytest
```

Los tests cubren citas cortas, validación, inmutabilidad, DOI equivalentes,
duplicados, orden de inserción y exportación BibTeX a texto y archivo.
