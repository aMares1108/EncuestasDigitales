from kivymd.app import MDApp as App
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import DictProperty, StringProperty

from kivy.core.window import Window
Window.size = (320,480)

from componentes.login import LoginScreen
from componentes.register import RegisterScreen
from componentes.principal import PrincipalScreen
from componentes.crear import CrearScreen
from componentes.aplicar import AplicarScreen
from componentes.descargar import DescargarScreen
from componentes.generar import GenerarScreen
from componentes.principal_reducida import PrincipalReducidaScreen
from componentes.encuestas import EncuestasScreen
from componentes.preguntas import PreguntasScreen

from os import path, mkdir

class EncuestaApp(App):
    user = DictProperty()
    user_type = StringProperty('login')

    def on_user(self, instance, value):
        if value:
            if value.type.lower() == 'investigador':
                self.user_type = 'principal'
            else:
                self.user_type = 'principal_reducida'
            self.root.current = self.user_type
        else:
            self.root.current = 'login'

    def build(self):
        for carpeta in ('respuestas', 'reportes', 'encuestas'):
            if not path.isdir(carpeta):
                mkdir(carpeta)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Black"
        self.theme_cls.accent_palette = 'Blue'
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(PreguntasScreen(name='preguntas'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(PrincipalScreen(name='principal'))
        sm.add_widget(PrincipalReducidaScreen(name='principal_reducida'))
        sm.add_widget(CrearScreen(name='crear'))
        sm.add_widget(DescargarScreen(name='descargar'))
        sm.add_widget(AplicarScreen(name='aplicar'))
        sm.add_widget(GenerarScreen(name='generar'))
        sm.add_widget(EncuestasScreen(name='encuestas'))
        
        return sm
    
    def check_complete(self):
        checked_error = any(self.root.current_screen.ids.get(input).error for input in self.root.current_screen.ids if input.startswith("input_"))
        self.root.current_screen.ids.button_enter.disabled = checked_error

    
if __name__ == '__main__':
    EncuestaApp().run()