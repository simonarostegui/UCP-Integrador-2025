import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datums.vehiculos import VEHICULOS_DISPONIBLES, Vehiculo
from datums.conductor import CONDUCTOR_PREDETERMINADO
from datums.ruta import RUTAS, PuntoRuta
import math
import requests

class CalculadoraLogistica:
    def __init__(self, root):
        self.peso_carga = tk.DoubleVar(value=500) # 500 kg
        self.vehiculo_seleccionado = tk.StringVar(value="berlingo_furgon")
        self.ruta_seleccionada = tk.StringVar(value="ruta_9")
        
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
        
        # Ventana Principal
        self.root = root
        self.root.title("Calculadora de Logística")
        self.root.geometry("1200x800")
        
        self.marco_principal = ttk.Frame(root)
        self.marco_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # mapa
        self.crear_panel_mapa()
        
        # calculos
        self.crear_panel_calculos()
        
    def crear_panel_mapa(self):
        marco_mapa = ttk.LabelFrame(self.marco_principal, text="Mapa de Ruta")
        marco_mapa.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.mapa = TkinterMapView(marco_mapa, width=600, height=500, corner_radius=0)
        self.mapa.pack(fill="both", expand=True)
        self.mapa.set_position(-32.9510139, -60.6260167)  # Puerto de Rosario
        self.mapa.set_zoom(8)
        
        # marcadores
        self.marcador_casa_central = self.mapa.set_marker(-34.6037, -58.3816, "Casa Central")
        self.marcador_puerto_rosario = self.mapa.set_marker(-32.9510139, -60.6260167, "Puerto de Rosario")
        
        # ruta
        self.ruta_actual = None
        
    def crear_panel_calculos(self):
        marco_calculos = ttk.LabelFrame(self.marco_principal, text="Cálculos")
        marco_calculos.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # pestañas
        notebook = ttk.Notebook(marco_calculos)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # calculo
        pestaña_calculo = ttk.Frame(notebook)
        notebook.add(pestaña_calculo, text="Cálculo de Ruta")
        
        # nuevo vehiculo
        pestaña_vehiculo = ttk.Frame(notebook)
        notebook.add(pestaña_vehiculo, text="Nuevo Vehículo")
        
        # calculo
        self.crear_panel_calculo_ruta(pestaña_calculo)
        
        # nuevo vehiculo
        self.crear_panel_nuevo_vehiculo(pestaña_vehiculo)
        
    def crear_panel_calculo_ruta(self, parent):
        # vehiculos
        ttk.Label(parent, text="Vehículo:").pack(pady=5)
        combo_vehiculo = ttk.Combobox(parent, textvariable=self.vehiculo_seleccionado)
        combo_vehiculo['values'] = list(VEHICULOS_DISPONIBLES.keys())
        combo_vehiculo.pack(pady=5)
        
        # rutas
        ttk.Label(parent, text="Ruta:").pack(pady=5)
        combo_ruta = ttk.Combobox(parent, textvariable=self.ruta_seleccionada)
        combo_ruta['values'] = list(RUTAS.keys())
        combo_ruta.pack(pady=5)
        
        # peso de carga
        ttk.Label(parent, text="Peso de Carga (kg):").pack(pady=5)
        ttk.Entry(parent, textvariable=self.peso_carga).pack(pady=5)
        
        ttk.Button(parent, text="Calcular", command=self.calcular).pack(pady=20)
        
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
    # https://github.com/Project-OSRM/osrm-backend/blob/master/docs/api.md#get-route-v1driving
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
        
    def calcular(self):
        try:
            # obtener vehiculo y ruta seleccionados
            vehiculo = VEHICULOS_DISPONIBLES[self.vehiculo_seleccionado.get()]
            ruta = RUTAS[self.ruta_seleccionada.get()]
            peso = self.peso_carga.get()
            
            # actualizar ruta en el mapa
            self.actualizar_ruta_mapa(ruta)
            
            # limpiar resultados anteriores
            for widget in self.marco_resultados.winfo_children():
                widget.destroy()
            
            # calcular costos y tiempos
            costo_combustible = vehiculo.calcular_costo_combustible(ruta.distancia_km)
            costo_mantenimiento = vehiculo.calcular_costo_mantenimiento(ruta.distancia_km)
            costo_conductor = CONDUCTOR_PREDETERMINADO.calcular_costo_viaje(ruta.tiempo_estimado_horas / 24)
            costo_total = costo_combustible + costo_mantenimiento + costo_conductor + ruta.costo_peajes
            
            # mostrar resultados
            resultados = [
                f"Distancia: {ruta.distancia_km:.1f} km",
                f"Tiempo estimado: {ruta.tiempo_estimado_horas:.1f} horas",
                f"Costo combustible: ${costo_combustible:.2f}",
                f"Costo mantenimiento: ${costo_mantenimiento:.2f}",
                f"Costo conductor: ${costo_conductor:.2f}",
                f"Costo peajes: ${ruta.costo_peajes:.2f}",
                f"Costo total: ${costo_total:.2f}",
                f"Paradas de combustible: {len(ruta.paradas_combustible)}"
            ]
            
            for resultado in resultados:
                ttk.Label(self.marco_resultados, text=resultado).pack(pady=2)
            
            # verificar si el vehiculo puede transportar el peso
            if not vehiculo.puede_transportar_peso(peso):
                messagebox.showwarning("Advertencia", 
                    f"El vehículo seleccionado no puede transportar {peso}kg. " +
                    f"Capacidad máxima: {vehiculo.capacidad_kg}kg")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en el cálculo: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraLogistica(root)
root.mainloop()