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
            self.load_user_classes(username)  # Load classes for the user
            self.switch_to_class_homepage(username)
        else:
            self.show_popup('Error', 'Invalid username or password.')
        
    def load_user_classes(self, username):
        if not username:
            self.show_popup('Error', 'Username cannot be empty.')
            return

        classes_ref = db.reference('user_classes')
        user_classes = classes_ref.child(username).get()

        if user_classes:
            if username.startswith("t!"):
                for class_name, class_code in user_classes.items():
                    class_button = ClassButton(text=f"{class_name}: {class_code}", bold=True)
                    self.teacher_classpage.ids.classes_layout.add_widget(class_button)
            else:
                for class_code in user_classes:
                    class_button = ClassButton(text=class_code, bold=True)
                    self.student_classpage.ids.classes_layout.add_widget(class_button)


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
            App.get_running_app().switch_to_teacher_classpage(username)  # Pass username here
        else:
            App.get_running_app().switch_to_student_classpage()

class ClassPage(BoxLayout):
    pass

class TeacherClassPage(ClassPage):
    class_data = {}

    def __init__(self, username, **kwargs):
        super(TeacherClassPage, self).__init__(**kwargs)
        self.username = username  # Store the username
        self.register_event_type('on_class_selected')
        self.load_class_data()

    def load_class_data(self):
        class_data_ref = db.reference('class_data')
        self.class_data = class_data_ref.get()
        if not self.class_data:
            self.class_data = {}

        # Display classes already created by the teacher
        for class_name, code in self.class_data.items():
            class_button = ClassButton(text=f"{class_name}: {code}", bold=True)
            class_button.class_code = code
            class_button.bind(on_release=self.on_class_button_pressed)
            self.ids.classes_layout.add_widget(class_button)

    def open_popup(self):
        popup_layout = BoxLayout(orientation="vertical", padding="10dp")
        self.class_name_input = TextInput(hint_text="Enter class name", multiline=False, size_hint_y=None, height="40dp")
        self.class_name_input.bind(on_text_validate=self.add_class)
        popup_layout.add_widget(self.class_name_input)

        add_class_button = Button(text="Add Class", on_press=self.add_class, background_color=(0.2, 0.6, 1, 1))
        popup_layout.add_widget(add_class_button)

        popup = Popup(title="New Class", content=popup_layout, size_hint=(None, None), size=("300dp", "200dp"))
        popup.open()

    def add_class(self, instance):
        class_name = self.class_name_input.text
        if class_name and self.username:
            code = self.generate_unique_code()
            self.class_data[class_name] = code

            # Write to Firebase Realtime Database
            class_data_ref = db.reference('class_data')
            class_data_ref.set(self.class_data)

            # Update user classes
            user_classes_ref = db.reference('user_classes')
            user_classes_ref.child('t!' + self.username).update({class_name: code})

            # Add button for the newly added class
            class_button = ClassButton(text=f"{class_name}: {code}", bold=True)
            class_button.class_code = code
            class_button.bind(on_release=self.on_class_button_pressed)
            self.ids.classes_layout.add_widget(class_button)

            
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

                # Update user's classes in Firebase Realtime Database
                user_classes_ref = db.reference('user_classes')
                user_classes_ref.child(student_name).push(class_code)
            else:
                self.show_popup('Error', 'Invalid class code.')
        else:
            self.show_popup('Error', 'Please enter both class code and your name.')

    def add_student_to_class_list(self, class_code, student_name):
        if not class_code or not student_name:
            self.show_popup('Error', 'Class code and student name cannot be empty.')
            return

        class_list_ref = db.reference('class_list')
        class_list_ref.child(class_code).push(student_name)

    def validate_class_code(self, class_code_input):
        class_data_ref = db.reference('class_data')
        class_data = class_data_ref.get()
        if class_code_input in class_data.values():
            for class_name, class_code in class_data.items():
                if class_code == class_code_input:
                    return class_name
        return None

    def switch_to_student_homepage(self):
        self.clear_widgets()
        student_homepage = StudentHomepage()
        self.add_widget(student_homepage)
    
    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

class ClassListPage(BoxLayout):
    def __init__(self, class_code, **kwargs):
        super().__init__(**kwargs)
        self.class_code = class_code
        self.load_students()

    def load_students(self):
        if not self.class_code:
            self.ids.students.add_widget(Label(text="Invalid class code", font_size=30, bold=True))
            return

        students_ref = db.reference('class_list')
        students = students_ref.child(self.class_code).get()

        if students:
            for student_id, student_name in students.items():
                student_button = Button(text=student_name, font_size=30, bold=True, size_hint_y=None, height="50dp")
                student_button.bind(on_release=lambda instance, student_name=student_name: self.on_student_button_pressed(student_name))
                self.ids.students.add_widget(student_button)
        else:
            self.ids.students.add_widget(Label(text="No students found for class code {}".format(self.class_code), font_size=30, bold=True))

    def on_student_button_pressed(self, student_name):
        # Navigate to TeacherGoalpage and pass the student_name
        App.get_running_app().switch_to_teacher_goalpage(student_name)

class TeacherGoalpage(BoxLayout):
    def __init__(self, student_name, **kwargs):
        super().__init__(**kwargs)
        self.student_name = student_name
        self.load_goals()

    # Load goals from Firebase Realtime Database and display them
    def load_goals(self):
        goals_ref = db.reference('goal_database')
        goals_data = goals_ref.get()
        
        if not goals_data:
            goals_data = []

        # Clear existing labels if any
        self.ids.goals_box.clear_widgets()

        # Find goals for the selected student
        student_goals = None
        for student_id, student_data in goals_data.items():
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

        if goal1 == '' or goal2 == '' or goal3 == '':
            self.show_popup('Error', 'Please enter three goals.')
            return

        new_goal = {
            'Name': name,
            'Goals': {
                'Goal 1': goal1,
                'Goal 2': goal2,
                'Goal 3': goal3
            }
        }

        goals_ref = db.reference('goal_database')
        goals_ref.push(new_goal)

        self.show_popup('Success', 'Goals saved successfully.')

    
    # Popup display
    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()
    
    def switch_to_exercise_screen(self):
        App.get_running_app().switch_to_exercise_screen()

class ExerciseInput(TextInput):
    pass

class ExerciseLabel(Label):
    pass

class HomeScreen(BoxLayout):
    def switch_to_round(self, round_number):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(RoundScreen(round_number=round_number))

class RoundScreen(BoxLayout):
    def __init__(self, round_number, **kwargs):
        super(RoundScreen, self).__init__(**kwargs)
        self.round_number = round_number
        self.exercise_data = self.load_saved_data()
        self.orientation = 'vertical'
        self.spacing = '10dp'
        self.padding = '10dp'
        self.load_exercises()
        self.load_data()

    def load_exercises(self):
        self.ids.exercise_inputs.clear_widgets()

        exercises = [
            "12-minute run", "2-minute burpees", "shoulder taps", "hand release push-ups",
            "plank hold", "vertical/broad jump", "sit and reach", "20-yard dash",
            "stork test", "kneeling chest launch", "Illinois agility test", "ins and outs",
            "battle rope feed", "30s jump test"
        ]

        for exercise in exercises:
            exercise_label = ExerciseLabel(text=exercise)
            exercise_input_goal = ExerciseInput(hint_text="Goal")
            exercise_input_achieved = ExerciseInput(hint_text="Achieved")

            self.ids.exercise_inputs.add_widget(exercise_label)
            self.ids.exercise_inputs.add_widget(exercise_input_goal)
            self.ids.exercise_inputs.add_widget(exercise_input_achieved)

    def load_data(self):
        round_data = self.exercise_data.get(str(self.round_number), {})
        for widget in self.ids.exercise_inputs.children:
            if isinstance(widget, ExerciseInput):
                exercise_name = widget.parent.children[0].text
                exercise_round_data = round_data.get(exercise_name, {})
                widget.text = exercise_round_data.get("goal", "")
                widget.parent.children[2].text = exercise_round_data.get("achieved", "")

    def load_saved_data(self):
        try:
            with open("fitness_data.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_data(self):
        if str(self.round_number) not in self.exercise_data:
            self.exercise_data[str(self.round_number)] = {}

        exercise_inputs = self.ids.exercise_inputs.children
        user_name = self.ids.user_name_input.text  # Retrieve user's name from TextInput

        # Iterate through exercise inputs and update data in Firebase Realtime Database
        for i in range(0, len(exercise_inputs), 3):
            exercise_label = exercise_inputs[i + 2]
            exercise_input_goal = exercise_inputs[i + 1]
            exercise_input_achieved = exercise_inputs[i]

            exercise_name = exercise_label.text
            goal = exercise_input_goal.text
            achieved = exercise_input_achieved.text

            # Update data in Firebase Realtime Database with user's name
            round_ref = db.reference(f'fitness_data/{self.round_number}/{user_name}/{exercise_name}')
            round_ref.update({
                'goal': goal,
                'achieved': achieved
            })

        # Display success popup
        popup = Popup(title='Success',
                      content=Label(text='Your changes are saved!'),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

    def switch_to_home(self):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.switch_to_home()

class FitnessApp(App):
    def build(self):
        self.startinghomepage = StartingHomepage()
        self.loginpage = LogPage()
        self.exercise_screen = HomeScreen()

        # Initialize user database
        try:
            with open('user_database.json', 'r') as f:
                self.loginpage.user_database = json.load(f)
        except FileNotFoundError:
            self.loginpage.user_database = {}

        self.teacher_classpage = None  # Initialize as None
        self.class_list = ClassListPage(class_code="")

        return self.startinghomepage

    def switch_to_login(self):
        self.startinghomepage.clear_widgets()
        self.startinghomepage.add_widget(self.loginpage)

    def switch_to_teacher_classpage(self, username):  # Pass username here
        self.teacher_classpage = TeacherClassPage(username=username)  # Pass username to the constructor
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
    
    def switch_to_exercise_screen(self):
        self.root.clear_widgets() 
        self.root.add_widget(self.exercise_screen)
    
if __name__ == '__main__':
    Window.size=(397,697)
    Window.clearcolor = 0.2, 0.8, 1, 1
    FitnessApp().run()
