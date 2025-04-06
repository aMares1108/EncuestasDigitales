from kivy.uix.accordion import BooleanProperty
from kivy.uix.screenmanager import Screen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from bcrypt import gensalt,hashpw
from pymongo import MongoClient
from os import getenv

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText
)

from kivy.properties import BooleanProperty

class RegisterScreen(Screen):
    user_type_validator = BooleanProperty(True)

    def register(self):
        doc = {
            'name': self.ids.input_nombre.text, 
            'last_name': self.ids.input_apellido.text, 
            'email': self.ids.input_email.text, 
            'password': hashpw(self.ids.input_password.text.encode('utf-8'), gensalt()), 
            'type': self.ids.input_user_type.text
            }
        try:
            with MongoClient(getenv('MONGO_URI')) as mongo:
                db = mongo.get_database()
                res = db.user.insert_one(doc)
        except:
            MDDialog(
                MDDialogIcon(
                    icon='alert'
                ),
                MDDialogHeadlineText(
                    text='No se puede conectar con el servicio de autenticación.'
                )
            ).open()
        else:
            if res.acknowledged:
                self.manager.transition.direction = 'left'
                self.manager.current = 'principal'
            else:
                MDDialog(
                    MDDialogIcon(
                        icon='alert'
                    ),
                    MDDialogHeadlineText(
                        text='No se pudo crear el usuario.'
                    )
                ).open()
    def open_menu(self, item):
        menu_items = [
            {
                "text": f"{data}",
                "on_release": lambda x=f"{data}": self.menu_callback(x),
            } for data in ['Encuestador', 'Investigador']
        ]
        MDDropdownMenu(caller=item, items=menu_items).open()

    def menu_callback(self, text_item):
        self.user_type_validator = False
        self.ids.input_user_type.text = text_item

class CompareField(MDTextField):
    def compare(self, other: MDTextField):
        self.error = self.text != other.text

