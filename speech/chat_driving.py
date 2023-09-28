import serial
import time
import curses
import queue
import numpy as np

def chat_driver(q, command_queue):

    ser = serial.Serial('/dev/ttyUSB0', 9600)  # Change '/dev/ttyUSB0' to your specific port

    while True:
        if command_queue.queue[-1] == "SEARCH":
            command = q.get()
            command = command['motor_commands']
            print("QUEUE:", command)
            commands = [*command]
            for char in commands:
                print(f"THIS IS THE COMMAND: {char}")
                if char == 'w':
                    ser.write(b'w')  # Send byte to Arduino
                elif char == 's':
                    ser.write(b's')
                elif char == 'a':
                    ser.write(b'a')
                elif char == 'd':
                    ser.write(b'd')
                elif char == 'l':
                    ser.write(b'l')

def extract_characters(s):
    # Check if the string starts with '[' and ends with ']'
    if s.startswith('[') and s.endswith(']'):
        # Extract the characters between the square brackets and convert them to a list of strings
        return list(s[1:-1])
    else:
        return []

def ext_chr_motor(string):
    chars = [*string]
    chars= np.asarray(chars)
    hashes = np.where(chars == '#')[0]
    speech = chars[hashes[0]+1:hashes[1]]

    front_brack = np.where(chars == '[')[0][0]
    back_brack = np.where(chars == ']')[0][0]
    motor = chars[front_brack+1:back_brack]
    return motor

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

