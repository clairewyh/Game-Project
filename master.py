import json
import csv
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.core.window import Window
from random import randint


class Homepage(BoxLayout):
    pass

class LoginPage(BoxLayout):
    def login(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        
        if username == '' or password == '':
            self.show_popup('Error', 'Please enter both username and password.')
            return
        
        if "T!" in password:
            self.switch_to_teacher_class()
        else:
            self.switch_to_student_class()
    
    def switch_to_teacher_class(self):
        self.clear_widgets()
        teacher_class_page = TeacherClass()
        self.add_widget(teacher_class_page)
        
    def switch_to_student_class(self):
        self.clear_widgets()
        student_class_page = StudentClass()
        self.add_widget(student_class_page)
        
    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

class TeacherClass(BoxLayout):
    class_data = {}  

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
            class_button.bind(on_release=self.show_class_list)
            self.ids.classes_layout.add_widget(class_button)
            self.class_data[class_name] = code
        
        #write to csv file
        with open('class_data.csv', 'a') as file:  # 'a' to append to the file
            file.write(f"{class_name},{code}\n")
   
    def generate_unique_code(self):
        code = str(randint(10000, 99999))
        return code
    
    def show_class_list(self, instance):
        class_name, class_code = instance.text.split(": ")
        class_list_page = ClassList(class_name=class_name, class_code=class_code)
        self.clear_widgets()
        self.add_widget(class_list_page)

class ClassList(BoxLayout):
    def __init__(self, class_name, class_code, **kwargs):
        super(ClassList, self).__init__(**kwargs)
        self.class_name = class_name
        self.class_code = class_code
        self.load_students()

    def load_students(self):
        try:
            with open('class_list.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == self.class_code:
                        student_label = Label(text=row[1], font_size='20sp')
                        self.ids.students_layout.add_widget(student_label)
        except FileNotFoundError:
            pass

    def back_to_teacher_class(self):
        teacher_class_page = TeacherClass()
        self.clear_widgets()
        self.add_widget(teacher_class_page)

class StudentClass(BoxLayout):
    class_data = {}
    
    def open_popup(self):
        popup_layout = BoxLayout(orientation="vertical", padding="10dp")
        self.class_code_input = TextInput(hint_text="Enter class code", multiline=False, size_hint_y=None, height="40dp")
        self.student_name_input = TextInput(hint_text="Enter your name", multiline=False, size_hint_y=None, height="40dp")
        
        # Listen for key press event in TextInput
        self.class_code_input.bind(on_text_validate=self.join_class)
        popup_layout.add_widget(self.class_code_input)
        popup_layout.add_widget(self.student_name_input)
        # Set background color for the "Join Class" button
        join_class_button = Button(text="Join Class", on_press=self.join_class, background_color=(0.2, 0.6, 1, 1))
        popup_layout.add_widget(join_class_button)
        popup = Popup(title="Join Class", content=popup_layout, size_hint=(None, None), size=("300dp", "200dp"))
        popup.open()

    def join_class(self, instance):
        class_code = self.class_code_input.text
        student_name = self.student_name_input.text
        if class_code and student_name:
            class_name = self.validate_class_code(class_code)
            if class_name:
                class_button = ClassButton(text=f"{class_name}: {class_code}", bold=True)
                self.ids.classes_layout.add_widget(class_button)
                self.add_student_to_class_list(class_code, student_name)
                self.switch_to_student_homepage()  # Changed this line
            else:
                # Show error message if class code is not valid
                error_label = Label(text="Invalid class code. Please try again.", color=(1, 0, 0, 1))
                popup_layout = Popup(title="Error", content=error_label, size_hint=(None, None),
                                     size=("300dp", "150dp"))
                popup_layout.open()
        else:
            # Show error message if class code or student name is empty
            error_label = Label(text="Please enter class code and your name.", color=(1, 0, 0, 1))
            popup_layout = Popup(title="Error", content=error_label, size_hint=(None, None), size=("300dp", "150dp"))
            popup_layout.open()

    def add_student_to_class_list(self, class_code, student_name):
        with open('class_list.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([class_code, student_name])

    def fetch_class_data(self):
        # Clear existing class data
        self.class_data.clear()
        # Read class data from CSV file
        with open('class_data.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                class_name, class_code = row
                self.class_data[class_name] = class_code

    def validate_class_code(self, class_code_input):
        self.fetch_class_data()
        if class_code_input in self.class_data.values():
            for class_name, class_code in self.class_data.items():
                if class_code == class_code_input:
                    return class_name

    def switch_to_student_homepage(self):  # Added this method
        self.clear_widgets()
        student_homepage = StudentHomepage()
        self.add_widget(student_homepage) 

class ClassButton(Button):
    pass

class StudentHomepage(BoxLayout):
# Prompts the user to set 3 goals for themselves
    def goal_setting(self):
        goal1 = self.ids.first_goal.text
        goal2 = self.ids.second_goal.text
        goal3 = self.ids.third_goal.text
        
        # If not all 3 goals are inputted, popup error will display
        if goal1 == '' or goal2 == '' or goal3 == '':
            self.show_popup('Error', 'Please enter three goals.')
            return

        # Stores goals in database once 3 goals are inputted
        goals = {
            'Goal 1: ': goal1,
            'Goal 2: ': goal2,
            'Goal 3: ': goal3 
        }

        with open('goal_database.json', 'w') as f:
            json.dump(goals, f)
        
        self.show_popup('Success', 'Goals saved successfully.')
    
    # Popup display
    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()
    
class MasterApp(App):
    def build(self):
        return Homepage()

    def on_teacher_pressed(self):
        self.root.clear_widgets()
        login_page = LoginPage()
        try:
            with open('user_database.json', 'r') as f:
                login_page.user_database = json.load(f)
        except FileNotFoundError:
            login_page.user_database = {}
        self.root.add_widget(login_page)

    def on_student_pressed(self):
        self.root.clear_widgets()
        login_page = LoginPage()
        try:
            with open('user_database.json', 'r') as f:
                login_page.user_database = json.load(f)
        except FileNotFoundError:
            login_page.user_database = {}
        self.root.add_widget(login_page) 

if __name__ == '__main__':
    Window.clearcolor = 0.2, 0.8, 1, 1
    Window.size=(397,697)
    MasterApp().run()
