from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
import json


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

class StudentPage(App):
    kv_file = 'studenthomepage.kv'

    def build(self):
        return StudentHomepage()

# Running the application
if __name__ == '__main__':
    Window.clearcolor = (0.2, 0.8, 1, 1)
    Window.size=(397,697)
    StudentPage().run()
