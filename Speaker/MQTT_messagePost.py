import paho.mqtt.client as mqtt
import time

# MQTT broker settings
mqtt_server = "10.10.65.32"
mqtt_port = 1884
mqtt_topic = "hub/mic_control"

# WiFi credentials (if needed)
# ssid = "YourWiFiSSID"
# password = "YourWiFiPassword"

# Message to publish
message_to_publish = "0"  # You can change this value as needed

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_publish(client, userdata, mid):
    print("Message published")

# Uncomment the following lines if WiFi credentials are needed
# import network
# sta_if = network.WLAN(network.STA_IF)
# sta_if.active(True)
# sta_if.connect(ssid, password)

# Wait for WiFi connection
# while not sta_if.isconnected():
#     pass

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to the MQTT broker
client.connect(mqtt_server, mqtt_port, 60)

# Uncomment the following line if you want to wait for the connection to be established
# client.loop_start()

# Publish the message
client.publish(mqtt_topic, message_to_publish)

# Wait for a moment to ensure the message is sent
time.sleep(2)

# Disconnect from the MQTT broker
client.disconnect()
