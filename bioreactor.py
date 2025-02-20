from typing import List, Tuple, Optional, Union
import busio
import board
import adafruit_tca9548a
import adafruit_ads1x15.ads1115 as ADS_1
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads7830.ads7830 as ADS_2
from ledIO import LED_IO
from adafruit_bme280 import basic as adafruit_bme280
import numpy as np
import DS18B20
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# init external temp sensor - NO LONGER USED
#pct = adafruit_pct2075.PCT2075(i2c)
#print("Temperature: %.2f C"%pct.temperature)

class Bioreactor():
    """Class to manage all sensors and operations for the bioreactor"""
    
    def __init__(self) -> None:
        """Initialize all sensors and store them as instance attributes"""
        try:
            self.init_stream()
            self.init_leds()
            self.init_optical_density()
            self.init_int_temp_humid_press()
            self.init_ext_temp()
            self.init_atm_temp_press()
        except OSError as e:
            logging.error(f"Hardware initialization error: {e}")
            raise
        except Exception as e:
            logging.error(f"Some (probably non-hardware) error during initialization: {e}")
            raise

    def init_stream(self) -> None:
        """Initialize I2C bus if not already initialized"""
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.mux = adafruit_tca9548a.PCA9546A(self.i2c)
    
    def init_leds(self) -> None:
        """Initialize the LEDs"""
        self.leds: LED_IO = LED_IO('bcm', 37)
    
    def init_optical_density(self) -> None:
        """Initialize the optical density sensors"""
        # ADS1115 setup (reference beam readings)
        self.adc_1: ADS_1.ADS1115 = ADS_1.ADS1115(address=0x49, i2c=self.i2c)
        self.channels_1: List[AnalogIn] = [
            AnalogIn(self.adc_1, ADS_1.P0),
            AnalogIn(self.adc_1, ADS_1.P1),
            AnalogIn(self.adc_1, ADS_1.P2),
            AnalogIn(self.adc_1, ADS_1.P3)
        ]
        
        # ADS7830 setup (through and deflected beam readings)
        self.adc_2: ADS_2.ADS7830 = ADS_2.ADS7830(self.i2c)
        self.REF: float = 4.2
    
    def init_int_temp_humid_press(self) -> None:
        """Initialize the humidity, temperature, and pressure sensors"""
        self.bme_count: int = 4
        self.int_sensors: List[adafruit_bme280.Adafruit_BME280_I2C] = [
            adafruit_bme280.Adafruit_BME280_I2C(self.mux[i], 0x76) 
            for i in range(self.bme_count)
        ]
    
    def init_ext_temp(self) -> None:
        """Initialize the external temperature sensors"""
        order: List[int] = [2, 0, 3, 1]
        self.ext_sensors: np.ndarray = np.array(DS18B20.get_all_sensors())[order]
    
    def init_atm_temp_press(self) -> None:
        """Initialize the atmospheric temperature and pressure sensors"""
        self.atm_temp_sensor: adafruit_bme280.Adafruit_BME280_I2C = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, 0x77)
    
    def led_on(self) -> None:
        """Turn on the LED"""
        self.leds.on()

    def led_off(self) -> None:
        """Turn off the LED"""
        self.leds.off()

    def finish(self) -> None:
        """Clean up LED resources"""
        self.leds.finish()
    
    def get_led_ref(self) -> List[Union[float, str]]:
        """Get the LED reference voltage readings"""
        try:
            return [ch.voltage for ch in self.channels_1]
        except OSError as e:
            logging.error(f"Hardware error reading LED reference voltages: {e}")
            return ['NaN'] * len(self.channels_1)
        except Exception as e:
            logging.error(f"Unexpected error reading LED reference voltages: {e}")
            return ['NaN'] * len(self.channels_1)

    def get_opt_dens(self) -> List[Union[float, str]]:
        """Get the optical density readings from deflected beams"""
        try:
            return [self.adc_2.read(i) * self.REF / 65535.0 for i in range(8)]
        except OSError as e:
            logging.error(f"Hardware error reading optical density: {e}")
            return ['NaN'] * 8
        except Exception as e:
            logging.error(f"Unexpected error reading optical density: {e}")
            return ['NaN'] * 8
    
    def get_int_temp(self) -> List[Union[float, str]]:
        """Get the internal temperature readings"""
        try:
            return [sensor.temperature for sensor in self.int_sensors]
        except OSError as e:
            logging.error(f"Hardware error reading internal temperature: {e}")
            return ['NaN'] * len(self.int_sensors)
        except Exception as e:
            logging.error(f"Unexpected error reading internal temperature: {e}")
            return ['NaN'] * len(self.int_sensors)

    def get_int_press(self) -> List[Union[float, str]]:
        """Get the internal pressure readings"""
        try:
            return [sensor.pressure for sensor in self.int_sensors]
        except OSError as e:
            logging.error(f"Hardware error reading internal pressure: {e}")
            return ['NaN'] * len(self.int_sensors)
        except Exception as e:
            logging.error(f"Unexpected error reading internal pressure: {e}")
            return ['NaN'] * len(self.int_sensors)
    
    def get_int_humid(self) -> List[Union[float, str]]:
        """Get the internal humidity readings"""
        try:
            return [sensor.humidity for sensor in self.int_sensors]
        except OSError as e:
            logging.error(f"Hardware error reading internal humidity: {e}")
            return ['NaN'] * len(self.int_sensors)
        except Exception as e:
            logging.error(f"Unexpected error reading internal humidity: {e}")
            return ['NaN'] * len(self.int_sensors)
    
    def get_ext_temp(self) -> Union[np.ndarray, List[str]]:
        """Get the external temperature readings"""
        try:
            return self.ext_sensors.temperature
        except OSError as e:
            logging.error(f"Hardware error reading external temperature: {e}")
            return ['NaN'] * len(self.ext_sensors)
        except Exception as e:
            logging.error(f"Unexpected error reading external temperature: {e}")
            return ['NaN'] * len(self.ext_sensors)
    
    def get_atm_temp(self) -> Union[float, str]:
        """Get the atmospheric temperature reading"""
        try:
            return self.atm_temp_sensor.temperature
        except OSError as e:
            logging.error(f"Hardware error reading atmospheric temperature: {e}")
            return 'NaN'
        except Exception as e:
            logging.error(f"Unexpected error reading atmospheric temperature: {e}")
            return 'NaN'

    def get_atm_press(self) -> Union[float, str]:
        """Get the atmospheric pressure reading"""
        try:
            return self.atm_temp_sensor.pressure
        except OSError as e:
            logging.error(f"Hardware error reading atmospheric pressure: {e}")
            return 'NaN'
        except Exception as e:
            logging.error(f"Unexpected error reading atmospheric pressure: {e}")
            return 'NaN'
