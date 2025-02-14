import busio
import board
import adafruit_tca9548a
from adafruit_bme280 import basic as adafruit_bme280

i2c_obj = busio.I2C(board.SCL, board.SDA)
mux_obj = adafruit_tca9548a.PCA9546A(i2c_obj)
bme_count=1
bme_objs = [adafruit_bme280.Adafruit_BME280_I2C(mux_obj[i], 0x77) for i in range(bme_count)]
T_s = [bme.temperature for bme in bme_objs]
P_s = [bme.pressure for bme in bme_objs]
H_s = [bme.humidity for bme in bme_objs]
print(T_s)
