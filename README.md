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

for audio  install scipy through apt-get, not pip 
`sudo apt-get install python3-scipy`


some commands you may want to consider for debugging, but should not be necessary
<!-- sudo apt-get update -->
<!-- sudo apt-get install portaudio19-dev -->
<!-- sudo apt-get install alsa-utils -->
