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

class Bioreactor():
    """Class to manage all sensors and operations for the bioreactor"""
    
    def __init__(self):
        """Initialize all sensors and store them as instance attributes"""
        # LED setup
        self.leds = LED_IO('bcm', 37)
        
        # init external temp sensor - NO LONGER USED
        #pct = adafruit_pct2075.PCT2075(i2c)
        #print("Temperature: %.2f C"%pct.temperature)
        
        # Multiplexer setup
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.mux = adafruit_tca9548a.PCA9546A(self.i2c)
        
        # ADS1115 setup (through beam readings)
        self.adc_1 = ADS_1.ADS1115(address=0x49, i2c=self.i2c)
        self.channels_1 = [AnalogIn(self.adc_1, ADS_1.P0), 
                          AnalogIn(self.adc_1, ADS_1.P1),
                          AnalogIn(self.adc_1, ADS_1.P2), 
                          AnalogIn(self.adc_1, ADS_1.P3)]
        
        # ADS7830 setup (deflected and reference beam readings)
        self.adc_2 = ADS_2.ADS7830(self.i2c)
        self.REF = 4.2
        
        # BME280 setup
        self.bme_count = 4
        self.bmes = [adafruit_bme280.Adafruit_BME280_I2C(self.mux[i], 0x76) 
                     for i in range(self.bme_count)]
        self.bme_ext = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, 0x77)
        print(f"Temperature: {self.bme_ext.temperature:.2f} C")
        
        # DS18B20 setup
        order = [2, 0, 3, 1]
        self.out_temp_sensors = np.array(DS18B20.get_all_sensors())
        self.out_temp_sensors = self.out_temp_sensors[order]


    def get_external_temperatures(self):
        """Get all external temperature readings"""
        temps = []
        temps.append(self.bme_ext.temperature)
        temps.append(self.bme_ext.pressure)
        for sensor in self.out_temp_sensors:
            temps.append(sensor.get_temperature())
        return temps

    def get_bme_readings(self):
        """Get temperature, pressure, and humidity from all BME sensors"""
        T_s = [bme.temperature for bme in self.bmes]
        P_s = [bme.pressure for bme in self.bmes]
        H_s = [bme.humidity for bme in self.bmes]
        return T_s, P_s, H_s

    def get_voltage_readings(self):
        """Get all voltage readings from both ADCs"""
        voltages_1 = [ch.voltage for ch in self.channels_1]
        channels_2 = [self.adc_2.read(i) for i in range(8)]
        voltages_2 = [((ch / 65535.0) * self.REF) for ch in channels_2]
        return voltages_1, voltages_2

    def led_on(self):
        """Turn on the LED"""
        self.leds.on()

    def led_off(self):
        """Turn off the LED"""
        self.leds.off()

    def finish(self):
        """Clean up LED resources"""
        self.leds.finish()
