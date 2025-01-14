from kivy.uix.screenmanager import Screen
from kivymd.uix.textfield import MDTextField

from bcrypt import gensalt,hashpw
from pymongo import MongoClient
from os import getenv

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText
)

class RegisterScreen(Screen):
    def register(self):
        doc = {
            'name': self.ids.input_nombre.text, 
            'last_name': self.ids.input_apellido.text, 
            'email': self.ids.input_email.text, 
            'password': hashpw(self.ids.input_password.text.encode('utf-8'), gensalt()), 
            'type': 'encuestador'
            }
        try:
            # with MongoClient(getenv('MONGO_URI')) as mongo:
            with MongoClient("mongodb+srv://user:contrasenia@clustered.kev66.mongodb.net/?retryWrites=true&w=majority&appName=ClusterED") as mongo:
            # mongo = MongoClient("mongodb+srv://user:contrasenia@clustered.kev66.mongodb.net/?retryWrites=true&w=majority&appName=ClusterED")  # Replace with your MongoDB URI if needed
                db = mongo["DBEncuestasDigitales"]
                collection = db["user"]
                res = collection.insert_one(doc)
                print(f"Document inserted with ID: {res.inserted_id}")
            # res = mongo.DBEncuestasDigitales.user.insert_one(doc)
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
            # if res.acknowledged:            
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

class CompareField(MDTextField):
    def compare(self, other: MDTextField):
        self.error = self.text != other.text

