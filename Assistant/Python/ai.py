#!/usr/bin/env python3
# prerequisites: as described in https://alphacephei.com/vosk/install and also python module `sounddevice` (simply run command `pip install sounddevice`)
# Example usage using Dutch (nl) recognition model: `python test_microphone.py -m nl`
# For more help run: `python test_microphone.py -h`

import argparse
import queue
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from gpt4all import GPT4All
import json
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play
from llama_cpp import Llama
from google.cloud import texttospeech
import openai
from simpleMQTT import create_mqtt_client, connect_to_broker, publish_message, disconnect_broker



def sendMQTT(state):
    if connect_to_broker(mqtt_client):
        # Publish a message
        publish_message(mqtt_client, 'esp/output', state)
    
        # Disconnect from the broker
        disconnect_broker(mqtt_client)

def load_KEY(keyfile):
    try:
        with open(keyfile, 'r') as f:
            api_key = f.readline().strip()
        return api_key

    except FileNotFoundError:
        print("Key file not found. Please make sure the file exists.")

    except Exception as e:
        print("An error occurred opening the API key file: ", e)


def promptOpenAI(input):
    summary = openai.ChatCompletion.create(
        model='gpt-3.5-turbo-16k',
        messages=[{"role":"user", "content": input}]
    )
    return summary.choices[0].message.content + " "

mqtt_client = create_mqtt_client()

FourAllmodel = GPT4All("/home/john/.local/share/nomic.ai/GPT4All/gpt4all-falcon-q4_0.gguf", allow_download=False)
# FourAllmodel = GPT4All("/home/john/.local/share/nomic.ai/GPT4All/mistral-7b-openorca.Q4_0.gguf", allow_download=False)
llm = Llama(model_path="./llama-2-7b-chat.Q4_0.gguf")

def playAudio(audioFile):
    sound = AudioSegment.from_file(audioFile)
    play(sound)

#def localTTS(inputText, outputFile):
model_name = 'tts_models/en/ljspeech/tacotron2-DDC'
tts = TTS(model_name)
# tts.tts_to_file(text=inputText, file_path=outputFile)

def googleTTS(inputText, outputFile):
    client = texttospeech.TextToSpeechClient()
    synthInput = texttospeech.SynthesisInput(text=inputText)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", 
        name="en-US-Neural2-I",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE

    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input = synthInput, voice=voice, audio_config=audio_config
    )

    with open(outputFile, "wb") as out:
        out.write(response.audio_content)


q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

audioPlaying = False  # Global variable to indicate audio playback status

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    global audioPlaying
    if status:
        print(status, file=sys.stderr)
    if not audioPlaying:  # Check if audio is not playing before adding to the queue
        q.put(bytes(indata))


# def callback(indata, frames, time, status):
#     """This is called (from a separate thread) for each audio block."""
#     if status:
#         print(status, file=sys.stderr)
#     q.put(bytes(indata))

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

openai.api_key = load_KEY("API_KEY")

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])
        
    if args.model is None:
        model = Model(lang="en-us")
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
                print("Raw Output:", rawOutput)

                # Loading the raw output as JSON
                parsedOutput = json.loads(rawOutput)

                # Extracting and printing the text
                userSpeech = parsedOutput['text']
                # print("Final output is: ", userSpeech)
                if (userSpeech != ""):
                    audioPlaying = True
                    playAudio("processing.mp3")
                    # inputToLLM = "Q: " + userSpeech  + " A:"
                    # print(inputToLLM)
                    #outputText = llm(inputToLLM, max_tokens=48, stop=["Q:", "\n"], echo=True)
                    print('User: ' + userSpeech)
                    if "on" in userSpeech:
                        sendMQTT('1')
                        pass
                    if "off" in userSpeech:
                        sendMQTT('0')
                    # userSpeech += "?"
                    # answer = FourAllmodel.generate(userSpeech, max_tokens=200)
                    #FourAllmodel.chat_session.append()
                    # answer = promptOpenAI(userSpeech)
                    #outputText = FourAllmodel.generate(userSpeech, max_tokens=200)
                    #outputSpeech = outputText



                    #outputSpeech = (outputText['choices'][0]['text'])

                    #answer = outputSpeech.split('A: ')[1]
                    #localTTS(answer, "out.wav")
                    # tts.tts_to_file(text=answer, file_path="out.wav")
                    # googleTTS(answer, "out.wav")
                    # audioPlaying = True
                    # playAudio("out.wav")
                    # audioPlaying = False

                    # Stop recording here
                    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
                                  dtype="int16", channels=1, callback=None):
                        # localTTS(answer, "out.wav")
                        #playAudio("out.wav")
                        playAudio("done.mp3")
                        # input("Press enter to continue...")
                        # playAudio("done.mp3")
                        audioPlaying = False

                
            else:
            # not audioPlaying:
                print(".",end="")
                #print(rec.PartialResult())
            if dump_fn is not None:
                dump_fn.write(data)


except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))
