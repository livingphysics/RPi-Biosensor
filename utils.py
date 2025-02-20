import csv

def create_csv_writer(csv_file):
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

def measure_and_write_sensor_data(bioreactor, writer, elapsed, csvfile):
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
