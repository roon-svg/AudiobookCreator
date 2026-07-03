import edge_tts
import asyncio
from PySide6.QtGui import QTextCursor, QColor
from PySide6.QtWidgets import QFileDialog, QProgressDialog, QTextEdit
import torchaudio.functional as f
import torchaudio.transforms as T
import torchaudio
import torch
import os


class AudioSynthesier:
    def __init__(self, textArea: QTextEdit):

        # This allows for the text area to be accessed and manipulated, as well as the cursor and document
        self.textArea = textArea
        self.doc = textArea.document()
        self.cursor = QTextCursor(self.doc)
        self.cursor.movePosition(QTextCursor.Start)
        

        self.audioChunks = []

    def getTextWithEmotions(self):
        # This function goes through the text and gets the text and the emotion connected to it, then adds it to a list of tuples
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

            # This checks if the emotion has changed, if it has then it adds the text and emotion to the list, if not it just adds the text to the current text
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

        # If there is no save path, then the function is exited
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

        # This creates a progress dialog to show the user that the audiobook is being generated
        progressDialog = QProgressDialog("Generating audiobook...", None, 0, 0, parent_window)
        progressDialog.setCancelButton(None)
        progressDialog.show()
        # end of progress dialog code

        for text, emotion in TextToConvertToSpeech:
            
            tempFileName = f"temp_audio_{audioChunksIndex}.wav"
            tempFileNames.append(tempFileName)

            tts = edge_tts.Communicate(text)
            asyncio.run(tts.save(tempFileName))

            # This checks the emotion and then calls the corresponding function to synthesise the audio, then it removes the temporary file
            if emotion == "Anger":
                self.AngrySynthesise(tempFileName)
            elif emotion == "Sadness":
                self.SadnessSynthesise(tempFileName)
            elif emotion == "Happiness":
                self.HappinessSynthesise(tempFileName)
            else:
                self.NeutralSynthesis(tempFileName)
            
            audioChunksIndex += 1
        
        if self.audioChunks:
            tensors = []
            targetSr = 24000
            
            # This resamples the audio chunks to the sample rate and then joints them together
            for wave, sr in self.audioChunks:
                if sr != targetSr:
                    wave = f.resample(wave, sr, targetSr)
                tensors.append(wave)
                
            try:
                finalAudio = torch.cat(tensors, dim=1)
                torchaudio.save(save_path, finalAudio, targetSr)
                print(f"Audiobook successfully generated: {save_path}")
            except Exception as e:
                print(f"Error generating audiobook: {e}")
            
            for i in range(audioChunksIndex):
                if os.path.exists(f"processed_{i}.wav"):
                    os.remove(f"processed_{i}.wav")
        
        import gc
        # Clean up lists and trigger global garbage collection safely at the very end
        self.audioChunks = []
        gc.collect()
        for file in tempFileNames:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except PermissionError:
                print(f"Permission error: Could not remove temporary file {file}. It may still be in use.") 
            except Exception as e:
                print(f"Error removing temporary file {file}: {e}")
        
        progressDialog.close()

    
    # These functions make the audio sound more like the emotion, by changing the speed, pitch, gain and overdrive
    def AngrySynthesise(self, filepath):
        waveform, sample_rate = torchaudio.load(filepath)

        if sample_rate is None:
            sample_rate = 24000
        
        waveform = f.pitch_shift(waveform, sample_rate, n_steps=-0.8)
        waveform, _ = f.speed(waveform, sample_rate, 1.16)

        waveform = f.highpass_biquad(waveform, sample_rate, cutoff_freq=90)
        waveform = f.equalizer_biquad(waveform, sample_rate, center_freq=220, gain=6, Q=1.0)
        waveform = f.equalizer_biquad(waveform, sample_rate, center_freq=2700, gain=7, Q=1.2)
        waveform = f.equalizer_biquad(waveform, sample_rate, center_freq=5000, gain=2, Q=1.0)

        waveform = f.gain(waveform, gain_db=9)
        waveform = torch.tanh(waveform * 1.8)
        waveform = f.overdrive(waveform, gain=5.0)
        waveform = torch.tanh(waveform * 2.2)
        
        self.audioChunks.append((waveform.clone(), sample_rate))


    def SadnessSynthesise(self, filepath):
        waveform, sample_rate = torchaudio.load(filepath)

        if sample_rate is None:
            sample_rate = 24000


        waveform = f.pitch_shift(waveform, sample_rate, n_steps=-0.1)
        waveform, _ = f.speed(waveform, sample_rate, 0.9)

        waveform = f.highpass_biquad(waveform, sample_rate, cutoff_freq=90)
        waveform = f.equalizer_biquad(waveform, sample_rate, center_freq=3000, gain=-2.5, Q=1.0)

        silence = torch.zeros((waveform.shape[0], int(0.1 * sample_rate)))
        waveform = torch.cat([waveform, silence], dim=1)

        waveform = f.gain(waveform, gain_db=-1.5)

        self.audioChunks.append((waveform.clone(), sample_rate))

    def HappinessSynthesise(self, filepath):
        waveform, sample_rate = torchaudio.load(filepath)

        if sample_rate is None:
            sample_rate = 24000

        waveform = f.pitch_shift(waveform, sample_rate, n_steps=0.1)
        waveform, _ = f.speed(waveform, sample_rate, 1.05)

        waveform = f.equalizer_biquad(waveform, sample_rate, center_freq=3500, gain=2.5, Q=1.0)

        waveform = f.gain(waveform, gain_db=1.5)

        self.audioChunks.append((waveform.clone(), sample_rate))
    
    def NeutralSynthesis(self, filepath):
        waveform, sample_rate = torchaudio.load(filepath)

        if sample_rate is None:
            sample_rate = 24000

        self.audioChunks.append((waveform.clone(), sample_rate))