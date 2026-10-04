from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator


class TipoConector(StrEnum):
    TIPO1 = "TIPO1"
    TIPO2 = "TIPO2"
    CCS1 = "CCS1"
    CCS2 = "CCS2"
    CHADEMO = "CHADEMO"
    GBT = "GBT"


class EstadoConector(StrEnum):
    DISPONIBLE = "DISPONIBLE"
    OCUPADO = "OCUPADO"
    FUERA_DE_SERVICIO = "FUERA_DE_SERVICIO"
    DESCONOCIDO = "DESCONOCIDO"


class Corriente(StrEnum):
    AC = "AC"
    DC = "DC"


SOLO_AC = {TipoConector.TIPO1, TipoConector.TIPO2}
SOLO_DC = {TipoConector.CCS1, TipoConector.CCS2, TipoConector.CHADEMO}


class Conector(BaseModel):
    tipo: TipoConector
    corriente: Corriente
    potencia_kw: float = Field(gt=0, le=400)
    estado: EstadoConector = EstadoConector.DESCONOCIDO

    @model_validator(mode="after")
    def validar_corriente(self) -> Self:
        if self.tipo in SOLO_AC and self.corriente is not Corriente.AC:
            raise ValueError(f"{self.tipo} solo funciona con corriente AC")
        if self.tipo in SOLO_DC and self.corriente is not Corriente.DC:
            raise ValueError(f"{self.tipo} solo funciona con corriente DC")
        return self


BOGOTA_LAT_MIN = 4.4699
BOGOTA_LAT_MAX = 4.8227
BOGOTA_LON_MIN = -74.2144
BOGOTA_LON_MAX = -74.0128


class Estacion(BaseModel):
    id: str
    nombre: str = Field(min_length=1)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    direccion: str | None = None
    operador: str | None = None
    conectores: list[Conector] = Field(default_factory=list)

    @property
    def potencia_max_kw(self) -> float:
        return max((c.potencia_kw for c in self.conectores), default=0.0)

    def tiene_conector(self, tipo: TipoConector) -> bool:
        return any(c.tipo == tipo for c in self.conectores)

    def esta_en_bogota(self) -> bool:
        return (
            BOGOTA_LAT_MIN <= self.lat <= BOGOTA_LAT_MAX
            and BOGOTA_LON_MIN <= self.lon <= BOGOTA_LON_MAX
        )
