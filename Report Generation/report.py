import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder

Builder.load_file("report.kv")

class ReportGeneration(BoxLayout):
    # Class for generating improvement percent report
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = self.load_data()
        self.calculate_improvement() 

    def load_data(self):
     # Loading data from JSON file
        with open("fitness_data.json") as f:
            return json.load(f)

    def calculate_improvement(self):
    # Calculate improvement % for each exercise.
        for exercise in self.data["1"].keys():
            if exercise:
                total_improvement = 0
                for i in range(1, 5):
                    initial_value = int(self.data[str(i)][exercise]["achieved"])
                    final_value = int(self.data[str(i+1)][exercise]["achieved"])
                    improvement_percent = ((final_value - initial_value) / initial_value) * 100
                    total_improvement += improvement_percent
                average_improvement = total_improvement / 4
                # Adding exercise name and improvement % to the layout
                self.ids.table.add_widget(Label(text=exercise))
                self.ids.table.add_widget(Label(text=f"{round(average_improvement, 2)}%"))

class ReportGenerationApp(App):
    def build(self):
        return ReportGeneration()

if __name__ == "__main__":
    ReportGenerationApp().run()  # Running the application
