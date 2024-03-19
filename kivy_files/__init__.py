from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.graphics import Color, Rectangle, Line

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget


from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.divider import MDDivider
from kivymd.uix.list import (
    MDListItem,
    MDListItemLeadingIcon,
    MDListItemHeadlineText,
)

import Database

class BottomNavigation(RelativeLayout):
    def __init__(self, **kwargs):
 
        super(BottomNavigation, self).__init__(**kwargs)
 
        # Arranging Canvas
        with self.canvas.before:
 
            Color(0,0,0, .5)  # set the colour 
 
            # Setting the size and position of canvas
            self.rect = Rectangle(pos_hint={'center_x':0.5, "bottom": 0},size =(self.width,108))
            
            Color(1,1,1,1)
            
            self.line = Line(points=(0.,125.,self.width,125.), width = 1)
            
            # Update the canvas as the screen size change
        self.bind(pos = self.update_rect,size = self.update_rect)
            
    def update_rect(self, instance, value):
        self.rect.size = (instance.width,108)
        self.line.points = (0,108,instance.width,108)

class StreakMeter(BoxLayout):
    current_streak = NumericProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        weekdays=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        items = []
        for i in weekdays:
            x = StreakItem(icon="circle-outline", text=i)
            self.add_widget(x)
            items.append(x)
        self.items = items
        
    def on_current_streak(self, instance, value):
        valueStr = f'{value:07.0f}'
        valueList = list(valueStr)
        for i in range(7):
            self.items[i].circle.icon = ('circle' if valueList[i] == '1' else 'circle-outline')
       
class StreakItem(RelativeLayout):
    icon = StringProperty()
    text = StringProperty()
    
    def __init__(self,**kwargs):
        self.elevation = 1
        
        super().__init__(**kwargs)
        self.circle = MDIcon(icon=self.icon, pos_hint={'center_x': 0.5,'center_y': 0.65})
        self.add_widget(self.circle)
        
        self.label = MDLabel(text=self.text, font_style="Label", role="small",
                             size_hint=(1,None), halign='center', height='10',
                             pos_hint={'center_x': 0.5,'center_y': 0.225})
        self.add_widget(self.label)
        
class LevelProgress(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.spacing = '5dp'
        self.padding_x = '5dp'
        self.add_widget(MDLabel(size_hint_x=None, 
                                text="Lvl 5", 
                                halign='left', 
                                text_size=(self.width, None), 
                                width='30dp',
                                role='small',
                                font_style='Body'))
        self.add_widget(MDLinearProgressIndicator(value=50,
                                                  size_hint_y=None))
        self.add_widget(MDLabel(size_hint_x=None, 
                                text="Lvl 6", 
                                halign='left', 
                                text_size=(self.width, None), 
                                width='30dp',
                                role='small',
                                font_style='Body'))
        
        
class UserInfoPanel(BoxLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        
        
        leftLayout = RelativeLayout(size_hint=(0.3,1))
        leftLayout.add_widget(MDIconButton(icon='account',
                                           style='filled',
                                           theme_font_size= "Custom",
                                           font_size= "30sp",
                                           radius= [self.height/2,],
                                           size_hint= (None,None),
                                           size= ('48dp','48dp'),
                                           pos_hint= {'center_x':0.5,'center_y':0.5}))
        rightLayout = RelativeLayout()
        info = BoxLayout(spacing='13dp', padding='13dp', orientation='vertical')
        self.username = MDLabel(text='-Username', halign='left',text_size=(self.width,None), role='small', font_style='Body')
        self.rank = MDLabel(text='-Rank', halign='left',text_size=(self.width,None), role='small', font_style='Body')
        self.xp = MDLabel(text='-XP: 10000', halign='left',text_size=(self.width,None), role='small', font_style='Body')
        info.add_widget(self.username)
        info.add_widget(self.rank)
        info.add_widget(self.xp)
        info.add_widget(LevelProgress())
        rightLayout.add_widget(info)
        self.add_widget(leftLayout)
        self.add_widget(rightLayout)
        
        self.UpdateInfo()
        
    def UpdateInfo(self):
        userData = Database.GetUserData()
        self.username.text = userData[1]
        self.rank.text = userData[6]
        self.xp.text = str(userData[7])
        
class BaseLabel(MDLabel):
    pass        

class BaseScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MissionScreen(BaseScreen):
    pass

language='English'
textLength='Medium'
textType='Sentence'

class HomeScreen(BaseScreen):
    languageDropdown: MDDropdownMenu = None
    typeDropdown: MDDropdownMenu = None
    languageDialog: MDDialog = None
    
    supportedLanguage = Database.GetSupportedLanguages()
    textTypes=["Sentence", "Paragraph", 'Story']
    textLengths=["Small", "Medium", "Large"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.supportedLanguage = Database.GetSupportedLanguages()
        
        languageContainer = MDDialogContentContainer(orientation='vertical')
        languageContainer.add_widget(MDDivider())
        for i in self.supportedLanguage:
            languageContainer.add_widget(MDListItem(MDListItemLeadingIcon(icon='web'), MDListItemHeadlineText(text=i[0]),on_release=lambda x, y=i[0]: self.selectLanguage(y), theme_bg_color="Custom",md_bg_color=self.theme_cls.transparentColor))
        languageContainer.add_widget(MDDivider())
    
        self.languageDialog = MDDialog(
            # -----------------------Headline text-------------------------
            MDDialogHeadlineText(
                text="Change Language",
            ),
            languageContainer,
            # ---------------------Button container------------------------
            MDDialogButtonContainer(
                Widget(),
                MDButton(MDButtonText(text="Cancel"),style="text", on_release=self.closeLanguageDialog),
                spacing="8dp",
            ),
            # -------------------------------------------------------------
        )
        
    def UpdateSessionList(self):
        lastSessionId = Database.GetLastSessionID()
        self.ids.recentSessionList.clear_widgets()
        for i in range(lastSessionId):
            self.ids.recentSessionList.add_widget(MDListItem(MDListItemLeadingIcon(icon='book'), MDListItemHeadlineText(text=f"Session {i+1}"), on_release=lambda x, y=i+1: MDApp.get_running_app().RepeatSession(y)))
            
    def openTypeDropdown(self, item):
        if not self.typeDropdown:
            menu_items = [
                {
                    "text": i,
                    "on_release": lambda x=i: self.typeMenuCallback(x),
                } for i in self.textTypes
            ]
            self.typeDropdown = MDDropdownMenu(
                caller=item, items=menu_items, position="top"
            )
            self.typeDropdown.open()
        else:
            self.typeDropdown.open()
            
    def openFilterDialog(self):
        pass

    def openLanguageDialog(self):
        self.languageDialog.open()
    
    def selectLanguage(self, text):
        global language
        language = text
        self.languageDialog.dismiss()
    
    def closeLanguageDialog(self, item):
        self.languageDialog.dismiss()
        
    def typeMenuCallback(self, text_item):
        global textType
        textType = text_item
        self.ids.typeDropText.text = text_item
        self.typeDropdown.dismiss()

class LessonCompleteScreen(BaseScreen):
    pass  

class AccountScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        data = Database.GetUserData()
        if data:
            self.add_widget(UserInfoPanel(pos_hint={'center_x': 0.5,'center_y': 0.5}))
        else:
            self.add_widget(MDButton(pos_hint={'center_x': 0.5,'center_y': 0.5}).add_widget(MDButtonText(text='Login')))

class SettingsScreen(BaseScreen):
    pass

class LoginScreen(BaseScreen):
    def Login(self):
        email = self.ids.emailField.text
        password = self.ids.passwordField.text
        
        if not Database.LoginUser(email, password):
            print('Cannot Login.')
        else:
            self.manager.current = 'HomeNavigation'
            homeScreen = self.manager.ids.navbarScreenManager.get_screen("Home")
            homeScreen.ids.userInfo.UpdateInfo()
            homeScreen.ids.userStreak.current_streak = Database.GetUserData()[8]

class SignupScreen(BaseScreen):
    def Signup(self):
        username = self.ids.usernameField.text
        email = self.ids.emailField.text
        password = self.ids.passwordField.text
        passwordRe = self.ids.reEnterPasswordField.text
        
        if password != passwordRe:
            print('Passwords do not match.')
        Database.RegisterNewUser(username, email, password)
    
class ForgotPasswordScreen(BaseScreen):
    def ForgotPassword(self):
        pass
    