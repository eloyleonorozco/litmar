from dataclasses import replace

import pytest

from litmar import Articulo, Biblioteca


@pytest.fixture
def articulo():
    return Articulo(
        "Un estudio", ("García, Ana", "Pérez, Luis"), 2021,
        DOI="10.1234/ABC", revista="Revista científica",
        resumen="Resultados del estudio", citas=12,
    )


def test_coleccion_y_orden(articulo):
    segundo = replace(articulo, DOI="10.1234/otro")
    biblioteca = Biblioteca([articulo])
    biblioteca.agregar(segundo)
    assert len(biblioteca) == 2
    assert list(biblioteca) == [articulo, segundo]
    assert biblioteca.articulos == (articulo, segundo)


def test_duplicado_no_modifica_biblioteca(articulo):
    biblioteca = Biblioteca([articulo])
    with pytest.raises(ValueError, match="DOI duplicado"):
        biblioteca.agregar(replace(articulo, DOI=" HTTPS://DOI.ORG/10.1234/abc "))
    assert biblioteca.articulos == (articulo,)


def test_constructor_rechaza_duplicados(articulo):
    with pytest.raises(ValueError, match="DOI duplicado"):
        Biblioteca([articulo, articulo])


def test_admite_varios_articulos_sin_doi(articulo):
    sin_doi = replace(articulo, DOI=None)
    assert len(Biblioteca([sin_doi, sin_doi])) == 2


def test_rechaza_otros_objetos():
    with pytest.raises(TypeError):
        Biblioteca().agregar("un artículo")


def test_exportacion_completa(articulo):
    assert Biblioteca([articulo]).exportar_bibtex() == (
        "@article{Garcia2021,\n"
        "  title = {Un estudio},\n"
        "  author = {García, Ana and Pérez, Luis},\n"
        "  year = {2021},\n"
        "  journal = {Revista científica},\n"
        "  doi = {10.1234/abc},\n"
        "  abstract = {Resultados del estudio},\n"
        "  citations = {12},\n"
        "}\n"
    )


def test_guarda_utf8(articulo, tmp_path):
    ruta = tmp_path / "biblioteca.bib"
    resultado = Biblioteca([articulo]).exportar_bibtex(ruta)
    assert ruta.read_text(encoding="utf-8") == resultado
    assert "García" in resultado


def test_claves_unicas_y_estables(articulo):
    biblioteca = Biblioteca([replace(articulo, DOI=None)] * 3)
    texto = biblioteca.exportar_bibtex()
    assert "@article{Garcia2021," in texto
    assert "@article{Garcia2021_2," in texto
    assert "@article{Garcia2021_3," in texto
    assert biblioteca.exportar_bibtex() == texto


def test_escapa_caracteres_bibtex(articulo):
    articulo = replace(articulo, titulo="A & B {50%} $x_1$ # ~ ^ " + chr(92))
    texto = Biblioteca([articulo]).exportar_bibtex()
    assert r"A \& B \{50\%\} \$x\_1\$ \# \textasciitilde{} \textasciicircum{} \textbackslash{}" in texto


def test_omite_campos_opcionales(articulo):
    texto = Biblioteca([replace(articulo, DOI=None, resumen="")]).exportar_bibtex()
    assert "  doi =" not in texto
    assert "  abstract =" not in texto


def test_biblioteca_vacia(tmp_path):
    ruta = tmp_path / "vacia.bib"
    assert Biblioteca().exportar_bibtex(ruta) == ""
    assert ruta.read_text(encoding="utf-8") == ""
