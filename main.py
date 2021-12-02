"""This script correponds to the main application mechanisms.
"""

import random
import functools
from collections import deque
import os
import re
from typing import List, Callable

from kivy.app import App
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path, resource_find
from kivy.core.window import Window

from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label



###############################################################################
# additional necessary functions

def rename(word: str, reverse: bool=False) -> str:
    """Renames a word into a version without special characters and the reverse
    in case reverse is specified.

    Args:
        word: word to rename
        reverse: Rename to version without special characters if true and the 
            reverse if false. Defaults to False.

    Returns:
        str: Renamed word
    """
    if reverse:
        new_word = re.sub("0", "ø", word)
        new_word = re.sub("23", "æ", new_word)
        return re.sub("8", "å", new_word)
    else:
        new_word = re.sub("ø", "0", word)
        new_word = re.sub("æ", "23", new_word)
        return re.sub("å", "8", new_word)


def find_words(filename: str) -> List:
    """Opens the file that has the words and respective translations and stores
    the values in a list of tuples. THIS IS TEMPORARY.

    Args:
        filename: name of the file that has the words and their respective
            translations

    Returns:
        list of the words and their respective translations
    
    Requires:
        filename must correspond to a valid file
        different words in file [filename] must be in separate lines
        words must be separated from their meaning by a # character
    """

    with open(filename, 'r', encoding='utf8') as datafile:
        data = datafile.read()
    
    vocab_groups = {}
    for line in data.splitlines():
        *value, key = line.split("#")
        if key in vocab_groups:
            vocab_groups[key].add(tuple(value))
        else:
            vocab_groups[key] = {tuple(value)}

    return vocab_groups


###############################################################################
# This next section includes a class that was not written by me
# This code was written by user Patrick from StackerOverFlow
# https://stackoverflow.com/users/6468862/patrick
# The code is copied from this link:
# https://stackoverflow.com/questions/45061116/playing-mp3-on-android

class MusicPlayerAndroid(object):

    def __init__(self):
        from jnius import autoclass
        MediaPlayer = autoclass('android.media.MediaPlayer')
        self.mplayer = MediaPlayer()

        self.secs = 0
        self.actualsong = ''
        self.length = 0
        self.isplaying = False


    def __del__(self):
        self.stop()
        self.mplayer.release()
        Logger.info('mplayer: deleted')


    def load(self, filename):
        try:
            self.actualsong = filename
            self.secs = 0
            self.mplayer.setDataSource(filename)        
            self.mplayer.prepare()
            self.length = self.mplayer.getDuration() / 1000
            Logger.info('mplayer load: %s' %filename)
            Logger.info ('type: %s' %type(filename) )
            return True
        except:
            Logger.info('error in title: %s' % filename) 
            return False


    def unload(self):
            self.mplayer.reset()


    def play(self):
        self.mplayer.start()
        self.isplaying = True
        Logger.info('mplayer: play')


    def stop(self):
        self.mplayer.stop()
        self.secs=0
        self.isplaying = False
        Logger.info('mplayer: stop')


    def seek(self,timepos_secs):
        self.mplayer.seekTo(timepos_secs * 1000)
        Logger.info ('mplayer: seek %s' %int(timepos_secs))



###############################################################################
# Main class

class MainApp(App):
    """Application class. Encopasses all the mechanisms related to the app.
    """
    resource_add_path(os.path.join(os.getcwd(), "mp3_files/"))


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = GridLayout(cols=1, row_default_height=0.2, 
                                        size_hint_y=None)
        self.screen = ScrollView(size_hint=(1, None), effect_cls="ScrollEffect",
                                    size=(Window.width, Window.height))
        self.screen.add_widget(self.main_layout)
        self.vocab_groups = find_words('words.txt')
        self.words_meannings = []
        self.mplayer = MusicPlayerAndroid()
        Window.bind(on_keyboard=self.back_button)


    def reset_layout(self):
        """Resets self.main_layout to the settings, most layouts and screens
        will require as a starting poit.
        """

        self.main_layout.clear_widgets()
        self.main_layout.height = Window.height
        self.main_layout.row_default_height=0.2


    def create_widget(self, label: bool, text: str, function: Callable=None, 
                        color: str=None):
        """Generates a label or a button with the information specified and adds
        it to the self.main_layout.

        Args:
            label: a flag indicating if the widget being created is a button or
                a label. If true, it creates a label. Otherwise, it creates a
                button.
            text: the text to include in the button.
            function (optional): The function that activates when the button
                created gets pressed. Defaults to None.
            color (optional): color of the button to be created. Defaults to 
                None. If it has None value, than the button will be created with
                default color (gray).
        
        Requires:
            if the widget being created corresponds to a button, then it is 
                required that a function is provided.
        """

        max_height = Window.height

        if label:
            label = Label(text=text, size_hint_y=None, height=.2*max_height)
            self.main_layout.add_widget(label)
        
        else:
            if color:
                button = Button(text=text, size_hint_y=None, 
                                height=.2*max_height, background_normal="", 
                                background_color=color)
            else:
                button = Button(text=text, size_hint_y=None, 
                                height=.2*max_height)
            button.bind(on_press=function)
            self.main_layout.add_widget(button)


    def back_button(self, window: Window, key: int, *args) -> ScrollView:
        """When the back button of the phone is pressed, go back to the
        main menu.

        Args:
            window: current app window
            key: key pressed on the phone

        Returns:
            layout of the application
        """
        
        if key == 27:
            self.mplayer.unload()
            return self.build()


    def incorrect_button(self, translation: int, pronounciation: bool, 
                            instance: Button):
        """When an incorrect solution is pressed, it changes the color of the 
        button to red. If the question word is in danish, then it pronounces
        the word.

        Args:
            translation: 1 if the question is a danish word and 0 if 
                it is a translation
            pronounciation: determi
            nes if there is an audio file of the 
                pronounciation of the word 
            instance: instance of the button that was pressed
        """

        instance.background_normal = ""
        instance.background_color = "red"
        if translation == 1 and pronounciation:
            self.mplayer.play()


    def correct_button(self, pronounciation: bool, instance: Button):
        """When the correct solution is pressed, it changes the color of the 
        button to green, pronounces the question word, waits a second and 
        creates a new set of question, correct solution and wrong solutions.

        Args:
            pronounciation: determines if there is an audio file of the 
                pronounciation of the word
            instance: instance of the button that was pressed
        """

        instance.background_normal = ""
        instance.background_color = "green"
        if pronounciation:
            self.mplayer.play()
        Clock.schedule_once(lambda dt: self.action(instance, pronounciation), 1)


    def obtain_words_or_meaning(self) -> tuple:
        """Picks whether the question will contain the word in danish and the 
        options will correspond to possible translations or the reverse, then 
        pick the corresponding question, correct solution and wrong solutions.

        Returns:
            word_or_meaning (int): 1 if the question is a danish word and 0 if 
                it is a translation
            question (str): the word for which we want the translation
            correct_sol (str): the correct translation of the question word
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


    def action(self, instance: Button, pronounciation:bool=False) -> ScrollView:
        """Generates instances of the multiple choice game. This consists in
        generating a question word which the user has to translate. If the word
        appears in danish, then the user has to choose one of 4 possible english
        translations. If the question word appears in english, then the user has
        to choose one of 4 danish translations. It is only possible to go to
        another instance of the game, if the user has clicked on the correct
        answer.
            Additionally, if the question word is in danish, the first time it
        appears, the sound of its pronounciation will be played when the 
        instance of the game is generated, when an incorrect choice is made and
        when a correct choice is made. If the question word is in english, 
        however, then the sound of the pronounciation of the word in danish is
        only played when the correct option is clicked.

        Args:
            instance: instance of the button the was pressed that triggered 
                    this function

        Returns:
            main_layout: updated version of the layout of the application
        """

        self.reset_layout()
        
        translation, question, corr_sol, wrong_sols = self.obtain_words_or_meaning()
        
        filename = rename(f"{question if translation == 1 else corr_sol}.mp3")
        mp3 = resource_find(filename)
        
        if pronounciation:
            self.mplayer.unload()
        pronounciation = self.mplayer.load(mp3)

        if translation == 1 and pronounciation:
            self.mplayer.play()

        self.create_widget(True, question)
        
        options = [corr_sol, *wrong_sols]
        random.shuffle(options)
        for sol in options:
            if sol == corr_sol:
                callback = functools.partial(self.correct_button, 
                                                pronounciation)
            else:
                callback = functools.partial(self.incorrect_button, translation, 
                                                pronounciation)
            self.create_widget(False, sol, callback)
        
        return self.screen


    def vocab_done(self, instance: Button) -> ScrollView:
        """Proceeds to the multiple choice game with the vocabulary sets chosen,
        if vocabulary sets have been chosen. Otherwise, it will return to the
        options layout.

        Args:
            instance: instance of the button the was pressed that triggered this
                function

        Returns:
            ScrollView: 
        """

        if len(self.words_meannings) > 0:
            vocab_to_use = set()
            for vocab in self.words_meannings:
                vocab_to_use |= set(self.vocab_groups[vocab])
            self.words_meannings = list(vocab_to_use)
            return self.action(instance)
        
        return self.vocab_options(instance)
    
    
    def vocab_choice(self, instance: Button):
        """Adds the vocabulary set chosen to the vocabulary set that is going
        to be used in the multiple choice game.

        Args:
            instance: instance of the button the was pressed that triggered this
                function
        """

        self.words_meannings.append(instance.text)
        instance.background_normal = ""
        instance.background_color = get_color_from_hex("#99ccff")


    def vocab_options(self, instance: Button) -> ScrollView:
        """Generates the screen that allows the user to choose one or more
        vocabulary sets to use in the multiple choice game.

        Args:
            instance: instance of the button the was pressed that triggered this
                function.

        Returns:
            self.screen: screen of the application.
        """

        options = self.vocab_groups.keys()
        self.words_meannings = []
        self.reset_layout()

        if len(options) > 3:
            self.main_layout.height += Window.height*(len(options)-2)*0.2

        self.create_widget(True, "Choose one or more vocabulary sets:")
        for option in options:
            self.create_widget(False, option, self.vocab_choice)

        # button to submit choice of vocabulary
        self.create_widget(False, "Done", self.vocab_done, 
                            get_color_from_hex("#0b6ac1"))
        
        # button to create a new vocabulary set
        self.create_widget(False, "Create a new vocabulary set", 
                            self.vocab_done, get_color_from_hex("#9e83e5"))
        return self.screen


    def build(self) -> ScrollView:
        """It creates the layout of the application and presents the first 
        screen when opening the app and its first options.

        Returns:
            self.screen: screen of the application
        """

        self.reset_layout()
        inside_layout = FloatLayout()
        self.main_layout.add_widget(inside_layout)

        button = Button(text="start", size_hint_y=None, color="black", 
                        background_normal="", background_color="yellow", 
                        size_hint=(0.3, 0.2), pos_hint={'x':.35, 'y':.4})
        button.bind(on_press=self.vocab_options)
        inside_layout.add_widget(button)
        return self.screen



###############################################################################

if __name__ == '__main__':
    app = MainApp()
    app.run()