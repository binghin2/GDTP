import time
from rpi_ws281x import PixelStrip, Color

# LED 설정
LED_COUNT = 30         # LED 개수
LED_PIN = 18           # GPIO 번호 (PWM 가능한 GPIO 18)
LED_FREQ_HZ = 800000   # WS2812 규격 주파수
LED_DMA = 10
LED_BRIGHTNESS = 255   # 0~255
LED_INVERT = False
LED_CHANNEL = 0

# PixelStrip 객체 생성
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT,
                   LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# 모든 LED를 빨간색으로 설정
for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(255, 0, 0))  # Color(R,G,B)
strip.show()
