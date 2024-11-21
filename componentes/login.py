from kivy.uix.screenmanager import Screen
from kivy.app import App
from pymongo import MongoClient
from os import getenv
from bcrypt import checkpw

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText
)
from kivymd.uix.progressindicator import MDCircularProgressIndicator

class LoginScreen(Screen):
    def show_load(self):
        MDDialog(
            MDDialogHeadlineText(
                MDCircularProgressIndicator(size_hint=(None, None))
            )
        ).open()
        
    def login(self):
        correo = self.ids.input_email.text
        passwd = self.ids.input_password.text

        try:
            with MongoClient(getenv('MONGO_URI')) as mongo:
                res = mongo.test.user.find_one({
                    'email': correo
                })
        except Exception as e:
            MDDialog(
                MDDialogIcon(
                    icon='alert'
                ),
                MDDialogHeadlineText(
                    text='No se puede conectar con el servicio de autenticación.'
                )
            ).open()
        else:
            if not res:
                MDDialog(
                    MDDialogIcon(
                        icon='account-alert'
                    ),
                    MDDialogHeadlineText(
                        text=f'Usuario {correo} no encontrado'
                    )
                ).open()
            elif not checkpw(passwd.encode('utf-8'), res['password']):
                MDDialog(
                    MDDialogIcon(
                        icon='account-alert'
                    ),
                    MDDialogHeadlineText(
                        text=f'Contraseña incorrecta para {correo}'
                    )
                ).open()
            else:
                app = App.get_running_app()
                app.user = res
                # self.manager.current = 'principal'
