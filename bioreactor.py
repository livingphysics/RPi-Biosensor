from typing import List, Tuple, Optional, Union
import busio
import board
import adafruit_tca9548a
import adafruit_ads1x15.ads1115 as ADS_1
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads7830.ads7830 as ADS_2
from adafruit_bme280 import basic as adafruit_bme280
import numpy as np
from ds18b20 import DS18B20
import logging
from config import BioreactorConfig as cfg
import RPi.GPIO as IO
from contextlib import contextmanager
import time


# Configure logging using config
logging.basicConfig(
    level=getattr(logging, cfg.LOG_LEVEL),
    format=cfg.LOG_FORMAT
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
        self.board_mode = cfg.LED_MODE.upper()
        self.pin = cfg.LED_PIN
        if self.board_mode == 'BOARD':
            IO.setmode(IO.BOARD)
        elif self.board_mode == 'BCM':
            self.pin = cfg.bcm[self.pin]
            IO.setmode(IO.BCM)
        else:
            raise ValueError("Invalid board mode: use 'BCM' or 'BOARD'")
        IO.setup(self.pin, IO.OUT)
        IO.output(self.pin, 0)
    
    def init_optical_density(self) -> None:
        """Initialize the optical density sensors"""
        # ADS1115 setup (reference beam readings)
        self.adc_1: ADS_1.ADS1115 = ADS_1.ADS1115(
            address=cfg.ADS1115_ADDRESS, 
            i2c=self.i2c
        )
        self.channels_1: List[AnalogIn] = [
            AnalogIn(self.adc_1, ADS_1.P0),
            AnalogIn(self.adc_1, ADS_1.P1),
            AnalogIn(self.adc_1, ADS_1.P2),
            AnalogIn(self.adc_1, ADS_1.P3)
        ]
        
        # ADS7830 setup (through and deflected beam readings)
        self.adc_2: ADS_2.ADS7830 = ADS_2.ADS7830(self.i2c)
        self.REF: float = cfg.ADS7830_REF_VOLTAGE
    
    def init_int_temp_humid_press(self) -> None:
        """Initialize the humidity, temperature, and pressure sensors"""
        self.int_sensors: List[adafruit_bme280.Adafruit_BME280_I2C] = [
            adafruit_bme280.Adafruit_BME280_I2C(
                self.mux[i], 
                cfg.BME280_ADDRESS
            ) 
            for i in range(cfg.BME_COUNT)
        ]
    
    def init_ext_temp(self) -> None:
        """Initialize the external temperature sensors"""
        self.ext_sensors: np.ndarray = np.array(DS18B20.get_all_sensors())[
            cfg.EXTERNAL_SENSOR_ORDER
        ]
    
    def init_atm_temp_press(self) -> None:
        """Initialize the atmospheric temperature and pressure sensors"""
        self.atm_temp_sensor: adafruit_bme280.Adafruit_BME280_I2C = (
            adafruit_bme280.Adafruit_BME280_I2C(
                self.i2c, 
                cfg.BME280_ATM_ADDRESS
            )
        )
    
    def led_on(self) -> None:
        """Turn on the LED"""
        IO.output(self.pin, 1)

    def led_off(self) -> None:
        """Turn off the LED"""
        IO.output(self.pin, 0)

    def finish(self) -> None:
        """Clean up LED resources"""
        IO.output(self.pin, 0)
        IO.cleanup()

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

    @contextmanager
    def led_context(self, settle_time: float = 1.0):
        """Context manager for LED control"""
        try:
            # Turn IR LEDs on and wait for signal to settle
            self.led_on()
            time.sleep(settle_time)
            yield
        finally:
            # Turn IR LEDs off
            self.led_off()
