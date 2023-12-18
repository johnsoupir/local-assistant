
#include <WiFi.h>
#include <PubSubClient.h>

//TODO: ESP32 MQTT user config
const char* ssid = "Blah"; // Wifi SSID
const char* password = "12345678"; // Wifi Password
const char* username = ""; // my AskSensors username
const char* subTopic = "esp/output"; // actuator/username/apiKeyOut
const int LED_pin = 4; // LEd pin

//AskSensors MQTT config
const char* mqtt_server = "192.168.128.64";
unsigned int mqtt_port = 1884;

WiFiClient askClient;
PubSubClient client(askClient);

void setup() 
{
  Serial.begin(115200);
  Serial.println("*****************************************************");
  Serial.println("********** Program Start : ESP32 controls LED with AskSensors over MQTT");
  Serial.println("Set LED as output");
  pinMode(LED_pin, OUTPUT); // set led as output
  
  Serial.print("********** connecting to WIFI : ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("->WiFi connected");
  Serial.println("->IP address: ");
  Serial.println(WiFi.localIP());
  
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  if (!client.connected())
  {
    reconnect();
  }
  
  
  Serial.print("********** Subscribe to AskSensors actuator topic:");
  Serial.print(subTopic);
  // susbscribe
  client.subscribe(subTopic);
}

void loop() 
{
  client.loop();
}


void callback(char* topic, byte* payload, unsigned int length) 
{
  Serial.print("Command teceived from AskSensors[");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) 
  {
    Serial.print((char)payload[i]);
  }
  Serial.println("********** Parse Actuator command");
  if( (char)*payload == '1' )
  { 
    digitalWrite(LED_pin, 1);
    Serial.println("LED is ON");
  } 
  else
  {
    digitalWrite(LED_pin, 0);
    Serial.println("LED is OFF");
  }
}

void reconnect() 
{
  // Loop until we're reconnected
  while (!client.connected()) 
  {
    Serial.print("********** Attempting MQTT connection...");
      // Attempt to connect
      if (client.connect("ESP32Client", username, "")) 
      { 
        Serial.println("-> MQTT client connected");
      }
      else 
      {
        Serial.print("failed, rc=");
        Serial.print(client.state());
        Serial.println("-> try again in 5 seconds");
        // Wait 5 seconds before retrying
        delay(5000);
      }
  }
}
