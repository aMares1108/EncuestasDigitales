from kivy.properties import (
    StringProperty, 
    ObjectProperty,
    ListProperty
)
from kivymd.uix.card import MDCard
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.accordion import Widget
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogContentContainer,
    MDDialogButtonContainer
)
from kivymd.uix.button import (
    MDButton,
    MDButtonText
)
from kivymd.uix.textfield import MDTextField
from form.retrieve import get_forms
from json import dump

class RListItem(MDCard):
    title = StringProperty()
    formId = StringProperty()
    password = StringProperty()
    user = ObjectProperty()
    sections = ListProperty()

    def save(self):
        app = App.get_running_app()
        screen = app.root.current_screen
        screen.comp_password = MDTextField(
            text=self.password if app.user._id==self.user else None,
            disabled=app.user._id==self.user
            )
        MDDialog(
            MDDialogIcon(
                icon='file-document-plus-outline'
            ),
            MDDialogHeadlineText(
                text="¿Desea decargar el formulario "+self.title+"?",
            ),
            MDDialogSupportingText(
                text= f"Al confirmar, se descargará un formulario con id {self.formId}.\nIngrese la contraseña de descarga:"
            ),
            MDDialogContentContainer(
                screen.comp_password
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Confirmar"),
                    style="text",
                    on_press = self.download
                )
            ),
        ).open()
        
    def download(self, obj):
        obj.parent.parent.parent.parent.dismiss()
        screen = App.get_running_app().root.current_screen
        if screen.comp_password.text == self.password:
            try:
                with open('encuestas/'+self.formId+'.json','w') as f:
                    dump({
                        'formId': self.formId,
                        'sections':self.sections
                    }, f)
            except Exception as e:
                title = 'Ocurrió un error'
                supText = str(e)
            else:
                title = 'Guardado'
                supText = 'Se ha guardado el formulario correctamente'
        else:
            title='Ocurrió un error'
            supText = 'La contraseña de descarga es incorrecta'
        MDDialog(
            MDDialogHeadlineText(
                text=title
            ),
            MDDialogSupportingText(
                text=supText
            )
        ).open()
        

class DescargarScreen(Screen):
    comp_password = ObjectProperty()

    def on_enter(self):
        self.ids.rv.data = get_forms()

