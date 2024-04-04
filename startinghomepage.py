from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.button import Button

Builder.load_file('startinghomepage.kv')

class Homepage(BoxLayout):
    pass

class UserButton(Button):
    pass

class FitnessApp(App):
    def build(self):
        return Homepage()

if __name__ == '__main__':
    application = FitnessApp()
    Window.size=(397,697)
    Window.clearcolor = 0.2, 0.8, 1, 1
    application.run()
