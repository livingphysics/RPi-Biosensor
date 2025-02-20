import time
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from bioreactor import Bioreactor
import csv

# Initialize the bioreactor
bioreactor = Bioreactor()

# Script start...
duration = 259200 #72 hrs

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

# Define fieldnames for CSV
fieldnames = ['elapsed', 'opt_dens1', 'opt_dens2', 'opt_dens3', 'opt_dens4',
              'opt_dens5', 'opt_dens6', 'opt_dens7', 'opt_dens8',
              'led_ref1', 'led_ref2', 'led_ref3', 'led_ref4',
              'int_temp1', 'int_temp2', 'int_temp3', 'int_temp4',
              'int_press1', 'int_press2', 'int_press3', 'int_press4',
              'int_humid1', 'int_humid2', 'int_humid3', 'int_humid4',
              'ext_temp1', 'ext_temp2', 'ext_temp3', 'ext_temp4',
              'atm_temp', 'atm_press']

def write_sensor_data_to_csv(writer, elapsed, opt_dens, led_ref, int_temp, int_press, int_humid, ext_temp, atm_temp, atm_press):
    """Write all sensor readings to CSV file.
    
    Args:
        writer: csv.DictWriter object
        elapsed: float, elapsed time in seconds
        opt_dens: list of 8 optical density readings
        led_ref: list of 4 LED reference readings
        int_temp: list of 4 internal temperature readings
        ext_temp: list of 4 external temperature readings
        atm_temp: float, atmospheric temperature
        atm_press: float, atmospheric pressure
    """
    data_row = {
        'elapsed': round(elapsed, 3),
        'opt_dens1': opt_dens[0], 'opt_dens2': opt_dens[1],
        'opt_dens3': opt_dens[2], 'opt_dens4': opt_dens[3],
        'opt_dens5': opt_dens[4], 'opt_dens6': opt_dens[5],
        'opt_dens7': opt_dens[6], 'opt_dens8': opt_dens[7],
        'led_ref1': led_ref[0], 'led_ref2': led_ref[1],
        'led_ref3': led_ref[2], 'led_ref4': led_ref[3],
        'int_temp1': int_temp[0], 'int_temp2': int_temp[1],
        'int_temp3': int_temp[2], 'int_temp4': int_temp[3],
        'int_press1': int_press[0], 'int_press2': int_press[1],
        'int_press3': int_press[2], 'int_press4': int_press[3],
        'int_humid1': int_humid[0], 'int_humid2': int_humid[1],
        'int_humid3': int_humid[2], 'int_humid4': int_humid[3],
        'ext_temp1': ext_temp[0], 'ext_temp2': ext_temp[1],
        'ext_temp3': ext_temp[2], 'ext_temp4': ext_temp[3],
        'atm_temp': atm_temp,
        'atm_press': atm_press
    }
    writer.writerow(data_row)

# Open CSV file with DictWriter
with open('data/250130_yeast_w303_0.1xypd.csv', 'w', newline='') as csvfile, tqdm(total=duration, desc="Processing: ") as pbar:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    start = time.time()
    

    elapsed = time.time() - start
    while elapsed <= duration + 1:
        pbar.update(elapsed - pbar.n)
        measurement_start = time.time()
            
        # turn on IR LEDs - sleep(1) to let signal settle
        bioreactor.led_on()
        time.sleep(1)

        # Get all sensor readings
        ext_temp = bioreactor.get_ext_temp()
        atm_temp = bioreactor.get_atm_temp()
        atm_press = bioreactor.get_atm_press()
        int_temp = bioreactor.get_int_temp()
        int_press = bioreactor.get_int_press()
        int_humid = bioreactor.get_int_humid()
        led_ref = bioreactor.get_led_ref()
        opt_dens = bioreactor.get_opt_dens()

        # turn off IR LEDs
        bioreactor.led_off()
        
        # Write sensor data to CSV
        write_sensor_data_to_csv(writer, elapsed, opt_dens, led_ref, int_temp, int_press, int_humid, ext_temp, atm_temp, atm_press)
        csvfile.flush()
        
        # Update plot
        times.append(elapsed)
        for i, pressure in enumerate(int_press):
            vials[i].append(pressure)
        vials[4].append(bioreactor.bme_ext.pressure)
        update_plot()
        
        # sets interval between measurements
        interval = 30
        measurement_end = time.time()
        measurement_time = measurement_end - measurement_start
        time.sleep(interval - measurement_time)

        elapsed = time.time() - start
    
    print('Data recording complete. Terminating...')
    pbar.update(duration - pbar.n)
    bioreactor.finish()
