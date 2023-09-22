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
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            return obj.data.decode('utf-8')
    return None
