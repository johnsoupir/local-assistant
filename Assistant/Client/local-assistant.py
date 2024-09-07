#!/usr/bin/env python3
from Modules.local_assistant_llm import *
from Modules.local_assistant_tts import *
from Modules.simpleMQTT import *
import time
import queue
import sys
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pvporcupine
from pvrecorder import PvRecorder

def callback(indata, frames, time, status):
    global muteVoskMic
    if status:
        print(status, file=sys.stderr)
    if not muteVoskMic:  # Check if audio is not playing before adding to the queue
        q.put(bytes(indata))


serverHost = "allevil.local"
llm_port = "8080"
tts_port = "4999"
wakeWords=['computer']
systemPrompt = "You are a home automation AI. If you are asked a question you will give a helpful answer. If you are asked to control a device, you will respond with Command Detected: <device> <state>.  User: "
pvAccessKey="Vt9IQDOAGkmaPfZYyoQHD+Dsdtc/k8P8Y+4zpOxFu9g/DVd8ARwBXg=="
pvWakeModel='./Skippy_en_linux_v3_0_0.ppn'

porcupine = pvporcupine.create(access_key=pvAccessKey, keywords=wakeWords)
recoder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

q = queue.Queue()
muteVoskMic=True

useLocalLLM(serverHost, llm_port)
try:
    recoder.start()
    args = sys.argv[1:]
    voskSamplerate = 16000  
    voskModel = Model("vosk-model-en-us-0.42-gigaspeech")

    while True:
        wakeWordIndex = porcupine.process(recoder.read())
        if wakeWordIndex >= 0:
            muteVoskMic = False
            playAudio("Sounds/done.mp3")
            print(f"Detected wakeword: {wakeWords[wakeWordIndex]}")
            with sd.RawInputStream(samplerate=voskSamplerate, blocksize=8000, dtype="int16", channels=1, callback=callback):
                rec = KaldiRecognizer(voskModel, voskSamplerate)
                data = q.get()
                while (rec.AcceptWaveform(data) != True):
                    data = q.get()
                muteVoskMic = True

                print("")
                rawOutput = rec.Result()
                parsedOutput = json.loads(rawOutput)
                userSpeech = parsedOutput['text']

                if (userSpeech != ""):
                    startTime = time.time()
                    muteVoskMic = True
                    print('User: ' + userSpeech + "\n")

                    answer = promptOpenAI(systemPrompt + userSpeech)
                    answer = promptWithThread(userSpeech, 1.8)
                    print('LLM: ' +  answer + "\n")
                    answer = removeEmojis(answer)
                    # googleTTS(answer, "out.wav")
                    localTTS(answer, serverHost, tts_port)

                    endTime = time.time()
                    totalTime = endTime - startTime
                    print("Response took " + str(totalTime) + " seconds.")
                    playAudio("out.wav")
                    #About 94-155 chars a second response time!
                    #Or about 26-30 words/second!
                    if "command detected" in answer.lower():
                        if "on" in answer.lower():
                            print("\n\n LIGHT ON \n\n")
                            sendMQTT('1')
                        if "off" in answer.lower():
                            print("\n\n LIGHT OFF \n\n")
                            sendMQTT('0')
                muteVoskMic = True

except KeyboardInterrupt:
    recoder.stop()
finally:
    porcupine.delete()
    recoder.delete()




# try:
#   # You can change the language model here

#     with sd.RawInputStream(samplerate=voskSamplerate, blocksize=8000, dtype="int16", channels=1, callback=callback):
#         rec = KaldiRecognizer(voskModel, voskSamplerate)
#         while True:
#             data = q.get()
#             if rec.AcceptWaveform(data):
#                 print(rec.Result())

# except KeyboardInterrupt:
#     print("\nDone")
# except Exception as e:
#     print(type(e).__name__ + ": " + str(e))
