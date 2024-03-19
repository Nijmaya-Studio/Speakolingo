from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import LabelBase

from kivymd.app import MDApp

import kivy_files

import SpeechToText as st
import Database
import random

listener = st.ListenToUser()

class PracticeScreen(kivy_files.BaseScreen):
    exercises=[]
    currentExercise=0
    textToSpeak = StringProperty()
    previewText = StringProperty()
    language = StringProperty("English")
    
    def on_pre_enter(self):
        self.language = kivy_files.language
        global listener
        listener.Initialize(self.exercises[self.currentExercise])
        
        self.textToSpeak = listener.GetText()[0]
        
    def NextExercise(self):
        self.currentExercise += 1
        if self.currentExercise >= len(self.exercises):
            self.manager.current = 'LessonComplete'
            return
        
        global listener
        listener.Initialize(self.exercises[self.currentExercise])
        
        self.textToSpeak = listener.GetText()[0]
    
    def ToggleListening(self):
        global listener
        toggleButton = self.ids.toggle_speech
        
        if toggleButton.icon == "microphone":
            listener.StartListening()
            Clock.schedule_interval(self.ListenCallback, 0.1)
            toggleButton.icon = "microphone-off"
            
        elif toggleButton.icon == "microphone-off":
            listener.StopListening(False)
            toggleButton.icon = "microphone"
            
    def StopListening(self):
        global listener
        listener.StopListening(False)
        
    def SkipWord(self):
        global listener
        listener.SkipWord()
    
    def ListenCallback(self, dt):
        listTC = listener.GetText()
        self.textToSpeak = listTC[0]
        self.previewText = listTC[3]
        self.ids.textToSpeakScrollView.scroll_y = listTC[2]
        if listTC[1]:
            self.ToggleListening()
            self.NextExercise()
            return False      

kvString = ""

with open('./kivy_files/main_layout.kv', encoding='utf-8') as f:
    kvString = f.read()
    
LabelBase.register(name="Japenese", fn_regular="./resources/Fonts/Noto_Sans_JP/static/NotoSansJP-SemiBold.ttf")
LabelBase.register(name="English", fn_regular="./resources/Fonts/KodeMono-VariableFont_wght.ttf")

Window.size = (405, 720)
class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(kvString)

    def on_start(self):
        super().on_start()
        homeScreen = self.root.ids.navbarScreenManager.get_screen("Home")
        homeScreen.UpdateSessionList()

    def switch_theme_style(self):
        self.theme_cls.theme_style = ("Dark" if self.theme_cls.theme_style == "Light" else "Light")
    
    def on_stop(self):
        global listener
        listener.StopListening(False)
        return super().on_stop()
    
    def ChangeToHomeScreen(self):
        self.root.current = "HomeNavigation"
        homeScreen = self.root.ids.navbarScreenManager.get_screen("Home")
        homeScreen.ids.userInfo.UpdateInfo()
        homeScreen.UpdateSessionList()
        homeScreen.ids.userStreak.current_streak = Database.GetUserData()[8]
        
    def StartNewSession(self):
        practiceScreen = self.root.get_screen("Practice")
        practiceScreen.exercises = Database.GetNewSession(kivy_files.textType, kivy_files.language, random.randint(10,12))
        self.root.current = "Practice"
        
    def RepeatSession(self, sessionID):
        practiceScreen = self.root.get_screen("Practice")
        sessionInfo = Database.GetSessionFromID(sessionID)
        practiceScreen.exercises = sessionInfo[0]
        kivy_files.language = sessionInfo[1]
        self.root.current = "Practice"
        
    def ChangeToLoginScreen(self):
        self.root.current = "Login"
        
if __name__ == "__main__":
    MainApp().run()