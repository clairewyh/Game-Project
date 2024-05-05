import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.button import Button

Builder.load_file('startinghomepage.kv')
Builder.load_file('loginpage.kv')

class Homepage(BoxLayout):
    pass

class UserButton(Button):
    pass

class LogPage(BoxLayout):
    def login(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        
        if username == '' or password == '':
            self.show_popup('Error', 'Please enter both username and password.')
            return
        
        # Check login credentials
        if username in self.user_database and self.user_database[username] == password:
            self.show_popup('Success', 'Login successful!')
        else:
            self.show_popup('Error', 'Invalid username or password.')
    
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

if __name__ == '__main__':
    Window.size=(397,697)
    Window.clearcolor = 0.2, 0.8, 1, 1
    FitnessApp().run()
