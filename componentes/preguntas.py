from kivy.uix.accordion import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogIcon
from kivymd.uix.label import MDLabel
from kivy.properties import NumericProperty, StringProperty
from kivy.app import App

from json import load

class PreguntasScreen(Screen):
    index = NumericProperty(-1)
    section_index = NumericProperty(-1)
    section_max = NumericProperty(0)
    section_offset = NumericProperty(0)
    total = NumericProperty(0)
    form_id = StringProperty()
    title = StringProperty("Encuesta")
    section = StringProperty("Sección 1")
    tipo = StringProperty()
    pregunta = StringProperty("Pregunta 1")

    def on_pre_enter(self, *args):
        if not self.form_id:
            return
        with open(f'encuestas/{self.form_id}.json','r') as file:
            self.json_data = load(file)
        self.total = sum([len(section['questions']) for section in self.json_data['sections']])
        self.button = self.MDButtonNext()
        self.index = 0
        self.pregunta = self.json_data['sections'][0]['questions'][0].get('question','') or ''
        self.tipo = self.json_data['sections'][0]['questions'][0]['type']
        if self.tipo == 'textQuestion':
            self.ids.response.clear_widgets()
            self.ids.response.add_widget(self.TextQuestion())
        self.ids.buttons.clear_widgets()
        self.ids.buttons.add_widget(self.button)

    def on_leave(self, *args):
        self.index = -1
        self.section_index = -1
        self.section_max = 0
        self.section_offset = 0

    def on_index(self, instance, value):
        if not hasattr(self, 'json_data'):
            self.index = 0
            return
        if value+self.section_offset+1==self.total:
            self.ids.buttons.clear_widgets()
            self.button = self.MDButtonFinish()
            self.ids.buttons.add_widget(self.button)
        if value==self.section_max:
            self.section_offset += self.section_max
            self.section_index += 1
            self.section_max = len(self.json_data['sections'][self.section_index]['questions'])
            self.section = self.json_data['sections'][self.section_index]['title']
            self.index = 0
        else:
            self.tipo = self.json_data['sections'][self.section_index]['questions'][value]['type']
            self.pregunta = self.json_data['sections'][self.section_index]['questions'][value].get('question','') or ''
            self.ids.response.clear_widgets()
            if self.tipo == 'textQuestion':
                self.ids.response.add_widget(self.TextQuestion())
            else:
                self.ids.response.add_widget(self.DefaultQuestion())


    def next_question(self):
        self.ids.response.add_widget(self.TextQuestion())
    
    class TextQuestion(MDBoxLayout):
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.orientation = 'vertical'
            self.padding = (20,20)
            self.size_hint_y = 1
            self.input = MDTextField(
                write_tab=False, 
                required=True
                )
            self.input.add_widget(MDTextFieldHintText(text='Respuesta:'))
            self.add_widget(self.input)
            self.add_widget(Widget(size_hint_y=1))

    class DefaultQuestion(TextQuestion):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.add_widget(MDLabel(
                text = 'ADVERTENCIA: No se pudo reconocer el tipo de pregunta. Inserte la respuesta manualmente',
                theme_text_color = 'Custom',
                text_color = (1,0,0,1),
                bold = True,
                halign = 'center'
            ), index=1)
    
    class RadioQuestion(MDBoxLayout):
        pass

    class MDButtonNext(MDButton):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.size_hint_x = None
            self.add_widget(
                MDButtonIcon(icon='arrow-right-circle')
                )
            self.add_widget(
                MDButtonText(text='Siguiente')
                )
        
        def on_release(self):
            screen = App.get_running_app().root.current_screen
            with open(f'respuestas/temp.tsv','+a') as file:
                file.write(f'\t{screen.ids.response.children[0].input.text}')
            screen.index += 1

    class MDButtonFinish(MDButtonNext):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.clear_widgets()
            self.add_widget(
                MDButtonIcon(icon='check-circle')
                )
            self.add_widget(
                MDButtonText(text='Finalizar')
                )
        
        def on_release(self):
            screen = App.get_running_app().root.current_screen
            with open(f'respuestas/temp.tsv','+a') as file:
                file.write(f'\t{screen.ids.response.children[0].input.text}')
            App.get_running_app().root.current = App.get_running_app().user_type
            MDDialog(
                MDDialogIcon(
                    icon='check-circle'
                ),
                MDDialogHeadlineText(
                    text='Registrado correctamente'
                )
            ).open()