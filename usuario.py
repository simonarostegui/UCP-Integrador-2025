import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
from dotenv import load_dotenv

class InterfazUsuario:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Pedidos - Usuario")
        self.root.geometry("800x600")
        
        # Inicializar almacenamiento local
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self.productos_file = os.path.join(self.data_dir, "productos.json")
        self.pedidos_file = os.path.join(self.data_dir, "pedidos.json")
        
        # Cargar datos
        self.cargar_datos_local()
        
        # Variables
        self.carrito = []
        self.total_carrito = tk.DoubleVar(value=0.0)
        
        # Crear interfaz
        self.crear_interfaz()
    
    def cargar_datos_local(self):
        # Cargar o inicializar productos
        if not os.path.exists(self.productos_file):
            self.productos = self.inicializar_productos()
        else:
            with open(self.productos_file, 'r', encoding='utf-8') as f:
                self.productos = json.load(f)
        
        # Cargar o inicializar pedidos
        if not os.path.exists(self.pedidos_file):
            self.pedidos = []
        else:
            with open(self.pedidos_file, 'r', encoding='utf-8') as f:
                self.pedidos = json.load(f)
    
    def guardar_datos_local(self):
        # Guardar productos
        with open(self.productos_file, 'w', encoding='utf-8') as f:
            json.dump(self.productos, f, ensure_ascii=False, indent=2)
        
        # Guardar pedidos
        with open(self.pedidos_file, 'w', encoding='utf-8') as f:
            json.dump(self.pedidos, f, ensure_ascii=False, indent=2)
    
    def inicializar_productos(self):
        productos_iniciales = [
            # Productos de higiene
            {"nombre": "Jabón líquido", "categoria": "higiene", "precio": 1200, "peso": 0.5, "stock": 100},
            {"nombre": "Shampoo", "categoria": "higiene", "precio": 1500, "peso": 0.5, "stock": 100},
            {"nombre": "Papel higiénico", "categoria": "higiene", "precio": 800, "peso": 1.0, "stock": 200},
            {"nombre": "Detergente", "categoria": "higiene", "precio": 2000, "peso": 2.0, "stock": 50},
            {"nombre": "Limpia pisos", "categoria": "higiene", "precio": 1800, "peso": 1.5, "stock": 50},
            
            # Productos alimenticios
            {"nombre": "Arroz", "categoria": "alimentos", "precio": 1500, "peso": 1.0, "stock": 100},
            {"nombre": "Fideos", "categoria": "alimentos", "precio": 800, "peso": 0.5, "stock": 150},
            {"nombre": "Aceite", "categoria": "alimentos", "precio": 2500, "peso": 1.0, "stock": 80},
            {"nombre": "Azúcar", "categoria": "alimentos", "precio": 1200, "peso": 1.0, "stock": 100},
            {"nombre": "Harina", "categoria": "alimentos", "precio": 1000, "peso": 1.0, "stock": 120}
        ]
        
        # Guardar productos iniciales
        with open(self.productos_file, 'w', encoding='utf-8') as f:
            json.dump(productos_iniciales, f, ensure_ascii=False, indent=2)
        
        return productos_iniciales
    
    def crear_interfaz(self):
        # Frame principal
        self.marco_principal = ttk.Frame(self.root)
        self.marco_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.marco_principal)
        self.notebook.pack(fill="both", expand=True)
        
        # Pestaña de productos
        self.pestaña_productos = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_productos, text="Productos")
        
        # Pestaña de carrito
        self.pestaña_carrito = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_carrito, text="Carrito")
        
        # Crear contenido de las pestañas
        self.crear_pestaña_productos()
        self.crear_pestaña_carrito()
    
    def crear_pestaña_productos(self):
        # Frame para filtros
        frame_filtros = ttk.LabelFrame(self.pestaña_productos, text="Filtros")
        frame_filtros.pack(fill="x", padx=5, pady=5)
        
        # Categoría
        ttk.Label(frame_filtros, text="Categoría:").pack(side="left", padx=5)
        self.categoria_var = tk.StringVar(value="todos")
        combo_categoria = ttk.Combobox(frame_filtros, textvariable=self.categoria_var, 
                                     values=["todos", "higiene", "alimentos"])
        combo_categoria.pack(side="left", padx=5)
        combo_categoria.bind("<<ComboboxSelected>>", self.actualizar_lista_productos)
        
        # Frame para lista de productos
        frame_lista = ttk.Frame(self.pestaña_productos)
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Treeview para productos
        self.tree_productos = ttk.Treeview(frame_lista, 
                                         columns=("nombre", "precio", "peso", "stock"), 
                                         show="headings")
        self.tree_productos.heading("nombre", text="Nombre")
        self.tree_productos.heading("precio", text="Precio ($)")
        self.tree_productos.heading("peso", text="Peso (kg)")
        self.tree_productos.heading("stock", text="Stock")
        self.tree_productos.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", 
                                command=self.tree_productos.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_productos.configure(yscrollcommand=scrollbar.set)
        
        # Botón agregar al carrito
        ttk.Button(self.pestaña_productos, text="Agregar al Carrito", 
                  command=self.agregar_al_carrito).pack(pady=10)
        
        # Inicializar lista de productos
        self.actualizar_lista_productos()
    
    def crear_pestaña_carrito(self):
        # Frame para lista del carrito
        frame_carrito = ttk.Frame(self.pestaña_carrito)
        frame_carrito.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Treeview para carrito
        self.tree_carrito = ttk.Treeview(frame_carrito, 
                                       columns=("nombre", "precio", "cantidad", "subtotal"),
                                       show="headings")
        self.tree_carrito.heading("nombre", text="Nombre")
        self.tree_carrito.heading("precio", text="Precio ($)")
        self.tree_carrito.heading("cantidad", text="Cantidad")
        self.tree_carrito.heading("subtotal", text="Subtotal ($)")
        self.tree_carrito.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_carrito, orient="vertical", 
                                command=self.tree_carrito.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_carrito.configure(yscrollcommand=scrollbar.set)
        
        # Frame para total y botones
        frame_total = ttk.Frame(self.pestaña_carrito)
        frame_total.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(frame_total, text="Total:").pack(side="left", padx=5)
        ttk.Label(frame_total, textvariable=self.total_carrito).pack(side="left", padx=5)
        
        # Botones
        ttk.Button(frame_total, text="Eliminar del Carrito", 
                  command=self.eliminar_del_carrito).pack(side="right", padx=5)
        ttk.Button(frame_total, text="Realizar Pedido", 
                  command=self.realizar_pedido).pack(side="right", padx=5)
    
    def actualizar_lista_productos(self, event=None):
        # Limpiar lista actual
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        # Obtener filtro de categoría
        categoria = self.categoria_var.get()
        
        try:
            # Filtrar productos locales
            productos = self.productos if categoria == "todos" else [
                p for p in self.productos if p["categoria"] == categoria
            ]
            
            # Agregar productos a la lista
            for producto in productos:
                self.tree_productos.insert("", "end",
                                         values=(producto["nombre"], producto["precio"], 
                                                producto["peso"], producto["stock"]))
        except Exception as e:
            print(f"Error al actualizar lista de productos: {str(e)}")
            messagebox.showerror("Error", "Error al cargar los productos")
    
    def agregar_al_carrito(self):
        # Obtener producto seleccionado
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return
        
        # Obtener datos del producto
        valores = self.tree_productos.item(seleccion[0])["values"]
        nombre = valores[0]
        precio = float(valores[1])
        
        # Encontrar producto en la lista
        producto = next((p for p in self.productos if p["nombre"] == nombre), None)
        if not producto or producto["stock"] <= 0:
            messagebox.showwarning("Advertencia", "No hay stock disponible")
            return
        
        # Pedir cantidad
        cantidad = simpledialog.askinteger("Cantidad", 
            f"Ingrese la cantidad de {nombre}:",
            minvalue=1, maxvalue=producto["stock"])
        
        if cantidad:
            # Agregar al carrito
            self.carrito.append({
                "nombre": nombre,
                "precio": precio,
                "cantidad": cantidad,
                "subtotal": precio * cantidad
            })
            
            # Actualizar lista del carrito
            self.actualizar_carrito()
    
    def actualizar_carrito(self):
        # Limpiar lista actual
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        # Calcular total
        total = 0
        
        # Agregar items al carrito
        for item in self.carrito:
            self.tree_carrito.insert("", "end",
                                   values=(item["nombre"], item["precio"], 
                                          item["cantidad"], item["subtotal"]))
            total += item["subtotal"]
        
        # Actualizar total
        self.total_carrito.set(f"${total:.2f}")
    
    def eliminar_del_carrito(self):
        # Obtener selección
        seleccion = self.tree_carrito.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un item")
            return
        
        # Eliminar del carrito
        nombre = self.tree_carrito.item(seleccion[0])["text"]
        self.carrito = [item for item in self.carrito if item["nombre"] != nombre]
        
        # Actualizar carrito
        self.actualizar_carrito()
    
    def realizar_pedido(self):
        if not self.carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
        
        # Crear pedido
        pedido = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.carrito,
            "total": sum(item["subtotal"] for item in self.carrito)
        }
        
        # Actualizar stock
        for item in self.carrito:
            producto = next(p for p in self.productos if p["nombre"] == item["nombre"])
            producto["stock"] -= item["cantidad"]
        
        # Guardar pedido
        self.pedidos.append(pedido)
        self.guardar_datos_local()
        
        # Limpiar carrito
        self.carrito = []
        self.actualizar_carrito()
        
        messagebox.showinfo("Éxito", "Pedido realizado correctamente")

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazUsuario(root)
    root.mainloop()
