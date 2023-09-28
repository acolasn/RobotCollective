import io
import logging
import socketserver
from http import server
from threading import Condition
import time

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from io import BytesIO
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
from utils import Timer, read_qr_code_from_PIL, calculate_distance_of_qr

PAGE = """\
<html>
<head>
<title>NB3 Camera Streaming</title>
</head>
<body>
<h1>Hi from NB3!</h1>
<img src="stream.mjpg" width="1280" height="720" />
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        qr_cache = np.zeros((30, ))
        qr_cache[:] = np.nan
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with Timer() as t:
                        with output.condition:
                            output.condition.wait()
                            frame = output.frame
                        frame_pil = Image.open(BytesIO(frame))
                        qr_decode_output, returning_points = read_qr_code_from_PIL(frame_pil)
                        print(qr_decode_output)
                        try:
                            center_x = (returning_points[0].x + returning_points[2].x)/2
                            center_y = (returning_points[0].y + returning_points[2].y)/2
                            area = (returning_points[2].x - returning_points[0].x) * (returning_points[2].y - returning_points[0].y)
                            distance = calculate_distance_of_qr(area, "poly")
                            print("CENTER x:", center_x)
                            print("CENTER y", center_y)
                            print("AREA: ", area)
                            print("DISTANCE: ", distance)
                        except:
                            print(None)
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                    print('Above operation took %f sec.' % (t.interval))
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def streaming_detecting_qr(q_qr):
    picam2 = Picamera2()
    camera_config = picam2.create_video_configuration(main={"size": (640, 480)}, lores={"size": (320,240)}, encode="lores")
    picam2.configure(camera_config)
    output = StreamingOutput()
    picam2.start_recording(MJPEGEncoder(), FileOutput(output))
    
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        picam2.stop_recording()
