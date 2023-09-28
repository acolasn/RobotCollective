import openai
import pyttsx3
import pyaudio
import curses
import queue
import numpy as np

def openAI_driver(data_queue, qr_queue):
    # Set OpenAI API Key (secret!!!)
    openai.api_key = "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"

    # Initialize conversation history
    conversation = [
        # {"role": "system", "content": "You are in control of a two wheeled robot body. You can reply in a very specific format and ONLY in a very specific format. Your reply has two parts: text that I can hear and motor commands that get passed to the motor. FOR THE TEXT PART: Write your response in English, after a hash. After your response, write three hashes. For example: ###Hi, I am chatgpt###. FOR THE MOTOR PART: Reply to my instructions JUST with letters in square brackets. Provide motor commands as a list of the following letters: w, a, s, d, where w is forward, a is to the left, s is backwards and d is to the right. For example, if I tell you to turn left and then go forward, you must reply ONLY [aw].  An example of a complete response tto go forward is: #I'm going forward#[w]. Do you understand clearly? Note that you don't have to move if you don't feel like it. To do that, return an empty bracket."},
        {"role": "system", "content": "You are in control of a two wheeled robot body. You can reply in a very specific format and ONLY in a very specific format. Your reply has two parts: text that I can hear and motor commands that get passed to the motor. FOR THE TEXT PART: Write your response in English, after a hash. After your response, write three hashes. For example: #Hi, I am chatgpt#. FOR THE MOTOR PART: Reply to my instructions JUST with letters in square brackets. Provide motor commands as a list of the following letters: w, a, s, d, where w is forward, a is to the left, s is backwards and d is to the right. For example, if I tell you to turn left and then go forward, you must reply ONLY [aw].  An example of a complete response tto go forward is: #I'm going forward#[w]. Your goal is to approach another robot using data about its distance and angle from the center of your field of view. These data will come in the form of length 3 tuples. These will be of the form (id, distance, x_deviation). If the distance is greater than 25, move forward. If it is less than 15, move backward. If it is in between 15 and 25, don't move forward or backward. If the x_deviation is less than -10, turn to the right. If the x_deviation is larger than +10, turn left. From now on, I will send you tuples in the form (id, distance, x_deviation) and you should respond with a series of motor commands. Do you understand clearly? Note that you don't have to move if you don't feel like it. To do that, return an empty bracket. Going forward once is roughly 23 cm: try to stay at 10 cm of your target. Your visual field is 50 degrees and turning is about 20 degrees of turn. Try to always face your target. If you feel lost because there is no visual information, you can toggle on lost moode by sending an l motor command. For example: #Better start looking!#[l]. Once you are in lost mode, there is no need to send the l command again"}, 
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
            # command = screen.getstr().decode('utf-8')  # Get a string from user
            if len(qr_queue.queue)>0:
                command = qr_queue.queue[-1]
            else:
                command = "There is no qr code yet"
            # while not qr_queue.queue.empty():
            qr_queue.queue.clear()
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
            data_queue.put(reply)
            print(reply)
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