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
        self.user_data = {}

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
            "battle rope feed", "30s jump test", "70% bodyweight pull-up"
        ]
        
        for exercise in exercises:
            exercise_label = ExerciseLabel(text=exercise)
            exercise_input_goal = ExerciseInput(hint_text="Goal")
            exercise_input_achieved = ExerciseInput(hint_text="Achieved")

            self.ids.exercise_inputs.add_widget(exercise_label)
            self.ids.exercise_inputs.add_widget(exercise_input_goal)
            self.ids.exercise_inputs.add_widget(exercise_input_achieved)

    def load_data(self):
        try:
            with open("user_data.json", "r") as f:
                self.user_data = json.load(f)
        except FileNotFoundError:
            self.user_data = {}

        for widget in self.ids.exercise_inputs.children:
            if isinstance(widget, ExerciseInput):
                exercise_name = widget.parent.children[0].text
                if exercise_name in self.user_data:
                    widget.text = self.user_data[exercise_name].get("goal", "")
                    widget.parent.children[2].text = self.user_data[exercise_name].get("achieved", "")

    def save_data(self):
        data = {}
        for widget in self.ids.exercise_inputs.children:
            if isinstance(widget, ExerciseInput):
                exercise_name = widget.parent.children[0].text
                data[exercise_name] = {
                    "goal": widget.text,
                    "achieved": widget.parent.children[2].text
                }

        with open("user_data.json", "w") as f:
            json.dump(data, f, indent=4)


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
        self.root.get_screen('exercise').round_number = round_number
        self.root.current = 'exercise'


if __name__ == '__main__':
    FitnessApp().run()
