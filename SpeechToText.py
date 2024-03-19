import speech_recognition as sr
import GoogleCloudSTTAPI

class SpeechSettings():
    Language=""

class ListenToUser():
    mic = sr.Microphone()
    googleCloudAPI = GoogleCloudSTTAPI.Listener()
    
    previewText = ""
    wordsToSpeak = []
    wordsToCheck = []
    wordsCompleted = []
    skippedWords = []
    numberOfLines = 0
    language = "en-US"
    
    
    def StopListening(self, wait_for_stop):
        pass

    def Initialize(self, data):
        self.wordsToSpeak = data[0]
        self.wordsToCheck = data[1]
        self.wordsCompleted = []
        numberOfCharacters = 0
        for i in self.wordsToSpeak:
            numberOfCharacters += len(i)
        self.numberOfLines = numberOfCharacters/20
    
    def GetText(self):
        totalCharactersSpoken = 0
        text = "[color=#b64f3a]"
        completeStreak = False
        for i in self.wordsCompleted:
            if i[1] == 'complete' and completeStreak == False:
                text += "[/color][color=#66dc56]" + i[0] + " "
                completeStreak = True
            elif i[1] == 'complete' and completeStreak == True:
                text += i[0] + " "
            elif i[1] == 'wrong' and completeStreak == True:
                text += "[/color][color=#b64f3a]" + i[0] + " "
                completeStreak = False
            else:
                text += i[0] + " "
                
            totalCharactersSpoken += len(i[0])
        text += "[/color][color=#ffffff]"
        for i in self.wordsToSpeak:
            text += i + " "
        text += "[/color]"
        
        currentLineIndex = totalCharactersSpoken/20
        scrollPercentage = 1 - (currentLineIndex/self.numberOfLines)
        
        complete = False
        if not self.wordsToSpeak:
            complete = True
        return [text, complete, scrollPercentage, self.previewText]
    
    def StartListening(self):
        self.StopListening = self.googleCloudAPI.listen_in_background(self.CheckForWordInSpeech, self.language)
    
    def CheckForWordInSpeech(self, text):
        if text == "":
            return
        
        text = text.lower()
        
        if self.language == "ja-JP":
            wordList = text.split()
            textList = list(text)
            self.previewText = wordList[-1]
            for i in textList:
                if not self.wordsToSpeak:
                    return
                if self.wordsToCheck[0] == ' ':
                    self.wordsCompleted.append([self.wordsToSpeak.pop(0), 'complete'])
                    self.wordsToCheck.pop(0)
                if self.wordsToCheck[0] in textList:
                    self.wordsCompleted.append([self.wordsToSpeak.pop(0), 'complete'])
                    self.wordsToCheck.pop(0)
        else:
            textList = text.split()
            self.previewText = textList[-1]
            
            if not self.wordsToSpeak:
                return
            if self.wordsToSpeak[0].lower() == textList[-1]:
                self.wordsCompleted.append([self.wordsToSpeak.pop(0), 'complete'])
    
    def SkipWord(self):
        if not self.wordsToSpeak:
            return
        word = self.wordsToSpeak.pop(0)
        if self.language == 'ja-JP':
            self.wordsToCheck.pop(0)
            print(self.wordsToCheck)
            print(self.wordsToSpeak)
        self.wordsCompleted.append([word, 'wrong'])