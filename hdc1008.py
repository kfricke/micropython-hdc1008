import pyb

class HDC1008(object):
    """This class implements access to an Texas Instruments HDC1008 Low 
    Power, High Accuracy Digital Humidity Sensor with Temperature Sensor.

    # Sensor Datasheet:
        http://www.ti.com/lit/ds/symlink/hdc1008.pdf

    # ToDo
        o DRDY pin usage
    """
    # Register map
    REG_TEMP = 0x00
    REG_HUMI = 0x01
    REG_CONFIG = 0x02
    REG_SER_ID1 = 0xfb
    REG_SER_ID2 = 0xfc
    REG_SER_ID3 = 0xfd

    # Config register bits are used for the MSB of the configuration 
    # register. The LSB must always stay 0 according to the datasheet.
    CFG_RST = 0b10000000
    CFG_HEAT_ON = 0b00100000
    CFG_HEAT_OFF = 0b00000000
    CFG_MODE_SINGLE = 0b00000000
    CFG_MODE_BOTH = 0b00010000
    CFG_BTST = 0b00001000
    CFG_TEMP_14BIT = 0b00000000
    CFG_TEMP_11BIT = 0b00000100
    CFG_HUMI_14BIT = 0b00000000
    CFG_HUMI_11BIT = 0b00000001
    CFG_HUMI_8BIT = 0b00000010

    def __init__(self, i2c, addr=0x40):
        """Initialize the sensor. The I2C bus for the sensor can be 
        specified by its logical number or as an pre-initialized object.
        """
        if type(i2c) == int:
            self.i2c = pyb.I2C(i2c)
            self.i2c.init(I2C.MASTER, baudrate=400000)
        elif type(i2c) == pyb.I2C:
            self.i2c = i2c
        self.__addr = addr
        self.__heated = False

    def __send(self, buf):
        """Sends the given bufer object over I2C to the sensor."""
        self.i2c.send(buf, self.__addr)
        
    def __recv(self, count=2):
        """Read bytes from the sensor using I2C. The byte count can be 
        specified as an argument. Default is to receive two bytes."""
        buf = bytearray(count)
        self.i2c.recv(buf, self.__addr)
        return buf

    def __config(self, reg=None):
        """Set the given config register to configure the sensor."""
        if reg == None:
            self.__send(self.REG_CONFIG)
            return self.__recv()
        else:
            if self.__heated:
                reg = reg | self.CFG_HEAT_ON
            buf = bytearray(3)
            buf[0] = self.REG_CONFIG
            buf[1] = reg
            self.__send(buf)

    def heated(self, state=None):
        """Sets the heater status for measurements. If no argument is 
        given returns the current state of the heater."""
        if state == None:
            return self.__heated
        else:
            self.__heated = state

    def battery_low(self):
        """Reads the battery status from the config register of the 
        sensor. In case the input voltage drops below 2.7 V this method 
        returns True."""
        # Initiate a temperature reading to update the battery bit of the
        # configuration register.
        raw = self.__raw_temp()
        return (self.__config()[0] & self.CFG_BTST) == self.CFG_BTST

    def reset(self):
        """Perform a software reset of the sensor."""
        buf = bytearray(3)
        buf[0] = self.REG_CONFIG
        buf[1] = self.CFG_RST
        self.__send(buf)
        # datasheet tells about 10-15 ms startup time
        pyb.delay(20)

    def __raw_temp(self, acc=14):
        """Read only the temperature from the seonsor. The accuracy can 
        be specified and is valid for 11 and 14 bits."""
        if not acc in (11, 14):
            raise ValueError('Temperature measure accuracy must be 11 or 14!')
        config = self.CFG_MODE_SINGLE
        if acc == 11:
            config = config | self.CFG_TEMP_11BIT
        elif acc == 14:
            config = config | self.CFG_TEMP_14BIT
        self.__config(config)
        self.__send(self.REG_TEMP)
        pyb.delay(15)
        raw = self.__recv()
        return raw[1] + (raw[0] << 8)
        
    def temp(self, acc=14):
        """Reads the temperature and returns degree in celsius. Use the 
        given accuracy in bits for the sensor reading. Valid accuracy 
        values are 8, 11 and 14."""
        if not acc in (11, 14):
            raise ValueError('Temperature measure accuracy must be 11 or 14!')
        return (self.__raw_temp(acc) / 65536.0) * 165.0 - 40.0
        
    def __raw_humi(self, acc=14):
        if not acc in (8, 11, 14):
            raise ValueError('Humidity measure accuracy must be 8, 11 or 14!')
        config = self.CFG_MODE_SINGLE
        if acc == 8:
            config = config | self.CFG_HUMI_8BIT
        elif acc == 11:
            config = config | self.CFG_HUMI_11BIT
        elif acc == 14:
            config = config | self.CFG_HUMI_14BIT
        self.__config(config)
        self.__send(self.REG_HUMI)
        pyb.delay(13)
        raw = self.__recv()
        return raw[1] + (raw[0] << 8)
        
    def humi(self, acc=14):
        """Return the relative humidity in percent. Use the given accuracy
        in bits for the sensor reading. Valid accuracy values are 8, 11 
        and 14."""
        if not acc in (8, 11, 14):
            raise ValueError('Humidity measure accuracy must be 8, 11 or 14!')
        return (self.__raw_humi(acc) / 65536.0) * 100.0

    def __raw_temp_humi(self, temp_acc=14, humi_acc=14):
        """Initiate a temperature and humidity sensor reading in one 
        operation. This safes time (and thereby energy). Accuracy for 
        both sensors can be specified. Same valid accuracy values apply to
        both seonsors."""
        if not temp_acc in (11, 14):
            raise ValueError('Temperature measure accuracy must be 11 or 14!')
        if not temp_acc in (8, 11, 14):
            raise ValueError('Humidity measure accuracy must be 8, 11 or 14!')
        config = self.CFG_MODE_BOTH
        if temp_acc == 11:
            config = config | self.CFG_TEMP_11BIT
        elif temp_acc == 14:
            config = config | self.CFG_TEMP_14BIT
        if humi_acc == 8:
            config = config | self.CFG_HUMI_8BIT
        elif humi_acc == 11:
            config = config | self.CFG_HUMI_11BIT
        elif humi_acc == 14:
            config = config | self.CFG_HUMI_14BIT
        self.__config(config)
        self.__send(self.REG_TEMP)
        pyb.delay(20)
        raw = self.__recv(4)
        raw_temp = raw[1] + (raw[0] << 8)
        raw_humi = raw[3] + (raw[2] << 8)
        return (raw_temp, raw_humi)

    def temp_humi(self, temp_acc=14, humi_acc=14):
        """Initiate a temperature and humidity sensor reading in one 
        operation. This safes time (and thereby energy). Accuracy for 
        both sensors can be specified. Same valid accuracy values apply to
        both seonsors."""
        if not temp_acc in (11, 14):
            raise ValueError('Temperature measure accuracy must be 11 or 14!')
        if not temp_acc in (8, 11, 14):
            raise ValueError('Humidity measure accuracy must be 8, 11 or 14!')
        (raw_temp, raw_humi) = self.__raw_temp_humi(temp_acc, humi_acc)
        return ((raw_temp / 65536.0) * 165.0 - 40.0, (raw_humi / 65536.0) * 100.0)

    def serial(self):
        """Retrieve the serial number of the sensor."""
        self.__send(self.REG_SER_ID1)
        raw_1 = self.__recv(2)
        self.__send(self.REG_SER_ID2)
        raw_2 = self.__recv(2)
        self.__send(self.REG_SER_ID3)
        raw_3 = self.__recv(2)
        serial = (raw_1[0] << 32) + (raw_1[1] << 24) + (raw_2[0] << 16) + (raw_2[1] << 8) + raw_3[0]
        return serial