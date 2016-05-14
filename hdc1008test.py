"""Tests for the hdc1008 module"""

import machine
try:
    import esp
    esp.osdebug(None)
    i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))
except:
    pass
try:
    import pyb
    i2c = machine.I2C(sda=machine.Pin('X10'), scl=machine.Pin('X9'), freq=400000)
except:
    pass
import utime
from hdc1008 import HDC1008

hdc = HDC1008(i2c)
hdc.reset()
hdc.heater(False)
print("Sensor ID: %s" % (hex(hdc.serial)))

def read_sensors():
    print("Temperature (degree celsius): %.2f" % (hdc.temp()))
    print("Relative humidity (percent):  %.2f" % (hdc.humi()))
    print("Both sensors read at once:    %.2f  %.2f" % hdc.temp_humi())
    print("Battery low: %s" % (hdc.battery_low()))

print("Reading sensors 10 times using idle sleeping...")
for i in range(10):
    read_sensors()
    utime.sleep_ms(100)

#print("Reading sensors 10 times using power-saving pyb.stop() and rtc.wakeup() ...")
#rtc = pyb.RTC()
#rtc.wakeup(1000)
#for i in range(10):
#    read_sensors()
#    pyb.stop()
#rtc.wakeup(None)
