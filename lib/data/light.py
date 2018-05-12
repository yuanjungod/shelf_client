import time
import ctypes
import time
from ctypes import *


class Light(object):
    def __init__(self):
        self.is_open = False
        self.open_time = -1
        self.lib = ctypes.cdll.LoadLibrary("./libled.so")
        self.func = self.lib.LED_Board_init
        self.func.restype = c_int
        print "led init ret:"
        self.fd = self.func()
        print self.fd
        self.open_func = self.lib.Open_Lights
        self.open_func.restype = c_int
        self.close_func = self.lib.Close_Lights
        self.close_func.restype = c_bool

    def open_light(self):
        self.is_open = True
        self.open_time = time.time()
        self.open_func(self.fd, 1)
        self.open_func(self.fd, 2)
        self.open_func(self.fd, 3)
        time.sleep(1)

    def close_light(self):
        self.is_open = False
        self.close_func(self.fd, 1)
        self.close_func(self.fd, 2)
        self.close_func(self.fd, 3)

    def auto_check(self):
        if self.is_open and time.time() - self.open_time > 300:
            self.close_light()


