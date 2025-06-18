import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from datums.pedido import Pedido, PEDIDOS

class InterfazUsuario:
    def __init__(self, root, parent=None):
        self.root = root
        self.parent = parent
        self.root.title("Sistema de Pedidos - Usuario")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_usuario)
        
        # variables de datos
        self.data_dir = "data"
        self.productos_file = os.path.join(self.data_dir, "productos.json")
        self.pedidos_file = os.path.join(self.data_dir, "pedidos.json")
        
        # variables del carrito
        self.carrito = []
        self.total_carrito = tk.StringVar(value="$0")
        
        # cargar datos
        self.cargar_datos_local()
        
        # crear interfaz
        self.crear_interfaz()
    
    def cerrar_usuario(self):
        self.root.destroy()
        if self.parent:
            self.parent.deiconify()
    
    def cargar_datos_local(self):
        # cargar o inicializar productos
        if os.path.exists(self.productos_file):
            with open(self.productos_file, 'r', encoding='utf-8') as f:
                self.productos = json.load(f)
        else:
            # productos de ejemplo, si no no anda
            self.productos = [
                {"nombre": "Jabón líquido", "precio": 1200, "peso": 0.5, "stock": 95},
                {"nombre": "Shampoo", "precio": 1500, "peso": 0.5, "stock": 94},
                {"nombre": "Papel higiénico", "precio": 800, "peso": 1.0, "stock": 200},
                {"nombre": "Detergente", "precio": 2000, "peso": 2.0, "stock": 50},
                {"nombre": "Limpia pisos", "precio": 1800, "peso": 1.5, "stock": 50},
                {"nombre": "Arroz", "precio": 1500, "peso": 1.0, "stock": 100},
                {"nombre": "Fideos", "precio": 800, "peso": 0.5, "stock": 100},
                {"nombre": "Aceite", "precio": 2500, "peso": 1.0, "stock": 80},
                {"nombre": "Azúcar", "precio": 1200, "peso": 1.0, "stock": 40},
                {"nombre": "Harina", "precio": 1000, "peso": 1.0, "stock": 120}
            ]
            self.guardar_datos_local()
        
        # cargar pedidos existentes
        if os.path.exists(self.pedidos_file):
            try:
                with open(self.pedidos_file, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:  # verificar que el archivo no esté vacío
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
                        # archivo vacío, inicializar lista vacía
                        PEDIDOS.clear()
            except (json.JSONDecodeError, FileNotFoundError):
                # si hay error al leer json, inicializar lista vacía
                PEDIDOS.clear()
        else:
            # archivo no existe, inicializar lista vacía
            PEDIDOS.clear()
    
    def guardar_datos_local(self):
        # guardar productos
        with open(self.productos_file, 'w', encoding='utf-8') as f:
            json.dump(self.productos, f, ensure_ascii=False, indent=4)
        
        # guardar pedidos
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
    
    def inicializar_productos(self):
        productos_iniciales = [
            # productos de higiene
            {"nombre": "Jabón líquido", "categoria": "higiene", "precio": 1200, "peso": 0.5, "stock": 100},
            {"nombre": "Shampoo", "categoria": "higiene", "precio": 1500, "peso": 0.5, "stock": 100},
            {"nombre": "Papel higiénico", "categoria": "higiene", "precio": 800, "peso": 1.0, "stock": 200},
            {"nombre": "Detergente", "categoria": "higiene", "precio": 2000, "peso": 2.0, "stock": 50},
            {"nombre": "Limpia pisos", "categoria": "higiene", "precio": 1800, "peso": 1.5, "stock": 50},
            
            # productos alimenticios
            {"nombre": "Arroz", "categoria": "alimentos", "precio": 1500, "peso": 1.0, "stock": 100},
            {"nombre": "Fideos", "categoria": "alimentos", "precio": 800, "peso": 0.5, "stock": 150},
            {"nombre": "Aceite", "categoria": "alimentos", "precio": 2500, "peso": 1.0, "stock": 80},
            {"nombre": "Azúcar", "categoria": "alimentos", "precio": 1200, "peso": 1.0, "stock": 100},
            {"nombre": "Harina", "categoria": "alimentos", "precio": 1000, "peso": 1.0, "stock": 120}
        ]
        
        # guardar productos iniciales
        with open(self.productos_file, 'w', encoding='utf-8') as f:
            json.dump(productos_iniciales, f, ensure_ascii=False, indent=2)
        
        return productos_iniciales
    
    def crear_interfaz(self):
        # frame principal
        self.marco_principal = ttk.Frame(self.root)
        self.marco_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # notebook para pestañas
        self.notebook = ttk.Notebook(self.marco_principal)
        self.notebook.pack(fill="both", expand=True)
        
        # pestaña de productos
        self.pestaña_productos = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_productos, text="Productos")
        
        # pestaña de carrito
        self.pestaña_carrito = ttk.Frame(self.notebook)
        self.notebook.add(self.pestaña_carrito, text="Carrito")
        
        # crear contenido de las pestañas
        self.crear_pestaña_productos()
        self.crear_pestaña_carrito()
    
    def crear_pestaña_productos(self):
        # frame para filtros
        frame_filtros = ttk.LabelFrame(self.pestaña_productos, text="Filtros")
        frame_filtros.pack(fill="x", padx=5, pady=5)
        
        # categoría
        ttk.Label(frame_filtros, text="Categoría:").pack(side="left", padx=5)
        self.categoria_var = tk.StringVar(value="todos")
        combo_categoria = ttk.Combobox(frame_filtros, textvariable=self.categoria_var, 
                                     values=["todos", "higiene", "alimentos"])
        combo_categoria.pack(side="left", padx=5)
        combo_categoria.bind("<<ComboboxSelected>>", self.actualizar_lista_productos)
        
        # frame para lista de productos
        frame_lista = ttk.Frame(self.pestaña_productos)
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        # treeview para productos
        self.tree_productos = ttk.Treeview(frame_lista, 
                                         columns=("nombre", "precio", "peso", "stock"), 
                                         show="headings")
        self.tree_productos.heading("nombre", text="Nombre")
        self.tree_productos.heading("precio", text="Precio ($)")
        self.tree_productos.heading("peso", text="Peso (kg)")
        self.tree_productos.heading("stock", text="Stock")
        self.tree_productos.pack(side="left", fill="both", expand=True)
        
        # scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", 
                                command=self.tree_productos.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_productos.configure(yscrollcommand=scrollbar.set)
        
        # botón agregar al carrito
        ttk.Button(self.pestaña_productos, text="Agregar al Carrito", 
                  command=self.agregar_al_carrito).pack(pady=10)
        
        # inicializar lista de productos
        self.actualizar_lista_productos()
    
    def crear_pestaña_carrito(self):
        # frame para lista del carrito
        frame_carrito = ttk.Frame(self.pestaña_carrito)
        frame_carrito.pack(fill="both", expand=True, padx=5, pady=5)
        
        # treeview para carrito
        self.tree_carrito = ttk.Treeview(frame_carrito, 
                                       columns=("nombre", "precio", "cantidad", "subtotal"),
                                       show="headings")
        self.tree_carrito.heading("nombre", text="Nombre")
        self.tree_carrito.heading("precio", text="Precio ($)")
        self.tree_carrito.heading("cantidad", text="Cantidad")
        self.tree_carrito.heading("subtotal", text="Subtotal ($)")
        self.tree_carrito.pack(side="left", fill="both", expand=True)
        
        # scrollbar
        scrollbar = ttk.Scrollbar(frame_carrito, orient="vertical", 
                                command=self.tree_carrito.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_carrito.configure(yscrollcommand=scrollbar.set)
        
        # frame para total y botones
        frame_total = ttk.Frame(self.pestaña_carrito)
        frame_total.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(frame_total, text="Total:").pack(side="left", padx=5)
        ttk.Label(frame_total, textvariable=self.total_carrito).pack(side="left", padx=5)
        
        # botones
        ttk.Button(frame_total, text="Eliminar del Carrito", 
                  command=self.eliminar_del_carrito).pack(side="right", padx=5)
        ttk.Button(frame_total, text="Finalizar Compra", 
                  command=self.finalizar_compra).pack(side="right", padx=5)
    
    def actualizar_lista_productos(self, event=None):
        # limpiar lista actual
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        # obtener filtro de categoría
        categoria = self.categoria_var.get()
        
        try:
            # filtrar productos locales
            productos = self.productos if categoria == "todos" else [
                p for p in self.productos if p["categoria"] == categoria
            ]
            
            # agregar productos a la lista
            for producto in productos:
                self.tree_productos.insert("", "end",
                                         values=(producto["nombre"], producto["precio"], 
                                                producto["peso"], producto["stock"]))
        except Exception as e:
            print(f"Error al actualizar lista de productos: {str(e)}")
            messagebox.showerror("Error", "Error al cargar los productos")
    
    def agregar_al_carrito(self):
        # obtener producto seleccionado
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return
        
        # obtener datos del producto
        valores = self.tree_productos.item(seleccion[0])["values"]
        nombre = valores[0]
        precio = float(valores[1])
        
        # encontrar producto en la lista
        producto = next((p for p in self.productos if p["nombre"] == nombre), None)
        if not producto or producto["stock"] <= 0:
            messagebox.showwarning("Advertencia", "No hay stock disponible")
            return
        
        # pedir cantidad
        cantidad = simpledialog.askinteger("Cantidad", 
            f"Ingrese la cantidad de {nombre}:",
            minvalue=1, maxvalue=producto["stock"])
        
        if cantidad:
            # agregar al carrito
            self.carrito.append({
                "nombre": nombre,
                "precio": precio,
                "cantidad": cantidad,
                "subtotal": precio * cantidad
            })
            
            # actualizar lista del carrito
            self.actualizar_carrito()
    
    def actualizar_carrito(self):
        # limpiar lista actual
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        # calcular total
        total = 0
        
        # agregar items al carrito
        for item in self.carrito:
            self.tree_carrito.insert("", "end",
                                   values=(item["nombre"], item["precio"], 
                                          item["cantidad"], item["subtotal"]))
            total += item["subtotal"]
        
        # actualizar total
        self.total_carrito.set(f"${total:.2f}")
    
    def eliminar_del_carrito(self):
        # obtener selección
        seleccion = self.tree_carrito.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un item")
            return
        
        # eliminar del carrito
        nombre = self.tree_carrito.item(seleccion[0])["text"]
        self.carrito = [item for item in self.carrito if item["nombre"] != nombre]
        
        # actualizar carrito
        self.actualizar_carrito()
    
    def finalizar_compra(self):
        if not self.carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
        
        # pedir nombre del usuario
        nombre_usuario = simpledialog.askstring("Datos de Usuario", 
            "Ingrese su nombre:")
        
        if not nombre_usuario:
            return
        
        # pedir dirección de entrega
        direccion = simpledialog.askstring("Dirección de Entrega", 
            "Ingrese la dirección de entrega:")
        
        if not direccion:
            return
        
        # crear nuevo pedido
        nuevo_pedido = Pedido(
            id=len(PEDIDOS) + 1,
            usuario=nombre_usuario,
            items=self.carrito.copy(),
            direccion_destino=direccion
        )
        
        # agregar a la lista de pedidos
        PEDIDOS.append(nuevo_pedido)
        
        # guardar pedidos en archivo
        self.guardar_datos_local()
        
        # limpiar carrito
        self.carrito = []
        self.actualizar_carrito()
        
        messagebox.showinfo("Éxito", 
            f"Pedido #{nuevo_pedido.id} creado exitosamente.\n" +
            f"Usuario: {nombre_usuario}\n" +
            f"Dirección de entrega: {direccion}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazUsuario(root)
    root.mainloop()
