import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.core.window import Window

Builder.load_file('startinghomepage.kv')
Builder.load_file('loginpage.kv')
Builder.load_file('homepagedesign.kv')

class Homepage(BoxLayout):
    pass

class UserButton(Button):
    pass

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

class FitnessApp(App):
    def build(self):
        self.homepage = Homepage()
        self.loginpage = LogPage()
        
        # Initialize user database
        try:
            with open('user_database.json', 'r') as f:
                self.loginpage.user_database = json.load(f)
        except FileNotFoundError:
            self.loginpage.user_database = {}

        return self.homepage

    def switch_to_login(self):
        self.homepage.clear_widgets()
        self.homepage.add_widget(self.loginpage)

    def switch_to_teacher_classpage(self):
        self.homepage.clear_widgets()
        self.homepage.add_widget(TeacherClassPage())

    def switch_to_student_classpage(self):
        self.homepage.clear_widgets()
        self.homepage.add_widget(StudentClassPage())

class TeacherClassPage(BoxLayout):
    pass

class StudentClassPage(BoxLayout):
    pass

if __name__ == '__main__':
    Window.size=(397,697)
    Window.clearcolor = 0.2, 0.8, 1, 1
    FitnessApp().run()
