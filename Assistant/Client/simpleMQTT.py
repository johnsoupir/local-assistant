import paho.mqtt.client as mqtt

# Configuration for MQTT Broker
MQTT_BROKER = '192.168.133.64'  # Replace with your MQTT broker's address
MQTT_PORT = 1884  # Standard MQTT port (use 8883 for TLS)
MQTT_TOPIC = 'esp/output'

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

# Callback when the client disconnects from the server
def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))

# Function to create and return an MQTT client
def create_mqtt_client(client_id=""):
    client = mqtt.Client(client_id=client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    return client

# Function to connect to the broker
def connect_to_broker(client, broker=MQTT_BROKER, port=MQTT_PORT):
    try:
        client.connect(broker, port, 60)
        # Start the loop to process received messages and to reconnect to broker if connection is lost
        client.loop_start()
        return True
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
        return False

# Function to publish a message to a topic
def publish_message(client, topic, message):
    try:
        result = client.publish(topic, message)
        # result: [0, 1] where 0=success and 1=error
        status = result[0]
        if status == 0:
            print(f"Sent `{message}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic `{topic}`")
    except Exception as e:
        print(f"Error publishing MQTT message: {e}")

# Function to disconnect from the broker
def disconnect_broker(client):
    client.loop_stop()  # Stop loop before disconnecting
    client.disconnect()

# Example usage
if __name__ == "__main__":
    client = create_mqtt_client()
    if connect_to_broker(client):
        publish_message(client, MQTT_TOPIC, '1')
        disconnect_broker(client)

