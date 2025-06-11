import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 9600)
time.sleep(2)  # 시리얼 포트 안정화 대기

ser.write(b'PLAY\n')
ser.close()
