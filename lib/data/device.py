import ctypes
from ctypes import *
import time
import logging


class Device(object):
    def __init__(self):
        self.is_open = False
        self.lib = ctypes.cdll.LoadLibrary("./liblock.so")
        self.func = self.lib.lock_init
        self.func.restype = c_int
        print "lock init ret:"
        self.fd = self.func()
        logging.debug(self.fd)
        self.door_status = self.get_door_status1()
        self.lock_status = self.get_lock_status1()
        self.close_func = self.lib.close_door
        self.close_func.restype = c_int
        self.open_func = self.lib.open_door
        self.open_func.restype = c_int
        self.lock_status_func = self.lib.getLockState
        self.lock_status_func.restype = c_bool
        self.door_func_status = self.lib.getDoorState
        self.door_func_status.restype = c_bool

    def get_door_status1(self):
        while True:
            result = self.door_func_status(self.fd)
            print "Door Status:", result
            yield result
            time.sleep(1)

    def get_lock_status1(self):
        while True:
            result = self.lock_status_func(self.fd)
            print "Lock Status:", result
            yield result
            time.sleep(1)

    def lock_lock(self):
        result = self.close_func(self.fd)
        print "close lock", result
        return result

    def open_lock(self):
        result = self.open_func(self.fd)
        print "open door", result
        return result

    def get_door_status(self):
        for i in range(3):
            self.is_open = False
            yield True
        self.is_open = True
        yield False

    def open_door(self):
        self.is_open = True

    def close_door(self):
        if self.is_open:
            time.sleep(5)
            return True
        else:
            return False


if __name__ == "__main__":
    device = Device()
    print device.lock_lock()
    print device.open_lock()

