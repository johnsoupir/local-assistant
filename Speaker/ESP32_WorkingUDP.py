import socket
import numpy as np
import sounddevice as sd

# Set the IP address and port used by the ESP32
esp32_ip = "10.10.65.35"  # Replace with the actual IP address of your ESP32
esp32_port = 12345

# Create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("0.0.0.0", esp32_port))  # Bind to all available interfaces

# Set up audio playback
sample_rate = 16000
channels = 1  # Adjust if needed
dtype = np.int32  # Adjust according to the ESP32 data format

# Open a sounddevice stream
stream = sd.OutputStream(channels=channels, samplerate=sample_rate, dtype=dtype)
stream.start()

amplification_factor = 5.0  # Adjust the amplification factor as needed

"""# Function to print the received audio data
def print_data(audio_data):
    print("Received audio data:")
    print(audio_data)
"""
    
try:
    while True:
        # Receive binary data from the ESP32
        data, addr = udp_socket.recvfrom(4096)  # Adjust the buffer size as needed

        # Decode the received data and print it
        audio_data = np.frombuffer(data, dtype=dtype)

        # Amplify the audio data
        amplified_data = amplification_factor * audio_data

        # Convert amplified data back to int32
        amplified_data_int32 = amplified_data.astype(dtype)

        # Play the amplified audio
        stream.write(amplified_data_int32)

        # Print the received data
        # print_data(audio_data)

except KeyboardInterrupt:
    print("Closing the script.")
finally:
    # Close the sounddevice stream
    stream.stop()
    stream.close()
