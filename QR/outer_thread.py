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

from queue import Queue
import threading
from main import run_qr_detection

main_queue = Queue()
QR_queue = Queue()
motor_queue = Queue()
speech_queue = Queue()

run_main = lambda x: x
run_speech = lambda x: x

main_thread = threading.Thread(target=run_main, args=(QR_queue,))
qr_thread = threading.Thread(target=run_qr_detection, args=(QR_queue,))
speech_thread = threading.Thread(target=run_speech, args=(speech_queue,))

qr_thread.start()