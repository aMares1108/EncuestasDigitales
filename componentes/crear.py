from queue import Queue
from threading import Thread
from kivymd.uix.dialog import MDDialog
from kivy.uix.accordion import Widget
from kivy.uix.screenmanager import Screen
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivymd.uix.dialog import(
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer
)
from kivymd.uix.button import (
    MDButton,
    MDButtonText
)
from kivy.properties import StringProperty
from kivy.app import App
from re import split

from pymongo.errors import DuplicateKeyError
from form.simplify_form import save_simplify_form

class CrearScreen(Screen):
    form_link = StringProperty()
    form_password = StringProperty()
    form_id = StringProperty()

    def on_enter(self):
        clip = Clipboard.paste()
        res = split(r"/d/([a-zA-Z0-9_-]+)", clip)
        if len(res) == 3 and res[0] == "https://docs.google.com/forms":
            self.ids.input_form_id.text = clip
            self.ids.button_enter.disabled = False

    def on_form_link(self, instance, value):
        res = split(r"/d/([a-zA-Z0-9_-]+)", value)
        if len(res) == 3 and res[0] == "https://docs.google.com/forms":
            self.form_id = res[1]
        else:
            self.form_id = ''

    def show_dialog(self):
        clave = self.form_password if self.form_password else "aleatoria"
        if self.form_id:
            MDDialog(
                MDDialogIcon(
                    icon='file-document-plus-outline'
                ),
                MDDialogHeadlineText(
                    text="¿Crear formulario?",
                ),
                MDDialogSupportingText(
                    text= f"Al confirmar, se creará un formulario con id {self.form_id} y contraseña {clave}."
                ),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Confirmar"),
                        style="text",
                        on_press = self.form  
                    )
                ),
            ).open()
        else:
            MDDialog(
                MDDialogIcon(
                    icon='file-document-alert'
                ),
                MDDialogHeadlineText(
                    text="URL incorrecta",
                ),
                MDDialogSupportingText(
                    text= "La URL no pertenece a Google Forms"
                )
            ).open()
        
    def form(self, obj):
        obj.parent.parent.parent.parent.dismiss()
        user = App.get_running_app().user
        try:
            if not user:
                raise Exception('No ha iniciado sesión')
            # save_simplify_form(self.form_id, self.form_password, user._id)
        except Exception as e:
            self.manager.current = 'login'
            MDDialog(
                MDDialogIcon(
                    icon='file-document-alert'
                ),
                MDDialogHeadlineText(
                    text="Ocurrió un error con el formulario",
                ),
                MDDialogSupportingText(
                    text= str(e)
                )
            ).open()
        else:
            self.ids.spinner.active = True
            self.ids.button_enter.disabled = True
            Thread(target=self.save, args=(self.form_id, self.form_password, user._id)).start()
        
    def save(self, *args):
        q = Queue()
        try:
            res = save_simplify_form(*args)
            q.put(res)
        except Exception as e:
            q.put(e)
        finally:
            Clock.schedule_once(lambda dt: self.save_end(q))
    def save_end(self, q:Queue,  *args):
        self.ids.spinner.active = False
        self.ids.input_form_id.text = ''
        res = q.get()
        try:
            if isinstance(res, BaseException):
                raise res
        except DuplicateKeyError as e:
            MDDialog(
                MDDialogIcon(
                    icon='file-document-alert'
                ),
                MDDialogHeadlineText(
                    text="El formulario ya ha sido registrado",
                ),
                MDDialogSupportingText(
                    text= str(e._OperationFailure__details['keyValue'])+" ya existe"
                )
            ).open()
        except Exception as e:
            MDDialog(
                MDDialogIcon(
                    icon='file-document-alert'
                ),
                MDDialogHeadlineText(
                    text="Ocurrió un error con el formulario",
                ),
                MDDialogSupportingText(
                    text= str(e)
                )
            ).open()
        else:
            if res.acknowledged:
                MDDialog(
                    MDDialogIcon(
                        icon='file-document-check'
                    ),
                    MDDialogHeadlineText(
                        text="Formulario registrado con ID: ",
                    ),
                    MDDialogSupportingText(
                        text= str(res.inserted_id)
                    )
                ).open()
            else:
                MDDialog(
                    MDDialogIcon(
                        icon='file-document-alert'
                    ),
                    MDDialogHeadlineText(
                        text="No se pudo crear el formulario",
                    ),
                ).open()
