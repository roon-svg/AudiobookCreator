import gtts
from PySide6.QtGui import QTextCursor, QColor
from PySide6.QtWidgets import QFileDialog, QTextEdit
import torchaudio.functional as f
import torchaudio
import torch
import os


class AudioSynthesier:
    def __init__(self, textArea: QTextEdit):

        self.textArea = textArea
        self.doc = textArea.document()
        self.cursor = QTextCursor(self.doc)
        self.cursor.movePosition(QTextCursor.Start)
        

        self.audioChunks = []

    def getTextWithEmotions(self):
        TextToConvertToSpeech = []
        currentEmotion = None
        currentText = ""


        self.cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        while not self.cursor.atEnd():

            # Moves the cursor to the next character and gets the colour
            self.cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            fmt = self.cursor.charFormat()
            CursText = self.cursor.selectedText()
            
            # This skipsnew lines and empty spaces
            if not CursText or CursText == "\u2029":
                self.cursor.setPosition(self.cursor.position())
                continue

            # Checks the background colour and then adds it to the connected emotion
            if fmt.background().color() == QColor("red"):
                newEmotion = "Anger"
            elif fmt.background().color() == QColor("blue"):
                newEmotion = "Sadness"
            elif fmt.background().color() == QColor("yellow"):
                newEmotion = "Happiness"
            else:
                newEmotion = "Neutral"

            import gc
            gc.collect()

            if currentEmotion is None:
                currentEmotion = newEmotion
                currentText = CursText
            elif newEmotion == currentEmotion:
                currentText += CursText
            else:
                TextToConvertToSpeech.append((currentText, currentEmotion))
                currentText = CursText
                currentEmotion = newEmotion
            
            self.cursor.setPosition(self.cursor.position())

        # Append the last text and emotion
        TextToConvertToSpeech.append((currentText, currentEmotion))
        self.cursor.movePosition(QTextCursor.NextCharacter)
        return TextToConvertToSpeech

    def MakeAudiobook(self):
        parent_window = self.textArea.window()
        
        # This allows for the user to save a file
        save_path, _ = QFileDialog.getSaveFileName(
            parent_window,
            "Save Audiobook",
            "audiobook.wav",
            "WAV Files (*.wav);;All Files (*)"
        )

        if not save_path:
            return

        self.audioChunks = [] 
        TextToConvertToSpeech = self.getTextWithEmotions()


        audioChunksIndex = 0   
        #This makes sure that there is text to convert to speech     
        if len(TextToConvertToSpeech) == 0:
            print("No text to convert to speech.")
            return

        tempFileNames = []

        for text, emotion in TextToConvertToSpeech:
            
            tempFileName = f"temp_audio_{audioChunksIndex}.mp3"
            tempFileNames.append(tempFileName)

            tts = gtts.gTTS(text)
            tts.save(tempFileName)

            if emotion == "Anger":
                self.AngrySynthesise(tempFileName, audioChunksIndex)
            elif emotion == "Sadness":
                self.SadnessSynthesise(tempFileName, audioChunksIndex)
            elif emotion == "Happiness":
                self.HappinessSynthesise(tempFileName, audioChunksIndex)
            else:
                self.NeutralSynthesis(tempFileName, audioChunksIndex)
            
            if os.path.exists(tempFileName):
                os.remove(tempFileName)
            audioChunksIndex += 1
        
        if self.audioChunks:
            tensors = []
            targetSr = 24000
            
            for wave, sr in self.audioChunks:
                if sr != targetSr:
                    wave = f.resample(wave, sr, targetSr)
                tensors.append(wave)
                
            finalAudio = torch.cat(tensors, dim=1)
            torchaudio.save(self.outputFilename, finalAudio, targetSr)
            print(f"Audiobook successfully generated: {self.outputFilename}")
            
            for i in range(audioChunksIndex):
                if os.path.exists(f"processed_{i}.wav"):
                    os.remove(f"processed_{i}.wav")
        
        import gc
        gc.collect()
        for file in tempFileNames:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except PermissionError:
                print(f"Permission error: Could not remove temporary file {file}. It may still be in use.") 
            except Exception as e:
                print(f"Error removing temporary file {file}: {e}")

    
    def AngrySynthesise(self, filepath, index):
        waveform, sample_rate = torchaudio.load(filepath)

        waveform = f.speed(waveform, sample_rate, 1.2)
        waveform = f.pitch_shift(waveform, sample_rate, n_steps=4)
        waveform = f.gain(waveform, gain_db=5)
        waveform = f.overdrive(waveform, gain=20.0)
        

        self.audioChunks.append((waveform.clone(), sample_rate))



    def SadnessSynthesise(self, filepath, index):
        waveform, sample_rate = torchaudio.load(filepath)

        waveform = f.speed(waveform, sample_rate, 0.85)
        waveform = f.pitch_shift(waveform, sample_rate, n_steps=-3)
        waveform = f.gain(waveform, gain_db=6)

        self.audioChunks.append((waveform.clone(), sample_rate))

    def HappinessSynthesise(self, filepath, index):
        waveform, sample_rate = torchaudio.load(filepath)

        waveform = f.speed(waveform, sample_rate, 1.2)
        waveform = f.pitch_shift(waveform, sample_rate, n_steps=3)
        waveform = f.gain(waveform, gain_db=2)

        self.audioChunks.append((waveform.clone(), sample_rate))
    
    def NeutralSynthesis(self, filepath, index):
        waveform, sample_rate = torchaudio.load(filepath)
        self.audioChunks.append((waveform.clone(), sample_rate))