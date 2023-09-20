  int speedRight = 9;
  int speedLeft = 3;
  int forwLeft = 4;
  int forwRight = 10;
  int backLeft = 5;
  int backRight = 11;
  int speed;
  bool right;
  bool left;
  bool forw;
  bool back;
  int direction;
  int tur
  int duration;

  char instruction; // for incoming serial data


void setup() {
  // put your setup code here, to run once:
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps

}

void drive(int direction, int turn, int speed, int duration){
  if (direction == 1){
    forw = true;
    back = false;
    right = false;
    left = false;
  }
  if (direction == 2){
    forw = false;
    back = true;
    right = false;
    left = false;
  }
  if (turn == 1){
    forw = false;
    back = false;
    right = true;
    left = false;
  }
  if (turn == 2){
    forw = false;
    back = false;
    right = false;
    left = true;
  }

  // running
  analogWrite(speedRight, speed);
  analogWrite(speedLeft, speed);
  if (right == true){ // TURNING TO THE RIGHT
    left == false;
    digitalWrite(forwRight, LOW);
    digitalWrite(forwLeft, HIGH);
    digitalWrite(backRight, HIGH);
    digitalWrite(backLeft, LOW);
  }
  if (left == true){ // TURNING TO THE LEFT
    right== false;
    digitalWrite(forwRight, HIGH);
    digitalWrite(forwLeft, LOW);
    digitalWrite(backRight, LOW);
    digitalWrite(backLeft, HIGH);
  }
  if (forw == true){ // MOVING FORWARD
    back== false;
    digitalWrite(forwRight, HIGH);
    digitalWrite(forwLeft, HIGH);
    digitalWrite(backRight, LOW);
    digitalWrite(backLeft, LOW);
  }
  if (back == true){ // MOVING FORWARD
    forw== false;
    digitalWrite(forwRight, LOW);
    digitalWrite(forwLeft, LOW);
    digitalWrite(backRight, HIGH);
    digitalWrite(backLeft, HIGH);
  }
  delay(duration);
}

void rasp_drive(){
  if (Serial.available() > 0) {
  // read the incoming byte:
  instruction = Serial.read();
  }
  if (instruction == 'w'){
    direction = 1;
    turn = 0;
  }
    if (instruction == 's'){
    direction = 2;
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
  drive(direction = direction, turn=turn, speed=255, duration=500);
  direction = 0
  turn = 0
}

void loop() {
  // put your main code here, to run repeatedly:
  rasp_drive();
  //drive (1, 0, 100, 500);
  //drive (2, 0, 100, 500);
  //drive (0, 1, 100, 500);
  //drive (0, 2, 100, 500);
}
