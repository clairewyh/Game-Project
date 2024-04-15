from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.button import Button
from random import randint
import requests
import json

Builder.load_file("HomepageDesign.kv")

class MainScreen(BoxLayout):
    class_data = {}
    firebase_url = "https://class-codes-10c3f-default-rtdb.firebaseio.com/.json"

    def open_popup(self):
        popup_layout = BoxLayout(orientation="vertical", padding="10dp")
        self.class_name_input = TextInput(hint_text="Enter class name", multiline=False, size_hint_y=None, height="40dp")
        # Listen for key press event in TextInput
        self.class_name_input.bind(on_text_validate=self.add_class)
        popup_layout.add_widget(self.class_name_input)
        # Set background color for the "Add Class" button
        add_class_button = Button(text="Add Class", on_press=self.add_class, background_color=(0.2, 0.6, 1, 1))
        popup_layout.add_widget(add_class_button)
        popup = Popup(title="New Class", content=popup_layout, size_hint=(None, None), size=("300dp", "200dp"))
        popup.open()
 
    def add_class(self, instance):
        class_name = self.class_name_input.text
        if class_name:
            code = self.generate_unique_code()
            class_button = ClassButton(text=f"{class_name}: {code}", bold=True)
            self.ids.classes_layout.add_widget(class_button)
            self.class_data[class_name] = code

        # Send to Firebase
        requests.patch(self.firebase_url, data = json.dumps(self.class_data))
                 
    def generate_unique_code(self):
        code = str(randint(10000, 99999))
        return code


class ClassButton(Button):
    pass

class Homepage(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    Homepage().run()
