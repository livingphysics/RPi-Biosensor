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

# Initialize the bioreactor
bioreactor: Bioreactor = Bioreactor()

# Script start...
duration: int = 259200  # 72 hrs

# Prepare data storage for plotting
times: List[float] = []
sensor_data: List[List[float]] = [[] for _ in range(30)]

# Set up the plot
fig: Figure
ax: Axes
live_plots: List[Line2D]
leg: plt.legend
fig, ax, live_plots, leg = setup_sensor_plot()

# Ring light scheduler
def ring_light_scheduler(t: float) -> Tuple[int, int, int]:
    """Calculate RGB values for ring light based on time.
    
    Args:
        t: Time in seconds
        
    Returns:
        Tuple of RGB values (0-255) for red, green, blue
    """
    # One hour period = 3600 seconds
    # Map time to position in color wheel (0-360 degrees)
    angle = (t % 3600) * (360 / 3600)
    
    # Convert angle to RGB using HSV->RGB conversion
    # Hue = angle, Saturation = 1, Value = 1
    h = angle / 60  # Convert to 0-6 range
    c = 255  # Chroma = Value * Saturation * 255
    x = int(c * (1 - abs((h % 2) - 1)))
    
    if 0 <= h < 1:
        return (c, x, 0)
    elif 1 <= h < 2:
        return (x, c, 0)
    elif 2 <= h < 3:
        return (0, c, x)
    elif 3 <= h < 4:
        return (0, x, c)
    elif 4 <= h < 5:
        return (x, 0, c)
    else:  # 5 <= h < 6
        return (c, 0, x)

def ring_light_thread(bioreactor: Bioreactor, start: float) -> None:
    """Thread for updating the ring light"""
    while True:
        bioreactor.change_ring_light(ring_light_scheduler(time.time()-start))
        time.sleep(10)

# Main data collection loop
with open('data/250130_yeast_w303_0.1xypd.csv', 'w', newline='') as csvfile, tqdm(total=duration, desc="Processing: ") as pbar:
    writer = create_csv_writer(csvfile)
    start: float = time.time()
    ring_light_thread: threading.Thread = threading.Thread(target=ring_light_thread, daemon=True, args=(bioreactor, start))
    ring_light_thread.start()
    
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
    bioreactor.finish()
