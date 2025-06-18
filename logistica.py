import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datums.vehiculos import VEHICULOS_DISPONIBLES, Vehiculo
from datums.conductor import CONDUCTOR_PREDETERMINADO, cargar_conductores, guardar_conductores
from datums.ruta import PuntoRuta, Ruta
from datums.pedido import PEDIDOS, Pedido
import math
import requests
import googlemaps
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()

class CalculadoraLogistica:
    def __init__(self, root, parent=None):
        self.root = root
        self.parent = parent
        self.conductor_actual = None
        
        # Configurar ventana
        self.root.title("Sistema de Logística - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.centrar_ventana()
        
        # Crear interfaz de login
        self.crear_interfaz_login()
        
        # Inicializar geocoder para direcciones
        self.geocoder = Nominatim(user_agent="logistica_app")
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def crear_interfaz_login(self):
        """Crea la interfaz de login"""
        # Frame principal
        frame_principal = ttk.Frame(self.root)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(frame_principal, text="SISTEMA DE LOGÍSTICA", 
                 font=("Arial", 16, "bold")).pack(pady=20)
        
        ttk.Label(frame_principal, text="Login de Conductor", 
                 font=("Arial", 12)).pack(pady=10)
        
        # Frame para formulario
        frame_formulario = ttk.LabelFrame(frame_principal, text="Credenciales")
        frame_formulario.pack(fill="x", pady=20)
        
        # Variables para login
        self.usuario_conductor = tk.StringVar()
        self.password_conductor = tk.StringVar()
        
        # Campos del formulario
        ttk.Label(frame_formulario, text="Usuario:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        entry_usuario = ttk.Entry(frame_formulario, textvariable=self.usuario_conductor, width=25)
        entry_usuario.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(frame_formulario, text="Contraseña:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        entry_password = ttk.Entry(frame_formulario, textvariable=self.password_conductor, show="*", width=25)
        entry_password.grid(row=1, column=1, padx=10, pady=10)
        
        # Configurar Enter para hacer login
        entry_usuario.bind('<Return>', lambda e: self.login_conductor())
        entry_password.bind('<Return>', lambda e: self.login_conductor())
        
        # Botones
        frame_botones = ttk.Frame(frame_principal)
        frame_botones.pack(pady=20)
        
        # Botón principal de login (ahora con ttk y fuente grande)
        btn_login = ttk.Button(
            frame_botones,
            text="INICIAR SESIÓN",
            command=self.login_conductor
        )
        btn_login.pack(pady=10, ipadx=20, ipady=10)  # Más grande y visible
        
        # Botón cancelar
        ttk.Button(
            frame_botones,
            text="Cancelar",
            command=self.cancelar_login,
            width=15
        ).pack(pady=5)
        
        # Instrucciones
        ttk.Label(frame_principal, text="Presiona Enter en cualquier campo para iniciar sesión", 
                 font=("Arial", 9), foreground="gray").pack(pady=5)
        
        # Enfocar en el campo de usuario
        entry_usuario.focus()
    
    def login_conductor(self):
        """Función de login"""
        usuario = self.usuario_conductor.get()
        password = self.password_conductor.get()
        
        if not usuario or not password:
            messagebox.showerror("Error", "Por favor complete usuario y contraseña")
            return
        
        # Buscar conductor en la lista
        conductores = cargar_conductores()
        conductor = next((c for c in conductores if c.get("usuario") == usuario), None)
        
        if not conductor:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        
        # Verificar contraseña
        if password != conductor.get("password"):
            messagebox.showerror("Error", "Contraseña incorrecta")
            return
        
        # Login exitoso - permitir acceso aunque tenga pedido asignado
        self.conductor_actual = conductor
        
        # Mostrar mensaje de bienvenida
        if conductor["estado"] == "ocupado":
            messagebox.showinfo("Bienvenido", 
                f"Bienvenido, {conductor['nombre']}\n\nNota: Tienes un pedido asignado actualmente.")
        else:
            messagebox.showinfo("Bienvenido", f"Bienvenido, {conductor['nombre']}")
        
        # Inicializar la interfaz completa de logística
        self.inicializar_interfaz_logistica()
    
    def cancelar_login(self):
        """Cancela el login y cierra la ventana"""
        self.cerrar_logistica()
    
    def inicializar_interfaz_logistica(self):
        """Inicializa la interfaz completa de logística después del login"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configurar ventana para logística
        self.root.title(f"Sistema de Logística - {self.conductor_actual['nombre']}")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Inicializar variables y archivos
        self.inicializar_variables()
        
        # Crear interfaz completa
        self.crear_interfaz_completa()
    
    def inicializar_variables(self):
        """Inicializa todas las variables necesarias para logística"""
        # Directorio de datos
        self.data_dir = "data"
        self.pedidos_file = os.path.join(self.data_dir, "pedidos.json")
        
        # Variables para vehículos
        self.vehiculo_seleccionado = tk.StringVar(value="Citroën Berlingo Furgón")
        self.peso_carga = tk.DoubleVar(value=1000)
        
        # Variables para nuevo vehículo
        self.nombre_vehiculo = tk.StringVar()
        self.capacidad_vehiculo = tk.DoubleVar(value=0)
        self.volumen_vehiculo = tk.DoubleVar(value=0)
        self.consumo_vehiculo = tk.DoubleVar(value=0)
        self.tipo_combustible = tk.StringVar(value="Nafta Premium")
        self.costo_combustible = tk.DoubleVar(value=1100)
        self.costo_mantenimiento = tk.DoubleVar(value=12000)
        
        # Variables para mapa
        self.ruta_actual = None
        self.destino_direccion = tk.StringVar()
        
        # Cargar datos
        self.cargar_pedidos()
        
        # Configurar Google Maps
        try:
            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            if api_key and api_key != 'TU_API_KEY_AQUI':
                self.gmaps = googlemaps.Client(key=api_key)
            else:
                self.gmaps = None
        except Exception as e:
            self.gmaps = None
            print(f"Advertencia: No se pudo configurar Google Maps - Error: {e}")
    
    def crear_interfaz_completa(self):
        """Crea la interfaz completa de logística"""
        # Frame principal
        self.frame_principal = ttk.Frame(self.root)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Barra de información del conductor
        frame_conductor_info = ttk.Frame(self.frame_principal)
        frame_conductor_info.pack(fill="x", pady=(0, 10))
        
        ttk.Label(frame_conductor_info, 
                 text=f"Conductor: {self.conductor_actual['nombre']} - {self.conductor_actual['licencia']}", 
                 font=("Arial", 12, "bold")).pack(side="left")
        
        ttk.Button(frame_conductor_info, text="Cerrar Sesión", 
                  command=self.logout_conductor).pack(side="right")
        
        # Frame para información de pedidos del conductor
        frame_pedidos_conductor = ttk.LabelFrame(self.frame_principal, text="Mis Pedidos")
        frame_pedidos_conductor.pack(fill="x", pady=(0, 10))
        
        # Treeview para pedidos del conductor
        self.tree_pedidos_conductor = ttk.Treeview(frame_pedidos_conductor, 
                                                  columns=("id", "usuario", "direccion", "items", "estado"), 
                                                  show="headings", height=3)
        self.tree_pedidos_conductor.heading("id", text="ID")
        self.tree_pedidos_conductor.heading("usuario", text="Cliente")
        self.tree_pedidos_conductor.heading("direccion", text="Dirección")
        self.tree_pedidos_conductor.heading("items", text="Items")
        self.tree_pedidos_conductor.heading("estado", text="Estado")
        self.tree_pedidos_conductor.pack(fill="x", pady=5)
        
        # Botones para conductor
        frame_botones_conductor = ttk.Frame(frame_pedidos_conductor)
        frame_botones_conductor.pack(pady=5)
        
        ttk.Button(frame_botones_conductor, text="Tomar Pedido Disponible", 
                  command=self.tomar_pedido_automatico).pack(side="left", padx=5)
        
        ttk.Button(frame_botones_conductor, text="Marcar Pedido como Terminado", 
                  command=self.marcar_pedido_terminado_conductor).pack(side="left", padx=5)
        
        ttk.Button(frame_botones_conductor, text="Cargar Dirección al Mapa", 
                  command=self.cargar_direccion_pedido).pack(side="left", padx=5)
        
        ttk.Button(frame_botones_conductor, text="Actualizar Lista", 
                  command=self.actualizar_pedidos_conductor).pack(side="left", padx=5)
        
        # Notebook para pestañas principales
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill="both", expand=True)
        
        # Crear pestañas principales
        self.crear_pestaña_mapa()
        self.crear_pestaña_calculos()
        
        # Botón para cerrar
        ttk.Button(self.frame_principal, text="Cerrar", 
                  command=self.cerrar_logistica).pack(pady=10)
        
        # Inicializar lista de pedidos del conductor
        self.actualizar_pedidos_conductor()
    
    def crear_pestaña_mapa(self):
        """Crea la pestaña del mapa"""
        self.pestaña_mapa = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_mapa, text="Mapa")
        self.crear_panel_mapa()
    
    def crear_pestaña_calculos(self):
        """Crea la pestaña de cálculos"""
        self.pestaña_calculos = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_calculos, text="Cálculos")
        self.crear_panel_calculos()
    
    def logout_conductor(self):
        """Cierra la sesión del conductor"""
        if self.conductor_actual:
            # Verificar si tiene un pedido en proceso
            pedido_actual = next((p for p in PEDIDOS if p.conductor == self.conductor_actual["nombre"] and p.estado == "en_proceso"), None)
            
            if pedido_actual:
                respuesta = messagebox.askyesno("Confirmar", 
                    f"Tienes el pedido #{pedido_actual.id} en proceso. ¿Estás seguro de que quieres cerrar sesión?")
                if not respuesta:
                    return
        
        # Volver a la interfaz de login
        self.conductor_actual = None
        self.inicializar_interfaz_login()
    
    def inicializar_interfaz_login(self):
        """Vuelve a la interfaz de login"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configurar ventana para login
        self.root.title("Sistema de Logística - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.centrar_ventana()
        
        # Crear interfaz de login
        self.crear_interfaz_login()

    def crear_panel_mapa(self):
        marco_mapa = ttk.LabelFrame(self.pestaña_mapa, text="Mapa de Ruta")
        marco_mapa.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.mapa = TkinterMapView(marco_mapa, width=600, height=500, corner_radius=0)
        self.mapa.pack(fill="both", expand=True)
        self.mapa.set_position(-32.9510139, -60.6260167)  # Puerto de Rosario
        self.mapa.set_zoom(8)
        
        self.marcador_puerto_rosario = self.mapa.set_marker(-32.9510139, -60.6260167, "Puerto de Rosario")
        
        # ruta
        self.ruta_actual = None
        
    def crear_panel_calculos(self):
        marco_calculos = ttk.LabelFrame(self.pestaña_calculos, text="Cálculos")
        marco_calculos.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Crear pestañas
        notebook = ttk.Notebook(marco_calculos)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Pestaña de cálculo primero
        pestaña_calculo = ttk.Frame(notebook)
        notebook.add(pestaña_calculo, text="Cálculo")
        pestaña_pedidos = ttk.Frame(notebook)
        notebook.add(pestaña_pedidos, text="Pedidos")
        # Crear paneles
        self.crear_panel_calculo_ruta(pestaña_calculo)
        self.crear_panel_pedidos(pestaña_pedidos)
    
    def crear_panel_pedidos(self, parent):
        # Frame para lista de pedidos
        frame_pedidos = ttk.LabelFrame(parent, text="Gestión de Pedidos")
        frame_pedidos.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame para filtros
        frame_filtros = ttk.Frame(frame_pedidos)
        frame_filtros.pack(fill="x", pady=5)
        
        ttk.Label(frame_filtros, text="Filtrar por estado:").pack(side="left", padx=5)
        self.filtro_estado = tk.StringVar(value="todos")
        combo_filtro = ttk.Combobox(frame_filtros, textvariable=self.filtro_estado, 
                                   values=["todos", "pendiente", "en_proceso", "completado"], 
                                   state="readonly", width=15)
        combo_filtro.pack(side="left", padx=5)
        combo_filtro.bind("<<ComboboxSelected>>", lambda e: self.actualizar_lista_pedidos())
        
        # Treeview para pedidos
        self.tree_pedidos = ttk.Treeview(frame_pedidos, columns=("ID", "Usuario", "Dirección", "Items", "Estado", "Conductor"), show="headings")
        self.tree_pedidos.heading("ID", text="ID")
        self.tree_pedidos.heading("Usuario", text="Usuario")
        self.tree_pedidos.heading("Dirección", text="Dirección")
        self.tree_pedidos.heading("Items", text="Items")
        self.tree_pedidos.heading("Estado", text="Estado")
        self.tree_pedidos.heading("Conductor", text="Conductor")
        self.tree_pedidos.pack(fill="both", expand=True, pady=5)
        
        # Botón para tomar pedido
        ttk.Button(frame_pedidos, text="Tomar Pedido Seleccionado", 
                  command=self.tomar_pedido).pack(pady=5)
        
        # Botón para marcar pedido como terminado
        ttk.Button(frame_pedidos, text="Marcar Pedido como Terminado", 
                  command=self.marcar_pedido_terminado_general).pack(pady=5)
        
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
        
        # Filtrar pedidos según el filtro de estado
        pedidos_filtrados = [p for p in PEDIDOS if self.filtro_estado.get() == "todos" or p.estado == self.filtro_estado.get()]
        
        # Agregar todos los pedidos filtrados
        for pedido in pedidos_filtrados:
            # Formatear items para mostrar
            items_texto = []
            for item in pedido.items:
                items_texto.append(f"{item['cantidad']}x {item['nombre']}")
            items_str = ", ".join(items_texto)
            
            # Mostrar conductor si está asignado
            conductor_str = pedido.conductor if pedido.conductor else "Sin asignar"
            
            self.tree_pedidos.insert("", "end", values=(
                pedido.id,
                pedido.usuario,
                pedido.direccion_destino,
                items_str,
                pedido.estado,
                conductor_str
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
            self.actualizar_pedidos_conductor()
            
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
        # Layout horizontal: frame_ruta a la izquierda, resultados a la derecha
        frame_main = ttk.Frame(parent)
        frame_main.pack(fill="both", expand=True)

        frame_ruta = ttk.LabelFrame(frame_main, text="Cálculo de Ruta")
        frame_ruta.pack(side="left", fill="y", padx=5, pady=5, ipadx=5, ipady=5)

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

        # Resultados a la derecha, más grande y con scroll
        frame_resultados = ttk.LabelFrame(frame_main, text="Resultados")
        frame_resultados.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.text_resultados = tk.Text(frame_resultados, wrap="word", height=20)
        self.text_resultados.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(frame_resultados, orient="vertical", command=self.text_resultados.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_resultados.configure(yscrollcommand=scrollbar.set)
        self.marco_resultados = frame_resultados

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
            self.text_resultados.delete(1.0, tk.END)

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
            
            self.text_resultados.insert(tk.END, "\n".join(resultados))
            self.text_resultados.see(tk.END)
            
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

    def cerrar_logistica(self):
        self.root.destroy()
        if self.parent:
            self.parent.deiconify()

    def actualizar_pedidos_conductor(self):
        """Actualiza la lista de pedidos del conductor logueado"""
        # Limpiar lista actual
        for item in self.tree_pedidos_conductor.get_children():
            self.tree_pedidos_conductor.delete(item)
        
        if not self.conductor_actual:
            return
        
        # Filtrar pedidos del conductor actual
        pedidos_conductor = [p for p in PEDIDOS if p.conductor == self.conductor_actual["nombre"]]
        
        for pedido in pedidos_conductor:
            # Formatear items para mostrar
            items_texto = []
            for item in pedido.items:
                items_texto.append(f"{item['cantidad']}x {item['nombre']}")
            items_str = ", ".join(items_texto)
            
            self.tree_pedidos_conductor.insert("", "end", values=(
                pedido.id,
                pedido.usuario,
                pedido.direccion_destino,
                items_str,
                pedido.estado
            ))

    def tomar_pedido_automatico(self):
        if not self.conductor_actual:
            messagebox.showerror("Error", "Debe iniciar sesión primero")
            return
        
        # Buscar pedidos pendientes
        pedidos_pendientes = [p for p in PEDIDOS if p.estado == "pendiente"]
        
        if not pedidos_pendientes:
            messagebox.showinfo("Información", "No hay pedidos pendientes disponibles")
            return
        
        # Tomar el primer pedido pendiente
        pedido = pedidos_pendientes[0]
        
        # Asignar conductor al pedido
        pedido.conductor = self.conductor_actual["nombre"]
        pedido.estado = "en_proceso"
        
        # Cambiar estado del conductor a ocupado
        conductores = cargar_conductores()
        for c in conductores:
            if c["nombre"] == self.conductor_actual["nombre"]:
                c["estado"] = "ocupado"
        guardar_conductores(conductores)
        
        # Guardar cambios
        self.guardar_pedidos()
        
        # Actualizar listas
        self.actualizar_lista_pedidos()
        self.actualizar_pedidos_conductor()
        
        messagebox.showinfo("Éxito", f"Pedido #{pedido.id} asignado automáticamente")
        
        # Establecer dirección de destino en el mapa
        self.destino_direccion.set(pedido.direccion_destino)

    def marcar_pedido_terminado_conductor(self):
        """Función específica para que el conductor marque su pedido como terminado"""
        if not self.conductor_actual:
            messagebox.showerror("Error", "Debe estar logueado")
            return
        
        # Obtener pedido seleccionado
        seleccion = self.tree_pedidos_conductor.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un pedido")
            return
        
        # Obtener ID del pedido
        pedido_id = int(self.tree_pedidos_conductor.item(seleccion[0])["values"][0])
        
        # Encontrar pedido
        pedido = next((p for p in PEDIDOS if p.id == pedido_id), None)
        if not pedido:
            messagebox.showerror("Error", "Pedido no encontrado")
            return
        
        # Verificar que el pedido pertenece al conductor logueado
        if pedido.conductor != self.conductor_actual["nombre"]:
            messagebox.showerror("Error", "Este pedido no le pertenece")
            return
        
        # Verificar que el pedido esté en proceso
        if pedido.estado != "en_proceso":
            messagebox.showwarning("Advertencia", "Solo se pueden marcar como terminados los pedidos en proceso")
            return
        
        # Marcar pedido como terminado
        if pedido.completar_pedido():
            self.guardar_pedidos()
            # Cambiar estado del conductor a disponible y guardar
            conductores = cargar_conductores()
            for c in conductores:
                if c["nombre"] == self.conductor_actual["nombre"]:
                    c["estado"] = "disponible"
            guardar_conductores(conductores)
            
            # Actualizar listas
            self.actualizar_lista_pedidos()
            self.actualizar_pedidos_conductor()
            
            messagebox.showinfo("Éxito", f"Pedido #{pedido_id} marcado como terminado")
        else:
            messagebox.showerror("Error", "No se pudo marcar el pedido como terminado")

    def marcar_pedido_terminado_general(self):
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
        
        # Marcar pedido como terminado
        if pedido.completar_pedido():
            self.guardar_pedidos()
            # Actualizar listas
            self.actualizar_lista_pedidos()
            self.actualizar_pedidos_conductor()
            
            messagebox.showinfo("Éxito", f"Pedido #{pedido_id} marcado como terminado")
        else:
            messagebox.showerror("Error", "No se pudo marcar el pedido como terminado")

    def cargar_direccion_pedido(self):
        """Carga la dirección del pedido seleccionado al panel de cálculos"""
        # Obtener pedido seleccionado del conductor
        seleccion = self.tree_pedidos_conductor.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un pedido")
            return
        
        try:
            # Obtener ID del pedido
            valores = self.tree_pedidos_conductor.item(seleccion[0])["values"]
            pedido_id = int(valores[0])
            
            # Encontrar pedido
            pedido = next((p for p in PEDIDOS if p.id == pedido_id), None)
            if not pedido:
                messagebox.showerror("Error", "Pedido no encontrado")
                return
            
            # Establecer dirección del pedido en el panel de cálculos
            self.destino_direccion.set(pedido.direccion_destino)
            
            # Cambiar a la pestaña de cálculos
            self.notebook.select(0)  # Primera pestaña (Cálculos)
            
            messagebox.showinfo("Éxito", f"Dirección del pedido #{pedido_id} cargada en el panel de cálculos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar dirección: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraLogistica(root)
    root.mainloop()