## Robot Audio Generation with Google Text-to-Speech

In order to be able to use Google TTS, you need access to my credentials for my Google Cloud account. They are in the file application_default_credentials.json. You need to go into your .config folder, create a folder called gcloud, and add the json file to it. From the command line, you can:

``````
cd
cd .config
mkdir gcloud
cp ~/RobotCollective/application_default_credentials.json ~/.config/gcloud
``````

Then, you also need to install Google Text-to-Speech and pydub (this allows you to concatenate the tones and the ChatGPT output).

``````
pip install --upgrade google-cloud-texttospeech
pip install pydub
``````

You also have a specific tone that you play, which means you need to change tone_filename in line 27 of the code. 

These are your filenames:

``````
ANTONIO: antonio_tone_523.wav
ARYA: arya_tone_439.wav
BARISCAN: bariscan_tone_739.wav
CRIS: cris_tone_659.wav
FRANCESCA: francesca_tone_783.wav
MASAHIRO: masahiro_tone_830.wav
MEG: meg_tone_587.wav
ORSI: orsi_tone_698.wav
VASCO: vasco_tone_622.wav
VINCE: vince_tone_554.wav
``````