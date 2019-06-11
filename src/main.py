from multiprocessing import Process, Queue
from robot_controller import Controller
from text_parser import Parser
import pyaudio
import librosa
import pickle
import sounddevice as sd
import numpy as np
import threading
from array import array
import wave

mapping = ['tien', 'lui', 'len', 'xuong', 'trai', 'phai', 'quay', 'dung', 'thoat']

CHUNK_SIZE = 1024
MIN_VOLUME = 1000
RECORD_SECONDS = 1
RATE = 44100
CHANNELS = 2
FORMAT = pyaudio.paInt16

MODEL = pickle.load(open('./train_hmm/hmm.pk', 'rb'))

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def parseText(text_queue, action_queue, parser, DEBUG=True):
	'''Get parse text_queue to get action'''
	while True:
		text = text_queue.get()
		if text is not None:
			action = parser.apply(text)
			if action is not None:
				action_queue.put(action)
		
def transcribe(data, fs=44100):
    global MODEL
    mfcc = librosa.feature.mfcc(data, sr=fs, n_fft=1024, hop_length=128).T

    score = [MODEL[i].score(mfcc) for i in range(len(mapping))]
    score = softmax(np.array(score))
    if max(score) > 0.8: 
        idx = np.argmax(score)
        text = mapping[idx]
        # print(score[idx], end=' ')
        return text
    return None

def saveFile(filename, frames):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def record(stopped, audio_queue, text_queue):
    while True:
        frames = audio_queue.get()

        isContinue = True
        for frame in frames:
            vol = max(array('h', frame))
            if vol >= MIN_VOLUME:
                isContinue = False

        if isContinue:
            continue

        filename = 'command.wav'
        saveFile(filename, frames)

        data, fs = librosa.load(filename, sr=None)
        text_queue.put(transcribe(data, fs))

def listen(stopped, audio_queue):
    stream = pyaudio.PyAudio().open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )

    while True:
        frames = []
        for i in range(0, int(RATE / CHUNK_SIZE * RECORD_SECONDS)):
            data = stream.read(CHUNK_SIZE)
            frames.append(data)
        audio_queue.put(frames)

if __name__ == '__main__':
    parser = Parser()
    controller = Controller()


    text_queue = Queue()
    action_queue = Queue()
    audio_queue = Queue()

    stopped = threading.Event()

    listen_t = threading.Thread(target=listen, args=(stopped, audio_queue))
    listen_t.start()

    record_t = threading.Thread(target=record, args=(stopped, audio_queue, text_queue))
    record_t.start()

    parser_process = Process(target=parseText, args=(
            text_queue, action_queue, parser
    ))
    parser_process.start()
    controller.start()

    prev_action = None
    while True:
        action = action_queue.get()

        if action is not None:
            if action == 'quit':
                print('thoat')
                break
            else:
                controller.apply(action)
                prev_action = action
                print(action)
        elif prev_action == 'tien' or prev_action == 'lui':
            controller.apply(prev_action)

    # Clean up the multiprocessing process.
    controller.stop()
    listen_t.join()
    record_t.join()
    parser_process.terminate()
    parser_process.join()