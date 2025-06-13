import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim
from datums.vehiculos import berlingo_furgon

root = tk.Tk()
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

mapa_frame = ttk.LabelFrame(main_frame, text="Mapa")
mapa_frame.pack(side = "left", fill="both", expand=True, padx=5, pady=5)
mapa = TkinterMapView(mapa_frame, width=600, height=500, corner_radius=0)
mapa.pack(fill="both", expand=True)
mapa.set_position(-32.9510139, -60.6260167)
mapa.set_zoom(15)

# frame para los datos del vehículo
datos_frame = ttk.LabelFrame(main_frame, text="Datos del Vehículo")
datos_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

# Etiquetas para mostrar los datos del vehículo
nombre_label = ttk.Label(datos_frame, text="Nombre:")
nombre_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
nombre_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

combustible_label = ttk.Label(datos_frame, text="Combustible:")
combustible_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
combustible_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

capacidad_tanque_label = ttk.Label(datos_frame, text="Capacidad del Tanque:")
capacidad_tanque_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
capacidad_tanque_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")

capacidad_maxima_label = ttk.Label(datos_frame, text="Capacidad Máxima:")
capacidad_maxima_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
capacidad_maxima_label.grid(row=3, column=1, padx=5, pady=5, sticky="w")

velocidad_promedio_label = ttk.Label(datos_frame, text="Velocidad Promedio:")
velocidad_promedio_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
velocidad_promedio_label.grid(row=4, column=1, padx=5, pady=5, sticky="w")

consumicion_combustible_label = ttk.Label(datos_frame, text="Consumición de Combustible:")
consumicion_combustible_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
consumicion_combustible_label.grid(row=5, column=1, padx=5, pady=5, sticky="w")

costo_mantenimiento_label = ttk.Label(datos_frame, text="Costo de Mantenimiento:")
costo_mantenimiento_label.grid(row=6, column=0, padx=5, pady=5, sticky="e")
costo_mantenimiento_label.grid(row=6, column=1, padx=5, pady=5, sticky="w")

costo_combustible_label = ttk.Label(datos_frame, text="Costo de Combustible:")
costo_combustible_label.grid(row=7, column=0, padx=5, pady=5, sticky="e")
costo_combustible_label.grid(row=7, column=1, padx=5, pady=5, sticky="w")

#Etiquetas de los datos del vehículo
nombre_label.config(text=berlingo_furgon.nombre)
combustible_label.config(text=berlingo_furgon.combustible)
capacidad_tanque_label.config(text=berlingo_furgon.capacidad_tanque)
capacidad_maxima_label.config(text=berlingo_furgon.capacidad_maxima)
velocidad_promedio_label.config(text=berlingo_furgon.velocidad_promedio)
consumicion_combustible_label.config(text=berlingo_furgon.consumicion_combustible)
costo_mantenimiento_label.config(text=berlingo_furgon.costo_mantenimiento)
costo_combustible_label.config(text=berlingo_furgon.costo_combustible)

root.mainloop()