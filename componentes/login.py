from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.clock import Clock
from pymongo import MongoClient
from os import getenv
from bcrypt import checkpw

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogSupportingText
)

from queue import Queue
from threading import Thread

class LoginException(Exception):
    def __init__(self, icon: str = '', *args: object):
        self.icon = icon
        return super().__init__(*args)

class LoginScreen(Screen):

    def __init__(self, **kw):
        self.queue = Queue()
        super().__init__(**kw)

    def login(self, *args):
        self.ids.spinner.active = True
        self.ids.button_enter.disabled = True
        correo = self.ids.input_email.text
        passwd = self.ids.input_password.text
        Thread(target=self.connect, args=(correo, passwd)).start()
        # t.join()

    def connect(self, correo: str, passwd: str):
        try:
            with MongoClient(getenv('MONGO_URI')) as mongo:
                res = mongo.test.user.find_one({
                    'email': correo
                })
            
            if not res:
                raise LoginException('account-alert',f'Usuario {correo} no encontrado')
            elif not checkpw(passwd.encode('utf-8'), res['password']):
                raise LoginException('security',f'Contraseña incorrecta para {correo}')
            else:
                self.queue.put(res)
        except Exception as exc:
            self.queue.put(exc)
        finally:
            Clock.schedule_once(self.evaluate)

    def evaluate(self, *args):
        res = self.queue.get()
        try:
            if isinstance(res, BaseException):
                raise res
        except LoginException as e:
            MDDialog(
                MDDialogIcon(
                    icon=e.icon
                ),
                MDDialogSupportingText(
                    text=str(e)
                )
            ).open()
        except Exception:
            MDDialog(
                MDDialogIcon(
                    icon='database-alert'
                ),
                MDDialogSupportingText(
                    text='No se puede conectar con el servicio de autenticación.'
                )
            ).open()
        else:
            app = App.get_running_app()
            app.user = res
        self.ids.spinner.active = False
        self.ids.button_enter.disabled = False

