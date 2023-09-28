import os
import time
import openai
import numpy as np
import curses
from pydub import AudioSegment
from google.cloud import texttospeech
import speech.libs.NBB_sound as sound
import importlib
importlib.reload(sound)
import json 
import time
from pathlib import Path

def find_wav_file(json_filename, search_folder):
    """
    Reads a .json file to get the value of 'identity', searches for the .wav file
    containing the identity in its name within a specified folder, and returns the
    path to the .wav file.
    
    :param json_filename: Name of the .json file in the main folder.
    :param search_folder: Name of the folder to search for the .wav file.
    :return: Path to the .wav file, or None if not found.
    """
    # Construct the path to the JSON file
    json_path = Path(json_filename)
    
    # Check if the JSON file exists
    if not json_path.is_file():
        print(f"{json_filename} does not exist.")
        return None
    
    # Read the JSON file and get the value of 'identity'
    with json_path.open('r') as f:
        data = json.load(f)
        identity = data.get('identity')
    
    # Check if 'identity' is not found in the JSON file
    if not identity:
        print(f"'identity' not found in {json_filename}")
        return None
    
    # Construct the path to the search folder
    folder_path = Path(search_folder)
    
    # Check if the search folder exists
    if not folder_path.is_dir():
        print(f"{search_folder} does not exist.")
        return None
    
    # Search for the .wav file containing the identity in its name
    for file in folder_path.glob('**/*.wav'):
        if identity in file.name:
            return file
    
    # If the .wav file is not found, return None
    print(f".wav file containing '{identity}' not found in {search_folder}")
    return None

def get_extra_prompt():
    json_path = Path("robot_config.json")
    with json_path.open('r') as f:
        data = json.load(f)
        extra_prompt = data.get('get_extra_prompt')
    return extra_prompt

response_format = [
    {
      "name": "talk_and_move_as_a_robot",
      "description": "Say whatever you want aloud and provide a motor output",
      "parameters": {
        "type": "object",
        "properties": {
          "text": {
            "type": "string",
            "description": "What you want to say out loud"
          },
          "motor_commands": {
            "type": "string",
            "description": "A string composed of the characters w (forward), a (turn left), s (go backwards) and d (turn right)"
          },
          "bool_leave": {
            "type": "string",
            "description": "Whether to end the conversation.",
            "enum": ["yes", "no"]
          },
          "friendship_score": {
            "type": "string",
            "description": ""
          }
        }
      }
    }
]

def openAI_driver_function(data_queue, qr_queue, recorded_audio_queue, command_queue):

    # Get user name
    username = os.getlogin()

    # Specify paths
    repo_path = '/home/' + username + '/RobotCollective'
    box_path = repo_path + '/chat_virtualmachine'
    output_wav_path = box_path + '/_tmp/output.wav'
    tone_path = str(find_wav_file(json_filename = "robot_config.json", search_folder = "tone_recognition/tone_lib"))
    
    # Specify params
    input_device = 1
    output_device = 1
    num_input_channels = 2
    num_output_channels = 1
    sample_rate = 96000
    buffer_size = int(sample_rate / 100)
    buffer_size = int(sample_rate / 100)
    max_samples = int(sample_rate * 10)

    # List available sound devices
    sound.list_devices()

    # Instantiates a Google TTS client
    google_tts_client = texttospeech.TextToSpeechClient()

    # Initialize speaker
    speaker = sound.speaker(output_device, num_output_channels, 'int16', sample_rate, buffer_size)
    speaker.start()

    # Clear error ALSA/JACK messages from terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    # Set OpenAI API Key (secret!!!)
    openai.api_key = "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"

    # Initialize conversation history
    conversation = [
        # {"role": "system", "content": "You are in control of a two wheeled robot body. You can reply in a very specific format and ONLY in a very specific format. Your reply has two parts: text that I can hear and motor commands that get passed to the motor. FOR THE TEXT PART: Write your response in English, after a hash. After your response, write three hashes. For example: ###Hi, I am chatgpt###. FOR THE MOTOR PART: Reply to my instructions JUST with letters in square brackets. Provide motor commands as a list of the following letters: w, a, s, d, where w is forward, a is to the left, s is backwards and d is to the right. For example, if I tell you to turn left and then go forward, you must reply ONLY [aw].  An example of a complete response tto go forward is: #I'm going forward#[w]. Do you understand clearly? Note that you don't have to move if you don't feel like it. To do that, return an empty bracket."},
        {"role": "system", "content": "You are in control of a two-wheeled robot body. You can say things out loud and also provide motor commands. Sometimes, you will see other robots: you want to approach them and interact with them. When you see other robots, you will get data. These data will come in the form of length 3 tuples. These will be of the form (id, distance, x_deviation). If the distance is greater than 25, move forward. If it is less than 15, move backward. If it is in between 15 and 25, don't move forward or backward. If the x_deviation is less than -10, turn to the left. If the x_deviation is larger than +10, turn right. From now on, I will send you tuples in the form (id, distance, x_deviation) and you should respond with a series of motor commands. Do you understand clearly? Note that you don't have to move if you don't feel like it, but you should explain that this is the reason you are not moving. Going forward once is roughly 23 cm: try to stay at 20 cm of your target. Your visual field is 50 degrees and turning is about 20 degrees of turn. Try to always face your target. If you feel lost because there is no visual information, you should go into lost mode by sending the character l as a motor command. Please, always provide something in motor command, even if it is an empty string, and try not to remain still when there is notthing around. Just enter lost mode!"+str(get_extra_prompt())}, 
    ]

    # Setup the curses screen window
    screen = curses.initscr()    
    # ---------------------------------------------------------------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------
    # Chat Loop
    # --------------------------------------------------------------------------------
    try:
        while True:
            if command_queue.queue[-1] == 'SEARCH':
                screen.addstr("Enter a string: ")
                screen.clrtoeol()
                curses.echo()  # Enable echoing of characters
                # command = screen.getstr().decode('utf-8')  # Get a string from user
                if len(qr_queue.queue)>0:
                    command = qr_queue.queue[-1]
                    command_queue.put("INITIATE_CONVERSATION")
                else:
                    command = "There is no QR code yet."
                # while not qr_queue.queue.empty():
                qr_queue.queue.clear()
                screen.addstr(4, 0, "You: {0}\n".format(command), curses.A_STANDOUT)

                conversation.append({'role': 'user', 'content': f'{command}'})
                
                # Get ChatGPT response
                response = openai.ChatCompletion.create(
                    model="gpt-4-0613",
                    temperature=0.2,
                    messages=conversation, 
                    functions = response_format,
                    function_call= {"name":"talk_and_move_as_a_robot"}
                )
                # Extract and display reply
                if response_message.get("function_call"):
                    #print("OH THERE IS A FUNCTION CALL")
                    #print(response_message.get("function_call"))
                    #print(response["choices"][0]["message"]["function_call"]["arguments"])
                    uncleaned_response = response["choices"][0]["message"]["function_call"]["arguments"]
                    cleaned_response_str = uncleaned_response.replace("'", '"')
                    #print('cleaned_response_str: {0}'.format(cleaned_response_str))
                    reply = json.loads(cleaned_response_str)
                    #print(reply)
                    data_queue.put(reply)


                #reply = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])
                conversation.append({'role': 'assistant', 'content': f'{reply}'})
                #data_queue.put(reply)

                speech = reply["text"]
                # Synthesize reply
                synthesis_input = texttospeech.SynthesisInput(text=speech)
                voice = texttospeech.VoiceSelectionParams(language_code="en-GB", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
                audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=44100)
                response = google_tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
                with open(output_wav_path, "wb") as out:
                    out.write(response.audio_content)
                
                speaker.play_wav(output_wav_path)
                screen.addstr(8, 0, "NB3: {0}\n".format(speech), curses.A_NORMAL)
                while speaker.is_playing():
                    time.sleep(0.1)
                screen.refresh()
            
            if command_queue.queue[-1] == 'SPEAK':
                what_i_heard = recorded_audio_queue.queue[-1]
                conversation.append({'role': 'user', 'content': f'{what_i_heard}'})

                # Get ChatGPT response
                response = openai.ChatCompletion.create(
                    model="gpt-4-0613",
                    temperature=0.2,
                    messages=conversation, 
                    functions = response_format,
                    function_call= {"name":"talk_and_move_as_a_robot"}
                )

                response_message = response.choices[0].message
                if response_message.get("function_call"):
                    reply = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])
                    if reply.get("bool_leave"):
                        if reply["bool_leave"] == "yes":
                            command_queue.put("SEARCH")
                conversation.append({'role': 'assistant', 'content': f'{reply}'})

                speech = reply["text"]
                synthesis_input = texttospeech.SynthesisInput(text=speech)
                voice = texttospeech.VoiceSelectionParams(language_code="en-GB", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
                audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=44100)
                response = google_tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
                with open(output_wav_path, "wb") as out:
                    out.write(response.audio_content)

                tone = AudioSegment.from_file(tone_path)
                output = AudioSegment.from_file(output_wav_path)
                combined = tone + output + tone
                combined.export(output_wav_path, format="wav")
                speaker.play_wav(output_wav_path)
                screen.addstr(8, 0, "NB3: {0}\n".format(speech), curses.A_NORMAL)
                while speaker.is_playing():
                    time.sleep(0.1)
                screen.refresh()
            
            if command_queue.queue[-1] == "INITIATE_CONVERSATION":
                speech = "Hello, this is a robot talking. How are you doing?"
                synthesis_input = texttospeech.SynthesisInput(text=speech)
                voice = texttospeech.VoiceSelectionParams(language_code="en-GB", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
                audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=44100)
                response = google_tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
                with open(output_wav_path, "wb") as out:
                    out.write(response.audio_content)

                tone = AudioSegment.from_file(tone_path)
                output = AudioSegment.from_file(output_wav_path)
                combined = tone + output + tone
                combined.export(output_wav_path, format="wav")
                speaker.play_wav(output_wav_path)
                screen.addstr(8, 0, "NB3: {0}\n".format(speech), curses.A_NORMAL)
                while speaker.is_playing():
                    time.sleep(0.1)
                screen.refresh()
                command_queue.put("LISTEN")

    finally:
        # Shutdown microphone
        # microphone.stop()

        # Shutdown speaker
        speaker.stop()

        # Shutdown curses

        curses.nocbreak()
        screen.keypad(0)
        curses.echo()
        curses.endwin()
    # FIN