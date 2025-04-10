from kivy.properties import (
    StringProperty, 
    ObjectProperty,
    ListProperty,
    BooleanProperty,
    AliasProperty
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
    MDButtonText,
    MDIconButton
)
from kivymd.uix.textfield import MDTextField
from kivy.core.clipboard import Clipboard
from form.retrieve import get_forms
from json import dump
from bson import ObjectId

class RListItem(MDCard):
    title = StringProperty()
    description = StringProperty()
    _id = ObjectProperty()
    def _formId_to_creationDate(self):
        # try:
        #     oid = ObjectId(self._id)
        #     return oid.generation_time.strftime('%d-%b-%Y')
        # except:
        #     return self.formId
        if self._id is not None:
            return self._id.generation_time.strftime('%d-%b-%Y')
        else:
            return 'Unkown date'
    date = AliasProperty(_formId_to_creationDate, bind=['_id'])
    password = StringProperty()
    user = ObjectProperty()
    sections = ListProperty()

    def save(self):
        app = App.get_running_app()
        screen = app.root.current_screen
        screen.comp_password=self.password if app.user._id==self.user else ''
        screen.comp_password_disabled=app.user._id==self.user
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
                MDTextField(
                    text=screen.comp_password,
                    disabled=screen.comp_password_disabled
                ),
                MDIconButton(
                    icon='content-copy',
                    on_release=lambda x:Clipboard.copy(self.password if app.user._id==self.user else None),
                    disabled=app.user._id!=self.user
                )
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
        if screen.comp_password == self.password:
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
        screen.comp_password = ''
        

class DescargarScreen(Screen):
    comp_password = StringProperty()
    comp_password_enabled = BooleanProperty()

    def on_enter(self):
        self.ids.rv.data = get_forms()

