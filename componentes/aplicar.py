from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import BooleanProperty
import csv
from os.path import exists
from os import makedirs

class AplicarScreen(Screen):
    state_validator = BooleanProperty(True)

    def register(self):
        user_data = [self.ids.get(input).text for input in self.ids if input.startswith("input_")]
        if not exists('respuestas'):
            makedirs('respuestas')
        with open('respuestas/temp.tsv', 'w', encoding='utf-8') as tsv:
            escritor = csv.writer(tsv, delimiter='\t')
            escritor.writerow(user_data)
        self.manager.current = 'encuestas'

    def open_menu(self, item):
        estados_mexico = [
                "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas",
                "Chihuahua", "Coahuila", "Colima", "Durango", "Guanajuato", "Guerrero",
                "Hidalgo", "Jalisco", "México", "Michoacán", "Morelos", "Nayarit",
                "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo", "San Luis Potosí",
                "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz",
                "Yucatán","Zacatecas"
            ]
        menu_items = [
            {
                "text": f"{data}",
                "on_release": lambda x=f"{data}": self.menu_callback(x),
            } for data in estados_mexico
        ]
        MDDropdownMenu(caller=item, items=menu_items).open()

    def menu_callback(self, text_item):
        self.state_validator = False
        self.ids.input_estado.text = text_item