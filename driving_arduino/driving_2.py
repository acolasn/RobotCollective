import serial
import time
import curses

ser = serial.Serial('/dev/ttyUSB0', 9600)  # Change '/dev/ttyUSB0' to your specific port

#Setup the curses screen interface

# Setup the curses screen window
screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.nodelay(True)

while True:
    char = screen.getch()
    if char == ord('w'):
        ser.write(b'w')  # Send byte to Arduino
    elif char == ord('s'):
        ser.write(b's')
    elif char == ord('a'):
        ser.write(b'a')
    elif char == 'd':
        ser.write(b'd')

