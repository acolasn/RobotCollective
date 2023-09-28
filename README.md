# RobotCollective
Robots talking to each other, chasing each other, running from each other

## Installation

The repo is now a python package that you can install by going to the RobotCollective directory and typing

`pip install -e .`

This is an interactive installation, so that the package will change whenever you pull the repo. If you include any dependencies, please put them in the requirements.txt file, so that any installations just install all the dependencies at once. 

To import the modules, follow this example:

`from speech.chat_commanding import openAI_driver`

## Non-python dependencies:

You need to install zbar to read QRs. You can do it by typing 

`sudo apt-get install libzbar0`

## tone
for audio  install scipy through apt-get, not pip 
`sudo apt-get install python3-scipy`


some commands you may want to consider for debugging, but should not be necessary
<!-- sudo apt-get update -->
<!-- sudo apt-get install portaudio19-dev -->
<!-- sudo apt-get install alsa-utils -->

## Collision detection rewiring

We changed pin11 in the arduino from the motor's `backRight` pin to the collision detector `echoPin`. `backRight` is now in pin7. If you re-upload `driving_from_rasp_pi.ino` to your arduino, make sure you remove the cable from pin11 and put it on pin7. 

Connect the collision detector echoPin to pin11 and the trigPin to pin6. Connect its 5V to the 5V of the Arduino, and its 0V to the ground of the arduino. You should end up with:

``````

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

