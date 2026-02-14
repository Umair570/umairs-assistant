import json
import os
import sys
from vosk import Model, KaldiRecognizer
from config import Config

class SpeechEngine:
    def __init__(self):
        if not os.path.exists(Config.MODEL_PATH):
            print(f"ERROR: Model not found at '{Config.MODEL_PATH}'.")
            print("Please download 'vosk-model-small-en-us-0.15', unzip it, and rename folder to 'model'.")
            sys.exit(1)
            
        print("Loading offline model... (this may take a few seconds)")
        self.model = Model(Config.MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, Config.SAMPLE_RATE)

    def process_audio(self, data):
        """Returns text if a full sentence is recognized, else None."""
        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result())
            return result.get('text', '')
        return None