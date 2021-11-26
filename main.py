"""This script correponds to the main application mechanisms.
"""

import random
import functools
from collections import deque
import os
import re
from typing import List

from kivy.app import App
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.resources import resource_add_path, resource_find
from kivy.core.window import Window

from android.permissions import request_permissions, Permission


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
    return [line.split("#") for line in data.splitlines()]


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
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
    resource_add_path(os.path.join(os.getcwd(),"mp3_files/"))


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = FloatLayout()
        self.positions = (0, 0.2, 0.4, 0.6)
        self.words_meannings = find_words("words.txt")
        self.mplayer = MusicPlayerAndroid()
        Window.bind(on_keyboard=self.back_button)


    def back_button(self, window: Window, key: int, *args) -> FloatLayout:
        """When the back button of the phone is pressed, go back to the
        main menu.

        Args:
            window: current app window
            key: key pressed on the phone

        Returns:
            FloatLayout: layout of the application
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
            pronounciation: determines if there is an audio file of the 
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
                it is a translafrom kivy.logger import LoggerHistorytion
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


    def action(self, instance: Button, pronounciation:bool=False) -> FloatLayout:
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
        
        translation, question, corr_sol, wrong_sols = self.obtain_words_or_meaning()
        correct = random.choice(self.positions)
        
        filename = rename(f"{question if translation == 1 else corr_sol}.mp3")
        mp3 = resource_find(filename)
        if pronounciation:
            self.mplayer.unload()
        pronounciation = self.mplayer.load(mp3)

        if translation == 1 and pronounciation:
            self.mplayer.play()
        
        for pos in self.positions:
            button = Button(text = corr_sol 
                            if pos == correct else wrong_sols.pop(), 
                            size_hint =(1, .2), pos_hint={'x':0, 'y':pos})
            callback = (functools.partial(self.correct_button, pronounciation)
                if pos == correct else functools.partial(self.incorrect_button, 
                                                        translation, 
                                                        pronounciation))
            button.bind(on_press=callback)
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

        self.main_layout.clear_widgets()

        button = Button(text="start", size_hint =(0.3, .2),
                        pos_hint={'x':0.35, 'y':.4}, background_normal="", 
                        background_color="yellow", color = "black")
        button.bind(on_press=self.action)
        self.main_layout.add_widget(button)

        return self.main_layout



###############################################################################

if __name__ == '__main__':
    app = MainApp()
    app.run()