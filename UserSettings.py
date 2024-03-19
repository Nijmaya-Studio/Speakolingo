import json

currentSettings = {}

with open('./data/user_settings.json', 'r') as data:
    currentSettings = json.load(data)
    
def GetCurrentSettings():
    return currentSettings

def SaveCurrentSettings():
    with open('./data/user_settings.json', 'w') as file:
        json.dump(currentSettings, file)
        
def UpdateCurrentSettings(key, value):
    currentSettings[key] = value
    SaveCurrentSettings()

def IsLoggedIn():
    if currentSettings['UserID'] != 'NotLoggedIn':
        return currentSettings['UserID']
    else:
        return ''