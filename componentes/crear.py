from kivy.uix.accordion import Widget
from kivy.uix.screenmanager import Screen
from kivy.core.clipboard import Clipboard
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
from re import split

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
        try:
            save_simplify_form(self.form_id, self.form_password)
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
