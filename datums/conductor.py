from dataclasses import dataclass
from datetime import timedelta

@dataclass
class Conductor:
    nombre: str
    salario_base: float  # Salario mensual base
    viaticos_diarios: float  # Viáticos diarios para comida y alojamiento
    horas_conduccion_maximas: int = 8  # Horas máximas de conducción por día
    horas_descanso: int = 11  # Horas de descanso requeridas entre turnos
    
    def calcular_costo_viaje(self, dias_viaje: int) -> float:
        """Calcula el costo total para un conductor durante el viaje."""
        costo_diario = self.salario_base / 30 + self.viaticos_diarios
        return costo_diario * dias_viaje
    
    def calcular_duracion_viaje(self, distancia_km: float, velocidad_promedio_kmh: float) -> timedelta:
        """Calcula la duración total del viaje considerando las regulaciones de conducción."""
        horas_conduccion = distancia_km / velocidad_promedio_kmh
        dias_necesarios = horas_conduccion / self.horas_conduccion_maximas
        return timedelta(days=dias_necesarios)

# Configuración predeterminada del conductor
CONDUCTOR_PREDETERMINADO = Conductor(
    nombre="Juan Pérez",
    salario_base=150000,  # $150,000 por mes
    viaticos_diarios=5000  # $5,000 por día
)
