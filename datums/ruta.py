from dataclasses import dataclass
from typing import List, Tuple
import math

@dataclass
class PuntoRuta:
    nombre: str
    latitud: float
    longitud: float
    tiene_peaje: bool = False
    limite_velocidad: float = 100.0  # km/h
    estado_camino: str = "bueno"  # bueno, regular, malo

@dataclass
class Ruta:
    puntos: List[PuntoRuta]
    distancia_km: float
    tiempo_estimado_horas: float
    costo_peajes: float
    paradas_combustible: List[Tuple[float, str]]  # (distancia_km, nombre_ubicacion)
    
    @staticmethod
    def calcular_distancia(punto1: PuntoRuta, punto2: PuntoRuta) -> float:
        # calcula la distancia entre dos puntos usando la fórmula de haversine
        R = 6371  # radio de la tierra en kilometros
        
        lat1, lon1 = math.radians(punto1.latitud), math.radians(punto1.longitud)
        lat2, lon2 = math.radians(punto2.latitud), math.radians(punto2.longitud)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
