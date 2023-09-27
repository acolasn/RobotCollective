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

int previousMillis = 0;
int currentMillis;

int state = 0;
bool input;

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
  previousMillis = millis();
  duration = 1000;
  randomSeed(analogRead(0));
}

void drive(int direction, int turn, int speed){
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

int define_Levy_duration(){
  // Define your list (array)
  float Levy[] = {
    3465.17028, 1007.77986, 866.078642, 691.339405,
    1387.53641, 1274.71687, 2115.08719, 1240.61066,
    12778.2832, 2541.73792, 14134.6460, 1273.41625,
    12133.703, 1354.78531, 2649.40816, 273.131518,
    1234.48219, 10238.5817, 8488.8231, 12349.1826,
    816.455628, 2905.39032, 20762.8227, 2203.52042,
    862.021999, 4087.85048, 599.677376, 6679.65616,
    7276.82035, 3621.94540, 2139.60993, 1665.81882,
    972.948340, 6842.68138, 2171.29900, 418.870449,
    1335.70559, 1918.88707, 578.060357, 1656.83842,
    4182.8625, 1321.78963, 1460.36116, 3288.3810,
    201.404831, 207.143045, 7606.09808, 3159.69027,
    12986.42, 279.323389
  };
  
  // Calculate the number of elements in the array
  int arraySize = sizeof(Levy) / sizeof(Levy[0]);
  
  // Generate a random index between 0 and arraySize - 1
  int randomIndex = random(arraySize);
  
  // Use the random index to access an element from the array
  int sampledValue = Levy[randomIndex];
  
  return sampledValue;
}

void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}

char read_instruction(){
  if (Serial.available() > 0) {
    // read the incoming byte:
    instruction = Serial.read();
  }
  else if(instruction != 'l'){
    instruction = 'v';
  }
  return instruction;
}

void lostMode(){
    switch (state) {
    case 0:
        drive(direction = 0, turn = 2, speed=150);
        duration = 2000;
        break;
    case 1:
        drive(direction = 2, turn = 0, speed=255);
        duration = define_Levy_duration();
        break;
    case 2:
        drive(direction = 0, turn = 1, speed=150);
        duration = 2000;
        break;
    case 3:
        drive(direction = 1, turn = 0, speed=150);
        duration = define_Levy_duration()/2;
        state = -1;
        break;
    }
    // Move to the next state in the sequence
    state++;
}

void drive_rasp_pi(){

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
    drive(direction = direction, turn = turn, speed = 255);
}

void loop(){
    currentMillis = millis();
    //instruction = read_instruction();

    //if (instruction == "s"){
    //drive(direction = 0, turn = 0, speed=255)
    //}
    instruction = read_instruction();
    if ((currentMillis-previousMillis) > duration){
       if (instruction == 'l'){
            //LOST MODE
            lostMode();
       }
        else{
            duration = 100;
            drive_rasp_pi();
        }
      previousMillis = millis();
    }

    US_distance = measure_distance();
    if (US_distance>0 && US_distance<10){
        drive(direction = 1, turn = 0, speed=255);
        delay(700);
        drive(direction = 0, turn = 0, speed=255);
        serialFlush();
        Serial.println("c");
    }
}