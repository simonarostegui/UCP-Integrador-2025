import tkinter as tk
from tkinter import ttk, messagebox
from logistica import CalculadoraLogistica
from usuario import InterfazUsuario
from admin import InterfazAdmin
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datums.vehiculos import VEHICULOS_DISPONIBLES, Vehiculo
from datums.conductor import CONDUCTOR_PREDETERMINADO
from datums.ruta import PuntoRuta, Ruta
import math
import requests
import googlemaps
import os
from dotenv import load_dotenv

# cargar variables de entorno
load_dotenv()

class LoginInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Logística")
        self.root.geometry("400x300")
        
        # centrar la ventana
        self.centrar_ventana()
        
        # crear el marco principal
        self.marco_principal = ttk.Frame(root)
        self.marco_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # título
        ttk.Label(self.marco_principal, 
                 text="Sistema de Logística", 
                 font=("Helvetica", 16, "bold")).pack(pady=20)
        
        # botones para acceder a cada cosa
        ttk.Button(self.marco_principal, 
                  text="Acceso Usuario",
                  command=self.acceso_usuario,
                  width=20).pack(pady=10)
        
        ttk.Button(self.marco_principal, 
                  text="Acceso Conductor",
                  command=self.acceso_conductor,
                  width=20).pack(pady=10)
        
        ttk.Button(self.marco_principal, 
                  text="Acceso Admin",
                  command=self.acceso_admin,
                  width=20).pack(pady=10)
    
    def centrar_ventana(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def acceso_usuario(self):
        self.root.withdraw()
        win = tk.Toplevel(self.root)
        app = InterfazUsuario(win, parent=self.root)
        win.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana_secundaria(win))
    
    def acceso_conductor(self):
        self.root.withdraw()
        win = tk.Toplevel(self.root)
        app = CalculadoraLogistica(win, parent=self.root)
        win.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana_secundaria(win))
    
    def acceso_admin(self):
        self.root.withdraw()
        win = tk.Toplevel(self.root)
        app = InterfazAdmin(win, parent=self.root)
        win.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana_secundaria(win))

    def cerrar_ventana_secundaria(self, win):
        win.destroy()
        self.root.deiconify()

    
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginInterface(root)
    root.mainloop()