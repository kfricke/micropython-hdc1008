"""Tests for the hdc1008 module"""
from hdc1008 import HDC1008
import utime

i2c = pyb.I2C(1)
i2c.init(pyb.I2C.MASTER, baudrate=400000)

hdc = HDC1008(i2c)
hdc.reset()
hdc.heated(False)
print("Sensor ID: %s" % (hex(hdc.serial())))

def read_sensors():
    print("Temperature (degree celsius): %.2f" % (hdc.temp()))
    print("Relative humidity (percent):  %.2f" % (hdc.humi()))
    print("Both sensors read at once:    %.2f  %.2f" % hdc.temp_humi())
    print("Battery low: %s" % (hdc.battery_low()))

print("Reading sensors 10 times using normal pyb.delay() ...")
for i in range(10):
    read_sensors()
    utime.sleep(1000)

#print("Reading sensors 10 times using power-saving pyb.stop() and rtc.wakeup() ...")
#rtc = pyb.RTC()
#rtc.wakeup(1000)
#for i in range(10):
#    read_sensors()
#    pyb.stop()
#rtc.wakeup(None)
