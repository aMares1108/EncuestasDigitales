from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import BooleanProperty
from os.path import exists
from os import makedirs
from time import time

class AplicarScreen(Screen):
    state_validator = BooleanProperty(True)

    def register(self):
        user_data = [self.ids.get(input).text for input in self.ids if input.startswith("input_")]
        user_data.insert(0, str(int(time())))
        if not exists('respuestas'):
            makedirs('respuestas')
        with open('respuestas/temp.tsv', 'w', encoding='utf-8', newline='') as tsv:
            tsv.write("\t".join(user_data))
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