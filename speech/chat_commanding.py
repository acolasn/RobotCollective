import openai
import pyttsx3
import pyaudio
import curses
import queue
import numpy as np

def openAI_driver(q):
    if not q.empty():
        print("CHAT COMMAND: ", q.queue[-1])
    # Set OpenAI API Key (secret!!!)
    openai.api_key = "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"

    # Initialize conversation history
    conversation = [
        # {"role": "system", "content": "You are in control of a two wheeled robot body. You can reply in a very specific format and ONLY in a very specific format. Your reply has two parts: text that I can hear and motor commands that get passed to the motor. FOR THE TEXT PART: Write your response in English, after a hash. After your response, write three hashes. For example: ###Hi, I am chatgpt###. FOR THE MOTOR PART: Reply to my instructions JUST with letters in square brackets. Provide motor commands as a list of the following letters: w, a, s, d, where w is forward, a is to the left, s is backwards and d is to the right. For example, if I tell you to turn left and then go forward, you must reply ONLY [aw].  An example of a complete response tto go forward is: #I'm going forward#[w]. Do you understand clearly? Note that you don't have to move if you don't feel like it. To do that, return an empty bracket."},
        {"role": "system", "content": "You are in control of a two wheeled robot body. You can reply in a very specific format and ONLY in a very specific format. Your reply has two parts: text that I can hear and motor commands that get passed to the motor. FOR THE TEXT PART: Write your response in English, after a hash. After your response, write three hashes. For example: ###Hi, I am chatgpt###. FOR THE MOTOR PART: Reply to my instructions JUST with letters in square brackets. Provide motor commands as a list of the following letters: w, a, s, d, where w is forward, a is to the left, s is backwards and d is to the right. For example, if I tell you to turn left and then go forward, you must reply ONLY [aw].  An example of a complete response tto go forward is: #I'm going forward#[w]. If you are given a distance and rotation information, please move accordingly. For example, if you are told that the rotation is left, you may want to move left. If the distance is 60, you may want to move forward. If the distance is 30, you may want to stay still. If the distance is away and the rotation is left, you may want to move forward and then left. Do you understand clearly? Note that you don't have to move if you don't feel like it. To do that, return an empty bracket."},
    ]

    # Initialize speech engine
    engine = pyttsx3.init()

    # Set sound recording format
    CHUNK = 1600                # Buffer size
    FORMAT = pyaudio.paInt32    # Data type
    CHANNELS = 1                # Number of channels
    RATE = 16000                 # Sample rate (Hz)
    MAX_DURATION = 5            # Max recording duration
    WAVE_OUTPUT_FILENAME = "speech.wav"

    # Setup the curses screen window
    screen = curses.initscr()

    
    # ---------------------------------------------------------------------------------------------------------------------------------------------------


    # --------------------------------------------------------------------------------
    # Chat Loop
    # --------------------------------------------------------------------------------
    try:
        while True:

            screen.addstr("Enter a string: ")
            screen.clrtoeol()
            curses.echo()  # Enable echoing of characters
            command = screen.getstr().decode('utf-8')  # Get a string from user

            screen.addstr(4, 0, "You: {0}\n".format(command), curses.A_STANDOUT)

            conversation.append({'role': 'user', 'content': f'{command}'})
            
            # Get ChatGPT response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=0.2,
                messages=conversation
            )

            # Extract and display reply
            reply = response['choices'][0]['message']['content']
            conversation.append({'role': 'assistant', 'content': f'{reply}'})
            q.put(reply)
            # Speak reply
            engine.say(ext_chr_string(reply))
            engine.runAndWait()
            # try:
            screen.addstr(7, 0, "NB3: {0}\n".format(reply), curses.A_NORMAL)
            # except curses.error:
            #     pass
            screen.refresh()

    finally:
        # shut down

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