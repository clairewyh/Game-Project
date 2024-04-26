from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField
import json

# Define the screen manager
sm = ScreenManager()


class HomeScreen(Screen):
    pass


class ExerciseScreen(Screen):
    def __init__(self, **kwargs):
        super(ExerciseScreen, self).__init__(**kwargs)
        self.round_number = None
        self.exercise_data = self.load_saved_data()  # Load saved data during initialization

    def on_pre_enter(self, *args):
        if self.round_number:
            self.load_exercises()
            self.load_data()

    def load_exercises(self):
        # Remove previously added widgets
        self.ids.exercise_inputs.clear_widgets()

        exercises = [
            "12-minute run", "2-minute burpees", "shoulder taps", "hand release push-ups",
            "plank hold", "vertical jump or broad jump", "sit and reach", "20-yard dash",
            "stork test", "kneeling chest launch", "Illinois agility test", "ins and outs",
            "battle rope feed", "30s jump test", "70 percent bodyweight pull-up"
        ]

        for exercise in exercises:
            exercise_label = ExerciseLabel(text=exercise)
            exercise_input_goal = ExerciseInput(hint_text="Goal")
            exercise_input_achieved = ExerciseInput(hint_text="Achieved")

            self.ids.exercise_inputs.add_widget(exercise_label)
            self.ids.exercise_inputs.add_widget(exercise_input_goal)
            self.ids.exercise_inputs.add_widget(exercise_input_achieved)

    def load_data(self):
        # Load exercise data for the current round
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
        # Save exercise data to the exercise_data dictionary
        if str(self.round_number) not in self.exercise_data:
            self.exercise_data[str(self.round_number)] = {}

        exercise_inputs = self.ids.exercise_inputs.children
        # Iterate over widgets in pairs, each pair represents an exercise
        for i in range(0, len(exercise_inputs), 3):
            exercise_label = exercise_inputs[i + 2]
            exercise_input_goal = exercise_inputs[i + 1]
            exercise_input_achieved = exercise_inputs[i]

            exercise_name = exercise_label.text
            self.exercise_data[str(self.round_number)][exercise_name] = {
                "goal": exercise_input_goal.text,
                "achieved": exercise_input_achieved.text
            }

        # Save exercise data to the JSON file
        with open("fitness_data.json", "w") as f:
            json.dump(self.exercise_data, f, indent=4)

        # Show popup after saving data
        popup = Popup(title='Success',
                      content=Label(text='Your changes are saved!'),
                      size_hint=(None, None), size=(400, 200))
        # Show the popup
        popup.open()


class ExerciseInput(MDTextField):
    pass


class ExerciseLabel(MDTextField):
    pass


class FitnessApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        Builder.load_file('fitness.kv')
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ExerciseScreen(name='exercise'))
        return sm

    def on_round_click(self, round_number):
        exercise_screen = self.root.get_screen('exercise')
        exercise_screen.round_number = round_number
        exercise_screen.load_data()  # Load data when round is clicked
        self.root.current = 'exercise'


if __name__ == '__main__':
    FitnessApp().run()
