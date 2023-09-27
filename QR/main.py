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

from io import BytesIO
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
from typing import Optional

class Timer:
    """A simple timer class for performance profiling Taken from https://github.com/flat
    ironinstitute/online_psp/blob/master/online_psp/online_psp_simulations.py.

    Usage:
    with Timer() as t:
        DO SOMETHING HERE
    print('Above (DO SOMETHING HERE) took %f sec.' % (t.interval))
    """

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.interval = self.end - self.start

def image_to_byte_array(image: Image) -> bytes:
  # BytesIO is a file-like buffer stored in memory
  imgByteArr = io.BytesIO()
  # image.save expects a file-like as a argument
  image.save(imgByteArr, format="JPEG")
  # Turn the BytesIO object back into a bytes object
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

def read_qr_code(image_path: str) -> Optional[str]:
    """
    Reads a QR code from an image file.

    Args:
        image_path (str): The path to the image containing the QR code.

    Returns:
        Optional[str]: The decoded data from the QR code if found, or None if no QR code is detected.
    """
    image = Image.open(image_path)
    decoded_objects = decode(image)
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            return obj.data.decode('utf-8')
    return None


def read_qr_code_from_PIL(pil_image: Image.Image) -> Optional[str]:
    """
    Reads a QR code from a PIL Image.

    Args:
        pil_image (Image.Image): The PIL Image containing the QR code.

    Returns:
        Optional[str]: The decoded data from the QR code if found, or None if no QR code is detected.
    """
    decoded_objects = decode(pil_image)
    returning_qr = None
    returning_points = None
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            returning_qr = obj.data.decode('utf-8')
            returning_points = obj.polygon
            # return obj.data.decode('utf-8')
    return returning_qr, returning_points

def calculate_distance_of_qr(area, mode = "poly"):
    coefs_linear = np.array([-0.32297904, 69.71250129])
    coefs_poly = np.array([ 3.75838506e-03, -1.19422144e+00,  1.08565503e+02])
    area = abs(area)
    area_root = np.sqrt(area)
    distance = 250
    if mode == "poly":
        distance = coefs_poly[0] * area + coefs_poly[1] * area_root + coefs_poly[2]
    elif mode == "linear":
        distance = coefs_linear[0] * area_root + coefs_linear[1]
    if distance < 15:
        distance = 0
    return distance

def calculate_distance_qr_main_resolution(area):
    coefs_linear = np.array([-6.39270188e-04,  7.22677038e+01])
    area = abs(area)
    distance = coefs_linear[0] * area + coefs_linear[1]
    return distance

def create_my_logger(
    logger_level="INFO",
    logger_name="logger",
    create_logger_folder=True,
    logger_folder_name="Loggers",
):
    """Generate a logger file and returns the logger to use it in a python script.

    Args:
        logger_level (str, optional): Logging level. Please see: https://docs.python.org/3/library/logging.html#logging-levels.
                                      Defaults to "INFO".
        logger_name (str, optional): Logger file name. Defaults to "logger".
        create_logger_folder (bool, optional): If true, it creates a new folder to save the logger file. Defaults to True.
        logger_folder_name (str, optional): The name of the folder to keep the logger file if a new folder will be created.
                                             Defaults to "Loggers".

    Returns:
        _type_: Logger

    Example:
    >>> l = create_my_logger(logger_level = "INFO", logger_name = "logger",
                             create_logger_folder = True, logger_folder_name = "Loggers")
    >>> l.info("Here I am")
    """
    if create_logger_folder:
        if not os.path.exists(logger_folder_name):
            os.mkdir(logger_folder_name)
    logger = logging.getLogger(__name__)
    if logger_level == "INFO":
        logger.setLevel(logging.INFO)
    elif logger_level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif logger_level == "ERROR":
        logger.setLevel(logging.ERROR)
    elif logger_level == "CRITICAL":
        logger.setLevel(logging.CRITICAL)
    else:
        print(
            "Wrong logging level has been entered. Please try INFO, WARNING, ERROR, or CRITICAL."
        )

    formatter = logging.Formatter("%(asctime)s | | %(levelname)s | | %(message)s")
    logger_file_name = os.path.join(logger_folder_name, logger_name)
    file_handler = logging.FileHandler(logger_file_name, "w")

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

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

logger = create_my_logger(logger_name="qr_logger")
class StreamingHandler(server.BaseHTTPRequestHandler):
    def __init__(self, queue):
        super().__init__(self, request, client_address, server)
        self.queue = queue

    def do_GET(self):
        qr_cache = [None for _ in range(30)]
        readed_qr = False
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
                    # with Timer() as t:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    frame_pil = Image.open(BytesIO(frame))
                    qr_decode_output, returning_points = read_qr_code_from_PIL(frame_pil)

                    # print(qr_decode_output)
                    if qr_decode_output is not None:
                        frame_numpy = np.array(frame_pil)

                        center_x = (returning_points[0].x + returning_points[2].x)/2
                        center_y = (returning_points[0].y + returning_points[2].y)/2
                        area = (returning_points[2].x - returning_points[0].x) * (returning_points[2].y - returning_points[0].y)
                        # distance = calculate_distance_of_qr(area, "linear")
                        distance_of_qr = calculate_distance_qr_main_resolution(area)
                        qr_dict = {"qr_info": qr_decode_output, "distance": distance_of_qr, "center_x": center_x, "center_y": center_y}
                        qr_cache.append(qr_dict)
                        # logger.info("CENTER x: {}".format(center_x))
                        # logger.info("CENTER y {}".format(center_y))
                        # logger.info("AREA: {}".format(area))
                        # logger.info("DISTANCE: {}".format(distance))
                        # print("CENTER x: {}".format(center_x))

                        centroid = np.mean(np.array([[x['center_x'], x['center_y']] for x in qr_cache if x is not None]), axis = 0)
                        distance = np.mean([x['distance'] for x in qr_cache if x is not None])
                        queue.put(centroid)
                        # print(centroid)
                        # print(distance)
                        # print(qr_decode_output)
                        # print("AREA: {}".format(area))
                        frame_numpy[int(centroid[1]-10):int(centroid[1]+10),int(centroid[0]-10):int(centroid[0]+10),:] = 0
                        frame = image_to_byte_array(Image.fromarray(frame_numpy))
                        # print("CENTER y {}".format(center_y))
                        # print("AREA: {}".format(area))
                        # print("DISTANCE: {}".format(distance))
                        # print("Number of nans: {}".format(qr_cache.count(None)))
                    else:
                        qr_cache.append(None)
                        
                    qr_cache.pop(0)
                    # print("Number of nans: {}".format(qr_cache.count(None)))
                    if qr_cache.count(None) < 7:
                        readed_qr = True
                    else:
                        readed_qr = False
                    queue.put(centroid)
                    if readed_qr:
                        print(distance)
                        if distance > 30:
                            print("move forward")
                        if centroid[0] - 320 > 50:
                            print("move right")
                        elif centroid[0] - 320 < -50:
                            print("move left")
                        
                    # print(readed_qr)
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
                    # print('Above operation took %f sec.' % (t.interval))
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    def __init__(self, address, streaming_handler, queue=None):
        super().__init__(address, streaming_handler)
        self.queue = queue
    
    allow_reuse_address = True
    daemon_threads = True

picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"size": (640, 480)}, lores={"size": (320,240)}, encode="main")
picam2.configure(camera_config)
output = StreamingOutput()
picam2.start_recording(MJPEGEncoder(), FileOutput(output))

def run_qr_detection(queue):
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler, queue)
        server.serve_forever()
    finally:
        picam2.stop_recording()

if __name__ == "__main__":
    run_qr_detection()