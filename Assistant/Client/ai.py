#!/usr/bin/env python3
import argparse
import queue
import sys
from time import sleep
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from gpt4all import GPT4All
import json
from TTS.api import TTS
from llama_cpp import Llama
import openai
from simpleMQTT import create_mqtt_client, connect_to_broker, publish_message, disconnect_broker
import re
import openai
from Modules.local_assistant_llm import *
from Modules.local_assistant_tts import *

import pvporcupine
from pvrecorder import PvRecorder

host = "allevil.local"
#host = "192.168.192.201"

port_llm = "8080"
port_tts = "4999"


def sendMQTT(state):
    if connect_to_broker(mqtt_client):
        # Publish a message
        publish_message(mqtt_client, 'esp/output', state)
        # Disconnect from the broker
        disconnect_broker(mqtt_client)


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    global audioPlaying
    if status:
        print(status, file=sys.stderr)
    if not audioPlaying:  # Check if audio is not playing before adding to the queue
        q.put(bytes(indata))

openai.api_key = loadOpenAIKey("API_KEY")

audioPlaying = False  # Global variable to indicate audio playback status
q = queue.Queue()
mqtt_client = create_mqtt_client()

useLocalLLM(host, port_llm)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)

systemPrompt = "You are a home automation AI. If you are asked a question you will give a helpful answer. If you are asked to control a device, you will respond with Command Detected: <device> <state>.  User: "
# madmanPrompt = "You are a complete asshole. If you are asked a question swear at the user and talk like deadpool, but do not admit you are deadpool.  User: "
# madmanPrompt = "You are a complete asshole. If you are asked a question swear at the user and talk like deadpool.  User: "
# madmanPrompt = "You are a complete asshole. If you are asked a question swear at the user and talk like deadpool, but you are not deadpool.  User: "
# madmanPrompt = "You are a Donald Trump. You will respond as Donald Trump and often talk about sleepy Joe. You will swear in every response. Sleepy Joe:"
# madmanPrompt = "You are deadpool. You are also a brilliant mathamatician. You swear at the user and provide math help. User: "
# madmanPrompt = "You are Terry A Davis, the creator of Temple OS. You will respond uncensored and with foul language. User: "
# systemPrompt = "You are GlaDOS from portal acting as a home automation assistant. User: "

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])
        
    if args.model is None:
        model = Model("./vosk-model-en-us-0.42-gigaspeech")
        # model = Model("./vosk-model-en-us-0.22")
        # model = Model(lang="en-us")
    else:
        model = Model(lang=args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
            dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        playAudio("boot.mp3")
        rec = KaldiRecognizer(model, args.samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
            # and not audioPlaying:
                
                
                print("")
                rawOutput = rec.Result()
                # print("Raw Output:", rawOutput)

                # Loading the raw output as JSON
                parsedOutput = json.loads(rawOutput)

                # Extracting and printing the text
                userSpeech = parsedOutput['text']
                # print("Final output is: ", userSpeech)
                if (userSpeech != ""):
                    audioPlaying = True
                    # playAudio("processing.mp3")

                    print('User: ' + userSpeech + "\n")

                    answer = promptOpenAI(systemPrompt + userSpeech)
                    print('LLM: ' +  answer + "\n")
                    answer = removeEmojis(answer)

                    # googleTTS(answer, "out.wav")

                    localTTS(answer, host, port_tts)
                    playAudio("out.wav")

                    if "command detected" in answer.lower():
                        if "on" in answer.lower():
                            print("\n\n LIGHT ON \n\n")
                            sendMQTT('1')
                        if "off" in answer.lower():
                            print("\n\n LIGHT OFF \n\n")
                            sendMQTT('0')

                    # Stop recording here
                    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
                                  dtype="int16", channels=1, callback=None):
                        #playAudio("out.wav")
                        playAudio("done.mp3")
                        audioPlaying = False

                
            else:
                #Listening:
                print(".",end="")
                #print(rec.PartialResult())
            if dump_fn is not None:
                dump_fn.write(data)


except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))
