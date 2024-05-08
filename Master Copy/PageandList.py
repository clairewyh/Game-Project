from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.lang import Builder 
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from random import randint
import csv
  
Builder.load_file("PageandList.kv")

class MainScreen(Screen):
    class_data = {}  

    def open_popup(self):
        popup_layout = BoxLayout(orientation="vertical", padding="10dp")
        self.class_name_input = TextInput(hint_text="Enter class name", multiline=False, size_hint_y=None, height="40dp")
        # Listen for key press event in TextInput
        self.class_name_input.bind(on_text_validate=self.add_class)
        popup_layout.add_widget(self.class_name_input)

        
        add_class_button = Button(text="Add Class", on_press=self.add_class, background_color=(0.2, 0.6, 1, 1))
        popup_layout.add_widget(add_class_button)
        popup = Popup(title="New Class", content=popup_layout, size_hint=(None, None), size=("300dp", "200dp"))
        popup.open()
 
    def add_class(self, instance):
        
        class_name = self.class_name_input.text
        if class_name:
            code = self.generate_unique_code()
            class_button = ClassButton(text=f"{class_name}: {code}", bold=True)
            class_button.class_code = code  # Setting custom property
            class_button.bind(on_release=self.switch_to_class_list)
            self.ids.classes_layout.add_widget(class_button)
            self.class_data[code] = class_name
        
        # Write to csv file
        with open('class_data.csv', 'a') as file:  # 'a' to append to the file
            file.write(f"{code},{class_name}\n")

    def generate_unique_code(self):
        code = str(randint(10000, 99999))
        return code

    def switch_to_class_list(self, instance):
        app = App.get_running_app()
        class_code = instance.class_code
        app.root.current = 'class_list'
        app.root.get_screen('class_list').update_class_list(class_code)

class ClassButton(Button):
    class_code = ''  # Custom property

class ClassListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.class_code = None

    def update_class_list(self, class_code):
        self.class_code = class_code
        self.ids.students_layout.clear_widgets()
        self.load_students()

    def load_students(self):        
        with open('class_list.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            students = [row[1] for row in reader if row[0] == self.class_code] 
            if students:
                for student in students:
                    self.ids.students_layout.add_widget(Label(text=student, font_size=30, bold=True))

class HomepageApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ClassListScreen(name='class_list'))
        return sm

if __name__ == '__main__': 
    HomepageApp().run()
