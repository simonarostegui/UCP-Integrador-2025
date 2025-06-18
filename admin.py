import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
from datums.pedido import PEDIDOS, Pedido
from datums.vehiculos import VEHICULOS_DISPONIBLES, Vehiculo
from datums.conductor import CONDUCTOR_PREDETERMINADO, cargar_conductores, guardar_conductores
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sys

class InterfazAdmin:
    def __init__(self, root, parent=None):
        self.root = root
        self.parent = parent
        self.root.title("Panel de Administración")
        self.root.geometry("1400x900")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_admin)
        
        # Variables de datos
        self.data_dir = "data"
        self.productos_file = os.path.join(self.data_dir, "productos.json")
        self.pedidos_file = os.path.join(self.data_dir, "pedidos.json")
        self.multas_file = os.path.join(self.data_dir, "multas.json")
        self.reportes_file = os.path.join(self.data_dir, "reportes.json")
        
        # Cargar datos
        self.cargar_datos()
        
        # Crear interfaz
        self.crear_interfaz()
        
    def cargar_datos(self):
        # Cargar productos
        if os.path.exists(self.productos_file):
            try:
                with open(self.productos_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:
                        self.productos = json.loads(contenido)
                        # Agregar campos faltantes a productos existentes
                        for producto in self.productos:
                            if "categoria" not in producto:
                                producto["categoria"] = "otros"
                            if "marca" not in producto:
                                producto["marca"] = "Sin marca"
                            if "marca_propia" not in producto:
                                producto["marca_propia"] = False
                    else:
                        self.productos = []
            except (json.JSONDecodeError, FileNotFoundError):
                self.productos = []
        else:
            self.productos = []
        
        # Cargar pedidos
        if os.path.exists(self.pedidos_file):
            try:
                with open(self.pedidos_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:
                        pedidos_data = json.loads(contenido)
                        PEDIDOS.clear()  # Limpiar lista actual
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
                        PEDIDOS.clear()
            except (json.JSONDecodeError, FileNotFoundError):
                PEDIDOS.clear()
        else:
            PEDIDOS.clear()
        
        # Cargar multas
        if os.path.exists(self.multas_file):
            try:
                with open(self.multas_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:
                        self.multas = json.loads(contenido)
                    else:
                        self.multas = []
            except (json.JSONDecodeError, FileNotFoundError):
                self.multas = []
        else:
            self.multas = []
        
        # Cargar reportes
        if os.path.exists(self.reportes_file):
            try:
                with open(self.reportes_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:
                        self.reportes = json.loads(contenido)
                    else:
                        self.reportes = []
            except (json.JSONDecodeError, FileNotFoundError):
                self.reportes = []
        else:
            self.reportes = []
    
    def guardar_datos(self):
        # Guardar productos
        with open(self.productos_file, 'w', encoding='utf-8') as f:
            json.dump(self.productos, f, ensure_ascii=False, indent=4)
        
        # Guardar multas
        with open(self.multas_file, 'w', encoding='utf-8') as f:
            json.dump(self.multas, f, ensure_ascii=False, indent=4)
        
        # Guardar reportes
        with open(self.reportes_file, 'w', encoding='utf-8') as f:
            json.dump(self.reportes, f, ensure_ascii=False, indent=4)
    
    def crear_interfaz(self):
        # Frame principal
        self.frame_principal = ttk.Frame(self.root)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(self.frame_principal, text="PANEL DE ADMINISTRACIÓN", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill="both", expand=True)
        
        # Crear pestañas
        self.crear_pestaña_productos()
        self.crear_pestaña_estadisticas()
        self.crear_pestaña_conductores()
        self.crear_pestaña_vehiculos()
        self.crear_pestaña_multas()
        self.crear_pestaña_reportes()
        
        # Botón para cerrar
        ttk.Button(self.frame_principal, text="Cerrar", 
                  command=self.cerrar_admin).pack(pady=10)
    
    def crear_pestaña_productos(self):
        # Pestaña de productos
        self.pestaña_productos = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_productos, text="Gestión de Productos")
        
        # Frame para agregar productos
        frame_agregar = ttk.LabelFrame(self.pestaña_productos, text="Agregar/Editar Producto")
        frame_agregar.pack(fill="x", padx=5, pady=5)
        
        # Variables para formulario
        self.nombre_producto = tk.StringVar()
        self.categoria_producto = tk.StringVar(value="alimentos")
        self.precio_producto = tk.DoubleVar()
        self.peso_producto = tk.DoubleVar()
        self.stock_producto = tk.IntVar()
        self.marca_producto = tk.StringVar()
        self.es_marca_propia = tk.BooleanVar()
        self.producto_editando = None  # Para rastrear qué producto se está editando
        
        # Campos del formulario
        ttk.Label(frame_agregar, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.nombre_producto, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="Categoría:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Combobox(frame_agregar, textvariable=self.categoria_producto, 
                    values=["alimentos", "higiene", "limpieza", "otros"]).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="Precio ($):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.precio_producto, width=15).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_agregar, text="Peso (kg):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.peso_producto, width=15).grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_agregar, text="Stock:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.stock_producto, width=15).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_agregar, text="Marca:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.marca_producto, width=20).grid(row=2, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Checkbutton(frame_agregar, text="Marca Propia", variable=self.es_marca_propia).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Botones
        ttk.Button(frame_agregar, text="Agregar Producto", 
                  command=self.agregar_producto).grid(row=3, column=2, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Editar Producto Seleccionado", 
                  command=self.editar_producto).grid(row=3, column=3, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Actualizar Producto", 
                  command=self.actualizar_producto).grid(row=4, column=2, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Cancelar Edición", 
                  command=self.cancelar_edicion).grid(row=4, column=3, padx=5, pady=5)
        
        # Frame para lista de productos
        frame_lista = ttk.LabelFrame(self.pestaña_productos, text="Lista de Productos")
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Treeview para productos
        self.tree_productos = ttk.Treeview(frame_lista, 
                                         columns=("nombre", "categoria", "precio", "peso", "stock", "marca", "marca_propia"), 
                                         show="headings")
        self.tree_productos.heading("nombre", text="Nombre")
        self.tree_productos.heading("categoria", text="Categoría")
        self.tree_productos.heading("precio", text="Precio ($)")
        self.tree_productos.heading("peso", text="Peso (kg)")
        self.tree_productos.heading("stock", text="Stock")
        self.tree_productos.heading("marca", text="Marca")
        self.tree_productos.heading("marca_propia", text="Marca Propia")
        self.tree_productos.pack(fill="both", expand=True, pady=5)
        
        # Botón para actualizar lista
        ttk.Button(frame_lista, text="Actualizar Lista", 
                  command=self.actualizar_lista_productos).pack(pady=5)
        
        # Inicializar lista
        self.actualizar_lista_productos()
    
    def crear_pestaña_estadisticas(self):
        # Pestaña de estadísticas
        self.pestaña_estadisticas = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_estadisticas, text="Estadísticas")
        
        # Frame para filtros
        frame_filtros = ttk.LabelFrame(self.pestaña_estadisticas, text="Filtros")
        frame_filtros.pack(fill="x", padx=5, pady=5)
        
        self.periodo_estadisticas = tk.StringVar(value="mes")
        ttk.Label(frame_filtros, text="Período:").pack(side="left", padx=5)
        ttk.Combobox(frame_filtros, textvariable=self.periodo_estadisticas, 
                    values=["semana", "mes", "trimestre", "año"]).pack(side="left", padx=5)
        ttk.Button(frame_filtros, text="Generar Estadísticas", 
                  command=self.generar_estadisticas).pack(side="left", padx=5)
        
        # Frame para gráficos
        frame_graficos = ttk.LabelFrame(self.pestaña_estadisticas, text="Gráficos")
        frame_graficos.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Crear figura de matplotlib
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, frame_graficos)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Frame para estadísticas detalladas
        frame_detalle = ttk.LabelFrame(self.pestaña_estadisticas, text="Detalle")
        frame_detalle.pack(fill="x", padx=5, pady=5)
        
        self.texto_estadisticas = tk.Text(frame_detalle, height=12)
        self.texto_estadisticas.pack(fill="x", padx=5, pady=5)
    
    def crear_pestaña_conductores(self):
        # Pestaña de conductores
        self.pestaña_conductores = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_conductores, text="Gestión de Conductores y Pedidos")
        
        # Frame para agregar conductor
        frame_agregar = ttk.LabelFrame(self.pestaña_conductores, text="Agregar/Editar Conductor")
        frame_agregar.pack(fill="x", padx=5, pady=5)
        
        # Variables para formulario
        self.nombre_conductor = tk.StringVar()
        self.dni_conductor = tk.StringVar()
        self.telefono_conductor = tk.StringVar()
        self.usuario_conductor = tk.StringVar()
        self.password_conductor = tk.StringVar()
        self.licencia_conductor = tk.StringVar(value="B1")
        self.conductor_editando = None  # Para rastrear qué conductor se está editando
        
        # Campos del formulario
        ttk.Label(frame_agregar, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.nombre_conductor, width=25).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="DNI:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.dni_conductor, width=15).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.telefono_conductor, width=15).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_agregar, text="Licencia:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Combobox(frame_agregar, textvariable=self.licencia_conductor, 
                    values=["B1", "B2", "B3", "C1", "C2"], width=12).grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="Usuario:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.usuario_conductor, width=25).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="Contraseña:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.password_conductor, show="*", width=15).grid(row=2, column=3, padx=5, pady=5)
        
        # Botones
        ttk.Button(frame_agregar, text="Agregar Conductor", 
                  command=self.agregar_conductor).grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Editar Conductor Seleccionado", 
                  command=self.editar_conductor).grid(row=4, column=0, columnspan=4, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Actualizar Conductor", 
                  command=self.actualizar_conductor).grid(row=5, column=0, columnspan=4, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Cancelar Edición", 
                  command=self.cancelar_edicion_conductor).grid(row=6, column=0, columnspan=4, padx=5, pady=5)
        
        # Frame para estado de conductores
        frame_conductores = ttk.LabelFrame(self.pestaña_conductores, text="Estado de Conductores")
        frame_conductores.pack(fill="x", padx=5, pady=5)
        
        # Treeview para conductores
        self.tree_conductores = ttk.Treeview(frame_conductores, 
                                            columns=("nombre", "licencia", "estado", "pedido_actual"), 
                                            show="headings", height=4)
        self.tree_conductores.heading("nombre", text="Nombre")
        self.tree_conductores.heading("licencia", text="Licencia")
        self.tree_conductores.heading("estado", text="Estado")
        self.tree_conductores.heading("pedido_actual", text="Pedido Actual")
        self.tree_conductores.pack(fill="x", pady=5)
        
        # Frame para gestión de pedidos
        frame_gestion_pedidos = ttk.LabelFrame(self.pestaña_conductores, text="Gestión de Pedidos")
        frame_gestion_pedidos.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Notebook para diferentes estados de pedidos
        notebook_pedidos = ttk.Notebook(frame_gestion_pedidos)
        notebook_pedidos.pack(fill="both", expand=True, pady=5)
        
        # Pestaña de pedidos disponibles
        pestaña_disponibles = ttk.Frame(notebook_pedidos)
        notebook_pedidos.add(pestaña_disponibles, text="Pedidos Disponibles")
        
        # Treeview para pedidos disponibles
        self.tree_pedidos_disponibles = ttk.Treeview(pestaña_disponibles, 
                                                    columns=("id", "usuario", "direccion", "items", "fecha"), 
                                                    show="headings", height=4)
        self.tree_pedidos_disponibles.heading("id", text="ID")
        self.tree_pedidos_disponibles.heading("usuario", text="Cliente")
        self.tree_pedidos_disponibles.heading("direccion", text="Dirección")
        self.tree_pedidos_disponibles.heading("items", text="Items")
        self.tree_pedidos_disponibles.heading("fecha", text="Fecha")
        self.tree_pedidos_disponibles.pack(fill="both", expand=True, pady=5)
        
        # Pestaña de pedidos en curso
        pestaña_curso = ttk.Frame(notebook_pedidos)
        notebook_pedidos.add(pestaña_curso, text="Pedidos en Curso")
        
        # Treeview para pedidos en curso
        self.tree_pedidos_curso = ttk.Treeview(pestaña_curso, 
                                              columns=("id", "usuario", "direccion", "conductor", "fecha"), 
                                              show="headings", height=4)
        self.tree_pedidos_curso.heading("id", text="ID")
        self.tree_pedidos_curso.heading("usuario", text="Cliente")
        self.tree_pedidos_curso.heading("direccion", text="Dirección")
        self.tree_pedidos_curso.heading("conductor", text="Conductor")
        self.tree_pedidos_curso.heading("fecha", text="Fecha")
        self.tree_pedidos_curso.pack(fill="both", expand=True, pady=5)
        
        # Pestaña de pedidos completados
        pestaña_completados = ttk.Frame(notebook_pedidos)
        notebook_pedidos.add(pestaña_completados, text="Pedidos Completados")
        
        # Treeview para pedidos completados
        self.tree_pedidos_completados = ttk.Treeview(pestaña_completados, 
                                                    columns=("id", "usuario", "direccion", "conductor", "fecha"), 
                                                    show="headings", height=4)
        self.tree_pedidos_completados.heading("id", text="ID")
        self.tree_pedidos_completados.heading("usuario", text="Cliente")
        self.tree_pedidos_completados.heading("direccion", text="Dirección")
        self.tree_pedidos_completados.heading("conductor", text="Conductor")
        self.tree_pedidos_completados.heading("fecha", text="Fecha")
        self.tree_pedidos_completados.pack(fill="both", expand=True, pady=5)
        
        # Botones para gestión de pedidos
        frame_botones_pedidos = ttk.Frame(frame_gestion_pedidos)
        frame_botones_pedidos.pack(pady=5)
        
        ttk.Button(frame_botones_pedidos, text="Asignar Pedido a Conductor", 
                  command=self.asignar_pedido_conductor).pack(side="left", padx=5)
        
        ttk.Button(frame_botones_pedidos, text="Marcar Pedido como Terminado", 
                  command=self.marcar_pedido_terminado_admin).pack(side="left", padx=5)
        
        ttk.Button(frame_botones_pedidos, text="Actualizar Todas las Listas", 
                  command=self.actualizar_listas_admin).pack(side="left", padx=5)
        
        # Botón para actualizar lista de conductores
        ttk.Button(frame_conductores, text="Actualizar Lista de Conductores", 
                  command=self.actualizar_lista_conductores).pack(pady=5)
        
        # Inicializar listas
        self.actualizar_lista_conductores()
        self.actualizar_lista_pedidos_disponibles()
        self.actualizar_listas_pedidos()
    
    def crear_pestaña_vehiculos(self):
        # Pestaña de vehículos
        self.pestaña_vehiculos = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_vehiculos, text="Gestión de Vehículos")
        
        # Frame para agregar vehículo
        frame_agregar = ttk.LabelFrame(self.pestaña_vehiculos, text="Agregar Vehículo")
        frame_agregar.pack(fill="x", padx=5, pady=5)
        
        # Variables para formulario
        self.nombre_vehiculo = tk.StringVar()
        self.capacidad_vehiculo = tk.DoubleVar()
        self.consumo_vehiculo = tk.DoubleVar()
        self.tipo_combustible = tk.StringVar(value="Nafta Premium")
        self.costo_combustible = tk.DoubleVar(value=1100)
        self.costo_mantenimiento = tk.DoubleVar(value=12000)
        self.es_respaldo = tk.BooleanVar()
        
        # Campos del formulario
        ttk.Label(frame_agregar, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.nombre_vehiculo, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="Capacidad (kg):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.capacidad_vehiculo, width=15).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="Consumo (L/100km):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.consumo_vehiculo, width=15).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_agregar, text="Tipo Combustible:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Combobox(frame_agregar, textvariable=self.tipo_combustible, 
                    values=["Nafta Premium", "Nafta Regular", "Gasoil"]).grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="Costo Combustible ($/L):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.costo_combustible, width=15).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_agregar, text="Costo Mantenimiento ($/km):").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.costo_mantenimiento, width=15).grid(row=2, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Checkbutton(frame_agregar, text="Vehículo de Respaldo", variable=self.es_respaldo).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Botón
        ttk.Button(frame_agregar, text="Agregar Vehículo", 
                  command=self.agregar_vehiculo).grid(row=3, column=2, columnspan=2, padx=5, pady=5)
        
        # Frame para lista de vehículos
        frame_lista = ttk.LabelFrame(self.pestaña_vehiculos, text="Vehículos Disponibles")
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Treeview para vehículos
        self.tree_vehiculos = ttk.Treeview(frame_lista, 
                                         columns=("nombre", "capacidad", "consumo", "tipo_combustible", "costo_combustible", "costo_mantenimiento"), 
                                         show="headings")
        self.tree_vehiculos.heading("nombre", text="Nombre")
        self.tree_vehiculos.heading("capacidad", text="Capacidad (kg)")
        self.tree_vehiculos.heading("consumo", text="Consumo (L/100km)")
        self.tree_vehiculos.heading("tipo_combustible", text="Tipo Combustible")
        self.tree_vehiculos.heading("costo_combustible", text="Costo Combustible ($/L)")
        self.tree_vehiculos.heading("costo_mantenimiento", text="Costo Mantenimiento ($/km)")
        self.tree_vehiculos.pack(fill="both", expand=True, pady=5)
        
        # Botón para actualizar lista
        ttk.Button(frame_lista, text="Actualizar Lista", 
                  command=self.actualizar_lista_vehiculos).pack(pady=5)
        
        # Inicializar lista
        self.actualizar_lista_vehiculos()
    
    def crear_pestaña_multas(self):
        # Pestaña de multas
        self.pestaña_multas = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_multas, text="Registro de Multas")
        
        # Frame para agregar multa
        frame_agregar = ttk.LabelFrame(self.pestaña_multas, text="Registrar Multa")
        frame_agregar.pack(fill="x", padx=5, pady=5)
        
        # Variables para formulario
        self.fecha_multa = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.monto_multa = tk.DoubleVar()
        self.descripcion_multa = tk.StringVar()
        self.responsable_multa = tk.StringVar()
        self.vehiculo_multa = tk.StringVar()
        
        # Campos del formulario
        ttk.Label(frame_agregar, text="Fecha:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.fecha_multa, width=15).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_agregar, text="Monto ($):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.monto_multa, width=15).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_agregar, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame_agregar, textvariable=self.descripcion_multa, width=40).grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame_agregar, text="Responsable:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.combo_responsable_multa = ttk.Combobox(frame_agregar, textvariable=self.responsable_multa, 
                    values=[c["nombre"] for c in cargar_conductores()], 
                    state="readonly")
        self.combo_responsable_multa.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_agregar, text="Vehículo:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        ttk.Combobox(frame_agregar, textvariable=self.vehiculo_multa, 
                    values=list(VEHICULOS_DISPONIBLES.keys())).grid(row=2, column=3, padx=5, pady=5)
        
        # Botón
        ttk.Button(frame_agregar, text="Registrar Multa", 
                  command=self.registrar_multa).grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        
        # Frame para lista de multas
        frame_lista = ttk.LabelFrame(self.pestaña_multas, text="Historial de Multas")
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Treeview para multas
        self.tree_multas = ttk.Treeview(frame_lista, 
                                      columns=("fecha", "monto", "descripcion", "responsable", "vehiculo"), 
                                      show="headings")
        self.tree_multas.heading("fecha", text="Fecha")
        self.tree_multas.heading("monto", text="Monto ($)")
        self.tree_multas.heading("descripcion", text="Descripción")
        self.tree_multas.heading("responsable", text="Responsable")
        self.tree_multas.heading("vehiculo", text="Vehículo")
        self.tree_multas.pack(fill="both", expand=True, pady=5)
        
        # Botón para actualizar lista
        ttk.Button(frame_lista, text="Actualizar Lista", 
                  command=self.actualizar_lista_multas).pack(pady=5)
        
        # Inicializar lista
        self.actualizar_lista_multas()
    
    def crear_pestaña_reportes(self):
        # Pestaña de reportes
        self.pestaña_reportes = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_reportes, text="Reportes de Gastos")
        
        # Frame para generar reportes
        frame_generar = ttk.LabelFrame(self.pestaña_reportes, text="Generar Reporte")
        frame_generar.pack(fill="x", padx=5, pady=5)
        
        self.tipo_reporte = tk.StringVar(value="gastos_logisticos")
        self.fecha_inicio = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        self.fecha_fin = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(frame_generar, text="Tipo de Reporte:").pack(side="left", padx=5)
        ttk.Combobox(frame_generar, textvariable=self.tipo_reporte, 
                    values=["gastos_logisticos", "multas", "consumo_combustible", "mantenimiento"]).pack(side="left", padx=5)
        
        ttk.Label(frame_generar, text="Fecha Inicio:").pack(side="left", padx=5)
        ttk.Entry(frame_generar, textvariable=self.fecha_inicio, width=12).pack(side="left", padx=5)
        
        ttk.Label(frame_generar, text="Fecha Fin:").pack(side="left", padx=5)
        ttk.Entry(frame_generar, textvariable=self.fecha_fin, width=12).pack(side="left", padx=5)
        
        ttk.Button(frame_generar, text="Generar Reporte", 
                  command=self.generar_reporte).pack(side="left", padx=5)
        
        # Frame para mostrar reporte
        frame_reporte = ttk.LabelFrame(self.pestaña_reportes, text="Reporte")
        frame_reporte.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.texto_reporte = tk.Text(frame_reporte, wrap="word")
        scrollbar = ttk.Scrollbar(frame_reporte, orient="vertical", command=self.texto_reporte.yview)
        self.texto_reporte.configure(yscrollcommand=scrollbar.set)
        
        self.texto_reporte.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
    
    # Métodos para gestión de productos
    def agregar_producto(self):
        try:
            if not all([self.nombre_producto.get(), self.precio_producto.get(), 
                       self.peso_producto.get(), self.stock_producto.get()]):
                messagebox.showerror("Error", "Por favor complete todos los campos obligatorios")
                return
            
            nuevo_producto = {
                "nombre": self.nombre_producto.get(),
                "categoria": self.categoria_producto.get(),
                "precio": self.precio_producto.get(),
                "peso": self.peso_producto.get(),
                "stock": self.stock_producto.get(),
                "marca": self.marca_producto.get() if self.marca_producto.get() else "Sin marca",
                "marca_propia": self.es_marca_propia.get()
            }
            
            self.productos.append(nuevo_producto)
            self.guardar_datos()
            self.actualizar_lista_productos()
            
            # Limpiar campos
            self.limpiar_campos_producto()
            
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")
    
    def editar_producto(self):
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return
        
        try:
            valores = self.tree_productos.item(seleccion[0])["values"]
            nombre = valores[0]
            
            # Encontrar producto
            producto = next((p for p in self.productos if p.get("nombre", "") == nombre), None)
            if producto:
                self.nombre_producto.set(producto.get("nombre", ""))
                self.categoria_producto.set(producto.get("categoria", "otros"))
                self.precio_producto.set(producto.get("precio", 0))
                self.peso_producto.set(producto.get("peso", 0))
                self.stock_producto.set(producto.get("stock", 0))
                self.marca_producto.set(producto.get("marca", "Sin marca"))
                self.es_marca_propia.set(producto.get("marca_propia", False))
                self.producto_editando = producto
                
                messagebox.showinfo("Éxito", "Producto seleccionado para editar")
            else:
                messagebox.showerror("Error", "Producto no encontrado")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al seleccionar producto: {str(e)}")
    
    def actualizar_producto(self):
        try:
            if not self.producto_editando:
                messagebox.showwarning("Advertencia", "Por favor seleccione un producto para editar primero")
                return
                
            if not all([self.nombre_producto.get(), self.precio_producto.get(), 
                       self.peso_producto.get(), self.stock_producto.get()]):
                messagebox.showerror("Error", "Por favor complete todos los campos obligatorios")
                return
            
            # Actualizar el producto que se está editando
            self.producto_editando["nombre"] = self.nombre_producto.get()
            self.producto_editando["categoria"] = self.categoria_producto.get()
            self.producto_editando["precio"] = self.precio_producto.get()
            self.producto_editando["peso"] = self.peso_producto.get()
            self.producto_editando["stock"] = self.stock_producto.get()
            self.producto_editando["marca"] = self.marca_producto.get() if self.marca_producto.get() else "Sin marca"
            self.producto_editando["marca_propia"] = self.es_marca_propia.get()
            
            self.guardar_datos()
            self.actualizar_lista_productos()
            
            # Limpiar campos y modo edición
            self.limpiar_campos_producto()
            self.producto_editando = None
            
            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar producto: {str(e)}")
    
    def cancelar_edicion(self):
        """Función para cancelar la edición y limpiar campos"""
        self.limpiar_campos_producto()
        self.producto_editando = None
        messagebox.showinfo("Información", "Edición cancelada")
    
    def limpiar_campos_producto(self):
        """Función para limpiar todos los campos del formulario de productos"""
        self.nombre_producto.set("")
        self.categoria_producto.set("alimentos")
        self.precio_producto.set(0)
        self.peso_producto.set(0)
        self.stock_producto.set(0)
        self.marca_producto.set("")
        self.es_marca_propia.set(False)
    
    def actualizar_lista_productos(self):
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        for producto in self.productos:
            # Usar get() para campos que pueden no existir
            self.tree_productos.insert("", "end", values=(
                producto.get("nombre", ""),
                producto.get("categoria", "otros"),
                producto.get("precio", 0),
                producto.get("peso", 0),
                producto.get("stock", 0),
                producto.get("marca", "Sin marca"),
                "Sí" if producto.get("marca_propia", False) else "No"
            ))
    
    # Métodos para estadísticas
    def generar_estadisticas(self):
        try:
            # Recargar pedidos para asegurar datos actualizados
            self.cargar_pedidos_recientes()
            
            # Analizar pedidos para obtener estadísticas
            productos_vendidos = {}
            
            for pedido in PEDIDOS:
                for item in pedido.items:
                    nombre = item["nombre"]
                    cantidad = item["cantidad"]
                    if nombre in productos_vendidos:
                        productos_vendidos[nombre] += cantidad
                    else:
                        productos_vendidos[nombre] = cantidad
            
            # Ordenar por cantidad vendida
            productos_ordenados = sorted(productos_vendidos.items(), key=lambda x: x[1], reverse=True)
            
            if productos_ordenados:
                # Gráfico de barras
                self.ax1.clear()
                nombres = [p[0] for p in productos_ordenados[:10]]  # Top 10
                cantidades = [p[1] for p in productos_ordenados[:10]]
                self.ax1.bar(nombres, cantidades)
                self.ax1.set_title("Productos Más Vendidos")
                self.ax1.set_ylabel("Cantidad Vendida")
                self.ax1.tick_params(axis='x', rotation=45)
                
                # Gráfico de torta para categorías
                self.ax2.clear()
                categorias = {}
                for producto in self.productos:
                    cat = producto.get("categoria", "otros")
                    if cat in categorias:
                        categorias[cat] += 1
                    else:
                        categorias[cat] = 1
                
                if categorias:
                    self.ax2.pie(categorias.values(), labels=categorias.keys(), autopct='%1.1f%%')
                    self.ax2.set_title("Distribución de nuestros productos por Categorías")
                
                self.canvas.draw()
                
                # Texto de estadísticas
                self.texto_estadisticas.delete(1.0, tk.END)
                self.texto_estadisticas.insert(tk.END, f"ESTADÍSTICAS DE VENTAS - {self.periodo_estadisticas.get().upper()}\n")
                self.texto_estadisticas.insert(tk.END, "=" * 50 + "\n\n")
                
                self.texto_estadisticas.insert(tk.END, "PRODUCTOS MÁS VENDIDOS:\n")
                for i, (nombre, cantidad) in enumerate(productos_ordenados[:5], 1):
                    self.texto_estadisticas.insert(tk.END, f"{i}. {nombre}: {cantidad} unidades\n")
                
                self.texto_estadisticas.insert(tk.END, "\nPRODUCTOS MENOS VENDIDOS:\n")
                for i, (nombre, cantidad) in enumerate(productos_ordenados[-5:], 1):
                    self.texto_estadisticas.insert(tk.END, f"{i}. {nombre}: {cantidad} unidades\n")
                
                total_ventas = sum(productos_vendidos.values())
                self.texto_estadisticas.insert(tk.END, f"\nTOTAL DE UNIDADES VENDIDAS: {total_ventas}\n")
                self.texto_estadisticas.insert(tk.END, f"TOTAL DE PEDIDOS: {len(PEDIDOS)}\n")
                
            else:
                messagebox.showinfo("Información", "No hay datos de ventas para mostrar")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar estadísticas: {str(e)}")
    
    def cargar_pedidos_recientes(self):
        """Función para recargar solo los pedidos desde el archivo"""
        if os.path.exists(self.pedidos_file):
            try:
                with open(self.pedidos_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:
                        pedidos_data = json.loads(contenido)
                        PEDIDOS.clear()  # Limpiar lista actual
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
                        PEDIDOS.clear()
            except (json.JSONDecodeError, FileNotFoundError):
                PEDIDOS.clear()
        else:
            PEDIDOS.clear()
    
    # Métodos para gestión de vehículos
    def agregar_vehiculo(self):
        try:
            if not all([self.nombre_vehiculo.get(), self.capacidad_vehiculo.get(),
                       self.consumo_vehiculo.get(), self.costo_combustible.get(),
                       self.costo_mantenimiento.get()]):
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            nuevo_vehiculo = Vehiculo(
                nombre=self.nombre_vehiculo.get(),
                capacidad_kg=self.capacidad_vehiculo.get(),
                consumo_combustible=self.consumo_vehiculo.get(),
                tipo_combustible=self.tipo_combustible.get(),
                costo_combustible_por_litro=self.costo_combustible.get(),
                costo_mantenimiento_por_km=self.costo_mantenimiento.get()
            )
            
            clave = self.nombre_vehiculo.get().lower().replace(" ", "_")
            VEHICULOS_DISPONIBLES[clave] = nuevo_vehiculo
            
            # Limpiar campos
            self.nombre_vehiculo.set("")
            self.capacidad_vehiculo.set(0)
            self.consumo_vehiculo.set(0)
            self.tipo_combustible.set("Nafta Premium")
            self.costo_combustible.set(1100)
            self.costo_mantenimiento.set(12000)
            self.es_respaldo.set(False)
            
            self.actualizar_lista_vehiculos()
            messagebox.showinfo("Éxito", "Vehículo agregado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar vehículo: {str(e)}")
    
    def actualizar_lista_vehiculos(self):
        for item in self.tree_vehiculos.get_children():
            self.tree_vehiculos.delete(item)
        
        for vehiculo in VEHICULOS_DISPONIBLES.values():
            self.tree_vehiculos.insert("", "end", values=(
                vehiculo.nombre,
                vehiculo.capacidad_kg,
                vehiculo.consumo_combustible,
                vehiculo.tipo_combustible,
                vehiculo.costo_combustible_por_litro,
                vehiculo.costo_mantenimiento_por_km
            ))
    
    # Métodos para gestión de multas
    def registrar_multa(self):
        try:
            if not all([self.fecha_multa.get(), self.monto_multa.get(),
                       self.descripcion_multa.get(), self.responsable_multa.get()]):
                messagebox.showerror("Error", "Por favor complete todos los campos obligatorios")
                return
            
            nueva_multa = {
                "fecha": self.fecha_multa.get(),
                "monto": self.monto_multa.get(),
                "descripcion": self.descripcion_multa.get(),
                "responsable": self.responsable_multa.get(),
                "vehiculo": self.vehiculo_multa.get() if self.vehiculo_multa.get() else "No especificado"
            }
            
            self.multas.append(nueva_multa)
            self.guardar_datos()
            self.actualizar_lista_multas()
            
            # Limpiar campos
            self.fecha_multa.set(datetime.now().strftime("%Y-%m-%d"))
            self.monto_multa.set(0)
            self.descripcion_multa.set("")
            self.responsable_multa.set("")
            self.vehiculo_multa.set("")
            
            messagebox.showinfo("Éxito", "Multa registrada correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar multa: {str(e)}")
    
    def actualizar_lista_multas(self):
        for item in self.tree_multas.get_children():
            self.tree_multas.delete(item)
        
        for multa in self.multas:
            self.tree_multas.insert("", "end", values=(
                multa["fecha"],
                multa["monto"],
                multa["descripcion"],
                multa["responsable"],
                multa["vehiculo"]
            ))
    
    # Métodos para reportes
    def generar_reporte(self):
        try:
            self.texto_reporte.delete(1.0, tk.END)
            
            tipo = self.tipo_reporte.get()
            fecha_inicio = datetime.strptime(self.fecha_inicio.get(), "%Y-%m-%d")
            fecha_fin = datetime.strptime(self.fecha_fin.get(), "%Y-%m-%d")
            
            self.texto_reporte.insert(tk.END, f"REPORTE DE {tipo.upper().replace('_', ' ')}\n")
            self.texto_reporte.insert(tk.END, f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}\n")
            self.texto_reporte.insert(tk.END, "=" * 60 + "\n\n")
            
            if tipo == "multas":
                self.generar_reporte_multas(fecha_inicio, fecha_fin)
            elif tipo == "consumo_combustible":
                self.generar_reporte_combustible(fecha_inicio, fecha_fin)
            elif tipo == "mantenimiento":
                self.generar_reporte_mantenimiento(fecha_inicio, fecha_fin)
            else:  # gastos_logisticos
                self.generar_reporte_gastos_logisticos(fecha_inicio, fecha_fin)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def generar_reporte_multas(self, fecha_inicio, fecha_fin):
        multas_periodo = []
        for multa in self.multas:
            fecha_multa = datetime.strptime(multa["fecha"], "%Y-%m-%d")
            if fecha_inicio <= fecha_multa <= fecha_fin:
                multas_periodo.append(multa)
        
        if multas_periodo:
            total_multas = sum(m["monto"] for m in multas_periodo)
            self.texto_reporte.insert(tk.END, f"Total de multas en el período: {len(multas_periodo)}\n")
            self.texto_reporte.insert(tk.END, f"Monto total: ${total_multas:,.2f}\n\n")
            
            self.texto_reporte.insert(tk.END, "DETALLE DE MULTAS:\n")
            for multa in multas_periodo:
                self.texto_reporte.insert(tk.END, f"• {multa['fecha']}: ${multa['monto']:,.2f} - {multa['descripcion']} (Responsable: {multa['responsable']})\n")
        else:
            self.texto_reporte.insert(tk.END, "No se registraron multas en el período especificado.\n")
    
    def generar_reporte_combustible(self, fecha_inicio, fecha_fin):
        self.texto_reporte.insert(tk.END, "REPORTE DE CONSUMO DE COMBUSTIBLE\n\n")
        
        for vehiculo in VEHICULOS_DISPONIBLES.values():
            self.texto_reporte.insert(tk.END, f"Vehículo: {vehiculo.nombre}\n")
            self.texto_reporte.insert(tk.END, f"Tipo de combustible: {vehiculo.tipo_combustible}\n")
            self.texto_reporte.insert(tk.END, f"Consumo: {vehiculo.consumo_combustible} L/100km\n")
            self.texto_reporte.insert(tk.END, f"Costo por litro: ${vehiculo.costo_combustible_por_litro:,.2f}\n")
            self.texto_reporte.insert(tk.END, "-" * 40 + "\n")
    
    def generar_reporte_mantenimiento(self, fecha_inicio, fecha_fin):
        self.texto_reporte.insert(tk.END, "REPORTE DE MANTENIMIENTO\n\n")
        
        for vehiculo in VEHICULOS_DISPONIBLES.values():
            self.texto_reporte.insert(tk.END, f"Vehículo: {vehiculo.nombre}\n")
            self.texto_reporte.insert(tk.END, f"Costo de mantenimiento: ${vehiculo.costo_mantenimiento_por_km:,.2f}/km\n")
            self.texto_reporte.insert(tk.END, "-" * 40 + "\n")
    
    def generar_reporte_gastos_logisticos(self, fecha_inicio, fecha_fin):
        self.texto_reporte.insert(tk.END, "REPORTE DE GASTOS LOGÍSTICOS\n\n")
        
        # Gastos de combustible
        self.texto_reporte.insert(tk.END, "GASTOS DE COMBUSTIBLE:\n")
        for vehiculo in VEHICULOS_DISPONIBLES.values():
            self.texto_reporte.insert(tk.END, f"• {vehiculo.nombre}: ${vehiculo.costo_combustible_por_litro:,.2f}/L\n")
        
        # Gastos de mantenimiento
        self.texto_reporte.insert(tk.END, "\nGASTOS DE MANTENIMIENTO:\n")
        for vehiculo in VEHICULOS_DISPONIBLES.values():
            self.texto_reporte.insert(tk.END, f"• {vehiculo.nombre}: ${vehiculo.costo_mantenimiento_por_km:,.2f}/km\n")
        
        # Multas
        multas_periodo = [m for m in self.multas if fecha_inicio <= datetime.strptime(m["fecha"], "%Y-%m-%d") <= fecha_fin]
        if multas_periodo:
            total_multas = sum(m["monto"] for m in multas_periodo)
            self.texto_reporte.insert(tk.END, f"\nMULTAS EN EL PERÍODO: ${total_multas:,.2f}\n")
        
        # Resumen
        self.texto_reporte.insert(tk.END, "\nRESUMEN:\n")
        self.texto_reporte.insert(tk.END, f"• Vehículos registrados: {len(VEHICULOS_DISPONIBLES)}\n")
        self.texto_reporte.insert(tk.END, f"• Multas en período: {len(multas_periodo)}\n")
        self.texto_reporte.insert(tk.END, f"• Total multas: ${total_multas if multas_periodo else 0:,.2f}\n")

    def actualizar_listas_pedidos(self):
        """Actualiza las listas de pedidos en curso y completados"""
        # Limpiar listas
        for item in self.tree_pedidos_curso.get_children():
            self.tree_pedidos_curso.delete(item)
        
        for item in self.tree_pedidos_completados.get_children():
            self.tree_pedidos_completados.delete(item)
        
        # Agregar pedidos en curso
        for pedido in PEDIDOS:
            if pedido.estado == "en_proceso":
                self.tree_pedidos_curso.insert("", "end", values=(
                    pedido.id,
                    pedido.usuario,
                    pedido.direccion_destino,
                    pedido.conductor or "Sin asignar",
                    pedido.fecha_creacion.strftime("%d/%m/%Y %H:%M") if pedido.fecha_creacion else "N/A"
                ))
        
        # Agregar pedidos completados
        for pedido in PEDIDOS:
            if pedido.estado == "completado":
                self.tree_pedidos_completados.insert("", "end", values=(
                    pedido.id,
                    pedido.usuario,
                    pedido.direccion_destino,
                    pedido.conductor or "Sin asignar",
                    pedido.fecha_creacion.strftime("%d/%m/%Y %H:%M") if pedido.fecha_creacion else "N/A"
                ))

    def cerrar_admin(self):
        self.root.destroy()
        if self.parent:
            self.parent.deiconify()

    def actualizar_combobox_responsables(self):
        if hasattr(self, 'combo_responsable_multa'):
            self.combo_responsable_multa['values'] = [c["nombre"] for c in cargar_conductores()]

    def on_tab_changed(self, event):
        if self.notebook.index(self.notebook.select()) == 4:  # Verifica si se ha cambiado a la pestaña de multas
            self.actualizar_combobox_responsables()

    def agregar_conductor(self):
        try:
            if not all([self.nombre_conductor.get(), self.dni_conductor.get(), self.telefono_conductor.get()]):
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            # Cargar conductores existentes
            conductores = cargar_conductores()
            
            # Verificar si ya existe un conductor con esa cédula
            if any(c.get("dni") == self.dni_conductor.get() for c in conductores):
                messagebox.showerror("Error", "Ya existe un conductor con esa cédula")
                return
            
            # Crear nuevo conductor
            nuevo_conductor = {
                "nombre": self.nombre_conductor.get(),
                "dni": self.dni_conductor.get(),
                "telefono": self.telefono_conductor.get(),
                "licencia": self.licencia_conductor.get(),
                "estado": "disponible",
                "usuario": self.usuario_conductor.get(),
                "password": self.password_conductor.get()
            }
            
            conductores.append(nuevo_conductor)
            guardar_conductores(conductores)
            
            # Limpiar campos
            self.limpiar_campos_conductor()
            
            # Actualizar lista
            self.actualizar_lista_conductores()
            
            messagebox.showinfo("Éxito", "Conductor agregado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar conductor: {str(e)}")
    
    def editar_conductor(self):
        seleccion = self.tree_conductores.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un conductor")
            return
        
        try:
            valores = self.tree_conductores.item(seleccion[0])["values"]
            nombre = valores[0]
            
            # Cargar conductores y encontrar el seleccionado
            conductores = cargar_conductores()
            conductor = next((c for c in conductores if c.get("nombre") == nombre), None)
            
            if conductor:
                self.nombre_conductor.set(conductor.get("nombre", ""))
                self.dni_conductor.set(conductor.get("dni", ""))
                self.telefono_conductor.set(conductor.get("telefono", ""))
                self.licencia_conductor.set(conductor.get("licencia", "B1"))
                self.usuario_conductor.set(conductor.get("usuario", ""))
                self.password_conductor.set(conductor.get("password", ""))
                self.conductor_editando = conductor
                
                messagebox.showinfo("Éxito", "Conductor seleccionado para editar")
            else:
                messagebox.showerror("Error", "Conductor no encontrado")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al seleccionar conductor: {str(e)}")
    
    def actualizar_conductor(self):
        try:
            if not self.conductor_editando:
                messagebox.showwarning("Advertencia", "Por favor seleccione un conductor para editar primero")
                return
                
            if not all([self.nombre_conductor.get(), self.dni_conductor.get(), self.telefono_conductor.get()]):
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            # Cargar conductores
            conductores = cargar_conductores()
            
            # Verificar si el DNI ya existe en otro conductor
            for c in conductores:
                if c != self.conductor_editando and c.get("dni") == self.dni_conductor.get():
                    messagebox.showerror("Error", "Ya existe otro conductor con ese DNI")
                    return
            
            # Actualizar el conductor
            self.conductor_editando["nombre"] = self.nombre_conductor.get()
            self.conductor_editando["dni"] = self.dni_conductor.get()
            self.conductor_editando["telefono"] = self.telefono_conductor.get()
            self.conductor_editando["licencia"] = self.licencia_conductor.get()
            self.conductor_editando["usuario"] = self.usuario_conductor.get()
            self.conductor_editando["password"] = self.password_conductor.get()
            
            guardar_conductores(conductores)
            
            # Limpiar campos y modo edición
            self.limpiar_campos_conductor()
            self.conductor_editando = None
            
            # Actualizar lista
            self.actualizar_lista_conductores()
            
            messagebox.showinfo("Éxito", "Conductor actualizado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar conductor: {str(e)}")
    
    def cancelar_edicion_conductor(self):
        self.limpiar_campos_conductor()
        self.conductor_editando = None
        messagebox.showinfo("Información", "Edición cancelada")
    
    def limpiar_campos_conductor(self):
        self.nombre_conductor.set("")
        self.dni_conductor.set("")
        self.telefono_conductor.set("")
        self.licencia_conductor.set("B1")
        self.usuario_conductor.set("")
        self.password_conductor.set("")
    
    def actualizar_lista_conductores(self):
        # Limpiar lista actual
        for item in self.tree_conductores.get_children():
            self.tree_conductores.delete(item)
        
        # Cargar la lista de conductores desde el JSON
        conductores = cargar_conductores()
        
        # Verificar qué conductores están ocupados basado en pedidos en proceso
        for pedido in PEDIDOS:
            if pedido.estado == "en_proceso" and pedido.conductor:
                for conductor in conductores:
                    if conductor["nombre"] == pedido.conductor:
                        conductor["estado"] = "ocupado"
        
        # Guardar cambios de estado
        guardar_conductores(conductores)
        
        # Agregar conductores a la lista
        for conductor in conductores:
            # Buscar pedido actual del conductor
            pedido_actual = next((p for p in PEDIDOS if p.conductor == conductor["nombre"] and p.estado == "en_proceso"), None)
            pedido_info = f"#{pedido_actual.id}" if pedido_actual else "Sin pedido"
            
            self.tree_conductores.insert("", "end", values=(
                conductor["nombre"],
                conductor.get("licencia", "B1"),
                conductor["estado"],
                pedido_info
            ))
    
    def asignar_pedido_conductor(self):
        # Obtener pedido seleccionado
        seleccion_pedido = self.tree_pedidos_disponibles.selection()
        if not seleccion_pedido:
            messagebox.showwarning("Advertencia", "Por favor seleccione un pedido")
            return
        
        # Obtener conductor seleccionado
        seleccion_conductor = self.tree_conductores.selection()
        if not seleccion_conductor:
            messagebox.showwarning("Advertencia", "Por favor seleccione un conductor")
            return
        
        try:
            # Obtener ID del pedido
            valores_pedido = self.tree_pedidos_disponibles.item(seleccion_pedido[0])["values"]
            id_pedido = valores_pedido[0]
            
            # Obtener nombre del conductor
            valores_conductor = self.tree_conductores.item(seleccion_conductor[0])["values"]
            nombre_conductor = valores_conductor[0]
            
            # Verificar que el conductor esté disponible
            if valores_conductor[2] == "ocupado":
                messagebox.showerror("Error", "Este conductor ya tiene un pedido asignado")
                return
            
            # Encontrar pedido
            pedido = next((p for p in PEDIDOS if p.id == id_pedido), None)
            if not pedido:
                messagebox.showerror("Error", "Pedido no encontrado")
                return
            
            # Asignar pedido al conductor
            pedido.estado = "en_proceso"
            pedido.conductor = nombre_conductor
            
            # Guardar cambios
            self.guardar_pedidos()
            
            # Actualizar listas
            self.actualizar_lista_conductores()
            self.actualizar_lista_pedidos_disponibles()
            self.actualizar_listas_pedidos()
            
            messagebox.showinfo("Éxito", f"Pedido #{pedido.id} asignado a {nombre_conductor}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al asignar pedido: {str(e)}")
    
    def marcar_pedido_terminado_admin(self):
        # Obtener pedido seleccionado de la lista de pedidos en curso
        seleccion = self.tree_pedidos_curso.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un pedido en curso")
            return
        
        try:
            valores = self.tree_pedidos_curso.item(seleccion[0])["values"]
            id_pedido = valores[0]
            
            # Encontrar pedido
            pedido = next((p for p in PEDIDOS if p.id == id_pedido), None)
            if not pedido:
                messagebox.showerror("Error", "Pedido no encontrado")
                return
            
            # Marcar como terminado
            pedido.estado = "completado"
            pedido.conductor = None
            
            # Guardar cambios
            self.guardar_pedidos()
            
            # Actualizar listas
            self.actualizar_lista_conductores()
            self.actualizar_listas_pedidos()
            
            messagebox.showinfo("Éxito", f"Pedido #{pedido.id} marcado como terminado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al marcar pedido como terminado: {str(e)}")
    
    def actualizar_listas_admin(self):
        """Actualiza todas las listas de la pestaña de conductores"""
        self.actualizar_lista_conductores()
        self.actualizar_lista_pedidos_disponibles()
        self.actualizar_listas_pedidos()
    
    def guardar_pedidos(self):
        """Guarda los pedidos en el archivo JSON"""
        try:
            # Convertir pedidos a formato JSON
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
            
            # Guardar en archivo
            with open("data/pedidos.json", "w", encoding="utf-8") as f:
                json.dump(pedidos_data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar pedidos: {str(e)}")

    def actualizar_lista_pedidos_disponibles(self):
        """Actualiza la lista de pedidos disponibles"""
        # Limpiar lista actual
        for item in self.tree_pedidos_disponibles.get_children():
            self.tree_pedidos_disponibles.delete(item)
        
        # Agregar pedidos pendientes
        for pedido in PEDIDOS:
            if pedido.estado == "pendiente":
                self.tree_pedidos_disponibles.insert("", "end", values=(
                    pedido.id,
                    pedido.usuario,
                    pedido.direccion_destino,
                    ", ".join([f"{item['cantidad']}x {item['nombre']}" for item in pedido.items]),
                    pedido.fecha_creacion.strftime("%d/%m/%Y %H:%M") if pedido.fecha_creacion else "N/A"
                ))

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazAdmin(root)
    root.mainloop() 