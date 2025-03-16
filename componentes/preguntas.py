from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogIcon
from kivymd.uix.label import MDLabel
from kivy.properties import (
    NumericProperty, 
    StringProperty, 
    BooleanProperty,
    ListProperty,
    AliasProperty
)
from kivy.app import App

from json import load
from os import path

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
        self.update_input_field(0)
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
            self.update_input_field(value)

    def update_input_field(self, value):
        if self.tipo == 'textQuestion':
            self.ids.response.add_widget(self.TextQuestion())
        elif self.tipo == 'choiceQuestion':
            if self.json_data['sections'][self.section_index]['questions'][value]['choiceType'] == "RADIO":
                self.ids.response.add_widget(self.RadioQuestion(*self.json_data['sections'][self.section_index]['questions'][value]['options']))
            elif self.json_data['sections'][self.section_index]['questions'][value]['choiceType'] == "DROP_DOWN":
                self.ids.response.add_widget(self.RadioQuestion(*self.json_data['sections'][self.section_index]['questions'][value]['options']))
            elif self.json_data['sections'][self.section_index]['questions'][value]['choiceType'] == "CHECKBOX":
                self.ids.response.add_widget(self.MultiRadioQuestion(*self.json_data['sections'][self.section_index]['questions'][value]['options']))
            else:
                self.ids.response.add_widget(self.DefaultQuestion())
        else:
            self.ids.response.add_widget(self.DefaultQuestion())
    
    class TextQuestion(MDBoxLayout):
        response = StringProperty()
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.orientation = 'vertical'
            self.padding = (20,20)
            self.size_hint_y = 1
            input = MDTextField(
                MDTextFieldHintText(text='Respuesta:'),
                write_tab=False, 
                required=True
                )
            input.bind(text=self.update_response)
            self.add_widget(input)
            self.add_widget(Widget(size_hint_y=1))

        def update_response(self, instance, value):
            self.response = value

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
        response = StringProperty()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.orientation = 'vertical'
            self.selected = MDLabel(
                text="Opción seleccionada: "+self.response,
                shorten=True
                )
            self.add_widget(self.selected)
            for arg in args:
                if 'value' in arg:
                    checkbox = CheckItem(text=arg['value'], group='group')
                    checkbox.bind(active=self.update_response)
                    self.add_widget(checkbox)
                elif 'isOther' in arg:
                    if arg['isOther']:
                        checkbox = CheckOther(group='group')
                        checkbox.bind(
                            active=self.update_response,
                            focus=self.update_focus
                            )
                        self.add_widget(checkbox)
            self.add_widget(Widget(size_hint_y=1))
        
        def update_response(self, instance, value):
            if value:
                self.response = instance.text

        def on_response(self, instance, value):
            self.selected.text = "Opción seleccionada: " + value

        def update_focus(self, instance, value):
            if instance.active:
                self.response = instance.text
    
    class MultiRadioQuestion(MDBoxLayout):
        options = ListProperty()
        def _listtostr(self):
            return ",".join(map(str,[x for x in self.options if x is not None]))
        response = AliasProperty(_listtostr, bind=['options'])

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.orientation = 'vertical'
            self.selected = MDLabel(
                text="Opciones seleccionadas: "+self.response,
                shorten=True
                )
            self.add_widget(self.selected)
            for arg in args:
                if 'value' in arg:
                    checkbox = CheckItem(text=arg['value'])
                    checkbox.bind(active=self.update_response)
                    checkbox.index = len(self.options)
                    checkbox.group = str(checkbox.index)
                    self.options.append(None)
                    self.add_widget(checkbox)
                elif 'isOther' in arg:
                    if arg['isOther']:
                        checkbox = CheckOther()
                        checkbox.index = len(self.options)
                        checkbox.group = str(checkbox.index)
                        self.options.append(None)
                        checkbox.bind(
                            active=self.update_response,
                            focus=self.update_focus
                            )
                        self.add_widget(checkbox)
            self.add_widget(Widget(size_hint_y=1))
        
        def update_response(self, instance, value):
            self.options[instance.index] = instance.text if value else None

        def on_response(self, instance, value):
            self.selected.text = "Opciones seleccionadas: " + value

        def update_focus(self, instance, value):
            self.options[instance.index] = instance.text if instance.active else None

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
            with open(f'respuestas/temp.tsv','+a', encoding="utf-8") as file:
                file.write(f'\t{screen.ids.response.children[0].response}')
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
            with open(f'respuestas/temp.tsv','a', encoding="utf-8") as file:
                file.write(f'\t{screen.ids.response.children[0].response}')
            with open(f'respuestas/temp.tsv','r', encoding="utf-8") as file:
                content = file.read()
            if not path.exists(f'respuestas/{screen.form_id}.tsv'):
                with open(f'respuestas/{screen.form_id}.tsv','w', encoding="utf-8") as file:
                    file.write('Timestamp\tEstado\tApellidos\tDirección\tMunicipio\tTeléfono')
                    for section in self.json_data['sections']:
                        for question in section['questions']:
                            file.write(f'\t{question['question']}')
                    file.write('\n')
            with open(f'respuestas/{screen.form_id}.tsv','a', encoding="utf-8") as file:
                file.write(f'{content}\n')
            
            App.get_running_app().root.current = App.get_running_app().user_type
            MDDialog(
                MDDialogIcon(
                    icon='check-circle'
                ),
                MDDialogHeadlineText(
                    text='Registrado correctamente'
                )
            ).open()

class CheckItem(MDBoxLayout):
    text = StringProperty()
    group = StringProperty()
    active = BooleanProperty(False)
    index = NumericProperty(0)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.adaptive_height = True
        # input = MDCheckbox(group=self.group)
        # input.bind(active=self.update_active)
        # self.add_widget(
        #     MDAnchorLayout(input)
        #     )
        # self.add_widget(
        #     MDBoxLayout(
        #         MDLabel(text=self.text)
        #     ))
    # def update_active(self, instance, value):
    #     self.active = value

class CheckOther(CheckItem):
    focus = BooleanProperty(False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_widget(self.children[1])
        # input = MDTextField(
        #     MDTextFieldHintText(text='Otro:')
        # )
        # input.bind(
        #     text=self.update_text,
        #     focus=self.update_focus
        #     )
        # self.add_widget(input, index=1)

    # def update_text(self, instance, value):
    #     self.text = value

    # def update_focus(self, instance, value):
    #     self.focus = value
