import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

class Page(BoxLayout):
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

class LoginPage(App):
    kv_file = 'loginpage.kv'  # Set the kv file here

    def build(self):
        self.page = Page()
        
        # Initialize user database
        try:
            with open('user_database.json', 'r') as f:
                self.page.user_database = json.load(f)
        except FileNotFoundError:
            self.page.user_database = {}

        return self.page

if __name__ == '__main__':
    Window.clearcolor = 0, 0.5, 1, 0.8
    Window.size=(397,697)
    LoginPage().run()
