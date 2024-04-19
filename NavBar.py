#Nav Bar 
#student: class join page, homepage 
#teacher: add class page, student data page
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window 
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout

Window.size = (300,500)

kv= """
#import NoTransition kivy.uix.screenmanager.NoTransition
MDFloatLayout:
    md_bg_color: 1,1,1,1 
        ScreenManager: 
            id:scr
            transition: NoTransition()
            MDScreen: 
                name: "Home"
                MDLabel: 
                    text: "Home" 
                    pos_hint: {"center_y":.5}
                    halign:"center"
            MDScreen: 
                name: "Add Class"
                MDLabel: 
                    text: "Add Class" 
                    pos_hint: {"center_y":.5}
                    halign:"center"
    NavBar:
        size_hint: .85, .1
        pos_hint: {"center_x":.5, "center_y":.1}
        elevation: 10
        md_bg_color: 1,1,1,1
        radius: [16]
        MDGridLayout:
            cols: 4
            size_hint_x: .9
            spacing: 8
            pos_hint: {"center_x": .5, "center_y":.5}
            MDIconButton:
                id: nav_icon1
                icon: "home"
                ripple_scale: 0
                user_font_size: "30dp"
                theme_text_color: "custom"
                text_color:1,0,0,1
            MDIconButton:
                id: nav_icon2
                icon: "account-multiple"
                ripple_scale: 0
                user_font_size: "30dp"
                theme_text_color: "custom"
                text_color:1,0,0,1
          
    """
class NavBar(FakeRectangularElevationBehavior, MDFloatLayout):
    pass

class DemoApp(MDApp):
    def build(self):
        return Builder.load_string(kv)
    
DemoApp().run()
