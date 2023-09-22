import io
import logging
import socketserver
from http import server
from threading import Condition
import time

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