"""This script correponds to the main application mechanisms.
"""

import random
from collections import deque

from kivy.app import App
from kivy.clock import Clock
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
        self.positions = (0, 0.2, 0.4, 0.6)
        self.words_meannings = (("aflevere", 
                                "entregar algo/tentar expressar algo"),
                                ("arbejde", "trabalhar"),
                                ("barbere", "fazer a barba/depilar"),
                                ("begynde", "começar"))


    def incorrect_button(self, instance: Button):
        """When an incorrect solution is pressed, it changes the color of the 
        button to red.

        Args:
            instance: instance of the button that was pressed
        """

        instance.background_normal = ""
        instance.background_color = "red"


    def correct_button(self, instance: Button):
        """When the correct solution is pressed, it changes the color of the 
        button to green, waits a second and creates a new set of question, 
        correct solution and wrong solutions.

        Args:
            instance: instance of the button that was pressed
        """
        instance.background_normal = ""
        instance.background_color = "green"
        Clock.schedule_once(lambda dt: self.action(instance), 1)


    def obtain_words_or_meaning(self) -> tuple:
        """Picks whether the question will contain the word in danish and the 
        options will correspond to possible translations or the reverse, then 
        pick the corresponding question, correct solution and wrong solutions.

        Returns:
            word_or_meaning (int): 1 if the question is a danish word and 0 if 
                it is a translation
            question (str): the word for which we want the translation
            correct_sol (str): the translation of the question word
            wrong_solutions (list[str]): wrong translations of the question word
        """
        
        word_or_meaning = random.choice((0,1))

        if word_or_meaning == 0:
            correct_sol, question = random.choice(self.words_meannings)
        else:
            question, correct_sol = random.choice(self.words_meannings)
        
        wrong_solutions = deque()
        while len(wrong_solutions) < 3:
            possible_wrong_solution = random.choice(self.words_meannings)[word_or_meaning]
            if possible_wrong_solution != correct_sol:
                wrong_solutions.append(possible_wrong_solution)
        
        return (word_or_meaning, question, correct_sol, wrong_solutions)


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
        
        word_or_meaning, question, correct_sol, wrong_sols = self.obtain_words_or_meaning()
        correct = random.choice(self.positions)

        for pos in self.positions:
            button = Button(text = correct_sol if pos == correct else wrong_sols.pop(), 
                            size_hint =(1, .2), pos_hint={'x':0, 'y':pos})
            button.bind(on_press=self.correct_button 
                                if pos == correct else self.incorrect_button)
            self.main_layout.add_widget(button)
        
        question = Label(text=question, size_hint =(1, .2), 
                            pos_hint={'x':0, 'y':.8})
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
                        background_color="yellow", color = "black")
        button.bind(on_press=self.action)
        self.main_layout.add_widget(button)

        return self.main_layout



###############################################################################

if __name__ == '__main__':
    app = MainApp()
    app.run()