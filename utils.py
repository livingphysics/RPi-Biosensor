import csv
import matplotlib.pyplot as plt
from typing import List, Tuple, TextIO, Dict, Any
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.legend import Legend

def create_csv_writer(csv_file: TextIO) -> csv.DictWriter:
    """Create a CSV DictWriter with predefined headers for sensor data.
    
    Args:
        csv_file: file object opened for writing CSV data
        
    Returns:
        csv.DictWriter: Configured writer object with sensor data headers
    """
    fieldnames = [
        'elapsed', 
        'opt_dens1', 'opt_dens2', 'opt_dens3', 'opt_dens4',
        'opt_dens5', 'opt_dens6', 'opt_dens7', 'opt_dens8',
        'led_ref1', 'led_ref2', 'led_ref3', 'led_ref4',
        'int_temp1', 'int_temp2', 'int_temp3', 'int_temp4',
        'int_press1', 'int_press2', 'int_press3', 'int_press4',
        'int_humid1', 'int_humid2', 'int_humid3', 'int_humid4',
        'ext_temp1', 'ext_temp2', 'ext_temp3', 'ext_temp4',
        'atm_temp', 'atm_press'
    ]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    return writer

def measure_and_write_sensor_data(
    bioreactor: 'Bioreactor',
    writer: csv.DictWriter,
    elapsed: float,
    csvfile: TextIO
) -> Dict[str, float]:
    """Measure all sensor readings and write them to CSV file.
    
    Args:
        bioreactor: Bioreactor object for interfacing with sensors
        writer: csv.DictWriter object for writing data to CSV
        elapsed: float, elapsed time in seconds since start
        csvfile: file object for the CSV file being written to
    
    This function:
    1. Turns on IR LEDs and lets signal settle
    2. Gets readings from all sensors (optical density, temperature, pressure, humidity)
    3. Turns off IR LEDs
    4. Writes all sensor data to CSV file
    5. Flushes CSV buffer to ensure data is written

    Returns:
        Dict[str, float]: Dictionary containing all sensor readings
    """
    with bioreactor.led_context():
        ext_temp = bioreactor.get_ext_temp()
        atm_temp = bioreactor.get_atm_temp()
        atm_press = bioreactor.get_atm_press()
        int_temp = bioreactor.get_int_temp()
        int_press = bioreactor.get_int_press()
        int_humid = bioreactor.get_int_humid()
        led_ref = bioreactor.get_led_ref()
        opt_dens = bioreactor.get_opt_dens()
        
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
    csvfile.flush()
    
    return data_row

def setup_sensor_plot() -> Tuple[Figure, List[Axes], List[Line2D], Legend]:
    """Set up the real-time plotting of all sensor data with interactive legend.
    
    Returns:
        tuple: (figure, list of axes, list of plot lines, legend)
    """
    plt.ion()  # Turn on interactive mode
    fig = plt.figure(figsize=(12, 10))
    
    # Create 4 subplots
    axes: List[Axes] = []
    # Temperature subplot (internal, external, atmospheric)
    ax_temp: Axes = fig.add_subplot(411)
    # Pressure subplot (internal, atmospheric)
    ax_press: Axes = fig.add_subplot(412)
    # Optical measurements subplot (optical density and LED reference)
    ax_opt: Axes = fig.add_subplot(413)
    # Humidity subplot (all internal humidity sensors)
    ax_humid: Axes = fig.add_subplot(414)
    
    axes = [ax_temp, ax_press, ax_opt, ax_humid]
    live_plots: List[Line2D] = []

    # Temperature plots
    for i in range(4):
        line, = ax_temp.plot([], [], label=f'Internal Temp {i+1}')
        live_plots.append(line)
    for i in range(4):
        line, = ax_temp.plot([], [], label=f'External Temp {i+1}')
        live_plots.append(line)
    line, = ax_temp.plot([], [], label='Atmospheric Temp')
    live_plots.append(line)
    ax_temp.set_ylabel('Temperature')
    ax_temp.grid(True)

    # Pressure plots
    for i in range(4):
        line, = ax_press.plot([], [], label=f'Internal Pressure {i+1}')
        live_plots.append(line)
    line, = ax_press.plot([], [], label='Atmospheric Pressure')
    live_plots.append(line)
    ax_press.set_ylabel('Pressure')
    ax_press.grid(True)

    # Optical measurements
    for i in range(8):
        line, = ax_opt.plot([], [], label=f'Optical Density {i+1}')
        live_plots.append(line)
    for i in range(4):
        line, = ax_opt.plot([], [], label=f'LED Reference {i+1}')
        live_plots.append(line)
    ax_opt.set_ylabel('Voltage')
    ax_opt.grid(True)

    # Humidity plots
    for i in range(4):
        line, = ax_humid.plot([], [], label=f'Internal Humidity {i+1}')
        live_plots.append(line)
    ax_humid.set_ylabel('Humidity (%)')
    ax_humid.set_xlabel('Time (s)')
    ax_humid.grid(True)

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Create legend and make it clickable
    # Place legend to the right of the subplots
    lines = []
    labels = []
    for ax in axes:
        ax_lines, ax_labels = ax.get_legend_handles_labels()
        lines.extend(ax_lines)
        labels.extend(ax_labels)
    
    leg = fig.legend(lines, labels, loc='center left', 
                    bbox_to_anchor=(1.0, 0.5))
    
    for legline in leg.get_lines():
        legline.set_picker(True)  # Enable picking on the legend lines
        legline.set_pickradius(5)  # Define pick radius

    def on_pick(event: Any) -> None:
        legline = event.artist
        origline = live_plots[leg.get_lines().index(legline)]
        visible = not origline.get_visible()
        origline.set_visible(visible)
        # Change alpha of legend item
        legline.set_alpha(1.0 if visible else 0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', on_pick)
    
    plt.title('Real-time Sensor Data')
    
    return fig, axes, live_plots, leg

def update_sensor_plot(
    fig: Figure,
    axes: List[Axes],
    live_plots: List[Line2D],
    times: List[float],
    sensor_data: List[List[float]],
    data_row: Dict[str, float]
) -> None:
    """Update the sensor plot with new data.
    
    Args:
        fig: matplotlib figure object
        axes: list of matplotlib axis objects
        live_plots: list of plot lines
        times: list of time points
        sensor_data: list of lists containing sensor data history
        data_row: dictionary containing current sensor readings
    """
    # Update all sensor values using the correct keys
    # Internal temperature (4 sensors)
    for i in range(4):
        sensor_data[i].append(data_row[f'int_temp{i+1}'])
    
    # External temperature (4 sensors)
    for i in range(4):
        sensor_data[i+4].append(data_row[f'ext_temp{i+1}'])
    
    # Atmospheric temperature
    sensor_data[8].append(data_row['atm_temp'])
    
    # Internal pressure (4 sensors)
    for i in range(4):
        sensor_data[i+9].append(data_row[f'int_press{i+1}'])
    
    # Atmospheric pressure
    sensor_data[13].append(data_row['atm_press'])
    
    # Optical density (8 sensors)
    for i in range(8):
        sensor_data[i+14].append(data_row[f'opt_dens{i+1}'])
    
    # LED reference (4 sensors)
    for i in range(4):
        sensor_data[i+22].append(data_row[f'led_ref{i+1}'])
    
    # Internal humidity (4 sensors)
    for i in range(4):
        sensor_data[i+26].append(data_row[f'int_humid{i+1}'])

    # Update plot lines
    for i, line in enumerate(live_plots):
        line.set_data(times, sensor_data[i])
    
    # Update all subplots
    for ax in axes:
        ax.relim()
        ax.autoscale_view()
    
    fig.canvas.draw()
    fig.canvas.flush_events()
