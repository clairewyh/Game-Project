from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.lang import Builder 
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout

Builder.load_file("test.kv")

class MainScreen(Widget):
    pass  

class TestApp(App):
    def build(self):
        Window.clearcolor = (0.7,0.9,1,1)  
        return MainScreen()

if __name__ == '__main__':
    TestApp().run()
 
