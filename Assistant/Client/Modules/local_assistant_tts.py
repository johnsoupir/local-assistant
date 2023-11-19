import requests
from google.cloud import texttospeech

from pydub import AudioSegment
from pydub.playback import play

def playAudio(audioFile):
    sound = AudioSegment.from_file(audioFile)
    play(sound)

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


def localTTS(text, host, port, output_file='out.wav'):
    server_url = "http://" + host + ":" + port + "/synthesize" 
    """
    Sends text to a server to be converted to speech and saves the returned audio.
    """
    try:
        response = requests.post(server_url, data=text)

        if response.status_code == 200:
            with open(output_file, 'wb') as audio_file:
                audio_file.write(response.content)
            print(f"Audio saved as {output_file}.")
        else:
            print(f"Error: Server responded with status code {response.status_code}")

    except requests.RequestException as e:
        print(f"An error occurred while making the request: {e}")





