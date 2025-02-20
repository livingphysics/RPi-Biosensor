import time
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from bioreactor import Bioreactor
from utils import measure_and_write_sensor_data, create_csv_writer

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

# Open CSV file with DictWriter
with open('data/250130_yeast_w303_0.1xypd.csv', 'w', newline='') as csvfile, tqdm(total=duration, desc="Processing: ") as pbar:
    writer = create_csv_writer(csvfile)
    start = time.time()
    
    elapsed = time.time() - start
    while elapsed <= duration + 1:
        pbar.update(elapsed - pbar.n)
        measurement_start = time.time()
        
        data_row = measure_and_write_sensor_data(bioreactor, writer, elapsed, csvfile)
        
        # Update plot
        times.append(elapsed)
        for i in range(4):
            vials[i].append(data_row[f'int_press{i+1}'])
        vials[4].append(data_row['atm_press'])
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
