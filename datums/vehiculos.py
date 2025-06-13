from dataclasses import dataclass

@dataclass
class Vehiculo:
    nombre: str
    combustible: str
    capacidad_tanque: float
    capacidad_maxima: float
    velocidad_promedio: float
    consumicion_combustible: float
    costo_mantenimiento: float
    costo_combustible: float

# https://www.citroen.com.ar/content/dam/citroen/argentina/ficha-tecnica/ENE_FT_BERLINGO_FURGON.pdf
berlingo_furgon = Vehiculo(
    nombre="Citroën Berlingo Furgón",
    combustible="Nafta Premium",
    capacidad_tanque=55, #litros
    capacidad_maxima=800, #kg
    velocidad_promedio=100, #km/h
    consumicion_combustible=10, #L/100km
    costo_mantenimiento=12000, #pesos
    costo_combustible=1100, #pesos/litro
)