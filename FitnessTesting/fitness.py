from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
import json

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
        Window.clearcolor = 0.2, 0.8, 1, 1
        return HomeScreen()

if __name__ == '__main__':
    FitnessApp().run()
