from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class Pedido:
    id: int
    usuario: str
    items: List[Dict]  # lista de items en el carrito
    direccion_destino: str
    estado: str = "pendiente"  # pendiente, en_proceso, completado
    conductor: str = None
    fecha_creacion: datetime = None
    
    def __init__(self, id: int, usuario: str, items: List[Dict], direccion_destino: str):
        self.id = id
        self.usuario = usuario
        self.items = items
        self.direccion_destino = direccion_destino
        self.fecha_creacion = datetime.now()
    
    def tomar_pedido(self, conductor: str):
        if self.estado == "pendiente":
            self.estado = "en_proceso"
            self.conductor = conductor
            return True
        return False
    
    def completar_pedido(self):
        if self.estado == "en_proceso":
            self.estado = "completado"
            return True
        return False

# lista global para almacenar todos los pedidos
PEDIDOS = [] 