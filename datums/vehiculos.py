from dataclasses import dataclass
from typing import Optional

@dataclass
class Vehiculo:
    nombre: str
    capacidad_kg: float  # capacidad en kilogramos
    consumo_combustible: float  # litros por 100km
    tipo_combustible: str
    costo_combustible_por_litro: float
    costo_mantenimiento_por_km: float
    
    def calcular_costo_combustible(self, distancia_km: float) -> float:
        # calculo de combustible necesario para la distancia
        combustible_necesario = (distancia_km * self.consumo_combustible) / 100
        return combustible_necesario * self.costo_combustible_por_litro
    
    def calcular_costo_mantenimiento(self, distancia_km: float) -> float:
        # calculo de costo de mantenimiento para la distancia
        return distancia_km * self.costo_mantenimiento_por_km
    
    def puede_transportar_peso(self, peso_kg: float) -> bool:
        # verifica si el vehiculo puede transportar el peso especificado
        return peso_kg <= self.capacidad_kg

# vehículos predefinidos
VEHICULOS_DISPONIBLES = {
    # https://www.citroen.com.ar/content/dam/citroen/argentina/ficha-tecnica/ENE_FT_BERLINGO_FURGON.pdf
    "Citroën Berlingo Furgón": Vehiculo(
        nombre="Citroën Berlingo Furgón",
        capacidad_kg=800,  
        consumo_combustible=10,  # 10L/100km
        tipo_combustible="Nafta Premium",
        costo_combustible_por_litro=1100,  # peso por litro
        costo_mantenimiento_por_km=12000  # peso por km
    )
}