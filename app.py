"""This script correponds to the main application mechanisms.
"""

from kivy.utils import get_color_from_hex
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

###############################################################################
# Main class

class MainApp(App):
    """Application class. Encopasses all the mechanisms related to the app.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = FloatLayout()
    

    def action(self, instance: Button) -> FloatLayout:
        """Action associated with the pressing of the start button. This
        generates a word and 4 possible which correspond to possible
        translations.

        Args:
            instance: instance of the button the was pressed that triggered 
                    this function

        Returns:
            main_layout: updated version of the layout of the application
        """

        self.main_layout.clear_widgets()

        button = Button(text ='Nop', size_hint =(1, .2), 
                        pos_hint={'x':0, 'y':0})
        button2 = Button(text ='Nop2', size_hint =(1, .2),
                        pos_hint={'x':0, 'y':.2})
        button3 = Button(text ='Nop3', size_hint =(1, .2),
                        pos_hint={'x':0, 'y':.4})
        button4 = Button(text ='Nop4', size_hint =(1, .2),
                        pos_hint={'x':0, 'y':.6})
        question = Label(text='Word', size_hint =(1, .2), 
                            pos_hint={'x':0, 'y':.8})
        self.main_layout.add_widget(button)
        self.main_layout.add_widget(button2)
        self.main_layout.add_widget(button3)
        self.main_layout.add_widget(button4)
        self.main_layout.add_widget(question)
        return self.main_layout


    def build(self) -> FloatLayout:
        """It creates the layout of the application and presents the first 
        screen when opening the app and its first options.

        Returns:
            main_layout: layout of the application
        """

        self.main_layout = FloatLayout()

        button = Button(text='Hello world', size_hint =(.3, .2),
                        pos_hint={'x':.35, 'y':.4}, background_normal="", 
                        background_color=get_color_from_hex('#fff466'), 
                        color = "black")
        button.bind(on_press=self.action)
        self.main_layout.add_widget(button)

        return self.main_layout



###############################################################################

if __name__ == '__main__':
    app = MainApp()
    app.run()