import serial
import time
import curses
import queue

def chat_driver(q):

    ser = serial.Serial('/dev/ttyUSB0', 9600)  # Change '/dev/ttyUSB0' to your specific port

    while True:
        command = q.get()
        print(command)
        commands = extract_characters(command)
        for char in commands:
            print(char)
            if char == 'w':
                ser.write(b'w')  # Send byte to Arduino
            elif char == 's':
                ser.write(b's')
            elif char == 'a':
                ser.write(b'a')
            elif char == 'd':
                ser.write(b'd')

def extract_characters(s):
    # Check if the string starts with '[' and ends with ']'
    if s.startswith('[') and s.endswith(']'):
        # Extract the characters between the square brackets and convert them to a list of strings
        return list(s[1:-1])
    else:
        return []


