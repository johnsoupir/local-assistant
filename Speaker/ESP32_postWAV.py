from flask import Flask, Response

app = Flask(__name__)

# Replace this with the path to your MP3 file
mp3_file_path = "music.mp3"

@app.route('/blah.mp3')
def serve_mp3_file():
    try:
        # Open the MP3 file for reading in binary mode
        with open(mp3_file_path, "rb") as mp3_file:
            # Set the content type to audio/mpeg
            headers = {'Content-Type': 'audio/mpeg'}
            # Stream the MP3 content as a response
            return Response(mp3_file.read(), headers=headers)
    except FileNotFoundError:
        return "MP3 file not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
________________________________________
