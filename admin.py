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
from dotenv import load_dotenv
import hashlib

# cargar variables de entorno
load_dotenv()

class InterfazAdmin:
    def __init__(self, root, parent=None):
        self.root = root
        self.parent = parent
        
        # configurar ventana inicial para login
        self.root.title("Panel de Administración - Login")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_admin)
        
        # Centrar ventana
        self.centrar_ventana()
        
        # crear interfaz de login
        self.crear_interfaz_login()
        
    def centrar_ventana(self):
        ### centra la ventana en la pantalla
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def crear_interfaz_login(self):
        ### crea la interfaz de login
        # frame principal
        frame_principal = ttk.Frame(self.root)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # título
        ttk.Label(frame_principal, text="PANEL DE ADMINISTRACIÓN", 
                 font=("Arial", 16, "bold")).pack(pady=20)
        
        ttk.Label(frame_principal, text="Login de Administrador", 
                 font=("Arial", 12)).pack(pady=10)
        
        # frame para el formulario
        frame_formulario = ttk.LabelFrame(frame_principal, text="Credenciales")
        frame_formulario.pack(fill="x", pady=20)
        
        # variables para el login
        self.usuario_admin = tk.StringVar()
        self.password_admin = tk.StringVar()
        
        # campos del formulario
        ttk.Label(frame_formulario, text="Usuario:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        entry_usuario = ttk.Entry(frame_formulario, textvariable=self.usuario_admin, width=25)
        entry_usuario.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(frame_formulario, text="Contraseña:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        entry_password = ttk.Entry(frame_formulario, textvariable=self.password_admin, show="*", width=25)
        entry_password.grid(row=1, column=1, padx=10, pady=10)
        
        # enter hace login, más rápido
        entry_usuario.bind('<Return>', lambda e: self.login_admin())
        entry_password.bind('<Return>', lambda e: self.login_admin())
        
        # botones para loguear o cancelar
        frame_botones = ttk.Frame(frame_principal)
        frame_botones.pack(pady=20)
        
        # botón principal de login
        btn_login = ttk.Button(
            frame_botones,
            text="INICIAR SESIÓN",
            command=self.login_admin
        )
        btn_login.pack(pady=10, ipadx=20, ipady=10)
        
        # botón cancelar por si te arrepentís
        ttk.Button(
            frame_botones,
            text="Cancelar",
            command=self.cancelar_login,
            width=15
        ).pack(pady=5)
        
        # instrucciones
        ttk.Label(frame_principal, text="Presiona Enter en cualquier campo para iniciar sesión", 
                 font=("Arial", 9), foreground="gray").pack(pady=5)
        
        # dejamos el foco en el usuario para que sea más rápido
        entry_usuario.focus()
    
    def login_admin(self):
        ### función de login del administrador
        usuario = self.usuario_admin.get().strip()
        password = self.password_admin.get().strip()
        
        if not usuario or not password:
            messagebox.showerror("Error", "Por favor complete usuario y contraseña")
            return
        
        # obtener credenciales desde variables de entorno
        admin_user = os.getenv('ADMIN_USER', 'admin')
        admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH', '')
        
        # si no hay hash configurado, usar credenciales por defecto
        if not admin_password_hash:
            admin_password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        
        # verificar credenciales
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if usuario == admin_user and password_hash == admin_password_hash:
            # login exitoso
            messagebox.showinfo("Bienvenido", "Acceso concedido al Panel de Administración")
            
            # inicializar la interfaz completa de administración
            self.inicializar_interfaz_admin()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            self.password_admin.set("")  # limpiar contraseña
            # enfocar en el campo de contraseña
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.Entry) and grandchild.cget('show') == '*':
                                    grandchild.focus()
                                    break
    
    def cancelar_login(self):
        ### cancela el login y cierra la ventana
        self.cerrar_admin()
    
    def inicializar_interfaz_admin(self):
        ### inicializa la interfaz completa de administración después del login
        # limpiar ventana porque si no se superpone todo
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # configurar ventana para administración
        self.root.title("Panel de Administración")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # variables de datos, porque todo va ahí
        self.data_dir = "data"
        self.productos_file = os.path.join(self.data_dir, "productos.json")
        self.pedidos_file = os.path.join(self.data_dir, "pedidos.json")
        self.multas_file = os.path.join(self.data_dir, "multas.json")
        self.reportes_file = os.path.join(self.data_dir, "reportes.json")
        
        # cargar datos
        self.cargar_datos()
        
        # crear interfaz
        self.crear_interfaz()
        
    def cargar_datos(self):
        # cargar productos
        if os.path.exists(self.productos_file):
            try:
                with open(self.productos_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:
                        self.productos = json.loads(contenido)
                        # agregar campos faltantes a productos existentes
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
        
        # cargar pedidos
        if os.path.exists(self.pedidos_file):
            try:
                with open(self.pedidos_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:
                        pedidos_data = json.loads(contenido)
                        PEDIDOS.clear()  # limpiar lista actual
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
        
        # cargar multas
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
        
        # cargar reportes
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
        # guardar productos
        with open(self.productos_file, 'w', encoding='utf-8') as f:
            json.dump(self.productos, f, ensure_ascii=False, indent=4)
        
        # guardar multas
        with open(self.multas_file, 'w', encoding='utf-8') as f:
            json.dump(self.multas, f, ensure_ascii=False, indent=4)
        
        # guardar reportes
        with open(self.reportes_file, 'w', encoding='utf-8') as f:
            json.dump(self.reportes, f, ensure_ascii=False, indent=4)
    
    def crear_interfaz(self):
        # frame principal para meter todo
        self.frame_principal = ttk.Frame(self.root)
        self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # título, porque si no nadie sabe qué es esto
        ttk.Label(self.frame_principal, text="PANEL DE ADMINISTRACIÓN", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        # notebook para pestañas
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill="both", expand=True)
        
        # crear pestañas
        self.crear_pestaña_productos()
        self.crear_pestaña_estadisticas()
        self.crear_pestaña_conductores()
        self.crear_pestaña_vehiculos()
        self.crear_pestaña_multas()
        self.crear_pestaña_reportes()
        
        # frame para botones
        frame_botones = ttk.Frame(self.frame_principal)
        frame_botones.pack(pady=10)
        
        # botón de logout
        ttk.Button(frame_botones, text="Cerrar Sesión", 
                  command=self.logout_admin).pack(side="left", padx=5)
        
        # botón para cerrar
        ttk.Button(frame_botones, text="Cerrar", 
                  command=self.cerrar_admin).pack(side="left", padx=5)
    
    def crear_pestaña_productos(self):
        # pestaña de productos
        self.pestaña_productos = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_productos, text="Gestión de Productos")
        
        # frame para agregar productos
        frame_agregar = ttk.LabelFrame(self.pestaña_productos, text="Agregar/Editar Producto")
        frame_agregar.pack(fill="x", padx=5, pady=5)
        
        # variables para formulario
        self.nombre_producto = tk.StringVar()
        self.categoria_producto = tk.StringVar(value="alimentos")
        self.precio_producto = tk.DoubleVar()
        self.peso_producto = tk.DoubleVar()
        self.stock_producto = tk.IntVar()
        self.marca_producto = tk.StringVar()
        self.es_marca_propia = tk.BooleanVar()
        self.producto_editando = None  # para rastrear qué producto se está editando
        
        # campos del formulario
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
        
        # botones
        ttk.Button(frame_agregar, text="Agregar Producto", 
                  command=self.agregar_producto).grid(row=3, column=2, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Editar Producto Seleccionado", 
                  command=self.editar_producto).grid(row=3, column=3, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Actualizar Producto", 
                  command=self.actualizar_producto).grid(row=4, column=2, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Cancelar Edición", 
                  command=self.cancelar_edicion).grid(row=4, column=3, padx=5, pady=5)
        
        # frame para lista de productos
        frame_lista = ttk.LabelFrame(self.pestaña_productos, text="Lista de Productos")
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        # treeview para productos
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
        
        # botón para actualizar lista
        ttk.Button(frame_lista, text="Actualizar Lista", 
                  command=self.actualizar_lista_productos).pack(pady=5)
        
        # inicializar lista
        self.actualizar_lista_productos()
    
    def crear_pestaña_estadisticas(self):
        # pestaña de estadísticas
        self.pestaña_estadisticas = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_estadisticas, text="Estadísticas")
        
        # frame para filtros
        frame_filtros = ttk.LabelFrame(self.pestaña_estadisticas, text="Filtros")
        frame_filtros.pack(fill="x", padx=5, pady=5)
        
        self.periodo_estadisticas = tk.StringVar(value="mes")
        ttk.Label(frame_filtros, text="Período:").pack(side="left", padx=5)
        ttk.Combobox(frame_filtros, textvariable=self.periodo_estadisticas, 
                    values=["semana", "mes", "trimestre", "año"]).pack(side="left", padx=5)
        ttk.Button(frame_filtros, text="Generar Estadísticas", 
                  command=self.generar_estadisticas).pack(side="left", padx=5)
        
        # frame para gráficos
        frame_graficos = ttk.LabelFrame(self.pestaña_estadisticas, text="Gráficos")
        frame_graficos.pack(fill="both", expand=True, padx=5, pady=5)
        
        # crear figura de matplotlib
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, frame_graficos)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # frame para estadísticas detalladas
        frame_detalle = ttk.LabelFrame(self.pestaña_estadisticas, text="Detalle")
        frame_detalle.pack(fill="x", padx=5, pady=5)
        
        self.texto_estadisticas = tk.Text(frame_detalle, height=12)
        self.texto_estadisticas.pack(fill="x", padx=5, pady=5)
    
    def crear_pestaña_conductores(self):
        # pestaña de conductores
        self.pestaña_conductores = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_conductores, text="Gestión de Conductores y Pedidos")
        
        # frame para agregar conductor
        frame_agregar = ttk.LabelFrame(self.pestaña_conductores, text="Agregar/Editar Conductor")
        frame_agregar.pack(fill="x", padx=5, pady=5)
        
        # variables para formulario
        self.nombre_conductor = tk.StringVar()
        self.dni_conductor = tk.StringVar()
        self.telefono_conductor = tk.StringVar()
        self.usuario_conductor = tk.StringVar()
        self.password_conductor = tk.StringVar()
        self.licencia_conductor = tk.StringVar(value="B1")
        self.conductor_editando = None  # para rastrear qué conductor se está editando
        
        # campos del formulario
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
        
        # botones
        ttk.Button(frame_agregar, text="Agregar Conductor", 
                  command=self.agregar_conductor).grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Editar Conductor Seleccionado", 
                  command=self.editar_conductor).grid(row=4, column=0, columnspan=4, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Actualizar Conductor", 
                  command=self.actualizar_conductor).grid(row=5, column=0, columnspan=4, padx=5, pady=5)
        ttk.Button(frame_agregar, text="Cancelar Edición", 
                  command=self.cancelar_edicion_conductor).grid(row=6, column=0, columnspan=4, padx=5, pady=5)
        
        # frame para estado de conductores
        frame_conductores = ttk.LabelFrame(self.pestaña_conductores, text="Estado de Conductores")
        frame_conductores.pack(fill="x", padx=5, pady=5)
        
        # treeview para conductores
        self.tree_conductores = ttk.Treeview(frame_conductores, 
                                            columns=("nombre", "licencia", "estado", "pedido_actual"), 
                                            show="headings", height=4)
        self.tree_conductores.heading("nombre", text="Nombre")
        self.tree_conductores.heading("licencia", text="Licencia")
        self.tree_conductores.heading("estado", text="Estado")
        self.tree_conductores.heading("pedido_actual", text="Pedido Actual")
        self.tree_conductores.pack(fill="x", pady=5)
        
        # frame para gestión de pedidos
        frame_gestion_pedidos = ttk.LabelFrame(self.pestaña_conductores, text="Gestión de Pedidos")
        frame_gestion_pedidos.pack(fill="both", expand=True, padx=5, pady=5)
        
        # notebook para diferentes estados de pedidos
        notebook_pedidos = ttk.Notebook(frame_gestion_pedidos)
        notebook_pedidos.pack(fill="both", expand=True, pady=5)
        
        # pestaña de pedidos disponibles
        pestaña_disponibles = ttk.Frame(notebook_pedidos)
        notebook_pedidos.add(pestaña_disponibles, text="Pedidos Disponibles")
        
        # treeview para pedidos disponibles
        self.tree_pedidos_disponibles = ttk.Treeview(pestaña_disponibles, 
                                                    columns=("id", "usuario", "direccion", "items", "fecha"), 
                                                    show="headings", height=4)
        self.tree_pedidos_disponibles.heading("id", text="ID")
        self.tree_pedidos_disponibles.heading("usuario", text="Cliente")
        self.tree_pedidos_disponibles.heading("direccion", text="Dirección")
        self.tree_pedidos_disponibles.heading("items", text="Items")
        self.tree_pedidos_disponibles.heading("fecha", text="Fecha")
        self.tree_pedidos_disponibles.pack(fill="both", expand=True, pady=5)
        
        # pestaña de pedidos en curso
        pestaña_curso = ttk.Frame(notebook_pedidos)
        notebook_pedidos.add(pestaña_curso, text="Pedidos en Curso")
        
        # treeview para pedidos en curso
        self.tree_pedidos_curso = ttk.Treeview(pestaña_curso, 
                                              columns=("id", "usuario", "direccion", "conductor", "fecha"), 
                                              show="headings", height=4)
        self.tree_pedidos_curso.heading("id", text="ID")
        self.tree_pedidos_curso.heading("usuario", text="Cliente")
        self.tree_pedidos_curso.heading("direccion", text="Dirección")
        self.tree_pedidos_curso.heading("conductor", text="Conductor")
        self.tree_pedidos_curso.heading("fecha", text="Fecha")
        self.tree_pedidos_curso.pack(fill="both", expand=True, pady=5)
        
        # pestaña de pedidos completados
        pestaña_completados = ttk.Frame(notebook_pedidos)
        notebook_pedidos.add(pestaña_completados, text="Pedidos Completados")
        
        # treeview para pedidos completados
        self.tree_pedidos_completados = ttk.Treeview(pestaña_completados, 
                                                    columns=("id", "usuario", "direccion", "conductor", "fecha"), 
                                                    show="headings", height=4)
        self.tree_pedidos_completados.heading("id", text="ID")
        self.tree_pedidos_completados.heading("usuario", text="Cliente")
        self.tree_pedidos_completados.heading("direccion", text="Dirección")
        self.tree_pedidos_completados.heading("conductor", text="Conductor")
        self.tree_pedidos_completados.heading("fecha", text="Fecha")
        self.tree_pedidos_completados.pack(fill="both", expand=True, pady=5)
        
        # botones para gestión de pedidos
        frame_botones_pedidos = ttk.Frame(frame_gestion_pedidos)
        frame_botones_pedidos.pack(pady=5)
        
        ttk.Button(frame_botones_pedidos, text="Asignar Pedido a Conductor", 
                  command=self.asignar_pedido_conductor).pack(side="left", padx=5)
        
        ttk.Button(frame_botones_pedidos, text="Marcar Pedido como Terminado", 
                  command=self.marcar_pedido_terminado_admin).pack(side="left", padx=5)
        
        ttk.Button(frame_botones_pedidos, text="Actualizar Todas las Listas", 
                  command=self.actualizar_listas_admin).pack(side="left", padx=5)
        
        # botón para actualizar lista de conductores
        ttk.Button(frame_conductores, text="Actualizar Lista de Conductores", 
                  command=self.actualizar_lista_conductores).pack(pady=5)
        
        # inicializar listas
        self.actualizar_lista_conductores()
        self.actualizar_lista_pedidos_disponibles()
        self.actualizar_listas_pedidos()
    
    def crear_pestaña_vehiculos(self):
        # pestaña de vehículos
        self.pestaña_vehiculos = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_vehiculos, text="Gestión de Vehículos")
        
        # frame para agregar vehículo
        frame_agregar = ttk.LabelFrame(self.pestaña_vehiculos, text="Agregar Vehículo")
        frame_agregar.pack(fill="x", padx=5, pady=5)
        
        # variables para formulario
        self.nombre_vehiculo = tk.StringVar()
        self.capacidad_vehiculo = tk.DoubleVar()
        self.consumo_vehiculo = tk.DoubleVar()
        self.tipo_combustible = tk.StringVar(value="Nafta Premium")
        self.costo_combustible = tk.DoubleVar(value=1100)
        self.costo_mantenimiento = tk.DoubleVar(value=12000)
        self.es_respaldo = tk.BooleanVar()
        
        # campos del formulario
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
        
        # botón
        ttk.Button(frame_agregar, text="Agregar Vehículo", 
                  command=self.agregar_vehiculo).grid(row=3, column=2, columnspan=2, padx=5, pady=5)
        
        # frame para lista de vehículos
        frame_lista = ttk.LabelFrame(self.pestaña_vehiculos, text="Vehículos Disponibles")
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        # treeview para vehículos
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
        
        # botón para actualizar lista
        ttk.Button(frame_lista, text="Actualizar Lista", 
                  command=self.actualizar_lista_vehiculos).pack(pady=5)
        
        # inicializar lista
        self.actualizar_lista_vehiculos()
    
    def crear_pestaña_multas(self):
        # pestaña de multas
        self.pestaña_multas = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_multas, text="Registro de Multas")
        
        # frame para agregar multa
        frame_agregar = ttk.LabelFrame(self.pestaña_multas, text="Registrar Multa")
        frame_agregar.pack(fill="x", padx=5, pady=5)
        
        # variables para formulario
        self.fecha_multa = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.monto_multa = tk.DoubleVar()
        self.descripcion_multa = tk.StringVar()
        self.responsable_multa = tk.StringVar()
        self.vehiculo_multa = tk.StringVar()
        
        # campos del formulario
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
        
        # botón
        ttk.Button(frame_agregar, text="Registrar Multa", 
                  command=self.registrar_multa).grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        
        # frame para lista de multas
        frame_lista = ttk.LabelFrame(self.pestaña_multas, text="Historial de Multas")
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        # treeview para multas
        self.tree_multas = ttk.Treeview(frame_lista, 
                                      columns=("fecha", "monto", "descripcion", "responsable", "vehiculo"), 
                                      show="headings")
        self.tree_multas.heading("fecha", text="Fecha")
        self.tree_multas.heading("monto", text="Monto ($)")
        self.tree_multas.heading("descripcion", text="Descripción")
        self.tree_multas.heading("responsable", text="Responsable")
        self.tree_multas.heading("vehiculo", text="Vehículo")
        self.tree_multas.pack(fill="both", expand=True, pady=5)
        
        # botón para actualizar lista
        ttk.Button(frame_lista, text="Actualizar Lista", 
                  command=self.actualizar_lista_multas).pack(pady=5)
        
        # inicializar lista
        self.actualizar_lista_multas()
    
    def crear_pestaña_reportes(self):
        # pestaña de reportes
        self.pestaña_reportes = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_reportes, text="Reportes de Gastos")
        
        # frame para generar reportes
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
        
        # frame para mostrar reporte
        frame_reporte = ttk.LabelFrame(self.pestaña_reportes, text="Reporte")
        frame_reporte.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.texto_reporte = tk.Text(frame_reporte, wrap="word")
        scrollbar = ttk.Scrollbar(frame_reporte, orient="vertical", command=self.texto_reporte.yview)
        self.texto_reporte.configure(yscrollcommand=scrollbar.set)
        
        self.texto_reporte.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
    
    # métodos para gestión de productos
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
            
            # limpiar campos
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
            
            # encontrar producto
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
            
            # actualizar el producto que se está editando
            self.producto_editando["nombre"] = self.nombre_producto.get()
            self.producto_editando["categoria"] = self.categoria_producto.get()
            self.producto_editando["precio"] = self.precio_producto.get()
            self.producto_editando["peso"] = self.peso_producto.get()
            self.producto_editando["stock"] = self.stock_producto.get()
            self.producto_editando["marca"] = self.marca_producto.get() if self.marca_producto.get() else "Sin marca"
            self.producto_editando["marca_propia"] = self.es_marca_propia.get()
            
            self.guardar_datos()
            self.actualizar_lista_productos()
            
            # limpiar campos y modo edición
            self.limpiar_campos_producto()
            self.producto_editando = None
            
            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar producto: {str(e)}")
    
    def cancelar_edicion(self):
        ### función para cancelar la edición y limpiar campos
        self.limpiar_campos_producto()
        self.producto_editando = None
        messagebox.showinfo("Información", "Edición cancelada")
    
    def limpiar_campos_producto(self):
        ### función para limpiar todos los campos del formulario de productos
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
            # usar get() para campos que pueden no existir
            self.tree_productos.insert("", "end", values=(
                producto.get("nombre", ""),
                producto.get("categoria", "otros"),
                producto.get("precio", 0),
                producto.get("peso", 0),
                producto.get("stock", 0),
                producto.get("marca", "Sin marca"),
                "Sí" if producto.get("marca_propia", False) else "No"
            ))
    
    # métodos para estadísticas
    def generar_estadisticas(self):
        try:
            # recargar pedidos para asegurar datos actualizados
            self.cargar_pedidos_recientes()
            
            # analizar pedidos para obtener estadísticas
            productos_vendidos = {}
            
            for pedido in PEDIDOS:
                for item in pedido.items:
                    nombre = item["nombre"]
                    cantidad = item["cantidad"]
                    if nombre in productos_vendidos:
                        productos_vendidos[nombre] += cantidad
                    else:
                        productos_vendidos[nombre] = cantidad
            
            # ordenar por cantidad vendida
            productos_ordenados = sorted(productos_vendidos.items(), key=lambda x: x[1], reverse=True)
            
            if productos_ordenados:
                # gráfico de barras
                self.ax1.clear()
                nombres = [p[0] for p in productos_ordenados[:10]]  # top 10
                cantidades = [p[1] for p in productos_ordenados[:10]]
                self.ax1.bar(nombres, cantidades)
                self.ax1.set_title("Productos Más Vendidos")
                self.ax1.set_ylabel("Cantidad Vendida")
                self.ax1.tick_params(axis='x', rotation=45)
                
                # gráfico de torta para categorías
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
                
                # texto de estadísticas
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
        ### función para recargar solo los pedidos desde el archivo
        if os.path.exists(self.pedidos_file):
            try:
                with open(self.pedidos_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:
                        pedidos_data = json.loads(contenido)
                        PEDIDOS.clear()  # limpiar lista actual
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
    
    # métodos para gestión de vehículos
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
            
            # limpiar campos
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
    
    # métodos para gestión de multas
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
            
            # limpiar campos
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
    
    # métodos para reportes
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
        
        # gastos de combustible
        self.texto_reporte.insert(tk.END, "GASTOS DE COMBUSTIBLE:\n")
        for vehiculo in VEHICULOS_DISPONIBLES.values():
            self.texto_reporte.insert(tk.END, f"• {vehiculo.nombre}: ${vehiculo.costo_combustible_por_litro:,.2f}/L\n")
        
        # gastos de mantenimiento
        self.texto_reporte.insert(tk.END, "\nGASTOS DE MANTENIMIENTO:\n")
        for vehiculo in VEHICULOS_DISPONIBLES.values():
            self.texto_reporte.insert(tk.END, f"• {vehiculo.nombre}: ${vehiculo.costo_mantenimiento_por_km:,.2f}/km\n")
        
        # multas
        multas_periodo = [m for m in self.multas if fecha_inicio <= datetime.strptime(m["fecha"], "%Y-%m-%d") <= fecha_fin]
        if multas_periodo:
            total_multas = sum(m["monto"] for m in multas_periodo)
            self.texto_reporte.insert(tk.END, f"\nMULTAS EN EL PERÍODO: ${total_multas:,.2f}\n")
        
        # resumen
        self.texto_reporte.insert(tk.END, "\nRESUMEN:\n")
        self.texto_reporte.insert(tk.END, f"• Vehículos registrados: {len(VEHICULOS_DISPONIBLES)}\n")
        self.texto_reporte.insert(tk.END, f"• Multas en período: {len(multas_periodo)}\n")
        self.texto_reporte.insert(tk.END, f"• Total multas: ${total_multas if multas_periodo else 0:,.2f}\n")

    def actualizar_listas_pedidos(self):
        ### actualiza las listas de pedidos en curso y completados
        # limpiar listas
        for item in self.tree_pedidos_curso.get_children():
            self.tree_pedidos_curso.delete(item)
        
        for item in self.tree_pedidos_completados.get_children():
            self.tree_pedidos_completados.delete(item)
        
        # agregar pedidos en curso
        for pedido in PEDIDOS:
            if pedido.estado == "en_proceso":
                self.tree_pedidos_curso.insert("", "end", values=(
                    pedido.id,
                    pedido.usuario,
                    pedido.direccion_destino,
                    pedido.conductor or "Sin asignar",
                    pedido.fecha_creacion.strftime("%d/%m/%Y %H:%M") if pedido.fecha_creacion else "N/A"
                ))
        
        # agregar pedidos completados
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

    def logout_admin(self):
        ### cierra sesión y vuelve a la pantalla de login
        # limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # volver a la configuración de login
        self.root.title("Panel de Administración - Login")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # centrar ventana
        self.centrar_ventana()
        
        # crear interfaz de login
        self.crear_interfaz_login()

    def actualizar_combobox_responsables(self):
        if hasattr(self, 'combo_responsable_multa'):
            self.combo_responsable_multa['values'] = [c["nombre"] for c in cargar_conductores()]

    def on_tab_changed(self, event):
        if self.notebook.index(self.notebook.select()) == 4:  # verifica si se ha cambiado a la pestaña de multas
            self.actualizar_combobox_responsables()

    def agregar_conductor(self):
        try:
            if not all([self.nombre_conductor.get(), self.dni_conductor.get(), self.telefono_conductor.get()]):
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            # cargar conductores existentes
            conductores = cargar_conductores()
            
            # verificar si ya existe un conductor con esa cédula
            if any(c.get("dni") == self.dni_conductor.get() for c in conductores):
                messagebox.showerror("Error", "Ya existe un conductor con esa cédula")
                return
            
            # crear nuevo conductor
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
            
            # limpiar campos
            self.limpiar_campos_conductor()
            
            # actualizar lista
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
            
            # cargar conductores y encontrar el seleccionado
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
            
            # cargar conductores
            conductores = cargar_conductores()
            
            # verificar si el DNI ya existe en otro conductor
            for c in conductores:
                if c != self.conductor_editando and c.get("dni") == self.dni_conductor.get():
                    messagebox.showerror("Error", "Ya existe otro conductor con ese DNI")
                    return
            
            # actualizar el conductor
            self.conductor_editando["nombre"] = self.nombre_conductor.get()
            self.conductor_editando["dni"] = self.dni_conductor.get()
            self.conductor_editando["telefono"] = self.telefono_conductor.get()
            self.conductor_editando["licencia"] = self.licencia_conductor.get()
            self.conductor_editando["usuario"] = self.usuario_conductor.get()
            self.conductor_editando["password"] = self.password_conductor.get()
            
            guardar_conductores(conductores)
            
            # limpiar campos y modo edición
            self.limpiar_campos_conductor()
            self.conductor_editando = None
            
            # actualizar lista
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
        # limpiar lista actual
        for item in self.tree_conductores.get_children():
            self.tree_conductores.delete(item)
        
        # cargar la lista de conductores desde el json
        conductores = cargar_conductores()
        
        # verificar qué conductores están ocupados basado en pedidos en proceso
        for pedido in PEDIDOS:
            if pedido.estado == "en_proceso" and pedido.conductor:
                for conductor in conductores:
                    if conductor["nombre"] == pedido.conductor:
                        conductor["estado"] = "ocupado"
        
        # guardar cambios de estado
        guardar_conductores(conductores)
        
        # agregar conductores a la lista
        for conductor in conductores:
            # buscar pedido actual del conductor
            pedido_actual = next((p for p in PEDIDOS if p.conductor == conductor["nombre"] and p.estado == "en_proceso"), None)
            pedido_info = f"#{pedido_actual.id}" if pedido_actual else "Sin pedido"
            
            self.tree_conductores.insert("", "end", values=(
                conductor["nombre"],
                conductor.get("licencia", "B1"),
                conductor["estado"],
                pedido_info
            ))
    
    def asignar_pedido_conductor(self):
        # obtener pedido seleccionado
        seleccion_pedido = self.tree_pedidos_disponibles.selection()
        if not seleccion_pedido:
            messagebox.showwarning("Advertencia", "Por favor seleccione un pedido")
            return
        
        # obtener conductor seleccionado
        seleccion_conductor = self.tree_conductores.selection()
        if not seleccion_conductor:
            messagebox.showwarning("Advertencia", "Por favor seleccione un conductor")
            return
        
        try:
            # obtener id del pedido
            valores_pedido = self.tree_pedidos_disponibles.item(seleccion_pedido[0])["values"]
            id_pedido = valores_pedido[0]
            
            # obtener nombre del conductor
            valores_conductor = self.tree_conductores.item(seleccion_conductor[0])["values"]
            nombre_conductor = valores_conductor[0]
            
            # verificar que el conductor esté disponible
            if valores_conductor[2] == "ocupado":
                messagebox.showerror("Error", "Este conductor ya tiene un pedido asignado")
                return
            
            # encontrar pedido
            pedido = next((p for p in PEDIDOS if p.id == id_pedido), None)
            if not pedido:
                messagebox.showerror("Error", "Pedido no encontrado")
                return
            
            # asignar pedido al conductor
            pedido.estado = "en_proceso"
            pedido.conductor = nombre_conductor
            
            # guardar cambios
            self.guardar_pedidos()
            
            # actualizar listas
            self.actualizar_lista_conductores()
            self.actualizar_lista_pedidos_disponibles()
            self.actualizar_listas_pedidos()
            
            messagebox.showinfo("Éxito", f"Pedido #{pedido.id} asignado a {nombre_conductor}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al asignar pedido: {str(e)}")
    
    def marcar_pedido_terminado_admin(self):
        # obtener pedido seleccionado de la lista de pedidos en curso
        seleccion = self.tree_pedidos_curso.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un pedido en curso")
            return
        
        try:
            valores = self.tree_pedidos_curso.item(seleccion[0])["values"]
            id_pedido = valores[0]
            
            # encontrar pedido
            pedido = next((p for p in PEDIDOS if p.id == id_pedido), None)
            if not pedido:
                messagebox.showerror("Error", "Pedido no encontrado")
                return
            
            # marcar como terminado
            pedido.estado = "completado"
            pedido.conductor = None
            
            # guardar cambios
            self.guardar_pedidos()
            
            # actualizar listas
            self.actualizar_lista_conductores()
            self.actualizar_listas_pedidos()
            
            messagebox.showinfo("Éxito", f"Pedido #{pedido.id} marcado como terminado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al marcar pedido como terminado: {str(e)}")
    
    def actualizar_listas_admin(self):
        ### actualiza todas las listas de la pestaña de conductores
        self.actualizar_lista_conductores()
        self.actualizar_lista_pedidos_disponibles()
        self.actualizar_listas_pedidos()
    
    def guardar_pedidos(self):
        ### guarda los pedidos en el archivo json
        try:
            # convertir pedidos a formato json
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
            
            # guardar en archivo
            with open("data/pedidos.json", "w", encoding="utf-8") as f:
                json.dump(pedidos_data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar pedidos: {str(e)}")

    def actualizar_lista_pedidos_disponibles(self):
        ### actualiza la lista de pedidos disponibles
        # limpiar lista actual
        for item in self.tree_pedidos_disponibles.get_children():
            self.tree_pedidos_disponibles.delete(item)
        
        # agregar pedidos pendientes
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