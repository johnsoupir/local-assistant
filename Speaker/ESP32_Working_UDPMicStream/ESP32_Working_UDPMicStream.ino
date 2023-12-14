#include <WiFi.h>
#include <WiFiUdp.h>
#include "driver/i2s.h"

const char *ssid = "UMary-Engineering";
const char *password = "UoM_EngLab";
const char *udpAddress = "10.10.65.15";  // Replace with your computer's IP address
const int udpPort = 12345;

const int bckPin = 4;  // BCK pin
const int wsPin = 5;  // WS pin
const int sdPin = 18;  // SD pin

WiFiUDP udp; // Declare udp globally

unsigned long startTime;
const unsigned long captureDuration = 2000; // 2 seconds in milliseconds
const unsigned long sendInterval = 5000;    // 5 seconds in milliseconds

void setup()
{
  Serial.begin(115200);

  // Connect to Wi-Fi with static IP and custom subnet
  IPAddress staticIP(10, 10, 65, 35);  // Replace with your desired static IP address
  IPAddress gateway(10, 10, 65, 1);     // Replace with your gateway IP address
  IPAddress subnet(255, 255, 255, 0);   // Replace with your subnet mask

  WiFi.config(staticIP, gateway, subnet);

  // Attempt to connect to Wi-Fi up to 10 times
  for (int attempts = 1; attempts <= 10; attempts++)
  {
    Serial.print("Connecting to WiFi (Attempt ");
    Serial.print(attempts);
    Serial.print(") ...");

    WiFi.begin(ssid, password);

    int attemptTimeout = 0;
    while (WiFi.status() != WL_CONNECTED && attemptTimeout < 20)
    {
      delay(1000);
      Serial.print(".");
      attemptTimeout++;
    }

    if (WiFi.status() == WL_CONNECTED)
    {
      Serial.println("\nConnected to WiFi");
      Serial.print("IP Address: ");
      Serial.println(WiFi.localIP());
      break;  // Exit the loop if connected
    }
    else
    {
      Serial.println("\nFailed to connect to WiFi");
      if (attempts == 10)
      {
        Serial.println("Rebooting ESP32...");
        ESP.restart();  // Reboot the ESP32 if maxAttempts reached
      }
      else
      {
        delay(5000);  // Wait for 5 seconds before the next attempt
      }
    }
  }

  // Initialize I2S
  i2s_config_t i2s_config = {
      .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
      .sample_rate = 16000,  // Adjust as needed
      .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
      .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
      .communication_format = I2S_COMM_FORMAT_I2S_MSB,
      .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
      .dma_buf_count = 8,
      .dma_buf_len = 64,
      .use_apll = true,
      .tx_desc_auto_clear = true,
      .fixed_mclk = 0};

  i2s_pin_config_t pin_config = {
      .bck_io_num = bckPin,
      .ws_io_num = wsPin,
      .data_out_num = -1,  // Not used
      .data_in_num = sdPin};

  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);

  // Start UDP
  udp.begin(udpPort);

  // Record start time
  startTime = millis();
}

void loop()
{
  size_t bytesRead;
  uint8_t audioData[4096];  // Adjust buffer size as needed

  // Read audio data from I2S
  i2s_read(I2S_NUM_0, audioData, sizeof(audioData), &bytesRead, portMAX_DELAY);

  // Send audio data over UDP
  udp.beginPacket(udpAddress, udpPort);
  udp.write(audioData, bytesRead);
  udp.endPacket();

  // Check if 2 seconds have passed
  if (millis() - startTime >= captureDuration)
  {
    Serial.println("Captured 2 seconds of audio. Sending...");

    // Reset start time for the next capture
    startTime = millis();

    // Continue capturing and sending while waiting for the next interval
    while (millis() - startTime < sendInterval)
    {
      // Read audio data from I2S
      i2s_read(I2S_NUM_0, audioData, sizeof(audioData), &bytesRead, portMAX_DELAY);

      // Send audio data over UDP
      udp.beginPacket(udpAddress, udpPort);
      udp.write(audioData, bytesRead);
      udp.endPacket();
    }
    
    Serial.println("Sending complete. Continuing to capture...");
  }
}
