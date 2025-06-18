import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datums.vehiculos import VEHICULOS_DISPONIBLES, Vehiculo
from datums.conductor import CONDUCTOR_PREDETERMINADO
from datums.ruta import PuntoRuta, Ruta
from datums.pedido import PEDIDOS, Pedido
import math
import requests
import googlemaps
import os
from dotenv import load_dotenv
import json
from datetime import datetime

class CalculadoraLogistica:
    def __init__(self, root):
        self.peso_carga = tk.DoubleVar(value=500) # 500 kg
        self.vehiculo_seleccionado = tk.StringVar(value="Citroën Berlingo Furgón")
        
        # Vehiculo Personalizado
        self.nombre_vehiculo = tk.StringVar()
        self.capacidad_vehiculo = tk.DoubleVar()
        self.volumen_vehiculo = tk.DoubleVar()
        self.consumo_vehiculo = tk.DoubleVar()
        self.tipo_combustible = tk.StringVar(value="Nafta Premium")
        self.costo_combustible = tk.DoubleVar(value=1100)
        self.costo_mantenimiento = tk.DoubleVar(value=12000)
        
        # Geocoder
        self.geocoder = Nominatim(user_agent="calculadora_logistica")
        
        # Google Maps
        load_dotenv()  # Cargar variables de entorno
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            messagebox.showerror("Error", 
                "No se encontró la clave de API de Google Maps.\n" +
                "Por favor, crea un archivo .env con tu clave de API:\n" +
                "GOOGLE_MAPS_API_KEY=tu_clave_aqui")
            root.destroy()
            return
            
        try:
            self.gmaps = googlemaps.Client(key=api_key)
            # Usar geopy para obtener coordenadas precisas
            origen = self.geocoder.geocode("Puerto de Rosario, Santa Fe, Argentina")
            destino = self.geocoder.geocode("Rosario, Santa Fe, Argentina")
            if not origen or not destino:
                raise Exception("No se pudo geocodificar una de las direcciones.")
            origen_coords = f"{origen.latitude},{origen.longitude}"
            destino_coords = f"{destino.latitude},{destino.longitude}"
            # Verificar que la API funciona usando coordenadas
            self.gmaps.directions(
                origen_coords,
                destino_coords,
                mode="driving"
            )
        except Exception as e:
            messagebox.showerror("Error", 
                f"Error al inicializar Google Maps API: {str(e)}\n" +
                "Por favor, verifica tu clave de API, la API de Directions y las direcciones.")
            root.destroy()
            return
        
        # Ventana Principal
        self.root = root
        self.root.title("Calculadora de Logística")
        self.root.geometry("1200x800")
        
        self.marco_principal = ttk.Frame(root)
        self.marco_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Inicializar variables de archivo antes de cargar pedidos
        self.data_dir = "data"
        self.pedidos_file = os.path.join(self.data_dir, "pedidos.json")
        
        # mapa
        self.crear_panel_mapa()
        
        # calculos
        self.crear_panel_calculos()
        
        # Cargar pedidos después de que todo esté inicializado
        self.cargar_pedidos()
        
    def crear_panel_mapa(self):
        marco_mapa = ttk.LabelFrame(self.marco_principal, text="Mapa de Ruta")
        marco_mapa.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.mapa = TkinterMapView(marco_mapa, width=600, height=500, corner_radius=0)
        self.mapa.pack(fill="both", expand=True)
        self.mapa.set_position(-32.9510139, -60.6260167)  # Puerto de Rosario
        self.mapa.set_zoom(8)
        
        self.marcador_puerto_rosario = self.mapa.set_marker(-32.9510139, -60.6260167, "Puerto de Rosario")
        
        # ruta
        self.ruta_actual = None
        
    def crear_panel_calculos(self):
        marco_calculos = ttk.LabelFrame(self.marco_principal, text="Cálculos")
        marco_calculos.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Crear pestañas
        notebook = ttk.Notebook(marco_calculos)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Pestaña de pedidos
        pestaña_pedidos = ttk.Frame(notebook)
        notebook.add(pestaña_pedidos, text="Pedidos")
        
        # Pestaña de cálculo
        pestaña_calculo = ttk.Frame(notebook)
        notebook.add(pestaña_calculo, text="Cálculo de Ruta")
        
        # Pestaña de nuevo vehículo
        pestaña_vehiculo = ttk.Frame(notebook)
        notebook.add(pestaña_vehiculo, text="Nuevo Vehículo")
        
        # Crear paneles
        self.crear_panel_pedidos(pestaña_pedidos)
        self.crear_panel_calculo_ruta(pestaña_calculo)
        self.crear_panel_nuevo_vehiculo(pestaña_vehiculo)
        
    def crear_panel_pedidos(self, parent):
        # Frame para lista de pedidos
        frame_pedidos = ttk.LabelFrame(parent, text="Pedidos Pendientes")
        frame_pedidos.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Treeview para pedidos
        self.tree_pedidos = ttk.Treeview(frame_pedidos, columns=("ID", "Usuario", "Dirección", "Items", "Estado"), show="headings")
        self.tree_pedidos.heading("ID", text="ID")
        self.tree_pedidos.heading("Usuario", text="Usuario")
        self.tree_pedidos.heading("Dirección", text="Dirección")
        self.tree_pedidos.heading("Items", text="Items")
        self.tree_pedidos.heading("Estado", text="Estado")
        self.tree_pedidos.pack(fill="both", expand=True, pady=5)
        
        # Botón para tomar pedido
        ttk.Button(frame_pedidos, text="Tomar Pedido Seleccionado", 
                  command=self.tomar_pedido).pack(pady=5)
        
        # Botón para actualizar lista
        ttk.Button(frame_pedidos, text="Actualizar Lista", 
                  command=self.actualizar_lista_pedidos).pack(pady=5)
        
        # Inicializar lista
        self.actualizar_lista_pedidos()
    
    def actualizar_lista_pedidos(self):
        self.cargar_pedidos()  # Asegura que siempre se lean los pedidos más recientes del archivo
        # Limpiar lista actual
        for item in self.tree_pedidos.get_children():
            self.tree_pedidos.delete(item)
        # Agregar pedidos pendientes
        for pedido in PEDIDOS:
            if pedido.estado == "pendiente":
                # Formatear items para mostrar
                items_texto = []
                for item in pedido.items:
                    items_texto.append(f"{item['cantidad']}x {item['nombre']}")
                items_str = ", ".join(items_texto)
                
                self.tree_pedidos.insert("", "end", values=(
                    pedido.id,
                    pedido.usuario,
                    pedido.direccion_destino,
                    items_str,
                    pedido.estado
                ))
    
    def tomar_pedido(self):
        # Obtener pedido seleccionado
        seleccion = self.tree_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un pedido")
            return
        
        # Obtener ID del pedido
        pedido_id = int(self.tree_pedidos.item(seleccion[0])["values"][0])
        
        # Encontrar pedido
        pedido = next((p for p in PEDIDOS if p.id == pedido_id), None)
        if not pedido:
            messagebox.showerror("Error", "Pedido no encontrado")
            return
        
        # Tomar pedido
        if pedido.tomar_pedido(CONDUCTOR_PREDETERMINADO.nombre):
            self.guardar_pedidos()
            messagebox.showinfo("Éxito", f"Pedido #{pedido_id} tomado exitosamente")
            self.actualizar_lista_pedidos()
            
            # Establecer dirección de destino en el mapa
            self.destino_direccion.set(pedido.direccion_destino)
        else:
            messagebox.showerror("Error", "No se pudo tomar el pedido")
    
    def guardar_pedidos(self):
        pedidos_data = []
        for pedido in PEDIDOS:
            pedido_dict = {
                "id": pedido.id,
                "usuario": pedido.usuario,
                "items": pedido.items,
                "direccion_destino": pedido.direccion_destino,
                "estado": pedido.estado,
                "conductor": pedido.conductor,
                "fecha_creacion": pedido.fecha_creacion.isoformat() if pedido.fecha_creacion else None
            }
            pedidos_data.append(pedido_dict)
        with open(self.pedidos_file, 'w', encoding='utf-8') as f:
            json.dump(pedidos_data, f, ensure_ascii=False, indent=4)
    
    def crear_panel_calculo_ruta(self, parent):
        # Frame para ruta
        frame_ruta = ttk.LabelFrame(parent, text="Cálculo de Ruta")
        frame_ruta.pack(fill="x", padx=5, pady=5)
        
        # vehiculos
        ttk.Label(frame_ruta, text="Vehículo:").pack(pady=5)
        combo_vehiculo = ttk.Combobox(frame_ruta, textvariable=self.vehiculo_seleccionado)
        combo_vehiculo['values'] = list(VEHICULOS_DISPONIBLES.keys())
        combo_vehiculo.pack(pady=5)
        
        # peso de carga
        ttk.Label(frame_ruta, text="Peso de Carga (kg):").pack(pady=5)
        ttk.Entry(frame_ruta, textvariable=self.peso_carga).pack(pady=5)
        
        # destino personalizado
        ttk.Label(frame_ruta, text="Dirección de Destino:").pack(pady=5)
        self.destino_direccion = tk.StringVar()
        ttk.Entry(frame_ruta, textvariable=self.destino_direccion, width=40).pack(pady=5)
        
        ttk.Button(frame_ruta, text="Calcular Mejor Ruta", 
                  command=self.calcular_mejor_ruta).pack(pady=20)
        
        # resultados
        self.marco_resultados = ttk.LabelFrame(parent, text="Resultados")
        self.marco_resultados.pack(fill="both", expand=True, pady=10)
        
    def crear_panel_nuevo_vehiculo(self, parent):
        # campos para nuevo vehiculo
        ttk.Label(parent, text="Nombre del Vehículo:").pack(pady=5)
        ttk.Entry(parent, textvariable=self.nombre_vehiculo).pack(pady=5)
        
        ttk.Label(parent, text="Capacidad (kg):").pack(pady=5)
        ttk.Entry(parent, textvariable=self.capacidad_vehiculo).pack(pady=5)
        
        ttk.Label(parent, text="Volumen (m³):").pack(pady=5)
        ttk.Entry(parent, textvariable=self.volumen_vehiculo).pack(pady=5)
        
        ttk.Label(parent, text="Consumo (L/100km):").pack(pady=5)
        ttk.Entry(parent, textvariable=self.consumo_vehiculo).pack(pady=5)
        
        ttk.Label(parent, text="Tipo de Combustible:").pack(pady=5)
        ttk.Combobox(parent, textvariable=self.tipo_combustible, 
                    values=["Nafta Premium", "Nafta Regular", "Gasoil"]).pack(pady=5)
        
        ttk.Label(parent, text="Costo Combustible (pesos/L):").pack(pady=5)
        ttk.Entry(parent, textvariable=self.costo_combustible).pack(pady=5)
        
        ttk.Label(parent, text="Costo Mantenimiento (pesos/km):").pack(pady=5)
        ttk.Entry(parent, textvariable=self.costo_mantenimiento).pack(pady=5)
        
        # boton para agregar vehiculo
        ttk.Button(parent, text="Agregar Vehículo", 
                  command=self.agregar_vehiculo).pack(pady=20)
        
    def agregar_vehiculo(self):
        try:
            # validar que todos los campos esten completos
            if not all([self.nombre_vehiculo.get(), 
                       self.capacidad_vehiculo.get(),
                       self.volumen_vehiculo.get(),
                       self.consumo_vehiculo.get(),
                       self.tipo_combustible.get(),
                       self.costo_combustible.get(),
                       self.costo_mantenimiento.get()]):
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            # si pasa todos los campos, se crea el vehiculo
            nuevo_vehiculo = Vehiculo(
                nombre=self.nombre_vehiculo.get(),
                capacidad_kg=self.capacidad_vehiculo.get(),
                volumen_m3=self.volumen_vehiculo.get(),
                consumo_combustible=self.consumo_vehiculo.get(),
                tipo_combustible=self.tipo_combustible.get(),
                costo_combustible_por_litro=self.costo_combustible.get(),
                costo_mantenimiento_por_km=self.costo_mantenimiento.get()
            )
            
            # agregar a la lista de vehiculos disponibles
            clave = self.nombre_vehiculo.get().lower().replace(" ", "_")
            VEHICULOS_DISPONIBLES[clave] = nuevo_vehiculo
            
            # actualizar la lista de vehiculos disponibles
            self.vehiculo_seleccionado.set(clave)
            
            messagebox.showinfo("Éxito", "Vehículo agregado correctamente")
            
            # limpiar campos
            self.nombre_vehiculo.set("")
            self.capacidad_vehiculo.set(0)
            self.volumen_vehiculo.set(0)
            self.consumo_vehiculo.set(0)
            self.tipo_combustible.set("Nafta Premium")
            self.costo_combustible.set(1100)
            self.costo_mantenimiento.set(12000)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar vehículo: {str(e)}")
    
    # API de OSRM para obtener la ruta real entre los puntos dados
    # https://github.com/Project-OSRM/osrm-backend/
    def obtener_ruta_osrm(self, puntos):
        #solicita a OSRM la ruta real entre los puntos dados
        if len(puntos) < 2:
            return puntos
        # OSRM espera lon,lat
        coords = ";".join([f"{lon},{lat}" for lat, lon in puntos])
        url = f"https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"
        try:
            resp = requests.get(url)
            data = resp.json()
            if 'routes' in data and data['routes']:
                geometry = data['routes'][0]['geometry']['coordinates']
                # OSRM devuelve [lon, lat], lo convertimos a (lat, lon)
                return [(lat, lon) for lon, lat in geometry] # gracias cursor
            else:
                return puntos  # si no hay ruta, se devuelve una linea recta
        except Exception as e:
            print(f"Error solicitando ruta OSRM: {e}")
            return puntos

    def actualizar_ruta_mapa(self, ruta):
        # eliminar ruta anterior si existe
        if self.ruta_actual:
            self.mapa.delete_all_path()
        # obtener puntos de la ruta
        puntos = [(punto.latitud, punto.longitud) for punto in ruta.puntos]
        # obtener ruta real usando OSRM
        ruta_real = self.obtener_ruta_osrm(puntos)
        # dibujar nueva ruta
        self.ruta_actual = self.mapa.set_path(ruta_real)
        # calcular el centro de la ruta
        latitudes = [lat for lat, lon in ruta_real]
        longitudes = [lon for lat, lon in ruta_real]
        centro_lat = sum(latitudes) / len(latitudes)
        centro_lon = sum(longitudes) / len(longitudes)
        # centrar el mapa en el punto medio
        self.mapa.set_position(centro_lat, centro_lon)
        self.mapa.set_zoom(8)
        
    def obtener_info_peajes(self, origen, destino):
        try:
            # Obtener direcciones con información de peajes
            directions_result = self.gmaps.directions(
                origen,
                destino,
                mode="driving",
                alternatives=True,
                language="es",
                region="ar"
            )
            
            if not directions_result:
                print("No se encontraron rutas disponibles")
                return 0, 0
            
            # Buscar la ruta con menos peajes
            mejor_ruta = None
            menos_peajes = float('inf')
            
            for ruta in directions_result:
                # Contar peajes en la ruta
                num_peajes = 0
                for paso in ruta['legs'][0]['steps']:
                    # Verificar en las instrucciones y el nombre del paso
                    instrucciones = paso.get('html_instructions', '').lower()
                    nombre_paso = paso.get('name', '').lower()
                    
                    # Palabras clave que indican peaje
                    palabras_clave = ['peaje', 'toll', 'cobro', 'pago']
                    
                    # Verificar si alguna palabra clave está presente
                    if any(palabra in instrucciones or palabra in nombre_paso for palabra in palabras_clave):
                        num_peajes += 1
                
                if num_peajes < menos_peajes:
                    menos_peajes = num_peajes
                    mejor_ruta = ruta
            
            if mejor_ruta:
                # Calcular costo total de peajes basado en el tipo de vehículo
                vehiculo = VEHICULOS_DISPONIBLES[self.vehiculo_seleccionado.get()]
                costo_base_peaje = 900  # Costo estimado por peaje segun https://www.argentina.gob.ar/transporte/vialidad-nacional/institucional/informacion-publica/tarifas-de-peajes
                
                # Ajustar costo según el tipo de vehículo
                if vehiculo.capacidad_kg > 1000:  # Vehículos pesados
                    costo_base_peaje *= 1.5
                elif vehiculo.capacidad_kg > 500:  # Vehículos medianos
                    costo_base_peaje *= 1.2
                
                costo_peajes = menos_peajes * costo_base_peaje
                return menos_peajes, costo_peajes
            return 0, 0
            
        except Exception as e:
            print(f"Error obteniendo información de peajes: {e}")
            return 0, 0

    def calcular_mejor_ruta(self):
        try:
            # Punto de origen fijo (Puerto de Rosario)
            punto_origen = PuntoRuta(
                nombre="Puerto de Rosario",
                latitud=-32.9510139,
                longitud=-60.6260167
            )
            
            # Obtener coordenadas de destino
            destino = self.geocoder.geocode(self.destino_direccion.get())
            if not destino:
                messagebox.showerror("Error", "No se pudo encontrar la dirección de destino")
                return
            
            # Crear punto de destino
            punto_destino = PuntoRuta(
                nombre=self.destino_direccion.get(),
                latitud=destino.latitude,
                longitud=destino.longitude
            )
            
            # Obtener vehículo seleccionado
            vehiculo = VEHICULOS_DISPONIBLES[self.vehiculo_seleccionado.get()]
            peso = self.peso_carga.get()
            
            # Calcular número de viajes necesarios
            viajes_necesarios = math.ceil(peso / vehiculo.capacidad_kg)
            
            # Definir las rutas posibles con sus puntos intermedios
            rutas_posibles = {
                "Ruta Nacional 9": [
                    PuntoRuta("San Nicolás", -33.3358, -60.2102),
                    PuntoRuta("San Pedro", -33.6791, -59.6664)
                ],
                "Autopista Córdoba (AU9)": [
                    PuntoRuta("Pilar", -31.6789, -63.8790),
                    PuntoRuta("Villa María", -32.4125, -63.2402)
                ],
                "Ruta Nacional 33": [
                    PuntoRuta("Casilda", -33.0442, -61.1681),
                    PuntoRuta("Venado Tuerto", -33.7467, -61.9689)
                ],
                "Autopista Brigadier López (AP01)": [
                    PuntoRuta("Rafaela", -31.2503, -61.4867),
                    PuntoRuta("Sunchales", -30.9440, -61.5614)
                ]
            }
            
            # Calcular la mejor ruta
            mejor_ruta = None
            mejor_costo_total = float('inf')
            mejor_nombre_ruta = ""
            mejor_num_peajes = 0
            
            for nombre_ruta, puntos_intermedios in rutas_posibles.items():
                # Crear puntos de ruta
                puntos_ruta = [punto_origen] + puntos_intermedios + [punto_destino]
                
                # Calcular distancia total
                distancia = sum(Ruta.calcular_distancia(puntos_ruta[i], puntos_ruta[i+1]) 
                              for i in range(len(puntos_ruta)-1))
                
                # Obtener información de peajes
                num_peajes, costo_peajes = self.obtener_info_peajes(
                    f"{punto_origen.latitud},{punto_origen.longitud}",
                    f"{punto_destino.latitud},{punto_destino.longitud}"
                )
                
                # Calcular costos
                costo_combustible = vehiculo.calcular_costo_combustible(distancia) * viajes_necesarios
                # Costo de mantenimiento fijo al rededor de los 550 km recorridos
                costo_mantenimiento = 200000 * viajes_necesarios if distancia >= 550 else 0
                tiempo_estimado = (distancia / 80) * viajes_necesarios  # 80 km/h promedio
                costo_conductor = CONDUCTOR_PREDETERMINADO.calcular_costo_viaje(tiempo_estimado / 24)
                costo_total = costo_combustible + costo_mantenimiento + costo_conductor + costo_peajes
                
                # Actualizar mejor ruta si es necesario
                if costo_total < mejor_costo_total:
                    mejor_costo_total = costo_total
                    mejor_ruta = Ruta(
                        puntos=puntos_ruta,
                        distancia_km=distancia,
                        tiempo_estimado_horas=tiempo_estimado,
                        costo_peajes=costo_peajes,
                        paradas_combustible=[(distancia/2, "Parada de Combustible")]
                    )
                    mejor_nombre_ruta = nombre_ruta
                    mejor_num_peajes = num_peajes
            
            # Actualizar mapa
            self.actualizar_ruta_mapa(mejor_ruta)
            
            # Limpiar resultados anteriores
            for widget in self.marco_resultados.winfo_children():
                widget.destroy()
            
            # Mostrar resultados
            resultados = [
                f"Origen: Puerto de Rosario",
                f"Destino: {self.destino_direccion.get()}",
                f"Ruta seleccionada: {mejor_nombre_ruta}",
                f"Distancia: {mejor_ruta.distancia_km:.1f} km",
                f"Tiempo estimado: {mejor_ruta.tiempo_estimado_horas:.1f} horas",
                f"Número de peajes: {mejor_num_peajes}",
                f"Costo combustible: ${costo_combustible:.2f}",
                f"Costo mantenimiento: ${costo_mantenimiento:.2f}",
                f"Costo conductor: ${costo_conductor:.2f}",
                f"Costo peajes: ${mejor_ruta.costo_peajes:.2f}",
                f"Costo total: ${mejor_costo_total:.2f}"
            ]
            
            if viajes_necesarios > 1:
                resultados.insert(3, f"Viajes necesarios: {viajes_necesarios} (debido a la capacidad del vehículo)")
                resultados.insert(4, f"Peso por viaje: {vehiculo.capacidad_kg:.1f} kg")
            
            for resultado in resultados:
                ttk.Label(self.marco_resultados, text=resultado).pack(pady=2)
            
            # Verificar si el vehiculo puede transportar el peso
            if not vehiculo.puede_transportar_peso(peso):
                messagebox.showinfo("Información", 
                    f"El peso total ({peso}kg) excede la capacidad del vehículo ({vehiculo.capacidad_kg}kg).\n" +
                    f"Se realizarán {viajes_necesarios} viajes para completar el transporte.\n" +
                    f"Los costos mostrados incluyen todos los viajes necesarios.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular la ruta: {str(e)}")

    def cargar_pedidos(self):
        if os.path.exists(self.pedidos_file):
            try:
                with open(self.pedidos_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:  # Verificar que el archivo no esté vacío
                        pedidos_data = json.loads(contenido)
                        PEDIDOS.clear()
                        for pedido_dict in pedidos_data:
                            pedido = Pedido(
                                id=pedido_dict["id"],
                                usuario=pedido_dict["usuario"],
                                items=pedido_dict["items"],
                                direccion_destino=pedido_dict["direccion_destino"]
                            )
                            pedido.estado = pedido_dict["estado"]
                            pedido.conductor = pedido_dict["conductor"]
                            if pedido_dict["fecha_creacion"]:
                                pedido.fecha_creacion = datetime.fromisoformat(pedido_dict["fecha_creacion"])
                            PEDIDOS.append(pedido)
                    else:
                        # Archivo vacío, inicializar lista vacía
                        PEDIDOS.clear()
            except (json.JSONDecodeError, FileNotFoundError):
                # Si hay error al leer JSON, inicializar lista vacía
                PEDIDOS.clear()
        else:
            # Archivo no existe, inicializar lista vacía
            PEDIDOS.clear()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraLogistica(root)
    root.mainloop()