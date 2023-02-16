import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from tkinter import Tk, messagebox, Button
import threading
import whisper
import pyperclip


DURATION = 5

FILENAME = "recording.wav"

def start_recording(stop_event):
    device_info = sd.query_devices()
    input_device = device_info[0]['name']
    sample_rate = device_info[0]['default_samplerate']
    channels = 1
    stream = sd.InputStream(device=input_device, samplerate=sample_rate, channels=channels)
    
    audio_frames = []
    stream.start()
    while not stop_event.is_set():
        audio_chunk, _ = stream.read(int(DURATION * sample_rate))
        audio_frames.append(audio_chunk)
    
    stop_button.configure(state="disabled")
    stream.stop()
    
    audio_frames = np.concatenate(audio_frames, axis=0)
    audio_frames = np.array(audio_frames, dtype='float32')
    
    sf.write(FILENAME, audio_frames, int(sample_rate))
        
    model = whisper.load_model("base.en")
    result = model.transcribe(FILENAME)
    
    pyperclip.copy(result['text'])
    
    os.system('osascript -e \'display notification "Transcription copied" with title "Audio Recorder"\' \
    -e \'delay 0.5\' \
    -e \'tell current notification to remove\'')
        
    start_button.configure(state="normal")


def stop_recording():
    stop_event.set()

def start_recording_thread():
    start_button.configure(state="disabled")
    stop_button.configure(state="normal")
    threading.Thread(target=start_recording, args=(stop_event,)).start()
    
root = Tk()
root.title("Audio Recorder")
start_button = Button(root, text="Start Recording", command=start_recording_thread)
stop_button = Button(root, text="Stop Recording", command=stop_recording, state="disabled")
start_button.pack()
stop_button.pack()

stop_event = threading.Event()

def enable_stop_button():
    stop_button.configure(state="normal")

root.mainloop()
