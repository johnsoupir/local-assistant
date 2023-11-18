from flask import Flask, request, send_file
from TTS.api import TTS

app = Flask(__name__)

# Initialize the TTS object with the specified model
tts = TTS(model_name="tts_models/en/ljspeech/fast_pitch", progress_bar=True, gpu=True)

@app.route('/synthesize', methods=['POST'])
def synthesize():
    text = request.data.decode()
    output_path = 'OUTPUT.wav'
    
    # Generate speech and save to file
    tts.tts_to_file(text, file_path=output_path)
    
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4999)
