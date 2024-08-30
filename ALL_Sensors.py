import time
from ds18b20 import DS18B20
from adafruit_bme280 import basic as adafruit_bme280
import board
import busio
import adafruit_ads1x15.ads1115 as ADS_1
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads7830.ads7830 as ADS_2
import adafruit_tca9548a
import RPi.GPIO as IO
import numpy as np
from tqdm import tqdm
from ledIO import LED_IO

# Setup the LEDs
leds = LED_IO('bcm', 38)

# MULTIPLEXER INITIALISATION
i2c = busio.I2C(board.SCL, board.SDA)
mux = adafruit_tca9548a.PCA9546A(i2c)

# ADS1115 INITIALISATION
# through beam readings
adc_1 = ADS_1.ADS1115(address=0x49, i2c=i2c)

channels_1 = [AnalogIn(adc_1,ADS_1.P0),AnalogIn(adc_1,ADS_1.P1),
AnalogIn(adc_1,ADS_1.P2),AnalogIn(adc_1,ADS_1.P3)]

# ADS7830 INITIALISATION
# deflected and reference beam readings
adc_2 = ADS_2.ADS7830(i2c)
REF = 4.2

channels_2 = [adc_2.read(i) for i in range(8)]

# BME280 INITIALISATION
bme_count = 4
bmes = [adafruit_bme280.Adafruit_BME280_I2C(mux[i], 0x76) for i in range(bme_count)]

# DS18B20 INITILISATION
out_temp_sensors = DS18B20.get_all_sensors()

# Script start...
duration = 30

out_file = open('data.txt','w')
string = """t(s) T1_ext T2_ext T3_ext T4_ext 
T1 T2 T3 T4 P1 P2 P3 P4 H1 H2 H3 H4
Turb1_180 Turb2_180 Turb3_180 Turb4_180
Turb1_90 Turb2_90 Turb3_90 Turb4_90
Turb1_ref Turb2_ref Turb3_ref Turb4_ref"""
split = string.split()
title = ','.join(split)
out_file.write(title + '\n')

with tqdm(total=duration, desc="Processing: ") as pbar:
    start = time.time()
    
    while True:
    # evaluating elapsed time at loop start effectively shifts timings by ~3s
    # this sets the time-scale at regular integer stesps
        current = time.time()
        elapsed = current - start
        
        if elapsed > (duration+1):
            print('Data recordng complete. Terminating...')
            pbar.update(duration - pbar.n)
            leds.finish()
            break
        else:
            pbar.update(elapsed - pbar.n)
            
        # turn on IR LEDs - sleep(1) to let signal settle
            leds.on()
            start_loop = time.time()
            time.sleep(1)
        
        # take DS18B20 readings first, reading temperature from 1-wire source file is the slowest operation
            out_temps = []
            for sensor in out_temp_sensors:
                out_temps.append(sensor.get_temperature())
                
        # BME readings
            T_s = [bme.temperature for bme in bmes]
            P_s = [bme.pressure for bme in bmes]
            H_s = [bme.humidity for bme in bmes]
            TPH = T_s + P_s + H_s
            
        # voltage readings from ADCs
        # 8-channel ADC reads the raw 16-bit number, divide this by 2**8 and multiply by reference voltage (REF)
            voltages_1 = [ch.voltage for ch in channels_1]
            voltages_2 = [((ch / 65535.0) * REF) for ch in channels_2]
            
            line = f"""{round(elapsed,3)},{",".join(map(str,out_temps))},{",".join(map(str,TPH))},
    {",".join(map(str,voltages_1))},{",".join(map(str,voltages_2))}"""
            end_loop = time.time()
            
        # turn off IR LEDs
            leds.off()
        
        # calculates correct pausing time
            diff = end_loop - start_loop
            dt = max(np.ceil(diff),diff) - diff
            pausing = dt + diff
            out_file.write(line + '\n')
            
        # sets interval between measurements
            interval = 15
            time.sleep(interval - pausing + dt)
    pbar.close()
out_file.close()
