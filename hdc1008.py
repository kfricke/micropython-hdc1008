from machine import I2C
from utime import sleep_ms

REG_TEMP = const(0x00)
REG_HUMI = const(0x01)
REG_CFG = const(0x02)
REG_SER_ID1 = const(0xfb)
REG_SER_ID2 = const(0xfc)
REG_SER_ID3 = const(0xfd)

CFG_RST = const(0b10000000)
CFG_HEAT_ON = const(0b100000)
CFG_HEAT_OFF = const(0b0)
CFG_MODE_SINGLE = const(0b0)
CFG_MODE_BOTH = const(0b10000)
CFG_BTST = const(0b1000)
CFG_TEMP_14BIT = const(0b0)
CFG_TEMP_11BIT = const(0b100)
CFG_HUMI_14BIT = const(0b0)
CFG_HUMI_11BIT = const(0b1)
CFG_HUMI_8BIT = const(0b10)

RES_8_BIT  = const(1)
RES_11_BIT = const(2)
RES_14_BIT = const(3)

class HDC1008(object):
    def __init__(self, i2c, addr=0x40, heater=False):
        if i2c == None or i2c.__class__ != I2C:
            raise ValueError('I2C object needed as argument!')
        self._i2c = i2c
        self._addr = addr
        self._heater = heater
        self._tmp = bytearray(4)
        # Read the sensor serial ID
        self.serial = 0
        self._send_byte(REG_SER_ID1)
        self._recv(self._tmp, 2)
        self.serial += (self._tmp[0] << 32) + (self._tmp[1] << 24)
        self._send_byte(REG_SER_ID2)
        self._recv(self._tmp, 2)
        self.serial += (self._tmp[0] << 16) + (self._tmp[1] << 8)
        self._send_byte(REG_SER_ID3)
        self._recv(self._tmp, 2)
        self.serial += self._tmp[0]

    def _send_byte(self, b):
        self._tmp[0] = b
        self._i2c.writeto(self._addr, self._tmp[0:1])

    def _send_bytes(self, b):
        self._i2c.writeto(self._addr, b)
        
    def _recv(self, buf, c):
        buf[0:c] = self._i2c.readfrom(self._addr, c)

    def _config(self, reg=None):
        if reg is None:
            self._send_byte(REG_CFG)
            self._recv(self._tmp, 2)
            return self._tmp[0:2]
        else:
            if self._heater:
                reg = reg | CFG_HEAT_ON
            self._tmp[0] = REG_CFG
            self._tmp[1] = reg
            self._tmp[2] = 0 
            self._send_bytes(self._tmp[0:3])

    def heater(self, s=None):
        if s is not None:
            if s.__class__ != bool:
                raise ValueError('Heater state must be a boolean value or None!')
            else:
                self._heater = s
        else:
            return self._heater

    def battery_low(self):
        # one read command needed to have the config register defined, where 
        # we can read this flag from
        self._raw_temp(CFG_TEMP_11BIT)
        return (self._config()[0] & CFG_BTST) == CFG_BTST

    def reset(self):
        self._tmp[0] = REG_CFG
        self._tmp[1] = CFG_RST
        self._tmp[2] = 0 
        self._send_bytes(self._tmp[0:3])
        sleep_ms(20)

    def _raw_temp(self, acc):
        self._config(CFG_MODE_SINGLE | acc)
        self._send_byte(REG_TEMP)
        sleep_ms(15)
        self._recv(self._tmp, 2)
        return self._tmp[1] + (self._tmp[0] << 8)
        
    def temp(self, acc=CFG_TEMP_14BIT):
        return (self._raw_temp(acc) / 65536) * 165 - 40
        
    def _raw_humi(self, acc):
        self._config(CFG_MODE_SINGLE | acc)
        self._send_byte(REG_HUMI)
        sleep_ms(13)
        self._recv(self._tmp, 2)
        return self._tmp[1] + (self._tmp[0] << 8)
        
    def humi(self, acc=CFG_HUMI_14BIT):
        return (self._raw_humi(acc) / 65536.0) * 100.0

    def _raw_temp_humi(self, t_acc, h_acc):
        self._config(CFG_MODE_BOTH | t_acc | h_acc)
        self._send_byte(REG_TEMP)
        sleep_ms(20)
        self._recv(self._tmp, 4)
        return (self._tmp[1] + (self._tmp[0] << 8), self._tmp[3] + (self._tmp[2] << 8))

    def temp_humi(self, t_acc=CFG_TEMP_14BIT, h_acc=CFG_HUMI_14BIT):
        (raw_temp, raw_humi) = self._raw_temp_humi(t_acc, h_acc)
        return (((raw_temp / 65536) * 165) - 40, (raw_humi / 65536) * 100.0)

    def serial(self):
        return self.serial
