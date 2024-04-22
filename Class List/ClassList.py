from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import csv
from kivy.lang import Builder

Builder.load_file("classList.kv")

class ClassListPage(BoxLayout):
    def __init__(self, class_code, **kwargs):
        super().__init__(**kwargs)
        self.class_code = class_code
        self.load_students()
  
    def load_students(self):
        try:
            with open('classes_list.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                students = [row[1] for row in reader if row[0] == self.class_code] 
                if students:
                    for student in students:
                        self.ids.students.add_widget(Label(text=student, font_size=30, bold=True))
                else:
                    self.ids.students.add_widget(Label(text="No students found for class code {}".format(self.class_code), font_size=30, bold=True))
        except FileNotFoundError:
            self.ids.students.add_widget(Label(text="File not found: classes_list.csv", font_size=30, bold=True))

class ClassListApp(App):
    def build(self):
        return ClassListPage("34723")

if __name__ == '__main__':
    ClassListApp().run()
 
