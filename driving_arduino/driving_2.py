import serial
import time
import curses

ser = serial.Serial('/dev/ttytUSB0', 9600)  # Change '/dev/ttyUSB0' to your specific port

#Setup the curses screen interface

# Setup the curses screen window
screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.nodelay(True)

while True:
    char = screen.getch()
    if char == ord('w'):
        print("Moving Forward")
        ser.write(b'w')  # Send byte to Arduino
    elif char == ord('s'):
        print("Moving Backward")
        ser.write(b's')
    elif char == ord('a'):
        print("Turning Left")
        ser.write(b'a')
    elif char == 'd':
        print("Turning Right")
        ser.write(b'd')
    elif char == 'q':
        break
    else:
        print('Invalid command')

