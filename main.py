import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim

root = tk.Tk()
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

mapa_frame = ttk.LabelFrame(main_frame, text="Mapa")
mapa_frame.pack(side = "left", fill="both", expand=True, padx=5, pady=5)
mapa = TkinterMapView(mapa_frame, width=600, height=500, corner_radius=0)
mapa.pack(fill="both", expand=True)
mapa.set_position(-32.9510139, -60.6260167, "TEST")
mapa.set_zoom(15)

root.mainloop()
