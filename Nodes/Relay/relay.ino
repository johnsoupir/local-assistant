const int relayPin = 16;

void setup() {
  pinMode(relayPin, OUTPUT);
}

void loop() {
  // Turn on the relay and the LED
  digitalWrite(relayPin, HIGH);
  delay(1000); // Delay for 1 second

  // Turn off the relay and the LED
  digitalWrite(relayPin, LOW);
  delay(1000); // Delay for 1 second
}
