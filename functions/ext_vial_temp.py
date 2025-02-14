from ds18b20 import DS18B20
import numpy as np

order = [2, 0, 3, 1]
out_temp_sensors = np.array(DS18B20.get_all_sensors())
out_temp_sensors = out_temp_sensors[order]
