from dataclasses import dataclass
from datetime import timedelta
import os
import json

@dataclass
class Conductor:
    nombre: str
    salario_base: float  # salario mensual base
    viaticos_diarios: float  # viáticos diarios para comida y alojamiento
    horas_conduccion_maximas: int = 8  # horas máximas de conducción por día
    horas_descanso: int = 11  # horas de descanso requeridas entre turnos
    
    def calcular_costo_viaje(self, dias_viaje: int) -> float:
        ### calcula el costo total para un conductor durante el viaje
        costo_diario = self.salario_base / 30 + self.viaticos_diarios
        return costo_diario * dias_viaje
    
    def calcular_duracion_viaje(self, distancia_km: float, velocidad_promedio_kmh: float) -> timedelta:
        ### calcula la duración total del viaje considerando las regulaciones de conducción
        horas_conduccion = distancia_km / velocidad_promedio_kmh
        dias_necesarios = horas_conduccion / self.horas_conduccion_maximas
        return timedelta(days=dias_necesarios)

# configuración predeterminada del conductor
CONDUCTOR_PREDETERMINADO = Conductor(
    nombre="Juan Pérez",
    salario_base=150000,  # $150,000 por mes
    viaticos_diarios=5000  # $5,000 por día
)

CONDUCTORES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'conductores.json')

def cargar_conductores():
    if not os.path.exists(CONDUCTORES_FILE):
        return []
    try:
        with open(CONDUCTORES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def guardar_conductores(conductores):
    with open(CONDUCTORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(conductores, f, ensure_ascii=False, indent=4)
