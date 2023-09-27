import os
import sys
import time
import openai
import numpy as np
import curses
import pyttsx3
import requests
import random

def openAI_driver(q):

    # Locals libs
    import libs.NBB_sound as sound

    # Reimport
    import importlib
    importlib.reload(sound)

    # Get user name
    username = os.getlogin()

    # Specify paths
    repo_path = '/home/' + username + '/RobotCollective'
    box_path = repo_path + '/chat_virtualmachine'
    input_wav_path = box_path + '/_tmp/input.wav'
    output_wav_path = box_path + '/_tmp/output.wav'

    # Specify params
    input_device = 1
    output_device = 1
    num_input_channels = 2
    num_output_channels = 1
    sample_rate = 16000
    buffer_size = int(sample_rate / 100)
    buffer_size = int(sample_rate / 100)
    max_samples = int(sample_rate * 10)

    # List available sound devices
    sound.list_devices()

    # Initialize microphone
    microphone = sound.microphone(input_device, num_input_channels, 'int32', sample_rate, buffer_size, max_samples)
    microphone.start()

    # Initialize speaker
    speaker = sound.speaker(output_device, num_output_channels,  'int16', sample_rate, buffer_size)
    speaker.start()

    # Clear error ALSA/JACK messages from terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    # Set OpenAI API Key (secret!!!)
    openai.api_key = "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"

    # Initialize conversation history
    conversation = [
        {"role": "system", "content": "You are in control of a two wheeled robot body. You can reply in a very specific format and ONLY in a very specific format. Your reply has two parts: text that I can hear and motor commands that get passed to the motor. FOR THE TEXT PART: Write your response in English, after a hash. After your response, write a hash. For example: #Hi, I am chatgpt#. FOR THE MOTOR PART: Reply to my instructions JUST with letters in square brackets. Provide motor commands as a list of the following letters: w, a, s, d, where w is forward, a is to the left, s is backwards and d is to the right. For example, if I tell you to turn left and then go forward, you must reply ONLY [aw].  An example of a complete response tto go forward is: #I'm going forward#[w]. Do you understand clearly? Note that you don't have to move if you don't feel like it. To do that, return an empty bracket. You must return brackets every time."},
    ]

    # Initialize speech engine
    engine = pyttsx3.init()

    # Setup the curses screen window
    screen = curses.initscr()    
    # ---------------------------------------------------------------------------------------------------------------------------------------------------


    # --------------------------------------------------------------------------------
    # Chat Loop
    # --------------------------------------------------------------------------------
    try:
        while True:

            # Wait to start talking
            screen.addstr(0, 0, "Press 'z' to talk to your NB3 ('q' to quit):")
            curses.echo()  # Enable echoing of characters
            screen.clrtoeol()
            while True:
                char = screen.getch()
                if char == ord('q'):
                    sys.exit()
                elif char == ord('z'):
                    break

            # Start recording
            screen.addstr("...press 'z' again to stop speaking.", curses.A_UNDERLINE)
            microphone.reset()
            while True:
                char = screen.getch()
                if char == ord('q'):
                    sys.exit()
                elif char == ord('z'):
                    break
            screen.erase()        
            microphone.save_wav(input_wav_path, max_samples)

            # Get transcription from Whisper
            audio_file= open(input_wav_path, "rb")
            transcription = openai.Audio.transcribe("whisper-1", audio_file)['text']
            conversation.append({'role': 'user', 'content': f'{transcription}'})
            screen.addstr(4, 0, "You: {0}\n".format(transcription), curses.A_STANDOUT)
            screen.refresh()

            # Get ChatGPT response
            response = openai.ChatCompletion.create(
                model="gpt-4",
                temperature=0.2,
                messages=conversation
            )

            # Extract and display reply
            reply = response['choices'][0]['message']['content']
            conversation.append({'role': 'assistant', 'content': f'{reply}'})
            q.put(reply)

            # Speak reply
            speech = ext_chr_string(reply)
            
            url = 'http://34.22.159.200:5000/convert'
            try:
                response = requests.post(url, data={'text': speech})
            except:
                amt = random.uniform(0,0.1)
                time.sleep(amt)
                response = requests.post(url, data={'text': speech})
            with open(output_wav_path, 'wb') as f:
                f.write(response.content)

            speaker.play_wav(output_wav_path)
            screen.addstr(8, 0, "NB3: {0}\n".format(reply), curses.A_NORMAL)
            while speaker.is_playing():
                time.sleep(0.1)
            screen.refresh()

    finally:
        # Shutdown microphone
        microphone.stop()

        # Shutdown speaker
        speaker.stop()

        # Shutdown curses

        curses.nocbreak()
        screen.keypad(0)
        curses.echo()
        curses.endwin()
    # FIN

def ext_chr_string(string):
    chars = [*string]
    chars= np.asarray(chars)
    hashes = np.where(chars == '#')[0]
    speech = chars[hashes[0]+1:hashes[1]]
    speechstring = ""
    for i in speech:
        i = str(i)
        speechstring = speechstring+i
    return speechstring