import time
import numpy as np
from typing import List, Tuple
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from bioreactor import Bioreactor
from utils import (measure_and_write_sensor_data, create_csv_writer, 
                  setup_sensor_plot, update_sensor_plot)
import threading
from control import ring_light_thread

# Script start...
duration: int = 259200  # 72 hrs
# duration: int = 604800  # 168 hrs

# Prepare data storage for plotting
times: List[float] = []
sensor_data: List[List[float]] = [[] for _ in range(30)]

# Set up the plot
fig: Figure
ax: Axes
live_plots: List[Line2D]
leg: plt.legend
fig, ax, live_plots, leg = setup_sensor_plot()

# Main data collection loop
with open('data/250328_yeast_w303_0.1xypda_3e6.csv', 'w', newline='') as csvfile, tqdm(total=duration, desc="Processing: ") as pbar, Bioreactor() as bioreactor:
    writer = create_csv_writer(csvfile)
    start: float = time.time()
#    ring_light_thread: threading.Thread = threading.Thread(target=ring_light_thread, daemon=True, args=(bioreactor, start))
#    ring_light_thread.start()
    
    elapsed: float = time.time() - start
    while elapsed <= duration + 1:
        pbar.update(elapsed - pbar.n)
        measurement_start: float = time.time()
        
        data_row: List[float] = measure_and_write_sensor_data(bioreactor, writer, elapsed, csvfile)
        
        # Update plot data
        times.append(elapsed)
        update_sensor_plot(fig, ax, live_plots, times, sensor_data, data_row)
        
        # sets interval between measurements
        interval: int = 30
        measurement_end: float = time.time()
        measurement_time: float = measurement_end - measurement_start
        time.sleep(interval - measurement_time)

        elapsed = time.time() - start
    
    print('Data recording complete. Terminating...')
    pbar.update(duration - pbar.n)
