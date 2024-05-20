import json
from random import randint
import csv
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

Builder.load_file('main.kv')
cred = credentials.Certificate("/Users/celina/Downloads/projectmanagement-27c6b-firebase-adminsdk-z87rb-8af201d7bc.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://projectmanagement-27c6b-default-rtdb.firebaseio.com/'
})

class StartingHomepage(BoxLayout):
    pass

class UserButton(Button):
    pass

class ClassButton(Button):
    class_code = ''

class LogPage(BoxLayout):
    def __init__(self, **kwargs):
        super(LogPage, self).__init__(**kwargs)
        self.user_database = {}  # Dictionary to store user credentials

    def login(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text

        if username == '' or password == '':
            self.show_popup('Error', 'Please enter both username and password.')
            return

        # Check login credentials
        if self.check_credentials(username, password):
            self.show_popup('Success', 'Login successful!')
            self.switch_to_class_homepage(username)
        else:
            self.show_popup('Error', 'Invalid username or password.')

    def check_credentials(self, username, password):
        # Check credentials
        users_ref = db.reference('users')
        user_data = users_ref.child(username).get()

        if user_data is not None and user_data == password:
            return True
        return False

    def signup(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text

        if username == '' or password == '':
            self.show_popup('Error', 'Please enter both username and password.')
            return

        # Add new user to Firebase Realtime Database
        users_ref = db.reference('users')
        users_ref.child(username).set(password)

        self.show_popup('Success', 'Sign up successful!')

    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

    def switch_to_class_homepage(self, username):
        if username.startswith("t!"):
            App.get_running_app().switch_to_teacher_classpage()
        else:
            App.get_running_app().switch_to_student_classpage()

class ClassPage(BoxLayout):
    pass

class TeacherClassPage(ClassPage):
    class_data = {}

    def __init__(self, **kwargs):
        super(TeacherClassPage, self).__init__(**kwargs)
        self.register_event_type('on_class_selected')
        self.load_class_data()

    def load_class_data(self):
        class_data_ref = db.reference('class_data')
        self.class_data = class_data_ref.get()
        if not self.class_data:
            self.class_data = {}

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
            class_button.class_code = code  # Setting custom property
            class_button.bind(on_release=self.on_class_button_pressed)  # Call on_class_button_pressed here
            self.ids.classes_layout.add_widget(class_button)
            self.class_data[class_name] = code

            # Write to Firebase Realtime Database
            class_data_ref = db.reference('class_data')
            class_data_ref.set(self.class_data)

    def generate_unique_code(self):
        code = str(randint(10000, 99999))
        return code

    def on_class_button_pressed(self, instance):
        self.dispatch('on_class_selected', instance.class_code)

    def on_class_selected(self, class_code):
        App.get_running_app().switch_to_classlist_page(class_code)

class StudentClassPage(ClassPage):
    class_data = {}

    def go_back_to_login(self):
        App.get_running_app().switch_to_login()
    
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
                self.switch_to_student_homepage()
            else:
                # Show error message if class code is not valid
                error_label = Label(text="Invalid class code. Please try again.", color=(1, 0, 0, 1))
                popup_layout = Popup(title="Error", content=error_label, size_hint=(None, None), size=("300dp", "150dp"))
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

class ClassListPage(BoxLayout):
    def __init__(self, class_code, **kwargs):
        super().__init__(**kwargs)
        self.class_code = class_code
        self.load_students()

    def load_students(self):
        try:
            with open('class_list.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                students = [row[1] for row in reader if row[0] == self.class_code] 
                if students:
                    for student in students:
                        student_button = Button(text=student, font_size=30, bold=True, size_hint_y=None, height="50dp")
                        student_button.bind(on_release=lambda instance, student_name=student: self.on_student_button_pressed(student_name))  # Pass student_name to the method
                        self.ids.students.add_widget(student_button)
                else:
                    self.ids.students.add_widget(Label(text="No students found for class code {}".format(self.class_code), font_size=30, bold=True))
        except FileNotFoundError:
            self.ids.students.add_widget(Label(text="File not found: class_list.csv", font_size=30, bold=True))

    def on_student_button_pressed(self, student_name):
        # Navigate to TeacherGoalpage and pass the student_name
        App.get_running_app().switch_to_teacher_goalpage(student_name)

class TeacherGoalpage(BoxLayout):
    def __init__(self, student_name, **kwargs):
        super().__init__(**kwargs)
        self.student_name = student_name
        self.load_goals()

    # Load goals from JSON file and display them
    def load_goals(self):
        try:
            with open('goal_database.json', 'r') as f:
                goals_list = json.load(f)
                print("Loaded goals list:", goals_list)  # Debugging: Print the loaded goals list
        except (FileNotFoundError, json.JSONDecodeError):
            goals_list = []

        # Clear existing labels if any
        self.ids.goals_box.clear_widgets()

        # Find goals for the selected student
        student_goals = None
        for student_data in goals_list:
            name = student_data.get('Name', 'Unknown')
            if name == self.student_name:
                student_goals = student_data.get('Goals', {})
                break

        # Display the student's goals if found
        if student_goals:
            for key, value in student_goals.items():
                goal_label = Label(text=f'{self.student_name} - {key}: {value}')
                self.ids.goals_box.add_widget(goal_label)
        else:
            error_label = Label(text=f'No goals found for {self.student_name}.', color=(1, 0, 0, 1))
            self.ids.goals_box.add_widget(error_label)

class StudentHomepage(BoxLayout):
    def goal_setting(self):
        name = self.ids.name_input.text
        goal1 = self.ids.first_goal.text
        goal2 = self.ids.second_goal.text
        goal3 = self.ids.third_goal.text

        # If not all 3 goals are inputted, popup error will display
        if goal1 == '' or goal2 == '' or goal3 == '':
            self.show_popup('Error', 'Please enter three goals.')
            return

        # Stores goals in dictionary
        new_goal = {
            'Name': name,
            'Goals': {
                'Goal 1': goal1,
                'Goal 2': goal2,
                'Goal 3': goal3
            }
        }

        # Load existing goals from the file
        goal_database_path = 'goal_database.json'
        if os.path.exists(goal_database_path):
            with open(goal_database_path, 'r') as f:
                try:
                    goals_list = json.load(f)
                except json.JSONDecodeError:
                    goals_list = []
        else:
            goals_list = []

        # Append the new goal to the list
        goals_list.append(new_goal)

        # Write the updated list back to the file
        with open(goal_database_path, 'w') as f:
            json.dump(goals_list, f, indent=4)

        self.show_popup('Success', 'Goals saved successfully.')
    
    # Popup display
    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

class FitnessApp(App):
    def build(self):
        self.startinghomepage = StartingHomepage()
        self.loginpage = LogPage()
        
        # Initialize user database
        try:
            with open('user_database.json', 'r') as f:
                self.loginpage.user_database = json.load(f)
        except FileNotFoundError:
            self.loginpage.user_database = {}

        self.teacher_classpage = TeacherClassPage()
        self.class_list = ClassListPage(class_code="")

        return self.startinghomepage

    def switch_to_login(self):
        self.startinghomepage.clear_widgets()
        self.startinghomepage.add_widget(self.loginpage)

    def switch_to_teacher_classpage(self):
        self.root.clear_widgets()  # Clear all widgets
        self.root.add_widget(self.teacher_classpage)

    def switch_to_student_classpage(self):
        self.root.clear_widgets()  # Clear all widgets
        self.student_classpage = StudentClassPage()
        self.root.add_widget(self.student_classpage) 

    def switch_to_classlist_page(self, class_code):
        self.root.clear_widgets()  # Clear all widgets
        self.class_list = ClassListPage(class_code=class_code)
        self.root.add_widget(self.class_list)

    def switch_to_teacher_goalpage(self, student_name):
        self.root.clear_widgets()  # Clear all widgets
        self.teacher_goalpage = TeacherGoalpage(student_name=student_name)  # Pass student_name to the TeacherGoalpage
        self.root.add_widget(self.teacher_goalpage)

if __name__ == '__main__':
    Window.size=(397,697)
    Window.clearcolor = 0.2, 0.8, 1, 1
    FitnessApp().run()
