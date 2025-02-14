import time
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from bioreactor import Bioreactor

# Initialize the bioreactor
bioreactor = Bioreactor()

# Script start...
duration = 259200 #72 hrs

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
        current = time.time()
        elapsed = current - start
        
        if elapsed > (duration+1):
            print('Data recording complete. Terminating...')
            pbar.update(duration - pbar.n)
            bioreactor.finish()
            break
        else:
            pbar.update(elapsed - pbar.n)
            
            # turn on IR LEDs - sleep(1) to let signal settle
            bioreactor.led_on()
            start_loop = time.time()
            time.sleep(1)
            try:
                # Get all sensor readings
                out_temps = bioreactor.get_external_temperatures()
                T_s, P_s, H_s = bioreactor.get_bme_readings()
                TPH = T_s + P_s + H_s
                voltages_1, voltages_2 = bioreactor.get_voltage_readings()
                
                line = f"""{current},{round(elapsed,3)},{",".join(map(str,out_temps))},{",".join(map(str,TPH))},{",".join(map(str,voltages_1))},{",".join(map(str,voltages_2))}"""
            except:
                line = f"""{round(elapsed,3)},{",".join(['NaN']*28)}"""
            finally:
                end_loop = time.time()
                
                # turn off IR LEDs
                bioreactor.led_off()
                
                # Update plot data
                times.append(elapsed)
                for i, pressure in enumerate(P_s):
                    vials[i].append(pressure)
                vials[4].append(bioreactor.bme_ext.pressure)
                
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
