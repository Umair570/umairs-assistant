import queue
import sounddevice as sd
import sys
from config import Config

class AudioEngine:
    def __init__(self):
        self.q = queue.Queue()

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def get_stream(self):
        return sd.RawInputStream(
            samplerate=Config.SAMPLE_RATE,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=self.callback
        )
    
    def get_queue(self):
        return self.q