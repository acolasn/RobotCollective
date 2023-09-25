// VCC goes to 5V of the Arduino 
// GND goes to GND of the Arduino 
// TRG and ECHO go to any digital pins of the Arduino - here, TRG --> D3 and ECHO --> D2

// defines pins numbers
const int trigPin = 6;
const int echoPin = 7;

// defines variables
long US_duration; // US: ultra-sound
int US_distance;

void setup() {
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  Serial.begin(9600); // Starts the serial communication
}

void loop() {
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  US_duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  US_distance = US_duration * 0.034 / 2;
  // Prints the distance on the Serial Monitor
  // Serial.print("Distance: ");
  Serial.println(US_distance);
}