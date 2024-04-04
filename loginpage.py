from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

#test
class LoginPage(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        self.layout.add_widget(Label(text='Welcome to the Login Page', size_hint_y=0.2))
        
        self.layout.add_widget(Label(text='Username:', size_hint_y=0.1))
        self.username_input = TextInput(multiline=False, size_hint_y=0.1)
        self.layout.add_widget(self.username_input)
        
        self.layout.add_widget(Label(text='Password:', size_hint_y=0.1))
        self.password_input = TextInput(multiline=False, password=True, size_hint_y=0.1)
        self.layout.add_widget(self.password_input)
        
        self.login_button = Button(text='Login', on_press=self.login, size_hint_y=0.1)
        self.layout.add_widget(self.login_button)
        
        self.signup_button = Button(text='Sign Up', on_press=self.signup, size_hint_y=0.1)
        self.layout.add_widget(self.signup_button)
        
        # Initialize user database
        self.user_database = {}
        
        return self.layout
    
    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        if username == '' or password == '':
            self.show_popup('Error', 'Please enter both username and password.')
            return
        
        # Check login credentials
        if username in self.user_database and self.user_database[username] == password:
            self.show_popup('Success', 'Login successful!')
        else:
            self.show_popup('Error', 'Invalid username or password.')
    
    def signup(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        if username == '' or password == '':
            self.show_popup('Error', 'Please enter both username and password.')
            return
        
        # Add new user to database
        self.user_database[username] = password
        self.show_popup('Success', 'Sign up successful!')
    
    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

if __name__ == '__main__':
    LoginPage().run()