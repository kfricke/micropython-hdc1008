from machine import I2C
from time import sleep_ms

R_TEMP    = const(0x00)
R_HUMI    = const(0x01)
R_CONFIG  = const(0x02)
R_SER_ID1 = const(0xfb)
R_SER_ID2 = const(0xfc)
R_SER_ID3 = const(0xfd)

C_RST         = const(0b10000000)
C_HEAT_ON     = const(0b00100000)
C_HEAT_OFF    = const(0b00000000)
C_MODE_SINGLE = const(0b00000000)
C_MODE_BOTH   = const(0b00010000)
C_BTST        = const(0b00001000)
C_TEMP_14BIT  = const(0b00000000)
C_TEMP_11BIT  = const(0b00000100)
C_HUMI_14BIT  = const(0b00000000)
C_HUMI_11BIT  = const(0b00000001)
C_HUMI_8BIT   = const(0b00000010)

class HDC1008(object):
    """
    This class implements access to an Texas Instruments HDC1008 humidity and
    Temperature sensor.
    """

    def __init__(self, i2c, addr=0x40):
        """
        Initialize the sensor. The I2C bus for the sensor can be
        specified by its logical number or as an pre-initialized object.
        """
        if i2c == None or i2c.__class__ != I2C:
            raise ValueError('I2C object needed as argument!')
        self._i2c = i2c
        self._addr = addr
        self._heated = False

    def _send(self, buf):
        """
        Sends the given bufer object over I2C to the sensor.
        """
        self._i2c.send(buf, self._addr)
        
    def _recv(self, count):
        """
        Read bytes from the sensor using I2C. The byte count can be
        specified as an argument.
        """
        buf = bytearray(count)
        self._i2c.recv(buf, self._addr)
        return buf

    def _config(self, reg=None):
        """
        Set the given config register to configure the sensor.
        """
        if reg == None:
            self._send(R_CONFIG)
            return self._recv()
        else:
            if self._heated:
                reg = reg | C_HEAT_ON
            buf = bytearray(3)
            buf[0] = R_CONFIG
            buf[1] = reg
            self._send(buf)

    def heated(self, s=None):
        """
        Sets the heater status for measurements. If no argument is given
        returns the current state of the heater.
        """
        if s == None:
            return self._heated
        else:
            assert state in (True, False), 'Heater state must be a boolean value!'
            self._heated = state

    def battery_low(self):
        """Reads the battery status from the config register of the 
        sensor. In case the input voltage drops below 2.7 V this method 
        returns True."""
        raw = self._raw_temp()
        return (self._config()[0] & C_BTST) == C_BTST

    def reset(self):
        """Perform a software reset of the sensor."""
        buf = bytearray(3)
        buf[0] = R_CONFIG
        buf[1] = C_RST
        self._send(buf)
        sleep_ms(20)

    def _raw_temp(self, acc=14):
        """Read only the temperature from the seonsor. The accuracy can 
        be specified and is valid for 11 and 14 bits."""
        if not acc in (11, 14):
            raise ValueError('Temperature measure accuracy must be 11 or 14!')
        config = C_MODE_SINGLE
        if acc == 11:
            config = config | C_TEMP_11BIT
        elif acc == 14:
            config = config | C_TEMP_14BIT
        self._config(config)
        self._send(R_TEMP)
        sleep_ms(15)
        raw = self._recv()
        return raw[1] + (raw[0] << 8)
        
    def temp(self, acc=14):
        """Reads the temperature and returns degree in celsius. Use the 
        given accuracy in bits for the sensor reading. Valid accuracy 
        values are 8, 11 and 14."""
        if not acc in (11, 14):
            raise ValueError('Temperature measure accuracy must be 11 or 14!')
        return (self._raw_temp(acc) / 65536.0) * 165.0 - 40.0
        
    def _raw_humi(self, acc=14):
        if not acc in (8, 11, 14):
            raise ValueError('Humidity measure accuracy must be 8, 11 or 14!')
        config = C_MODE_SINGLE
        if acc == 8:
            config = config | C_HUMI_8BIT
        elif acc == 11:
            config = config | C_HUMI_11BIT
        elif acc == 14:
            config = config | C_HUMI_14BIT
        self._config(config)
        self._send(R_HUMI)
        sleep_ms(13)
        raw = self._recv()
        return raw[1] + (raw[0] << 8)
        
    def humi(self, acc=14):
        """Return the relative humidity in percent. Use the given accuracy
        in bits for the sensor reading. Valid accuracy values are 8, 11 
        and 14."""
        if not acc in (8, 11, 14):
            raise ValueError('Humidity measure accuracy must be 8, 11 or 14!')
        return (self._raw_humi(acc) / 65536.0) * 100.0

    def _raw_temp_humi(self, temp_acc=14, humi_acc=14):
        """Initiate a temperature and humidity sensor reading in one 
        operation. This safes time (and thereby energy). Accuracy for 
        both sensors can be specified. Same valid accuracy values apply to
        both seonsors."""
        if not temp_acc in (11, 14):
            raise ValueError('Temperature measure accuracy must be 11 or 14!')
        if not temp_acc in (8, 11, 14):
            raise ValueError('Humidity measure accuracy must be 8, 11 or 14!')
        config = C_MODE_BOTH
        if temp_acc == 11:
            config = config | C_TEMP_11BIT
        elif temp_acc == 14:
            config = config | C_TEMP_14BIT
        if humi_acc == 8:
            config = config | C_HUMI_8BIT
        elif humi_acc == 11:
            config = config | C_HUMI_11BIT
        elif humi_acc == 14:
            config = config | C_HUMI_14BIT
        self._config(config)
        self._send(R_TEMP)
        sleep_ms(20)
        raw = self._recv(4)
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
        (raw_temp, raw_humi) = self._raw_temp_humi(temp_acc, humi_acc)
        return (((raw_temp / 65536) * 165) - 40, (raw_humi / 65536) * 100.0)

    def serial(self):
        """Retrieve the serial number of the sensor."""
        self._send(R_SER_ID1)
        raw_1 = self._recv(2)
        self._send(R_SER_ID2)
        raw_2 = self._recv(2)
        self._send(R_SER_ID3)
        raw_3 = self._recv(2)
        serial = (raw_1[0] << 32) + (raw_1[1] << 24) + (raw_2[0] << 16) + (raw_2[1] << 8) + raw_3[0]
        return serial