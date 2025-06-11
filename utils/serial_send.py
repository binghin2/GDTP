import serial
import time

def send_serial_command(command="PLAY\n", port="/dev/ttyUSB0", baudrate=9600):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            time.sleep(2)  # 포트 안정화
            ser.write(command.encode('utf-8'))
    except serial.SerialException as e:
        print("Serial communication error:", e)
