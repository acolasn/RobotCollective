import io
import logging
import socketserver
from http import server
from threading import Condition
import time
import os
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from io import BytesIO
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import io
import logging
import socketserver
from http import server
from threading import Condition
import serial
from io import BytesIO
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
from typing import Optional

def ext_chr_motor(string):
    chars = [*string]
    chars= np.asarray(chars)
    hashes = np.where(chars == '#')[0]
    speech = chars[hashes[0]+1:hashes[1]]

    front_brack = np.where(chars == '[')[0][0]
    back_brack = np.where(chars == ']')[0][0]
    motor = chars[front_brack+1:back_brack]
    return motor

def chat_driver(command):

    ser = serial.Serial('/dev/ttyUSB0', 9600)  # Change '/dev/ttyUSB0' to your specific port

    while True:
        commands = ext_chr_motor(command)
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

print(ext_chr_motor("#move forward#[wd]"))
chat_driver("#move forward#[wd]")