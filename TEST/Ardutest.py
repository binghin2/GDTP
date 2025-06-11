import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 9600)
time.sleep(2) # 아두이노 리셋 대기

try:
    while True:
        ser.write(b'1') # 아두이노로 '1' 명령 보내기 (LED 켜기)
        time.sleep(2) # 2초 대기
        ser.write(b'0') # 아두이노로 '0' 명령 보내기 (LED 끄기)
        time.sleep(2) # 2초 대기
except KeyboardInterrupt:
    ser.close() # 프로그램 종료시 시리얼 연결을 정상적으로 닫습니다.
