'''
This is the code to read collisions from the arduino. It 
still does not put anything into a queue. 
'''

import serial
ser = serial.Serial('/dev/ttyUSB0',9600)
while True:
    read_serial=ser.readline().decode().strip()
    #print(read_serial)
    if read_serial == "c":
        print("Ouch, that hurt!")
