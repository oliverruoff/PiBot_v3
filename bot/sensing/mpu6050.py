#!/usr/bin/python
import smbus
import math

# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c


def read_byte(reg):
    return bus.read_byte_data(address, reg)


def read_word(reg):
    _h = bus.read_byte_data(address, reg)
    _l = bus.read_byte_data(address, reg+1)
    value = (_h << 8) + _l
    return value


def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


def dist(a, b):
    return math.sqrt((a*a)+(b*b))


def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)


def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)


def get_gyro_x():
    return read_word_2c(0x43)


def get_gyro_y():
    return read_word_2c(0x45)


def get_gyro_z():
    return read_word_2c(0x47)


def get_acc_x():
    return read_word_2c(0x3b)


def get_acc_y():
    return read_word_2c(0x3d)


def get_acc_z():
    return read_word_2c(0x3f)


bus = smbus.SMBus(1)  # bus = smbus.SMBus(0) fuer Revision 1
address = 0x68       # via i2cdetect

# Aktivieren, um das Modul ansprechen zu koennen
bus.write_byte_data(address, power_mgmt_1, 0)
