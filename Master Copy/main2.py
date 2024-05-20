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
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.event import EventDispatcher
import os

Builder.load_file('main2.kv')

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
        if username in self.user_database and self.user_database[username] == password:
            return True
        return False
    
    def signup(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        
        if username == '' or password == '':
            self.show_popup('Error', 'Please enter both username and password.')
            return
        
        # Add new user to database
        self.user_database[username] = password
        self.show_popup('Success', 'Sign up successful!')
        
        # Save user database to file   
        with open('user_database.json', 'w') as f:
            json.dump(self.user_database, f)
    
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
        try:
            with open('class_data.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 2:  # Ensure there are exactly two values in the row
                        class_name, class_code = row
                        self.class_data[class_name] = class_code
                    else:
                        print(f"Ignoring row: {row}. Expected 2 values, found {len(row)}")
        except FileNotFoundError:
            pass  # Ignore if the file doesn't exist


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

            # Write to csv file
            with open('class_data.csv', 'a') as file:  # 'a' to append to the file
                file.write(f"{class_name},{code}\n")

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

    def switch_to_exercise_screen(self):
        App.get_running_app().switch_to_exercise_screen()



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
                        self.ids.students.add_widget(student_button)
                else:
                    self.ids.students.add_widget(Label(text="No students found for class code {}".format(self.class_code), font_size=30, bold=True))
        except FileNotFoundError:
            self.ids.students.add_widget(Label(text="File not found: class_list.csv", font_size=30, bold=True))

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
        for i in range(0, len(exercise_inputs), 3):
            exercise_label = exercise_inputs[i + 2]
            exercise_input_goal = exercise_inputs[i + 1]
            exercise_input_achieved = exercise_inputs[i]

            exercise_name = exercise_label.text
            self.exercise_data[str(self.round_number)][exercise_name] = {
                "goal": exercise_input_goal.text,
                "achieved": exercise_input_achieved.text
            }

        with open("fitness_data.json", "w") as f:
            json.dump(self.exercise_data, f, indent=4)

        popup = Popup(title='Success',
                      content=Label(text='Your changes are saved!'),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

    def switch_to_home(self):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(HomeScreen())

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

    def switch_to_exercise_screen(self):
        self.root.clear_widgets()
        self.root.add_widget(self.exercise_screen)

if __name__ == '__main__':
    Window.size=(397,697)
    Window.clearcolor = 0.2, 0.8, 1, 1
    FitnessApp().run() 
