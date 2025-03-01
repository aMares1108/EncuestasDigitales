from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from os import listdir
from json import load

class EListItem(MDCard):
    title = StringProperty()
    formId = StringProperty()
    description = StringProperty()

    def save(self):
        pass

class EncuestasScreen(Screen):
    def on_enter(self):
        data = list()
        for form in listdir('encuestas'):
            with open('encuestas/'+form,'r') as form_content:
                form_dict = load(form_content)
                data.append({
                    'formId':form_dict['formId'],
                    'title':form_dict['sections'][0]['title'],
                    'description':form_dict['sections'][0]['description'].strip()
                })
        self.ids.rv.data = data