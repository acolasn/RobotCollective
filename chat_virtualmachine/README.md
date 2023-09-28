## Robot Audio Generation with Google Text-to-Speech

In order to be able to use Google TTS, you need access to my credentials for my Google Cloud account. They are in the file application_default_credentials.json. You need to go into your .config folder, create a folder called gcloud, and add the json file to it. From the command line, you can:

`cd`

`cd .config`

`mkdir gcloud`

`cp ~/RobotCollective/application_default_credentials.json ~/.config/gcloud`

Then, you also need to install Google Text-to-Speech and pydub (this allows you to concatenate the tones and the ChatGPT output).

`pip install --upgrade google-cloud-texttospeech`

`pip install pydub`