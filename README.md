# micropython-hdc1008
This repository contains a MicroPython "driver" class for the Texas Instruments HDC1008 humidity and temperature sensor.

Currently only a reasonably small subset of the features the sensor is implemented.

## Implemented
* Read temperature or humidity alone
* Read temperature and humidity at once
* Retrieve different resolutions of the data readings. These do vary in accuracy and tme spent for acquiring the sensor data.
* Retrieve the sensor serial identifier unique to each physical sensor
* Activating and querying the builtin heater
* Query the battery low check built into the sensor

## Not yet implemented
* Usage of the DRDY (data ready) pin of the sensor