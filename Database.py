from pymysql import connect
from tabulate import tabulate

class db_manager:
    
    def __init__(self,paswd = '') -> None:
        self.paswd = paswd
        
        if self.is_available():
            pass
        
        elif self.is_available() == False:
            self.build()

    def is_available(self) -> bool :
        with connect(user = 'root', passwd = self.paswd) as conn:
            cur = conn.cursor()
            cur.execute("show databases;")
            if ('speakolingo',) in cur.fetchall():
                
                return True
            else:
                return False
    
    def build(self) -> None:
        with connect(user = 'root', passwd = self.paswd) as conn:
            conn.autocommit(1)
            
            cur = conn.cursor()
            
            cur.execute("create database speakolingo;")
            cur.execute("use speakolingo;")
            
            cur.execute("""CREATE TABLE users (
                        userid VARCHAR(25) PRIMARY KEY ,
                        username varchar(15) NOT NULL, 
                        password varchar(20) NOT NULL,
                        userimg varchar(100),
                        email varchar(40) NOT NULL,
                        level INT DEFAULT 0,
                        user_rank VARCHAR(25) DEFAULT 'BEGINNER',
                        xp INT DEFAULT 0,
                        currStreak VARCHAR(10000) DEFAULT '0000000'
                                );""")
            
            cur.execute("""CREATE TABLE supported_languages (
                        name VARCHAR(20),
                        language_id char(5) PRIMARY KEY);""")
            
            cur.execute("""CREATE TABLE language_data (
                        language_id char(5),
                        entry TEXT,
                        entry_type ENUM('sentence','paragraph','story'),
                        fluency_level varchar(20),
                        FOREIGN KEY (language_id) REFERENCES supported_languages(language_id));""")
            
            cur.execute("""CREATE TABLE recent_sessions (
                        language_id char(5),
                        session_id int NOT NULL,
                        entry TEXT,
                        FOREIGN KEY (language_id) REFERENCES supported_languages(language_id)));""")
            
            print('done building')
        
    def desc(self,table_name:str) -> None:
        with connect(user = 'root', passwd = self.paswd, database="speakolingo") as conn:  
            cur = conn.cursor()
            cur.execute(f"desc {table_name};")
            
            print(tabulate(cur.fetchall(),tablefmt='fancy_grid'))
                
    def insert_values(self,table_name,*args) -> None :
        with connect(user = 'root', passwd = self.paswd, database="speakolingo") as conn:
            conn.autocommit(1)
            cur = conn.cursor()
            print(f"insert into {table_name} values {args};")
            cur.execute(f"insert into {table_name} values {args};")      
                 
    def get_values(self,table_name, **kwargs) -> tuple :
        conditions:dict = kwargs
        s = ''
        multiple_constraint = 1 if (len(kwargs) > 1) else 0
        
        if conditions != None:
            for k,v in conditions.items():
                if v != None:
                    if type(v) == str:
                        s += f"{k} = '{v}'" + " and " * multiple_constraint
                    else:
                        s += f"{k} = {v}" + " and " * multiple_constraint
        
        if multiple_constraint:
            s = s[:-5]
        
        try:
            with connect(user = 'root', passwd = self.paswd, database="speakolingo") as conn:
                cur = conn.cursor()
                if s != '':
                   cur.execute(f"SELECT * FROM {table_name} WHERE {s};")
                else:
                    cur.execute(f"SELECT * FROM {table_name};")
        except Exception as e:
            print("Please check the filter values.")     
        
        return cur.fetchall()
    
    def show_values(self,table_name,**kwargs) -> None:
        print(tabulate(self.get_values(table_name,**kwargs),tablefmt="fancy_grid"))
    
    def clear_table(self, table_name) -> None:
        with connect(user = 'root', passwd = self.paswd, database="speakolingo") as conn:
            cur = conn.cursor()
            conn.autocommit(1)
            cur.execute(f"delete from {table_name};")
            
    def destroy_database(self):
        with connect(user = 'root', passwd = self.paswd) as conn:
            cur = conn.cursor() 
            cur.execute("drop database speakolingo;")
            
    def last_session_id(self):
        with connect(user = 'root', passwd = self.paswd, database="speakolingo") as conn:
            cur = conn.cursor()
            cur.execute("select max(session_id) from recent_sessions;")
            value = cur.fetchall()
            if value[0][0] == None:
                value = 0
            else:
                value = value[0][0]
            return value

import re

import random
import JapaneseTokenization
import UserSettings
from datetime import datetime

db = db_manager('Lambda@mysql')

# db.clear_table('language_data')
# with open(r"C:\Users\nijma\Downloads\N2 sentences.txt",encoding='utf-8') as file:
#     for line in file:
#         line  = re.sub(r"\\u3000",' ',line).rstrip('\n\r').split('.')[1]
        
#         db.insert_values('language_data','ja-JP',line,'sentence', 'BEGINNER')

# db.show_values('language_data',language_id = 'ja-JP')

# with open(r"C:\Users\nijma\Desktop\English.txt",encoding='utf-8') as file:
#     for line in file:
#         x = line.split('.')[1]
        
#         db.insert_values('language_data','en-US',x,'sentence', 'BEGINNER')

# db.show_values('language_data',language_id = 'en-US')

userData = ('User', 'User', 'password', '', 'email', 0,'Rank', 0, '0000000')
userSettings=UserSettings.GetCurrentSettings()

if userSettings['UserID'] != "NotLoggedIn":
    data = db.get_values('users', username=userSettings['UserID'])
    userData = data[0]

supportedLanguages = db.get_values('supported_languages')

lastDate = userSettings['LastLogin']
currentDate = datetime.now().strftime('%x')

if lastDate != currentDate:
    db.clear_table('recent_sessions')
    userSettings['LastLogin'] = currentDate
    UserSettings.UpdateCurrentSettings('LastLogin', currentDate)

def GetSupportedLanguages():
    return supportedLanguages

def GetLanguageID(language):
    lan_id=''
    for i in supportedLanguages:
        if language == i[0]:
            lan_id = i[1]
            break
    return lan_id

def GetLanguageFromID(languageID):
    language = ''
    for i in supportedLanguages:
        if languageID == i[1]:
            language = i[0]
            break
    return language

def GetFromTextType(type, language):
    wordsToCheck=[]
    wordsToSpeak=[]
    languageID = GetLanguageID(language)
    textData = db.get_values('language_data', language_id=languageID, entry_type=type, fluency_level=userData[7])
    dataToSpeak=textData[random.randint(0,len(textData)-1)]
    if language == "Japenese":
        data = JapaneseTokenization.Tokenize(dataToSpeak[1])
        wordsToCheck = data[0]
        wordsToSpeak = data[1]
    else:
        wordsToSpeak=dataToSpeak[1].split()
    
    return [wordsToSpeak, wordsToCheck, dataToSpeak[1]]

def GetNewSession(type, language, noOfExercise):
    session=[]
    lastSessionId = db.last_session_id()
    for i in range(noOfExercise):
        session.append(GetFromTextType(type, language))
        db.insert_values('recent_sessions', GetLanguageID(language), lastSessionId+1, session[i][2])
    return session

def GetSessionFromID(sessionID):
    session = []
    sessionData = db.get_values('recent_sessions', session_id=sessionID)
    for i in sessionData:
        wordsToSpeak = []
        wordsToCheck = []
        if i[0] == GetLanguageID('Japenese'):
            data = JapaneseTokenization.Tokenize(i[2])
            wordsToCheck = data[0]
            wordsToSpeak = data[1]
        else:
            wordsToSpeak=i[2].split()
        
        session.append([wordsToSpeak, wordsToCheck, i[2]])
    return (session, GetLanguageFromID(sessionData[0][0]))

def GetLastSessionID():
    return db.last_session_id()

def RegisterNewUser(user, emailId, passwd):
    db.insert_values('users', user, user, passwd,'', emailId, 0, 'BEGINNER', 0, '0000000')
    LoginUser(user, passwd)

def LoginUser(emailId, passwd):
    data = db.get_values('users', email=emailId)
    if not data:
        return False
    if data[0][2] != passwd:
        return False
    
    global userData
    userData = data[0]
    
    UserSettings.UpdateCurrentSettings('UserID', data[0][0])
    return True

def GetUserData():
    if UserSettings.IsLoggedIn():
        return userData
    return ()