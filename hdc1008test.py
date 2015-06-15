"""Tests for the hdc1008 module"""

import pyb
from hdc1008 import HDC1008

i2c = pyb.I2C(2)
i2c.init(pyb.I2C.MASTER, baudrate=400000)

hdc = HDC1008(i2c)
hdc.reset()
hdc.heated(False)
print("Sensor ID: %s" % (hex(hdc.serial())))

while True:
    print("Temperature (degree celsius): %.2f" % (hdc.temp()))
    print("Relative humidity (percent):  %.2f" % (hdc.humi()))
    #print("Both sensors read at once:    %.2f  %.2f" % hdc.temp_humi())
    print("Battery low: %s" % (hdc.battery_low()))
    pyb.delay(1000)
