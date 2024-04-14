from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
import requests
import json

Builder.load_file("TeacherHomepageDesign.kv")

class MainScreen(BoxLayout):
    class_data = {}
    firebase_url = "https://class-codes-10c3f-default-rtdb.firebaseio.com/.json"

    def open_popup(self):
        popup_layout = BoxLayout(orientation="vertical", padding="10dp")
        self.class_code_input = TextInput(hint_text="Enter class code", multiline=False, size_hint_y=None, height="40dp")
        # Listen for key press event in TextInput
        self.class_code_input.bind(on_text_validate=self.join_class)
        popup_layout.add_widget(self.class_code_input)
        # Set background color for the "Join Class" button
        join_class_button = Button(text="Join Class", on_press=self.join_class, background_color=(0.2, 0.6, 1, 1))
        popup_layout.add_widget(join_class_button)
        popup = Popup(title="Join Class", content=popup_layout, size_hint=(None, None), size=("300dp", "200dp"))
        popup.open()

    def join_class(self, instance):
        class_code = self.class_code_input.text
        if class_code:
            class_name = self.validate_class_code(class_code)
            if class_name:
                class_button = ClassButton(text=class_name, bold=True)
                self.ids.classes_layout.add_widget(class_button)
            else:
                # Show error message if class code is not valid
                error_label = Label(text="Invalid class code. Please try again.", color=(1, 0, 0, 1))
                popup_layout = Popup(title="Error", content=error_label, size_hint=(None, None), size=("300dp", "150dp"))
                popup_layout.open()

    def validate_class_code(self, class_code):
        response = requests.get(self.firebase_url)
        print(response.text)  # Print the response for debugging
        if response.status_code == 200:
            existing_data = response.json()
            for class_name, code in existing_data.items():
                if "code" in code and code["code"] == class_code:
                    return class_name
        return None

class ClassButton(Button):
    pass

class Homepage(App):
    
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    Homepage().run()
