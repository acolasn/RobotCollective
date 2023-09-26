  // motor pins
  int speedRight = 9;
  int speedLeft = 3;
  int forwLeft = 4;
  int forwRight = 10;
  int backLeft = 5;
  int backRight = 7;
  // ultrasound distance detection pins
  const int trigPin = 6;
  const int echoPin = 11;
  // motor variables
  int speed;
  bool right;
  bool left;
  bool forw;
  bool back;
  bool stop;
  int direction;
  int turn;
  int duration;
  //ultrasound distance detection variables
  long US_duration; // US: ultra-sound
  int US_distance;
  bool critical_distance;
  // instruction variables
  char instruction; // for incoming serial data



void setup() {
  // put your setup code here, to run once:
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps

}

void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}

int measure_distance(){
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
  //Serial.println(US_distance);
  return US_distance;
}

void drive(int direction, int turn, int speed, int duration){
  if (direction == 1){
    forw = true;
    back = false;
    right = false;
    left = false;
    stop = false;
  }
  if (direction == 2){
    forw = false;
    back = true;
    right = false;
    left = false;
    stop = false;
  }
  if (turn == 1){
    forw = false;
    back = false;
    right = true;
    left = false;
    stop = false;
  }
  if (turn == 2){
    forw = false;
    back = false;
    right = false;
    left = true;
    stop = false;
  }
  if ((direction == 0) && (turn == 0)){
    forw = false;
    back = false;
    right = false;
    left = false;
    stop = true; 
  }

  // running
  analogWrite(speedRight, speed);
  analogWrite(speedLeft, speed);
  if (right == true){ // TURNING TO THE RIGHT
    digitalWrite(forwRight, LOW);
    digitalWrite(forwLeft, HIGH);
    digitalWrite(backRight, HIGH);
    digitalWrite(backLeft, LOW);
  }
  if (left == true){ // TURNING TO THE LEFT
    digitalWrite(forwRight, HIGH);
    digitalWrite(forwLeft, LOW);
    digitalWrite(backRight, LOW);
    digitalWrite(backLeft, HIGH);
  }
  if (forw == true){ // MOVING FORWARD
    digitalWrite(forwRight, HIGH);
    digitalWrite(forwLeft, HIGH);
    digitalWrite(backRight, LOW);
    digitalWrite(backLeft, LOW);
  }
  if (back == true){ // MOVING BACKWARDS
    digitalWrite(forwRight, LOW);
    digitalWrite(forwLeft, LOW);
    digitalWrite(backRight, HIGH);
    digitalWrite(backLeft, HIGH);
  }
  if (stop == true){ // MOVING BACKWARDS
    digitalWrite(forwRight, LOW);
    digitalWrite(forwLeft, LOW);
    digitalWrite(backRight, LOW);
    digitalWrite(backLeft, LOW);
  }
  delay(duration);
}

void rasp_drive(int US_distance){
  if (Serial.available() > 0) {
  // read the incoming byte:
  instruction = Serial.read();
  }
  else{
    instruction = 'v';
  }
  direction = 0;
  turn = 0;

  if (instruction == 'w'){
    direction = 2;
    turn = 0;
  }
  if (instruction == 's'){
    direction = 1;
    turn = 0;
  }
  if (instruction == 'a'){
    direction = 0;
    turn = 1;
  }
  if (instruction == 'd'){
    direction = 0;
    turn = 2;
  }
  if (instruction == 'v'){
    direction = 0;
    turn = 0;
  }
  if (US_distance > 0 && US_distance < 20){
    critical_distance = true;
    direction = 1;
    turn = 0;
    speed = 255;
    duration = 1000;
    serialFlush();
  }
  drive(direction = direction, turn = turn, speed=255, duration=500);
}

void loop() {
  // put your main code here, to run repeatedly:
  US_distance = measure_distance();
  rasp_drive(US_distance = US_distance);
  //drive (1, 0, 100, 500);
  //drive (2, 0, 100, 500);
  //drive (0, 1, 100, 500);
  //drive (0, 2, 100, 500);
}
