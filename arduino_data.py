import serial

try:  
    arduino = serial.Serial('/dev/tty.usbmodem14301', 115200, timeout = 1)
except:
    print("check port")

rawdata =[]
count = 0

while count < 10000:
    print(arduino.readline().strip()) 
    count += 1

print(rawdata)