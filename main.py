from kivymd.app import MDApp as App
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import DictProperty

from kivy.core.window import Window
Window.size = (320,480)

from componentes.login import LoginScreen
from componentes.register import RegisterScreen
from componentes.principal import PrincipalScreen
from componentes.crear import CrearScreen
from componentes.aplicar import AplicarScreen
from componentes.descargar import DescargarScreen
from componentes.generar import GenerarScreen

class EncuestaApp(App):
    user = DictProperty()

    def on_user(self, instance, value):
        self.root.current = 'principal' if value else 'login'

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Black"
        self.theme_cls.accent_palette = 'Blue'
        sm = ScreenManager()
        sm.add_widget(CrearScreen(name='crear'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(PrincipalScreen(name='principal'))
        sm.add_widget(DescargarScreen(name='descargar'))
        sm.add_widget(AplicarScreen(name='aplicar'))
        sm.add_widget(GenerarScreen(name='generar'))
        
        return sm
    
    def check_complete(self):
        checked_error = any(self.root.current_screen.ids.get(input).error for input in self.root.current_screen.ids if input.startswith("input_"))
        self.root.current_screen.ids.button_enter.disabled = checked_error
    
    
if __name__ == '__main__':
    EncuestaApp().run()