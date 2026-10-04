import pytest
from pydantic import ValidationError

from cargadores_core.modelos import (
    Conector,
    Corriente,
    Estacion,
    EstadoConector,
    TipoConector,
)


def test_potencia_maxima():
    e = Estacion(
        id="1",
        nombre="X",
        lat=4.6,
        lon=-74.1,
        conectores=[
            Conector(tipo=TipoConector.TIPO2, corriente=Corriente.AC, potencia_kw=7.4),
            Conector(tipo=TipoConector.CCS2, corriente=Corriente.DC, potencia_kw=120),
        ],
    )
    assert e.potencia_max_kw == 120
    assert e.tiene_conector(TipoConector.CCS2)
    assert not e.tiene_conector(TipoConector.CHADEMO)


def test_estacion_sin_conectores():
    e = Estacion(id="1", nombre="X", lat=4.6, lon=-74.1)
    assert e.potencia_max_kw == 0.0


@pytest.mark.parametrize("potencia", [0, -5, 500])
def test_potencia_invalida(potencia):
    with pytest.raises(ValidationError):
        Conector(tipo=TipoConector.TIPO2, corriente=Corriente.AC, potencia_kw=potencia)


def test_ccs2_no_acepta_ac():
    with pytest.raises(ValidationError):
        Conector(tipo=TipoConector.CCS2, corriente=Corriente.AC, potencia_kw=50)


def test_estado_conector_vacio():
    c = Conector(tipo=TipoConector.TIPO2, corriente=Corriente.AC, potencia_kw=7.4)
    assert c.estado is EstadoConector.DESCONOCIDO


def test_estado_invalido():
    with pytest.raises(ValidationError):
        Conector(
            tipo=TipoConector.CCS2,
            corriente=Corriente.DC,
            potencia_kw=50,
            estado="ROTO",
        )


def estacion_en(lat: float, lon: float) -> Estacion:
    return Estacion(id="1", nombre="Prueba", lat=lat, lon=lon)


def test_plaza_de_bolivar_esta_en_bogota():
    assert estacion_en(4.5981, -74.0760).esta_en_bogota()


@pytest.mark.parametrize(
    ("lat", "lon"),
    [
        (4.8619, -74.0587),  # Chía (norte)
        (4.3365, -74.3638),  # Fusagasugá (sur)
        (4.7206, -73.9697),  # La Calera (oriente)
        (4.7059, -74.2302),  # Mosquera (occidente)
        (6.2442, -75.5812),
    ],
)
def test_puntos_fuera_bogota(lat, lon):
    assert not estacion_en(lat, lon).esta_en_bogota()
