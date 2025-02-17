from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from form.retrieve import get_forms
from os import listdir
from logging import debug

class EListItem(MDCard):
    title = StringProperty()
    formId = StringProperty()

    def save():
        pass

class EncuestasScreen(Screen):
    def on_enter(self, *args):
        self.ids.rv.data = [{
            'title': 'Encuesta',
            'formId': file
        }for file in listdir('encuestas') ]
        debug(f"{self.ids.rv.height} {self.ids.rv.parent.height}")