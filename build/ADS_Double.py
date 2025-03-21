import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads7830.ads7830 as ADC
import RPi.GPIO as IO
from ledIO import LED_IO

# ADS1115 INITIALISATION
i2c = busio.I2C(board.SCL, board.SDA)
leds = LED_IO('bcm', 37)

adc1 = ADS.ADS1115(address=0x49, i2c=i2c)

channels = [AnalogIn(adc1,ADS.P0),AnalogIn(adc1,ADS.P1),
AnalogIn(adc1,ADS.P2),AnalogIn(adc1,ADS.P3)]

adc = ADC.ADS7830(i2c)
REF = 4.2
leds.on()

while True: 	
	v_s1 = []
	for ele in channels:
		v = round(ele.voltage,3)
		v_s1.append(v)
	channels2 = [adc.read(i) for i in range(8)]
	v_s2 = [round((ch / 65535.0) * REF,3) for ch in channels2]
	print(v_s1)
	print(v_s2)
	time.sleep(2)

leds.off()
