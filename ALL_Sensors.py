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
import adafruit_pct2075
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Setup the LEDs
# choosing BCM mode - other imported packages utilise it
leds = LED_IO('bcm', 37)

# MULTIPLEXER INITIALISATION
i2c = busio.I2C(board.SCL, board.SDA)
mux = adafruit_tca9548a.PCA9546A(i2c)

# init external temp sensor
#pct = adafruit_pct2075.PCT2075(i2c)
#print("Temperature: %.2f C"%pct.temperature)

# ADS1115 INITIALISATION
# through beam readings
adc_1 = ADS_1.ADS1115(address=0x49, i2c=i2c)

channels_1 = [AnalogIn(adc_1,ADS_1.P0),AnalogIn(adc_1,ADS_1.P1),
AnalogIn(adc_1,ADS_1.P2),AnalogIn(adc_1,ADS_1.P3)]

# ADS7830 INITIALISATION
# deflected and reference beam readings
adc_2 = ADS_2.ADS7830(i2c)
REF = 4.2

# BME280 INITIALISATION
bme_count = 4
bmes = [adafruit_bme280.Adafruit_BME280_I2C(mux[i], 0x76) for i in range(bme_count)]
bme_ext = adafruit_bme280.Adafruit_BME280_I2C(i2c,0x77)
print("Temperature: %.2f C"%bme_ext.temperature)

# DS18B20 INITILISATION
order = [2, 0, 3, 1]
out_temp_sensors = np.array(DS18B20.get_all_sensors())
out_temp_sensors = out_temp_sensors[order]
 
# Script start...
duration = 259200 #72 hrs
# duration = 43200 #12 hrs
# duration = 86400 #24 hrs

out_file = open('data/250130_yeast_w303_0.1xypd.txt','w')
string = """time t(s) T_{env} P_{env} T1_{ext} T2_{ext} T3_{ext} T4_{ext} 
T1 T2 T3 T4 P1 P2 P3 P4 H1 H2 H3 H4
Turb1_{180} Turb2_{180} Turb3_{180} Turb4_{180}
Turb1_{135} Turb2_{135} Turb3_{135} Turb4_{135}
Turb1_{ref} Turb2_{ref} Turb3_{ref} Turb4_{ref}"""
split = string.split()
title = ','.join(split)
out_file.write(title + '\n')


# Prepare data storage for plotting
times = []
# create empty lists to store lists of points to plot against time
vials = [[] for _ in range(5)]

# Set up the plot
plt.ion()  # Turn on interactive mode
fig, ax1 = plt.subplots(figsize=(10, 6))
live_vials = [ax1.plot([], [], label=f'Vial {i+1}')[0] for i in range(5)]

ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Pressure (Vials) (mBar)')
ax1.tick_params(axis='y', labelcolor='r')

ax1.tick_params(axis='y', labelcolor='b')

plt.title('Real-time Pressure Data')
ax1.legend(loc='upper left')

# Function to update the plot
def update_plot():
    for i, line in enumerate(live_vials):
        line.set_data(times, vials[i])
    
    ax1.relim()
    ax1.autoscale_view()
    
    fig.canvas.draw()
    fig.canvas.flush_events()

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
            try:
        # take DS18B20 readings first, reading temperature from 1-wire source file is the slowest operation
                out_temps = []
                out_temps.append(bme_ext.temperature)
                out_temps.append(bme_ext.pressure)
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
                channels_2 = [adc_2.read(i) for i in range(8)]
                voltages_2 = [((ch / 65535.0) * REF) for ch in channels_2]
                line = f"""{current},{round(elapsed,3)},{",".join(map(str,out_temps))},{",".join(map(str,TPH))},{",".join(map(str,voltages_1))},{",".join(map(str,voltages_2))}"""
            except:
                line = f"""{round(elapsed,3)},{",".join(['NaN']*28)}"""
            finally:
                end_loop = time.time()
                
                # turn off IR LEDs
                leds.off()
                
                # Update plot data
                times.append(elapsed)
                for i, pressure in enumerate(P_s):
                    vials[i].append(pressure)
                vials[4].append(bme_ext.pressure)
            
            # Update the plot
                update_plot()
            
            # calculates correct pausing time
                diff = end_loop - start_loop
                dt = max(np.ceil(diff),diff) - diff
                pausing = dt + diff
                out_file.write(line + '\n')
                
            # sets interval between measurements
                interval = 30
                time.sleep(interval - pausing + dt)
    pbar.close()
out_file.close()
