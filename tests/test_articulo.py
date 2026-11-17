from dataclasses import FrozenInstanceError, replace

import pytest

from litmar import Articulo


@pytest.fixture
def articulo():
    return Articulo("Un estudio", ("García, Ana", "Pérez, Luis"), 2021)


def test_cita_corta_varios_autores(articulo):
    assert articulo.cita_corta == "García et al. (2021)"


@pytest.mark.parametrize("autor, esperado", [
    ("Ana García", "García (2021)"),
    ("García López, Ana", "García López (2021)"),
    ("García", "García (2021)"),
])
def test_cita_corta_un_autor(autor, esperado):
    assert Articulo("Estudio", (autor,), 2021).cita_corta == esperado


@pytest.mark.parametrize("doi", [
    "10.1234/ABC", " https://doi.org/10.1234/ABC ",
    "http://doi.org/10.1234/ABC", "DOI: 10.1234/ABC",
    "https://dx.doi.org/10.1234/ABC", "http://dx.doi.org/10.1234/ABC",
])
def test_normaliza_doi(articulo, doi):
    assert replace(articulo, DOI=doi).DOI == "10.1234/abc"


@pytest.mark.parametrize("doi", [None, "", "   "])
def test_doi_ausente(articulo, doi):
    assert replace(articulo, DOI=doi).DOI is None


def test_autores_y_doi_inmutables(articulo):
    autores = ["García, Ana"]
    copia = replace(articulo, autores=autores)
    autores.append("Pérez, Luis")
    assert copia.autores == ("García, Ana",)
    with pytest.raises(FrozenInstanceError):
        copia.DOI = "10.1234/otro"


@pytest.mark.parametrize("cambio", [
    {"titulo": " "}, {"autores": []}, {"autores": [" "]},
    {"año": 0}, {"año": 2021.5}, {"citas": -1}, {"citas": 1.5},
])
def test_rechaza_datos_invalidos(articulo, cambio):
    with pytest.raises(ValueError):
        replace(articulo, **cambio)


def test_rechaza_autores_como_cadena(articulo):
    with pytest.raises(TypeError):
        replace(articulo, autores="Ana García")
