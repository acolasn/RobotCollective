from PIL import Image
from pyzbar.pyzbar import decode

def read_qr_code(image_path):
    image = Image.open(image_path)
    decoded_objects = decode(image)
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            return obj.data.decode('utf-8')
    return None

# Example usage
image_path = 'test_qr.jpg'  # Replace with the path to your image file
result = read_qr_code(image_path)
if result:
    print(f"Decoded QR code: {result}")
else:
    print("No QR code found.")

'''
We need zbar. For MacOS: brew install zbar. For Debian:

sudo apt-get update
sudo apt-get install libzbar0
'''